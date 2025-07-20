"""
Competitor analysis service for tracking and analyzing competitor performance
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from loguru import logger

from app.models.competitor_analysis import CompetitorAccount, CompetitorAnalytics, CompetitorContent
from app.models.user import User


class CompetitorAnalysisService:
    """Service for competitor tracking and analysis"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_competitor(
        self, 
        user_id: int, 
        platform: str, 
        username: str, 
        display_name: Optional[str] = None
    ) -> CompetitorAccount:
        """Add a new competitor to track"""
        try:
            # Check if competitor already exists for this user
            existing_query = select(CompetitorAccount).where(
                and_(
                    CompetitorAccount.user_id == user_id,
                    CompetitorAccount.platform == platform.lower(),
                    CompetitorAccount.username == username.lower()
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                logger.warning(f"Competitor {username} on {platform} already exists for user {user_id}")
                return existing
            
            # Create new competitor account
            competitor = CompetitorAccount(
                user_id=user_id,
                platform=platform.lower(),
                username=username.lower(),
                display_name=display_name or username,
                profile_url=f"https://{platform.lower()}.com/{username}",
                # Mock initial data - in real implementation, fetch from platform API
                follower_count=random.randint(1000, 100000),
                following_count=random.randint(100, 5000),
                post_count=random.randint(50, 2000)
            )
            
            self.db.add(competitor)
            await self.db.commit()
            await self.db.refresh(competitor)
            
            # Generate initial analytics
            await self._generate_initial_analytics(competitor)
            
            logger.info(f"Added competitor {username} on {platform} for user {user_id}")
            return competitor
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding competitor: {e}")
            raise
    
    async def get_user_competitors(self, user_id: int) -> List[CompetitorAccount]:
        """Get all competitors for a user"""
        try:
            query = select(CompetitorAccount).where(
                and_(
                    CompetitorAccount.user_id == user_id,
                    CompetitorAccount.is_active == True
                )
            ).order_by(desc(CompetitorAccount.created_at))
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting user competitors: {e}")
            return []
    
    async def get_competitor_analytics(
        self, 
        competitor_id: int, 
        days: int = 30
    ) -> List[CompetitorAnalytics]:
        """Get analytics for a specific competitor"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = select(CompetitorAnalytics).where(
                and_(
                    CompetitorAnalytics.competitor_account_id == competitor_id,
                    CompetitorAnalytics.data_date >= start_date
                )
            ).order_by(desc(CompetitorAnalytics.data_date))
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting competitor analytics: {e}")
            return []
    
    async def analyze_competitor_trends(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze trends across all competitors for a user"""
        try:
            competitors = await self.get_user_competitors(user_id)
            
            if not competitors:
                return {
                    "total_competitors": 0,
                    "platform_distribution": {},
                    "growth_leaders": [],
                    "engagement_leaders": [],
                    "trending_hashtags": [],
                    "optimal_posting_times": [],
                    "content_themes": []
                }
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get recent analytics for all competitors
            competitor_ids = [c.id for c in competitors]
            analytics_query = select(CompetitorAnalytics).where(
                and_(
                    CompetitorAnalytics.competitor_account_id.in_(competitor_ids),
                    CompetitorAnalytics.data_date >= start_date
                )
            )
            analytics_result = await self.db.execute(analytics_query)
            analytics_data = analytics_result.scalars().all()
            
            # Analyze platform distribution
            platform_distribution = {}
            for competitor in competitors:
                platform = competitor.platform
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            # Find growth leaders (mock data for now)
            growth_leaders = []
            for competitor in competitors[:5]:  # Top 5
                recent_analytics = [a for a in analytics_data if a.competitor_account_id == competitor.id]
                if recent_analytics:
                    latest = max(recent_analytics, key=lambda x: x.data_date)
                    growth_leaders.append({
                        "competitor_id": competitor.id,
                        "username": competitor.username,
                        "platform": competitor.platform,
                        "follower_growth": latest.follower_growth,
                        "engagement_rate": latest.engagement_rate
                    })
            
            # Find engagement leaders
            engagement_leaders = []
            for competitor in competitors[:5]:  # Top 5
                recent_analytics = [a for a in analytics_data if a.competitor_account_id == competitor.id]
                if recent_analytics:
                    avg_engagement = sum(a.engagement_rate for a in recent_analytics) / len(recent_analytics)
                    engagement_leaders.append({
                        "competitor_id": competitor.id,
                        "username": competitor.username,
                        "platform": competitor.platform,
                        "avg_engagement_rate": round(avg_engagement, 2)
                    })
            
            # Sort leaders
            growth_leaders.sort(key=lambda x: x.get("follower_growth", 0), reverse=True)
            engagement_leaders.sort(key=lambda x: x.get("avg_engagement_rate", 0), reverse=True)
            
            # Aggregate trending hashtags (mock data)
            trending_hashtags = [
                {"hashtag": "#fashion", "usage_count": 45, "avg_engagement": 1250},
                {"hashtag": "#style", "usage_count": 38, "avg_engagement": 980},
                {"hashtag": "#ootd", "usage_count": 32, "avg_engagement": 1450},
                {"hashtag": "#lifestyle", "usage_count": 28, "avg_engagement": 875},
                {"hashtag": "#love", "usage_count": 25, "avg_engagement": 1120}
            ]
            
            # Optimal posting times (aggregated from all competitors)
            optimal_posting_times = [
                {"hour": 10, "day": "monday", "avg_engagement": 1350},
                {"hour": 14, "day": "tuesday", "avg_engagement": 1480},
                {"hour": 16, "day": "wednesday", "avg_engagement": 1620},
                {"hour": 12, "day": "thursday", "avg_engagement": 1290},
                {"hour": 15, "day": "friday", "avg_engagement": 1550}
            ]
            
            # Content themes analysis
            content_themes = [
                {"theme": "lifestyle", "percentage": 35.2, "avg_engagement": 1450},
                {"theme": "fashion", "percentage": 28.7, "avg_engagement": 1380},
                {"theme": "travel", "percentage": 18.4, "avg_engagement": 1620},
                {"theme": "food", "percentage": 12.1, "avg_engagement": 1220},
                {"theme": "fitness", "percentage": 5.6, "avg_engagement": 980}
            ]
            
            return {
                "total_competitors": len(competitors),
                "platform_distribution": platform_distribution,
                "growth_leaders": growth_leaders[:5],
                "engagement_leaders": engagement_leaders[:5],
                "trending_hashtags": trending_hashtags,
                "optimal_posting_times": optimal_posting_times,
                "content_themes": content_themes,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitor trends: {e}")
            return {"error": str(e)}
    
    async def get_competitor_insights(self, competitor_id: int) -> Dict[str, Any]:
        """Get detailed insights for a specific competitor"""
        try:
            # Get competitor info
            competitor_query = select(CompetitorAccount).where(CompetitorAccount.id == competitor_id)
            competitor_result = await self.db.execute(competitor_query)
            competitor = competitor_result.scalar_one_or_none()
            
            if not competitor:
                return {"error": "Competitor not found"}
            
            # Get recent analytics
            analytics = await self.get_competitor_analytics(competitor_id, 30)
            
            if not analytics:
                return {
                    "competitor": {
                        "id": competitor.id,
                        "username": competitor.username,
                        "platform": competitor.platform,
                        "follower_count": competitor.follower_count
                    },
                    "insights": [],
                    "recommendations": []
                }
            
            # Generate insights based on analytics
            insights = []
            latest_analytics = analytics[0] if analytics else None
            
            if latest_analytics:
                # Engagement rate insight
                if latest_analytics.engagement_rate > 5.0:
                    insights.append({
                        "type": "high_engagement",
                        "title": "High Engagement Rate",
                        "description": f"This competitor maintains a {latest_analytics.engagement_rate:.1f}% engagement rate, which is above average.",
                        "actionable": True,
                        "recommendation": "Analyze their content strategy and posting patterns to identify best practices."
                    })
                
                # Growth trend insight
                if latest_analytics.follower_growth > 1000:
                    insights.append({
                        "type": "rapid_growth",
                        "title": "Rapid Follower Growth",
                        "description": f"Gained {latest_analytics.follower_growth:,} followers recently.",
                        "actionable": True,
                        "recommendation": "Study their recent content and hashtag strategies for growth tactics."
                    })
                
                # Posting frequency insight
                if latest_analytics.posting_frequency > 1.0:
                    insights.append({
                        "type": "posting_frequency",
                        "title": "Active Posting Schedule",
                        "description": f"Posts {latest_analytics.posting_frequency:.1f} times per day on average.",
                        "actionable": True,
                        "recommendation": "Consider increasing your posting frequency to match competitor activity."
                    })
            
            # Generate recommendations
            recommendations = [
                "Monitor their hashtag usage patterns for trending tags",
                "Analyze their most engaging content types",
                "Track their posting schedule for optimal timing insights",
                "Study their visual content style and themes",
                "Monitor their audience engagement patterns"
            ]
            
            return {
                "competitor": {
                    "id": competitor.id,
                    "username": competitor.username,
                    "platform": competitor.platform,
                    "follower_count": competitor.follower_count,
                    "engagement_rate": latest_analytics.engagement_rate if latest_analytics else 0,
                    "posting_frequency": latest_analytics.posting_frequency if latest_analytics else 0
                },
                "insights": insights,
                "recommendations": recommendations,
                "analytics_summary": {
                    "data_points": len(analytics),
                    "latest_update": latest_analytics.recorded_at.isoformat() if latest_analytics else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting competitor insights: {e}")
            return {"error": str(e)}
    
    async def _generate_initial_analytics(self, competitor: CompetitorAccount):
        """Generate initial analytics data for a new competitor"""
        try:
            # Generate analytics for the past 7 days
            for i in range(7):
                date = datetime.utcnow() - timedelta(days=i)
                
                analytics = CompetitorAnalytics(
                    competitor_account_id=competitor.id,
                    follower_count=competitor.follower_count + random.randint(-100, 200),
                    following_count=competitor.following_count + random.randint(-10, 20),
                    post_count=competitor.post_count + random.randint(0, 3),
                    avg_likes=random.randint(50, 500),
                    avg_comments=random.randint(5, 50),
                    avg_shares=random.randint(2, 25),
                    engagement_rate=random.uniform(2.0, 8.0),
                    follower_growth=random.randint(-50, 150),
                    posting_frequency=random.uniform(0.5, 2.5),
                    optimal_posting_times=[
                        {"hour": 10, "day": "monday", "score": 0.85},
                        {"hour": 14, "day": "wednesday", "score": 0.92},
                        {"hour": 16, "day": "friday", "score": 0.78}
                    ],
                    popular_hashtags=[
                        {"hashtag": "#fashion", "count": 15, "engagement": 1250},
                        {"hashtag": "#style", "count": 12, "engagement": 980},
                        {"hashtag": "#ootd", "count": 8, "engagement": 1450}
                    ],
                    content_themes=[
                        {"theme": "lifestyle", "percentage": 45.2},
                        {"theme": "fashion", "percentage": 32.8},
                        {"theme": "travel", "percentage": 22.0}
                    ],
                    data_date=date,
                    recorded_at=datetime.utcnow()
                )
                
                self.db.add(analytics)
            
            await self.db.commit()
            logger.info(f"Generated initial analytics for competitor {competitor.username}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error generating initial analytics: {e}")
            raise
    
    async def remove_competitor(self, user_id: int, competitor_id: int) -> bool:
        """Remove a competitor from tracking"""
        try:
            query = select(CompetitorAccount).where(
                and_(
                    CompetitorAccount.id == competitor_id,
                    CompetitorAccount.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            competitor = result.scalar_one_or_none()
            
            if not competitor:
                return False
            
            # Soft delete - just mark as inactive
            competitor.is_active = False
            await self.db.commit()
            
            logger.info(f"Removed competitor {competitor.username} for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error removing competitor: {e}")
            return False