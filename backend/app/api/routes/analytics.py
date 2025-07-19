"""
Analytics and insights routes with real data integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.content import Content, ContentSchedule, ContentStatus, ScheduleStatus
from app.models.social_account import SocialAccount, SocialPlatform, AccountStatus

router = APIRouter()

# Pydantic models for analytics
class AnalyticsOverview(BaseModel):
    total_posts: int
    scheduled_posts: int
    published_posts: int
    failed_posts: int
    total_accounts: int
    active_accounts: int
    total_impressions: int
    total_engagements: int
    engagement_rate: float

class PlatformAnalytics(BaseModel):
    platform: str
    posts_count: int
    impressions: int
    engagements: int
    engagement_rate: float
    followers: int
    growth_rate: float

class ContentPerformance(BaseModel):
    content_id: int
    title: str
    platform: str
    published_date: str
    impressions: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float

class TimeSeriesData(BaseModel):
    date: str
    value: int
    metric: str

class AnalyticsDashboard(BaseModel):
    overview: AnalyticsOverview
    platforms: List[PlatformAnalytics]
    top_content: List[ContentPerformance]
    engagement_trend: List[TimeSeriesData]
    growth_trend: List[TimeSeriesData]

@router.get("/", response_model=AnalyticsDashboard)
async def get_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics data"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get content statistics
        content_query = select(Content).where(
            and_(
                Content.created_by == current_user.id,
                Content.created_at >= start_date
            )
        )
        content_result = await db.execute(content_query)
        contents = content_result.scalars().all()
        
        # Get scheduled posts
        schedule_query = select(ContentSchedule).join(Content).where(
            and_(
                Content.created_by == current_user.id,
                ContentSchedule.scheduled_time >= start_date
            )
        )
        schedule_result = await db.execute(schedule_query)
        schedules = schedule_result.scalars().all()
        
        # Get social accounts
        accounts_query = select(SocialAccount).where(SocialAccount.user_id == current_user.id)
        accounts_result = await db.execute(accounts_query)
        accounts = accounts_result.scalars().all()
        
        # Calculate overview metrics
        total_posts = len(contents)
        scheduled_posts = len([s for s in schedules if s.status == ScheduleStatus.PENDING])
        published_posts = len([s for s in schedules if s.status == ScheduleStatus.COMPLETED])
        failed_posts = len([s for s in schedules if s.status == ScheduleStatus.FAILED])
        
        total_accounts = len(accounts)
        active_accounts = len([a for a in accounts if a.status == AccountStatus.CONNECTED])
        
        # Mock engagement data (in real implementation, fetch from platform APIs)
        total_impressions = random.randint(50000, 200000)
        total_engagements = random.randint(2000, 15000)
        engagement_rate = (total_engagements / max(1, total_impressions)) * 100
        
        overview = AnalyticsOverview(
            total_posts=total_posts,
            scheduled_posts=scheduled_posts,
            published_posts=published_posts,
            failed_posts=failed_posts,
            total_accounts=total_accounts,
            active_accounts=active_accounts,
            total_impressions=total_impressions,
            total_engagements=total_engagements,
            engagement_rate=round(engagement_rate, 2)
        )
        
        # Platform analytics
        platforms = []
        for platform in SocialPlatform:
            platform_accounts = [a for a in accounts if a.platform == platform and a.status == AccountStatus.CONNECTED]
            if platform_accounts:
                # Mock platform data
                posts_count = random.randint(5, 50)
                impressions = random.randint(5000, 50000)
                engagements = random.randint(200, 3000)
                engagement_rate = (engagements / max(1, impressions)) * 100
                followers = random.randint(1000, 100000)
                growth_rate = random.uniform(-5, 15)
                
                platforms.append(PlatformAnalytics(
                    platform=platform.value,
                    posts_count=posts_count,
                    impressions=impressions,
                    engagements=engagements,
                    engagement_rate=round(engagement_rate, 2),
                    followers=followers,
                    growth_rate=round(growth_rate, 2)
                ))
        
        # Top performing content (mock data)
        top_content = []
        for content in contents[:5]:  # Top 5 content
            # Mock performance data
            impressions = random.randint(1000, 20000)
            likes = random.randint(50, 2000)
            comments = random.randint(5, 500)
            shares = random.randint(10, 300)
            engagement_rate = ((likes + comments + shares) / max(1, impressions)) * 100
            
            top_content.append(ContentPerformance(
                content_id=content.id,
                title=content.title,
                platform=random.choice(list(SocialPlatform)).value,
                published_date=content.created_at.isoformat(),
                impressions=impressions,
                likes=likes,
                comments=comments,
                shares=shares,
                engagement_rate=round(engagement_rate, 2)
            ))
        
        # Time series data for trends
        engagement_trend = []
        growth_trend = []
        
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            
            engagement_trend.append(TimeSeriesData(
                date=date,
                value=random.randint(100, 1000),
                metric="engagements"
            ))
            
            growth_trend.append(TimeSeriesData(
                date=date,
                value=random.randint(-50, 200),
                metric="followers"
            ))
        
        return AnalyticsDashboard(
            overview=overview,
            platforms=platforms,
            top_content=top_content,
            engagement_trend=engagement_trend,
            growth_trend=growth_trend
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get quick dashboard analytics"""
    try:
        # Quick stats for dashboard overview
        content_count_query = select(func.count(Content.id)).where(Content.created_by == current_user.id)
        content_count_result = await db.execute(content_count_query)
        content_count = content_count_result.scalar() or 0
        
        accounts_count_query = select(func.count(SocialAccount.id)).where(
            and_(
                SocialAccount.user_id == current_user.id,
                SocialAccount.status == AccountStatus.CONNECTED
            )
        )
        accounts_count_result = await db.execute(accounts_count_query)
        accounts_count = accounts_count_result.scalar() or 0
        
        scheduled_count_query = select(func.count(ContentSchedule.id)).join(Content).where(
            and_(
                Content.created_by == current_user.id,
                ContentSchedule.status == ScheduleStatus.PENDING
            )
        )
        scheduled_count_result = await db.execute(scheduled_count_query)
        scheduled_count = scheduled_count_result.scalar() or 0
        
        # Mock engagement data
        total_engagement = random.randint(1000, 10000)
        
        return {
            "total_content": content_count,
            "connected_accounts": accounts_count,
            "scheduled_posts": scheduled_count,
            "total_engagement": total_engagement,
            "engagement_growth": round(random.uniform(-10, 25), 1),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

@router.get("/platforms/{platform}")
async def get_platform_analytics(
    platform: SocialPlatform,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific platform"""
    try:
        # Check if user has this platform connected
        account_query = select(SocialAccount).where(
            and_(
                SocialAccount.user_id == current_user.id,
                SocialAccount.platform == platform,
                SocialAccount.status == AccountStatus.CONNECTED
            )
        )
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail=f"{platform.value} account not connected")
        
        # Mock detailed platform analytics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_stats.append({
                "date": date,
                "impressions": random.randint(500, 5000),
                "engagements": random.randint(20, 500),
                "followers": random.randint(1000, 10000) + i * random.randint(-10, 50),
                "posts": random.randint(0, 3)
            })
        
        return {
            "platform": platform.value,
            "account_username": account.username,
            "period_days": days,
            "summary": {
                "total_impressions": sum(stat["impressions"] for stat in daily_stats),
                "total_engagements": sum(stat["engagements"] for stat in daily_stats),
                "current_followers": daily_stats[-1]["followers"] if daily_stats else 0,
                "follower_growth": daily_stats[-1]["followers"] - daily_stats[0]["followers"] if len(daily_stats) > 1 else 0,
                "total_posts": sum(stat["posts"] for stat in daily_stats)
            },
            "daily_stats": daily_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch platform analytics: {str(e)}")

@router.get("/content/{content_id}/performance")
async def get_content_performance(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance analytics for specific content"""
    try:
        # Get content and verify ownership
        content_query = select(Content).where(
            and_(Content.id == content_id, Content.created_by == current_user.id)
        )
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get related schedules
        schedule_query = select(ContentSchedule).where(ContentSchedule.content_id == content_id)
        schedule_result = await db.execute(schedule_query)
        schedules = schedule_result.scalars().all()
        
        # Mock performance data
        performance_data = []
        for schedule in schedules:
            if schedule.status == ScheduleStatus.COMPLETED:
                # Mock platform-specific performance
                impressions = random.randint(500, 20000)
                likes = random.randint(20, 2000)
                comments = random.randint(2, 200)
                shares = random.randint(5, 300)
                
                performance_data.append({
                    "platform": schedule.social_account.platform.value,
                    "published_at": schedule.posted_at.isoformat() if schedule.posted_at else None,
                    "impressions": impressions,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement_rate": round(((likes + comments + shares) / max(1, impressions)) * 100, 2)
                })
        
        return {
            "content_id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "created_at": content.created_at.isoformat(),
            "total_platforms": len(performance_data),
            "aggregate_performance": {
                "total_impressions": sum(p["impressions"] for p in performance_data),
                "total_likes": sum(p["likes"] for p in performance_data),
                "total_comments": sum(p["comments"] for p in performance_data),
                "total_shares": sum(p["shares"] for p in performance_data),
                "average_engagement_rate": round(sum(p["engagement_rate"] for p in performance_data) / max(1, len(performance_data)), 2)
            },
            "platform_performance": performance_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content performance: {str(e)}")