"""
Content Scheduler Service
Background scheduler that auto-posts approved content at scheduled times.
Uses APScheduler for cron-like task execution without Redis/Celery.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.content import Content, ContentSchedule, ContentStatus, ScheduleStatus
from app.services.facebook_service import FacebookService

import logging
logger = logging.getLogger(__name__)


class ContentSchedulerService:
    """Manages content queue, scheduling, and auto-posting."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.fb = FacebookService()
        self._running = False

    # ── Lifecycle ────────────────────────────────────────────

    def start(self):
        """Start the background scheduler.  Call once at app startup."""
        if self._running:
            return
        # Check for due posts every 60 seconds
        self.scheduler.add_job(
            self._process_due_posts,
            trigger=IntervalTrigger(seconds=60),
            id="post_scheduler",
            replace_existing=True,
        )
        self.scheduler.start()
        self._running = True
        logger.info("Content scheduler started (checking every 60s)")

    def stop(self):
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Content scheduler stopped")

    # ── Queue Management ─────────────────────────────────────

    async def schedule_content(
        self,
        db: AsyncSession,
        content_id: int,
        publish_at: datetime,
        platform: str = "facebook",
    ) -> Dict[str, Any]:
        """Add content to the posting queue at a specific time."""
        schedule = ContentSchedule(
            content_id=content_id,
            scheduled_time=publish_at,
            platform=platform,
            status=ScheduleStatus.PENDING,
        )
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        logger.info(f"Scheduled content {content_id} for {publish_at} on {platform}")
        return {
            "schedule_id": schedule.id,
            "content_id": content_id,
            "publish_at": publish_at.isoformat(),
            "platform": platform,
            "status": "pending",
        }

    async def cancel_scheduled(self, db: AsyncSession, schedule_id: int) -> Dict[str, Any]:
        """Cancel a pending scheduled post."""
        stmt = (
            update(ContentSchedule)
            .where(and_(ContentSchedule.id == schedule_id, ContentSchedule.status == ScheduleStatus.PENDING))
            .values(status=ScheduleStatus.CANCELLED)
        )
        result = await db.execute(stmt)
        await db.commit()
        cancelled = result.rowcount > 0
        return {"schedule_id": schedule_id, "cancelled": cancelled}

    async def get_queue(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get the content posting queue."""
        stmt = select(ContentSchedule).order_by(ContentSchedule.scheduled_time.asc()).limit(limit)
        if status:
            stmt = stmt.where(ContentSchedule.status == status)
        result = await db.execute(stmt)
        schedules = result.scalars().all()
        return [
            {
                "schedule_id": s.id,
                "content_id": s.content_id,
                "scheduled_time": s.scheduled_time.isoformat() if s.scheduled_time else None,
                "platform": s.platform,
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
            }
            for s in schedules
        ]

    # ── Optimal Posting Times ────────────────────────────────

    def get_optimal_times(self) -> List[Dict[str, str]]:
        """Return best posting times for a gym Facebook page.
        Based on fitness industry data — these are CST times.
        """
        return [
            {"day": "Monday", "time": "06:00", "reason": "Morning motivation seekers"},
            {"day": "Monday", "time": "17:00", "reason": "Post-work gym crowd"},
            {"day": "Tuesday", "time": "12:00", "reason": "Lunch break scrollers"},
            {"day": "Wednesday", "time": "06:00", "reason": "Mid-week motivation"},
            {"day": "Wednesday", "time": "18:00", "reason": "Hump day wind-down"},
            {"day": "Thursday", "time": "07:00", "reason": "Early birds"},
            {"day": "Friday", "time": "12:00", "reason": "Weekend planning"},
            {"day": "Saturday", "time": "09:00", "reason": "Weekend warriors"},
            {"day": "Sunday", "time": "10:00", "reason": "Week-ahead planners"},
        ]

    # ── Background Processor ─────────────────────────────────

    async def _process_due_posts(self):
        """Check for and publish any posts that are due.  Runs every 60s."""
        try:
            async with AsyncSessionLocal() as db:
                now = datetime.now(timezone.utc)
                stmt = (
                    select(ContentSchedule)
                    .where(
                        and_(
                            ContentSchedule.status == ScheduleStatus.PENDING,
                            ContentSchedule.scheduled_time <= now,
                        )
                    )
                    .order_by(ContentSchedule.scheduled_time.asc())
                    .limit(10)
                )
                result = await db.execute(stmt)
                due_posts = result.scalars().all()

                for schedule in due_posts:
                    await self._publish_one(db, schedule)

        except Exception as e:
            logger.error(f"Scheduler tick error: {e}")

    async def _publish_one(self, db: AsyncSession, schedule: ContentSchedule):
        """Publish a single scheduled post."""
        try:
            # Mark processing
            schedule.status = ScheduleStatus.PROCESSING
            await db.commit()

            # Load content
            content_result = await db.execute(
                select(Content).where(Content.id == schedule.content_id)
            )
            content = content_result.scalar_one_or_none()
            if not content:
                schedule.status = ScheduleStatus.FAILED
                schedule.error_message = "Content not found"
                await db.commit()
                return

            # Post to Facebook
            post_result: Dict[str, Any] = {}
            caption = content.caption or content.title or ""

            if content.media_url and content.content_type and "video" in str(content.content_type).lower():
                post_result = await self.fb.post_video(
                    video_path=content.media_url,
                    description=caption,
                    title=content.title or "",
                )
            elif content.media_url:
                post_result = await self.fb.post_photo(
                    image_path=content.media_url,
                    caption=caption,
                )
            else:
                post_result = await self.fb.post_text(message=caption)

            if post_result.get("status") == "posted":
                schedule.status = ScheduleStatus.COMPLETED
                schedule.published_post_id = post_result.get("post_id", "")
                content.status = ContentStatus.PUBLISHED
                logger.info(f"Published scheduled content {content.id} → post {post_result.get('post_id')}")
            else:
                schedule.status = ScheduleStatus.FAILED
                schedule.error_message = post_result.get("error", "Unknown error")
                logger.warning(f"Failed to publish content {content.id}: {schedule.error_message}")

            await db.commit()

        except Exception as e:
            logger.error(f"Error publishing schedule {schedule.id}: {e}")
            schedule.status = ScheduleStatus.FAILED
            schedule.error_message = str(e)
            await db.commit()
