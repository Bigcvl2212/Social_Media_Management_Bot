"""
Growth recommendations service for AI-generated suggestions and insights
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from loguru import logger

from app.models.growth_recommendations import (
    GrowthRecommendation, ContentRecommendation, 
    TimingRecommendation, HashtagRecommendation
)
from app.models.analytics import Analytics
from app.models.content import Content
from app.models.social_account import SocialAccount
from app.models.user import User


class GrowthRecommendationService:
    """Service for generating AI-powered growth recommendations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive growth recommendations for a user"""
        try:
            recommendations = []
            
            # Generate content recommendations
            content_recs = await self._generate_content_recommendations(user_id, social_account_id)
            recommendations.extend(content_recs)
            
            # Generate timing recommendations
            timing_recs = await self._generate_timing_recommendations(user_id, social_account_id)
            recommendations.extend(timing_recs)
            
            # Generate hashtag recommendations
            hashtag_recs = await self._generate_hashtag_recommendations(user_id, social_account_id)
            recommendations.extend(hashtag_recs)
            
            # Generate engagement strategy recommendations
            engagement_recs = await self._generate_engagement_recommendations(user_id, social_account_id)
            recommendations.extend(engagement_recs)
            
            # Generate growth strategy recommendations
            growth_recs = await self._generate_growth_strategy_recommendations(user_id, social_account_id)
            recommendations.extend(growth_recs)
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def get_user_recommendations(
        self, 
        user_id: int, 
        recommendation_type: Optional[str] = None,
        status: str = "active"
    ) -> List[Dict[str, Any]]:
        """Get existing recommendations for a user"""
        try:
            query = select(GrowthRecommendation).where(
                and_(
                    GrowthRecommendation.user_id == user_id,
                    GrowthRecommendation.status == status
                )
            )
            
            if recommendation_type:
                query = query.where(GrowthRecommendation.recommendation_type == recommendation_type)
            
            query = query.order_by(desc(GrowthRecommendation.priority_score))
            
            result = await self.db.execute(query)
            recommendations = result.scalars().all()
            
            recommendations_data = []
            for rec in recommendations:
                rec_data = {
                    "id": rec.id,
                    "recommendation_type": rec.recommendation_type,
                    "category": rec.category,
                    "title": rec.title,
                    "description": rec.description,
                    "confidence_score": rec.confidence_score,
                    "impact_score": rec.impact_score,
                    "difficulty_score": rec.difficulty_score,
                    "priority_score": rec.priority_score,
                    "recommendation_data": rec.recommendation_data,
                    "expected_outcomes": rec.expected_outcomes,
                    "actionable_steps": rec.actionable_steps,
                    "estimated_effort": rec.estimated_effort,
                    "estimated_time": rec.estimated_time,
                    "is_urgent": rec.is_urgent,
                    "created_at": rec.created_at.isoformat(),
                    "valid_until": rec.valid_until.isoformat() if rec.valid_until else None
                }
                recommendations_data.append(rec_data)
            
            return recommendations_data
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []
    
    async def implement_recommendation(self, user_id: int, recommendation_id: int, notes: Optional[str] = None) -> bool:
        """Mark a recommendation as implemented"""
        try:
            query = select(GrowthRecommendation).where(
                and_(
                    GrowthRecommendation.id == recommendation_id,
                    GrowthRecommendation.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            recommendation = result.scalar_one_or_none()
            
            if not recommendation:
                return False
            
            recommendation.status = "implemented"
            recommendation.implementation_date = datetime.utcnow()
            recommendation.implementation_notes = notes
            
            await self.db.commit()
            logger.info(f"Recommendation {recommendation_id} marked as implemented")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error implementing recommendation: {e}")
            return False
    
    async def dismiss_recommendation(self, user_id: int, recommendation_id: int) -> bool:
        """Dismiss a recommendation"""
        try:
            query = select(GrowthRecommendation).where(
                and_(
                    GrowthRecommendation.id == recommendation_id,
                    GrowthRecommendation.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            recommendation = result.scalar_one_or_none()
            
            if not recommendation:
                return False
            
            recommendation.status = "dismissed"
            await self.db.commit()
            logger.info(f"Recommendation {recommendation_id} dismissed")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error dismissing recommendation: {e}")
            return False
    
    async def _generate_content_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate content-focused recommendations"""
        recommendations = []
        
        # Analyze user's content performance
        content_performance = await self._analyze_content_performance(user_id, social_account_id)
        
        # Video content recommendation
        video_rec = {
            "recommendation_type": "content",
            "category": "content_theme",
            "title": "Increase Video Content Production",
            "description": "Video content shows 73% higher engagement rates compared to static images. Consider increasing your video content ratio.",
            "confidence_score": 0.88,
            "impact_score": 0.75,
            "difficulty_score": 0.45,
            "priority_score": 0.72,
            "recommendation_data": {
                "content_type": "video",
                "current_ratio": 25,
                "recommended_ratio": 60,
                "expected_engagement_lift": 73
            },
            "expected_outcomes": [
                {"metric": "engagement_rate", "improvement": 15.2},
                {"metric": "reach", "improvement": 28.5},
                {"metric": "shares", "improvement": 45.3}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Create video content calendar", "estimated_time": "30 min"},
                {"step": 2, "action": "Set up basic video recording setup", "estimated_time": "2 hours"},
                {"step": 3, "action": "Plan 10 video topics", "estimated_time": "45 min"},
                {"step": 4, "action": "Record first 3 videos", "estimated_time": "3 hours"}
            ],
            "estimated_effort": "medium",
            "estimated_time": "2 weeks",
            "is_urgent": False
        }
        
        # Save to database
        saved_rec = await self._save_recommendation(user_id, social_account_id, video_rec)
        if saved_rec:
            recommendations.append({**video_rec, "id": saved_rec.id})
        
        # Behind-the-scenes content recommendation
        bts_rec = {
            "recommendation_type": "content",
            "category": "content_theme",
            "title": "Share Behind-the-Scenes Content",
            "description": "Behind-the-scenes content creates authentic connections and increases follower loyalty by 32%.",
            "confidence_score": 0.82,
            "impact_score": 0.65,
            "difficulty_score": 0.25,
            "priority_score": 0.68,
            "recommendation_data": {
                "content_theme": "behind_scenes",
                "frequency": "2 times per week",
                "content_types": ["stories", "reels", "posts"]
            },
            "expected_outcomes": [
                {"metric": "follower_loyalty", "improvement": 32.0},
                {"metric": "story_views", "improvement": 18.7},
                {"metric": "profile_visits", "improvement": 25.1}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Plan behind-the-scenes moments to capture", "estimated_time": "20 min"},
                {"step": 2, "action": "Create content schedule", "estimated_time": "15 min"},
                {"step": 3, "action": "Start sharing 2x per week", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "low",
            "estimated_time": "1 week",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, bts_rec)
        if saved_rec:
            recommendations.append({**bts_rec, "id": saved_rec.id})
        
        # User-generated content recommendation
        ugc_rec = {
            "recommendation_type": "content",
            "category": "engagement_strategy",
            "title": "Encourage User-Generated Content",
            "description": "User-generated content campaigns can increase engagement by 85% and provide authentic social proof.",
            "confidence_score": 0.89,
            "impact_score": 0.82,
            "difficulty_score": 0.35,
            "priority_score": 0.79,
            "recommendation_data": {
                "strategy": "ugc_campaign",
                "campaign_type": "hashtag_challenge",
                "incentives": ["feature_on_page", "giveaway_entry"]
            },
            "expected_outcomes": [
                {"metric": "engagement_rate", "improvement": 85.0},
                {"metric": "brand_mentions", "improvement": 120.0},
                {"metric": "content_volume", "improvement": 200.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Create branded hashtag", "estimated_time": "15 min"},
                {"step": 2, "action": "Design campaign graphics", "estimated_time": "2 hours"},
                {"step": 3, "action": "Launch campaign with clear instructions", "estimated_time": "30 min"},
                {"step": 4, "action": "Engage with participants", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "medium",
            "estimated_time": "3 weeks",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, ugc_rec)
        if saved_rec:
            recommendations.append({**ugc_rec, "id": saved_rec.id})
        
        return recommendations
    
    async def _generate_timing_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate timing-focused recommendations"""
        recommendations = []
        
        # Optimal posting time recommendation
        timing_rec = {
            "recommendation_type": "timing",
            "category": "posting_schedule",
            "title": "Optimize Posting Schedule",
            "description": "Your audience is most active between 2-4 PM and 7-9 PM. Posting during these windows can increase engagement by 45%.",
            "confidence_score": 0.91,
            "impact_score": 0.68,
            "difficulty_score": 0.15,
            "priority_score": 0.81,
            "recommendation_data": {
                "optimal_hours": [14, 15, 16, 19, 20, 21],
                "current_schedule_alignment": 35,
                "recommended_alignment": 80,
                "timezone": "EST"
            },
            "expected_outcomes": [
                {"metric": "engagement_rate", "improvement": 45.0},
                {"metric": "reach", "improvement": 32.0},
                {"metric": "impressions", "improvement": 28.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Update content calendar with optimal times", "estimated_time": "30 min"},
                {"step": 2, "action": "Set up scheduling tools", "estimated_time": "15 min"},
                {"step": 3, "action": "Monitor performance for 2 weeks", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "low",
            "estimated_time": "1 week",
            "is_urgent": True
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, timing_rec)
        if saved_rec:
            recommendations.append({**timing_rec, "id": saved_rec.id})
        
        # Posting frequency recommendation
        frequency_rec = {
            "recommendation_type": "timing",
            "category": "posting_schedule",
            "title": "Increase Posting Frequency",
            "description": "Accounts posting 5-7 times per week see 23% better follower growth compared to less frequent posting.",
            "confidence_score": 0.76,
            "impact_score": 0.58,
            "difficulty_score": 0.55,
            "priority_score": 0.60,
            "recommendation_data": {
                "current_frequency": 3,
                "recommended_frequency": 6,
                "optimal_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            },
            "expected_outcomes": [
                {"metric": "follower_growth", "improvement": 23.0},
                {"metric": "brand_awareness", "improvement": 18.0},
                {"metric": "engagement_volume", "improvement": 35.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Plan additional content topics", "estimated_time": "1 hour"},
                {"step": 2, "action": "Create content production schedule", "estimated_time": "30 min"},
                {"step": 3, "action": "Gradually increase to 6 posts/week", "estimated_time": "2 weeks"}
            ],
            "estimated_effort": "medium",
            "estimated_time": "3 weeks",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, frequency_rec)
        if saved_rec:
            recommendations.append({**frequency_rec, "id": saved_rec.id})
        
        return recommendations
    
    async def _generate_hashtag_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate hashtag strategy recommendations"""
        recommendations = []
        
        # Hashtag mix optimization
        hashtag_rec = {
            "recommendation_type": "hashtag",
            "category": "hashtag_strategy",
            "title": "Optimize Hashtag Mix Strategy",
            "description": "Use a balanced mix of trending, niche, and branded hashtags. Current strategy is missing niche hashtags that could increase discoverability by 40%.",
            "confidence_score": 0.84,
            "impact_score": 0.72,
            "difficulty_score": 0.25,
            "priority_score": 0.77,
            "recommendation_data": {
                "current_mix": {
                    "trending": 70,
                    "niche": 10,
                    "branded": 20
                },
                "recommended_mix": {
                    "trending": 40,
                    "niche": 40,
                    "branded": 20
                },
                "recommended_hashtags": {
                    "trending": ["#trending1", "#viral", "#popular"],
                    "niche": ["#specificniche", "#targetedaudience", "#nichekeyword"],
                    "branded": ["#yourbrand", "#brandedcampaign"]
                }
            },
            "expected_outcomes": [
                {"metric": "discoverability", "improvement": 40.0},
                {"metric": "new_followers", "improvement": 28.0},
                {"metric": "hashtag_reach", "improvement": 55.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Research niche hashtags in your industry", "estimated_time": "45 min"},
                {"step": 2, "action": "Create hashtag groups for different content types", "estimated_time": "30 min"},
                {"step": 3, "action": "Test new hashtag mix for 2 weeks", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "low",
            "estimated_time": "1 week",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, hashtag_rec)
        if saved_rec:
            recommendations.append({**hashtag_rec, "id": saved_rec.id})
        
        return recommendations
    
    async def _generate_engagement_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate engagement strategy recommendations"""
        recommendations = []
        
        # Community engagement recommendation
        engagement_rec = {
            "recommendation_type": "engagement",
            "category": "community_building",
            "title": "Increase Community Engagement",
            "description": "Responding to comments within 2 hours increases follower loyalty by 65% and encourages more engagement.",
            "confidence_score": 0.87,
            "impact_score": 0.78,
            "difficulty_score": 0.35,
            "priority_score": 0.76,
            "recommendation_data": {
                "current_response_time": "8 hours",
                "recommended_response_time": "2 hours",
                "engagement_tactics": [
                    "ask_questions_in_captions",
                    "respond_to_all_comments",
                    "create_polls_and_quizzes",
                    "share_user_stories"
                ]
            },
            "expected_outcomes": [
                {"metric": "follower_loyalty", "improvement": 65.0},
                {"metric": "comment_rate", "improvement": 42.0},
                {"metric": "repeat_engagement", "improvement": 38.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Set up comment notifications", "estimated_time": "5 min"},
                {"step": 2, "action": "Create response templates", "estimated_time": "20 min"},
                {"step": 3, "action": "Dedicate 30 min daily to engagement", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "low",
            "estimated_time": "immediate",
            "is_urgent": True
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, engagement_rec)
        if saved_rec:
            recommendations.append({**engagement_rec, "id": saved_rec.id})
        
        return recommendations
    
    async def _generate_growth_strategy_recommendations(self, user_id: int, social_account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate overall growth strategy recommendations"""
        recommendations = []
        
        # Cross-platform strategy
        cross_platform_rec = {
            "recommendation_type": "growth_strategy",
            "category": "cross_platform",
            "title": "Implement Cross-Platform Content Strategy",
            "description": "Brands using cross-platform strategies see 23% faster follower growth. Adapt your best-performing content for other platforms.",
            "confidence_score": 0.79,
            "impact_score": 0.69,
            "difficulty_score": 0.45,
            "priority_score": 0.67,
            "recommendation_data": {
                "current_platforms": ["instagram"],
                "recommended_platforms": ["tiktok", "twitter", "youtube"],
                "content_adaptation_strategy": {
                    "instagram_to_tiktok": "Convert carousel posts to video tutorials",
                    "instagram_to_twitter": "Break down captions into tweet threads",
                    "instagram_to_youtube": "Expand stories into longer-form content"
                }
            },
            "expected_outcomes": [
                {"metric": "total_reach", "improvement": 45.0},
                {"metric": "follower_growth", "improvement": 23.0},
                {"metric": "brand_awareness", "improvement": 35.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Analyze top-performing content", "estimated_time": "1 hour"},
                {"step": 2, "action": "Choose 1-2 additional platforms", "estimated_time": "30 min"},
                {"step": 3, "action": "Create platform-specific content calendar", "estimated_time": "2 hours"},
                {"step": 4, "action": "Start with 3 posts per week on new platforms", "estimated_time": "ongoing"}
            ],
            "estimated_effort": "high",
            "estimated_time": "1 month",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, cross_platform_rec)
        if saved_rec:
            recommendations.append({**cross_platform_rec, "id": saved_rec.id})
        
        # Collaboration strategy
        collab_rec = {
            "recommendation_type": "growth_strategy",
            "category": "collaboration",
            "title": "Partner with Micro-Influencers",
            "description": "Collaborations with micro-influencers (1K-100K followers) have 60% higher engagement rates and are more cost-effective.",
            "confidence_score": 0.82,
            "impact_score": 0.74,
            "difficulty_score": 0.55,
            "priority_score": 0.67,
            "recommendation_data": {
                "target_influencer_size": "1K-50K",
                "collaboration_types": ["content_exchanges", "product_reviews", "takeovers"],
                "budget_range": "$50-200 per collaboration"
            },
            "expected_outcomes": [
                {"metric": "engagement_rate", "improvement": 60.0},
                {"metric": "new_followers", "improvement": 25.0},
                {"metric": "brand_credibility", "improvement": 40.0}
            ],
            "actionable_steps": [
                {"step": 1, "action": "Identify potential micro-influencers in your niche", "estimated_time": "2 hours"},
                {"step": 2, "action": "Create collaboration proposal template", "estimated_time": "45 min"},
                {"step": 3, "action": "Reach out to 10 potential partners", "estimated_time": "1 hour"},
                {"step": 4, "action": "Execute first collaboration", "estimated_time": "1 week"}
            ],
            "estimated_effort": "medium",
            "estimated_time": "1 month",
            "is_urgent": False
        }
        
        saved_rec = await self._save_recommendation(user_id, social_account_id, collab_rec)
        if saved_rec:
            recommendations.append({**collab_rec, "id": saved_rec.id})
        
        return recommendations
    
    async def _analyze_content_performance(self, user_id: int, social_account_id: Optional[int] = None) -> Dict[str, Any]:
        """Analyze user's content performance to inform recommendations"""
        try:
            # This would normally analyze real user content and analytics
            # For now, return mock analysis data
            return {
                "total_posts": random.randint(50, 200),
                "avg_engagement_rate": random.uniform(3.0, 8.0),
                "top_content_types": [
                    {"type": "video", "engagement_rate": 8.5},
                    {"type": "carousel", "engagement_rate": 6.2},
                    {"type": "image", "engagement_rate": 4.8}
                ],
                "posting_frequency": random.uniform(2.0, 5.0),
                "peak_engagement_hours": [14, 15, 19, 20]
            }
        except Exception as e:
            logger.error(f"Error analyzing content performance: {e}")
            return {}
    
    async def _save_recommendation(self, user_id: int, social_account_id: Optional[int], rec_data: Dict[str, Any]) -> Optional[GrowthRecommendation]:
        """Save a recommendation to the database"""
        try:
            # Calculate priority score based on impact, confidence, and urgency
            priority_score = (
                rec_data["impact_score"] * 0.4 +
                rec_data["confidence_score"] * 0.3 +
                (1 - rec_data["difficulty_score"]) * 0.2 +
                (0.1 if rec_data.get("is_urgent") else 0)
            )
            
            recommendation = GrowthRecommendation(
                user_id=user_id,
                social_account_id=social_account_id,
                recommendation_type=rec_data["recommendation_type"],
                category=rec_data["category"],
                title=rec_data["title"],
                description=rec_data["description"],
                confidence_score=rec_data["confidence_score"],
                impact_score=rec_data["impact_score"],
                difficulty_score=rec_data["difficulty_score"],
                priority_score=priority_score,
                recommendation_data=rec_data["recommendation_data"],
                expected_outcomes=rec_data["expected_outcomes"],
                actionable_steps=rec_data["actionable_steps"],
                estimated_effort=rec_data["estimated_effort"],
                estimated_time=rec_data["estimated_time"],
                is_urgent=rec_data.get("is_urgent", False),
                valid_until=datetime.utcnow() + timedelta(days=30),  # Valid for 30 days
                refresh_after=datetime.utcnow() + timedelta(days=7)   # Refresh after 7 days
            )
            
            self.db.add(recommendation)
            await self.db.commit()
            await self.db.refresh(recommendation)
            
            return recommendation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error saving recommendation: {e}")
            return None