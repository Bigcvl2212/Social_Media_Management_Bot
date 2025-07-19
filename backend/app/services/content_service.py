"""
Content management service with database operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import os
import shutil
from pathlib import Path

from app.models.content import Content, ContentSchedule, ContentType, ContentStatus, ScheduleStatus
from app.models.user import User
from app.models.social_account import SocialAccount
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentScheduleCreate, ContentScheduleUpdate,
    ContentStatsResponse, CalendarEventResponse
)
from app.core.config import settings


class ContentService:
    """Service for content management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_content(self, content_data: ContentCreate, user_id: int, file_path: Optional[str] = None) -> Content:
        """Create new content"""
        content = Content(
            **content_data.model_dump(),
            created_by=user_id,
            file_path=file_path
        )
        
        # Generate thumbnail if it's an image or video
        if file_path and content.content_type in [ContentType.IMAGE, ContentType.VIDEO]:
            content.thumbnail_path = await self._generate_thumbnail(file_path, content.content_type)
        
        # Get file size if file exists
        if file_path and os.path.exists(file_path):
            content.file_size = os.path.getsize(file_path)
        
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        return content
    
    async def get_content_by_id(self, content_id: int, user_id: int) -> Optional[Content]:
        """Get content by ID (user must own it)"""
        query = select(Content).where(
            and_(Content.id == content_id, Content.created_by == user_id)
        ).options(selectinload(Content.schedules))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_content(
        self, 
        user_id: int, 
        page: int = 1, 
        size: int = 20, 
        content_type: Optional[ContentType] = None,
        status: Optional[ContentStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[Content], int]:
        """List user's content with pagination and filters"""
        
        query = select(Content).where(Content.created_by == user_id)
        
        # Apply filters
        if content_type:
            query = query.where(Content.content_type == content_type)
        
        if status:
            query = query.where(Content.status == status)
        
        if search:
            query = query.where(Content.title.ilike(f"%{search}%"))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Content.created_at)).offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        content_list = result.scalars().all()
        
        return list(content_list), total
    
    async def update_content(self, content_id: int, content_data: ContentUpdate, user_id: int) -> Optional[Content]:
        """Update content (user must own it)"""
        content = await self.get_content_by_id(content_id, user_id)
        if not content:
            return None
        
        update_data = content_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)
        
        await self.db.commit()
        await self.db.refresh(content)
        return content
    
    async def delete_content(self, content_id: int, user_id: int) -> bool:
        """Delete content and associated files"""
        content = await self.get_content_by_id(content_id, user_id)
        if not content:
            return False
        
        # Delete associated files
        if content.file_path and os.path.exists(content.file_path):
            os.remove(content.file_path)
        
        if content.thumbnail_path and os.path.exists(content.thumbnail_path):
            os.remove(content.thumbnail_path)
        
        await self.db.delete(content)
        await self.db.commit()
        return True
    
    async def schedule_content(self, schedule_data: ContentScheduleCreate, user_id: int) -> Optional[ContentSchedule]:
        """Schedule content for posting"""
        # Verify user owns the content
        content = await self.get_content_by_id(schedule_data.content_id, user_id)
        if not content:
            return None
        
        # Verify user has access to the social account
        social_account_query = select(SocialAccount).where(
            and_(SocialAccount.id == schedule_data.social_account_id, SocialAccount.user_id == user_id)
        )
        social_account_result = await self.db.execute(social_account_query)
        social_account = social_account_result.scalar_one_or_none()
        
        if not social_account:
            return None
        
        schedule = ContentSchedule(**schedule_data.model_dump())
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def get_scheduled_content(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[ScheduleStatus] = None
    ) -> List[ContentSchedule]:
        """Get scheduled content for calendar view"""
        
        # Build query with joins to get user's content
        query = select(ContentSchedule).join(Content).where(Content.created_by == user_id)
        
        if start_date:
            query = query.where(ContentSchedule.scheduled_time >= start_date)
        
        if end_date:
            query = query.where(ContentSchedule.scheduled_time <= end_date)
        
        if status:
            query = query.where(ContentSchedule.status == status)
        
        query = query.order_by(ContentSchedule.scheduled_time)
        query = query.options(selectinload(ContentSchedule.content), selectinload(ContentSchedule.social_account))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_calendar_events(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[CalendarEventResponse]:
        """Get calendar events for the dashboard"""
        
        schedules = await self.get_scheduled_content(user_id, start_date, end_date)
        
        events = []
        for schedule in schedules:
            events.append(CalendarEventResponse(
                id=schedule.id,
                title=schedule.content.title,
                content_type=schedule.content.content_type,
                scheduled_time=schedule.scheduled_time,
                status=schedule.status,
                platform=schedule.social_account.platform,
                content_id=schedule.content_id,
                social_account_id=schedule.social_account_id,
                thumbnail_path=schedule.content.thumbnail_path
            ))
        
        return events
    
    async def update_schedule(self, schedule_id: int, schedule_data: ContentScheduleUpdate, user_id: int) -> Optional[ContentSchedule]:
        """Update a content schedule"""
        
        # Get schedule with content to verify ownership
        query = select(ContentSchedule).join(Content).where(
            and_(ContentSchedule.id == schedule_id, Content.created_by == user_id)
        )
        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            return None
        
        update_data = schedule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def delete_schedule(self, schedule_id: int, user_id: int) -> bool:
        """Delete a content schedule"""
        
        query = select(ContentSchedule).join(Content).where(
            and_(ContentSchedule.id == schedule_id, Content.created_by == user_id)
        )
        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            return False
        
        await self.db.delete(schedule)
        await self.db.commit()
        return True
    
    async def get_content_stats(self, user_id: int) -> ContentStatsResponse:
        """Get content statistics for dashboard"""
        
        # Total content count
        total_query = select(func.count()).select_from(Content).where(Content.created_by == user_id)
        total_result = await self.db.execute(total_query)
        total_content = total_result.scalar()
        
        # Content by type
        type_query = select(Content.content_type, func.count()).where(Content.created_by == user_id).group_by(Content.content_type)
        type_result = await self.db.execute(type_query)
        by_type = {content_type: count for content_type, count in type_result.fetchall()}
        
        # Content by status
        status_query = select(Content.status, func.count()).where(Content.created_by == user_id).group_by(Content.status)
        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.fetchall()}
        
        # Recent uploads (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_query = select(func.count()).select_from(Content).where(
            and_(Content.created_by == user_id, Content.created_at >= thirty_days_ago)
        )
        recent_result = await self.db.execute(recent_query)
        recent_uploads = recent_result.scalar()
        
        # AI generated content count
        ai_query = select(func.count()).select_from(Content).where(
            and_(Content.created_by == user_id, Content.ai_generated == True)
        )
        ai_result = await self.db.execute(ai_query)
        ai_generated_count = ai_result.scalar()
        
        return ContentStatsResponse(
            total_content=total_content,
            by_type=by_type,
            by_status=by_status,
            recent_uploads=recent_uploads,
            ai_generated_count=ai_generated_count
        )
    
    async def _generate_thumbnail(self, file_path: str, content_type: ContentType) -> Optional[str]:
        """Generate thumbnail for content (placeholder implementation)"""
        # This is a placeholder - in a real implementation, you would:
        # - For images: resize and optimize
        # - For videos: extract frame and create thumbnail
        # For now, just return the original path
        return file_path
    
    async def save_uploaded_file(self, file_content: bytes, filename: str, user_id: int) -> str:
        """Save uploaded file to storage"""
        
        # Create user-specific upload directory
        upload_dir = Path(settings.UPLOAD_DIR) / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(filename).suffix
        unique_filename = f"{timestamp}_{filename}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)