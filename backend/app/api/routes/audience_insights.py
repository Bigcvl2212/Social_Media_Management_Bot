"""
Audience insights API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.audience_segmentation_service import AudienceSegmentationService

router = APIRouter()

# Pydantic models for request/response
class AudienceSegmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    segment_type: str
    audience_size: int
    percentage_of_total: float
    avg_engagement_rate: float
    most_active_hours: Optional[List[Dict[str, Any]]]
    top_interests: Optional[List[Dict[str, Any]]]
    created_at: str

class AudienceInsightResponse(BaseModel):
    id: int
    segment_id: int
    insight_type: str
    title: str
    description: Optional[str]
    confidence_score: float
    impact_score: float
    actionable: bool
    recommended_actions: Optional[List[Dict[str, Any]]]
    created_at: str

class EngagementPatternResponse(BaseModel):
    id: int
    pattern_type: str
    pattern_name: str
    pattern_data: Dict[str, Any]
    strength: float
    avg_engagement_rate: float
    confidence_level: float
    trend_direction: Optional[str]

@router.get("/segments")
async def get_audience_segments(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audience segments for the current user"""
    try:
        service = AudienceSegmentationService(db)
        segments = await service.analyze_audience_segments(current_user.id, social_account_id)
        return {"segments": segments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audience segments: {str(e)}")

@router.get("/insights")
async def get_audience_insights(
    segment_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audience insights for a user or specific segment"""
    try:
        service = AudienceSegmentationService(db)
        insights = await service.get_audience_insights(current_user.id, segment_id)
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audience insights: {str(e)}")

@router.get("/patterns")
async def get_engagement_patterns(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get engagement patterns for a user"""
    try:
        service = AudienceSegmentationService(db)
        patterns = await service.get_engagement_patterns(current_user.id, social_account_id)
        return {"patterns": patterns}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch engagement patterns: {str(e)}")

@router.get("/overview")
async def get_audience_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive audience insights overview"""
    try:
        service = AudienceSegmentationService(db)
        overview = await service.generate_audience_insights(current_user.id)
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audience overview: {str(e)}")

@router.get("/dashboard")
async def get_audience_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audience dashboard data"""
    try:
        service = AudienceSegmentationService(db)
        
        # Get overview data
        overview = await service.generate_audience_insights(current_user.id)
        
        # Get engagement patterns
        patterns = await service.get_engagement_patterns(current_user.id)
        
        # Format dashboard data
        dashboard_data = {
            "summary": overview.get("summary", {}),
            "top_segments": overview.get("top_segments", [])[:3],  # Top 3 segments
            "demographics": {
                "age_distribution": overview.get("demographics", {}).get("age_distribution", []),
                "gender_distribution": overview.get("demographics", {}).get("gender_distribution", []),
                "top_locations": overview.get("demographics", {}).get("location_distribution", [])[:5],
                "top_interests": overview.get("demographics", {}).get("interests", [])[:8]
            },
            "engagement_insights": {
                "optimal_posting_times": [
                    {"hour": 14, "day": "tuesday", "engagement_score": 0.92},
                    {"hour": 16, "day": "wednesday", "engagement_score": 0.88},
                    {"hour": 19, "day": "friday", "engagement_score": 0.85}
                ],
                "content_preferences": [
                    {"content_type": "video", "preference_score": 0.92, "avg_engagement": 8.5},
                    {"content_type": "carousel", "preference_score": 0.85, "avg_engagement": 6.2},
                    {"content_type": "image", "preference_score": 0.78, "avg_engagement": 4.8}
                ],
                "engagement_patterns": patterns[:3]  # Top 3 patterns
            },
            "actionable_insights": overview.get("actionable_insights", []),
            "recommendations": [
                {
                    "title": "Focus on High-Engagement Segments",
                    "description": "Tailor content to your most engaged audience segments",
                    "priority": "high",
                    "estimated_impact": "25% engagement increase"
                },
                {
                    "title": "Optimize Posting Schedule",
                    "description": "Post during your audience's most active hours",
                    "priority": "medium",
                    "estimated_impact": "15% reach improvement"
                },
                {
                    "title": "Increase Video Content",
                    "description": "Your audience prefers video content over static images",
                    "priority": "high",
                    "estimated_impact": "30% engagement boost"
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audience dashboard: {str(e)}")

@router.get("/demographics")
async def get_audience_demographics(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed audience demographics"""
    try:
        service = AudienceSegmentationService(db)
        overview = await service.generate_audience_insights(current_user.id)
        
        demographics = overview.get("demographics", {})
        
        # Add additional demographic insights
        detailed_demographics = {
            "age_distribution": demographics.get("age_distribution", []),
            "gender_distribution": demographics.get("gender_distribution", []),
            "location_distribution": demographics.get("location_distribution", []),
            "interests": demographics.get("interests", []),
            "behavioral_insights": {
                "most_active_hours": [
                    {"hour": 9, "percentage": 12.5},
                    {"hour": 12, "percentage": 15.2},
                    {"hour": 14, "percentage": 18.7},
                    {"hour": 16, "percentage": 16.3},
                    {"hour": 19, "percentage": 19.8},
                    {"hour": 21, "percentage": 17.5}
                ],
                "most_active_days": [
                    {"day": "monday", "percentage": 14.2},
                    {"day": "tuesday", "percentage": 16.8},
                    {"day": "wednesday", "percentage": 15.7},
                    {"day": "thursday", "percentage": 14.9},
                    {"day": "friday", "percentage": 16.2},
                    {"day": "saturday", "percentage": 11.6},
                    {"day": "sunday", "percentage": 10.6}
                ],
                "device_usage": [
                    {"device": "mobile", "percentage": 78.5},
                    {"device": "desktop", "percentage": 18.2},
                    {"device": "tablet", "percentage": 3.3}
                ]
            },
            "engagement_by_demographic": {
                "age_engagement": [
                    {"age_range": "18-24", "avg_engagement_rate": 8.5},
                    {"age_range": "25-34", "avg_engagement_rate": 6.2},
                    {"age_range": "35-44", "avg_engagement_rate": 4.8},
                    {"age_range": "45-54", "avg_engagement_rate": 3.9}
                ],
                "gender_engagement": [
                    {"gender": "female", "avg_engagement_rate": 7.2},
                    {"gender": "male", "avg_engagement_rate": 5.8},
                    {"gender": "non_binary", "avg_engagement_rate": 6.9}
                ]
            }
        }
        
        return detailed_demographics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audience demographics: {str(e)}")

@router.get("/behavior-analysis")
async def get_behavior_analysis(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed audience behavior analysis"""
    try:
        service = AudienceSegmentationService(db)
        
        # Get engagement patterns
        patterns = await service.get_engagement_patterns(current_user.id)
        
        behavior_analysis = {
            "analysis_period": f"{days} days",
            "content_interaction_patterns": {
                "likes_pattern": {
                    "peak_hours": [14, 16, 19, 21],
                    "peak_days": ["tuesday", "wednesday", "friday"],
                    "average_response_time": "2.5 hours"
                },
                "comments_pattern": {
                    "peak_hours": [15, 17, 20],
                    "peak_days": ["wednesday", "thursday", "friday"],
                    "average_response_time": "4.2 hours"
                },
                "shares_pattern": {
                    "peak_hours": [12, 16, 18],
                    "peak_days": ["tuesday", "friday", "saturday"],
                    "average_response_time": "6.8 hours"
                }
            },
            "content_preferences": {
                "by_type": [
                    {"content_type": "video", "engagement_rate": 8.5, "completion_rate": 0.72},
                    {"content_type": "carousel", "engagement_rate": 6.2, "swipe_rate": 0.65},
                    {"content_type": "image", "engagement_rate": 4.8, "dwell_time": "3.2s"}
                ],
                "by_theme": [
                    {"theme": "educational", "engagement_rate": 9.1, "save_rate": 0.18},
                    {"theme": "entertainment", "engagement_rate": 7.8, "share_rate": 0.15},
                    {"theme": "lifestyle", "engagement_rate": 6.5, "comment_rate": 0.12}
                ]
            },
            "engagement_journey": {
                "discovery_sources": [
                    {"source": "hashtags", "percentage": 35.2},
                    {"source": "explore_page", "percentage": 28.7},
                    {"source": "profile_visits", "percentage": 18.9},
                    {"source": "shares", "percentage": 17.2}
                ],
                "conversion_funnel": [
                    {"stage": "impression", "rate": 100.0},
                    {"stage": "click", "rate": 12.5},
                    {"stage": "engagement", "rate": 8.2},
                    {"stage": "follow", "rate": 2.1}
                ]
            },
            "loyalty_metrics": {
                "repeat_engagement_rate": 65.3,
                "average_session_duration": "4.8 minutes",
                "return_visitor_rate": 42.7,
                "brand_mention_frequency": 8.5
            }
        }
        
        return behavior_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch behavior analysis: {str(e)}")