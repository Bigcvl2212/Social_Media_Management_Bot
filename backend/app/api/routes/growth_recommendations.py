"""
Growth recommendations API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.growth_recommendation_service import GrowthRecommendationService

router = APIRouter()

# Pydantic models for request/response
class ImplementRecommendationRequest(BaseModel):
    notes: Optional[str] = None

class GrowthRecommendationResponse(BaseModel):
    id: int
    recommendation_type: str
    category: str
    title: str
    description: str
    confidence_score: float
    impact_score: float
    difficulty_score: float
    priority_score: float
    recommendation_data: Dict[str, Any]
    expected_outcomes: Optional[List[Dict[str, Any]]]
    actionable_steps: Optional[List[Dict[str, Any]]]
    estimated_effort: Optional[str]
    estimated_time: Optional[str]
    is_urgent: bool
    created_at: str

@router.get("/", response_model=List[GrowthRecommendationResponse])
async def get_recommendations(
    recommendation_type: Optional[str] = Query(None),
    status: str = Query("active"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get growth recommendations for the current user"""
    try:
        service = GrowthRecommendationService(db)
        recommendations = await service.get_user_recommendations(
            current_user.id, 
            recommendation_type, 
            status
        )
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendations: {str(e)}")

@router.post("/generate")
async def generate_recommendations(
    social_account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate new recommendations for the user"""
    try:
        service = GrowthRecommendationService(db)
        recommendations = await service.generate_recommendations(current_user.id, social_account_id)
        return {"recommendations": recommendations, "count": len(recommendations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/{recommendation_id}/implement")
async def implement_recommendation(
    recommendation_id: int,
    request: ImplementRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a recommendation as implemented"""
    try:
        service = GrowthRecommendationService(db)
        success = await service.implement_recommendation(
            current_user.id, 
            recommendation_id, 
            request.notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {"message": "Recommendation marked as implemented"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to implement recommendation: {str(e)}")

@router.post("/{recommendation_id}/dismiss")
async def dismiss_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dismiss a recommendation"""
    try:
        service = GrowthRecommendationService(db)
        success = await service.dismiss_recommendation(current_user.id, recommendation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {"message": "Recommendation dismissed"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dismiss recommendation: {str(e)}")

@router.get("/dashboard")
async def get_recommendations_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recommendations dashboard data"""
    try:
        service = GrowthRecommendationService(db)
        
        # Get all active recommendations
        recommendations = await service.get_user_recommendations(current_user.id, status="active")
        
        # Categorize recommendations
        by_type = {}
        by_priority = {"high": [], "medium": [], "low": []}
        urgent_recommendations = []
        
        for rec in recommendations:
            # Group by type
            rec_type = rec.get("recommendation_type", "other")
            if rec_type not in by_type:
                by_type[rec_type] = []
            by_type[rec_type].append(rec)
            
            # Group by priority
            priority_score = rec.get("priority_score", 0)
            if priority_score >= 0.7:
                by_priority["high"].append(rec)
            elif priority_score >= 0.4:
                by_priority["medium"].append(rec)
            else:
                by_priority["low"].append(rec)
            
            # Check if urgent
            if rec.get("is_urgent"):
                urgent_recommendations.append(rec)
        
        # Get implementation stats
        implemented_recs = await service.get_user_recommendations(current_user.id, status="implemented")
        dismissed_recs = await service.get_user_recommendations(current_user.id, status="dismissed")
        
        # Calculate quick wins (high impact, low effort)
        quick_wins = [
            rec for rec in recommendations 
            if rec.get("impact_score", 0) >= 0.6 and rec.get("difficulty_score", 1) <= 0.3
        ]
        
        dashboard_data = {
            "summary": {
                "total_recommendations": len(recommendations),
                "urgent_recommendations": len(urgent_recommendations),
                "quick_wins": len(quick_wins),
                "implemented_count": len(implemented_recs),
                "dismissed_count": len(dismissed_recs),
                "completion_rate": len(implemented_recs) / max(1, len(implemented_recs) + len(dismissed_recs) + len(recommendations)) * 100
            },
            "priority_breakdown": {
                "high_priority": len(by_priority["high"]),
                "medium_priority": len(by_priority["medium"]),
                "low_priority": len(by_priority["low"])
            },
            "recommendations_by_type": {
                "content": len(by_type.get("content", [])),
                "timing": len(by_type.get("timing", [])),
                "hashtag": len(by_type.get("hashtag", [])),
                "engagement": len(by_type.get("engagement", [])),
                "growth_strategy": len(by_type.get("growth_strategy", []))
            },
            "top_recommendations": sorted(recommendations, key=lambda x: x.get("priority_score", 0), reverse=True)[:5],
            "urgent_recommendations": urgent_recommendations,
            "quick_wins": quick_wins[:3],  # Top 3 quick wins
            "recent_implementations": implemented_recs[:5] if implemented_recs else []
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendations dashboard: {str(e)}")

@router.get("/content-suggestions")
async def get_content_suggestions(
    content_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated content suggestions"""
    try:
        service = GrowthRecommendationService(db)
        
        # Get content-specific recommendations
        content_recs = await service.get_user_recommendations(
            current_user.id, 
            recommendation_type="content"
        )
        
        # Generate content suggestions based on trends and analysis
        content_suggestions = {
            "trending_topics": [
                {
                    "topic": "Sustainable Living Tips",
                    "relevance_score": 0.92,
                    "estimated_engagement": "15% above average",
                    "hashtags": ["#sustainability", "#ecofriendly", "#greenliving"],
                    "content_formats": ["tutorial", "carousel", "video"]
                },
                {
                    "topic": "Behind-the-Scenes Content",
                    "relevance_score": 0.88,
                    "estimated_engagement": "28% above average",
                    "hashtags": ["#behindthescenes", "#process", "#authentic"],
                    "content_formats": ["stories", "reel", "live"]
                },
                {
                    "topic": "User-Generated Content Showcase",
                    "relevance_score": 0.85,
                    "estimated_engagement": "35% above average",
                    "hashtags": ["#community", "#customerfeature", "#testimonial"],
                    "content_formats": ["repost", "story_highlight", "carousel"]
                }
            ],
            "content_calendar_ideas": [
                {
                    "week": 1,
                    "theme": "Educational Week",
                    "posts": [
                        {"type": "tutorial", "title": "How-to Guide", "best_time": "2 PM Tuesday"},
                        {"type": "carousel", "title": "Tips & Tricks", "best_time": "4 PM Wednesday"},
                        {"type": "video", "title": "Process Breakdown", "best_time": "7 PM Friday"}
                    ]
                },
                {
                    "week": 2,
                    "theme": "Community Week",
                    "posts": [
                        {"type": "ugc_feature", "title": "Customer Spotlight", "best_time": "10 AM Monday"},
                        {"type": "poll", "title": "Community Choice", "best_time": "3 PM Wednesday"},
                        {"type": "live", "title": "Q&A Session", "best_time": "8 PM Thursday"}
                    ]
                }
            ],
            "hashtag_strategies": [
                {
                    "strategy": "Trending Mix",
                    "description": "Combine trending and niche hashtags",
                    "example_set": ["#trend1", "#trend2", "#nichekeyword1", "#nichekeyword2", "#branded"],
                    "expected_reach": "40% increase"
                },
                {
                    "strategy": "Community Hashtags",
                    "description": "Use hashtags that build community",
                    "example_set": ["#community", "#together", "#support", "#share", "#connect"],
                    "expected_engagement": "25% increase"
                }
            ],
            "posting_optimization": {
                "optimal_times": [
                    {"day": "Tuesday", "time": "2:00 PM", "engagement_boost": "18%"},
                    {"day": "Wednesday", "time": "4:00 PM", "engagement_boost": "15%"},
                    {"day": "Friday", "time": "7:00 PM", "engagement_boost": "22%"}
                ],
                "frequency_recommendation": "5-6 posts per week for optimal growth",
                "content_mix": {
                    "educational": "40%",
                    "entertainment": "30%",
                    "behind_scenes": "20%",
                    "promotional": "10%"
                }
            }
        }
        
        return content_suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content suggestions: {str(e)}")

@router.get("/growth-strategy")
async def get_growth_strategy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized growth strategy recommendations"""
    try:
        service = GrowthRecommendationService(db)
        
        # Get growth strategy recommendations
        growth_recs = await service.get_user_recommendations(
            current_user.id, 
            recommendation_type="growth_strategy"
        )
        
        growth_strategy = {
            "current_stage": "Growing",  # Could be: Starting, Growing, Established, Scaling
            "growth_pillars": [
                {
                    "pillar": "Content Quality",
                    "current_score": 7.2,
                    "target_score": 9.0,
                    "actions": [
                        "Increase video content ratio to 60%",
                        "Implement consistent visual branding",
                        "Create content series for better engagement"
                    ],
                    "priority": "high"
                },
                {
                    "pillar": "Audience Engagement",
                    "current_score": 6.8,
                    "target_score": 8.5,
                    "actions": [
                        "Respond to comments within 2 hours",
                        "Create more interactive content (polls, Q&As)",
                        "Engage with your audience's content"
                    ],
                    "priority": "high"
                },
                {
                    "pillar": "Reach & Discovery",
                    "current_score": 5.5,
                    "target_score": 8.0,
                    "actions": [
                        "Optimize hashtag strategy",
                        "Post during peak audience times",
                        "Collaborate with other creators"
                    ],
                    "priority": "medium"
                },
                {
                    "pillar": "Community Building",
                    "current_score": 6.0,
                    "target_score": 8.5,
                    "actions": [
                        "Create branded hashtag campaign",
                        "Feature user-generated content",
                        "Host live Q&A sessions"
                    ],
                    "priority": "medium"
                }
            ],
            "30_day_plan": [
                {
                    "week": 1,
                    "focus": "Content Optimization",
                    "goals": ["Increase video content", "Establish posting schedule"],
                    "metrics": ["engagement_rate", "reach"]
                },
                {
                    "week": 2,
                    "focus": "Audience Engagement",
                    "goals": ["Improve response time", "Create interactive content"],
                    "metrics": ["comment_rate", "story_engagement"]
                },
                {
                    "week": 3,
                    "focus": "Hashtag Strategy",
                    "goals": ["Research and test new hashtags", "Optimize tag mix"],
                    "metrics": ["hashtag_reach", "discovery_rate"]
                },
                {
                    "week": 4,
                    "focus": "Community Building",
                    "goals": ["Launch UGC campaign", "Collaborate with others"],
                    "metrics": ["brand_mentions", "follower_growth"]
                }
            ],
            "success_metrics": {
                "primary": [
                    {"metric": "follower_growth", "current": "5.2%", "target": "8.0%"},
                    {"metric": "engagement_rate", "current": "4.8%", "target": "7.5%"},
                    {"metric": "reach_growth", "current": "12.3%", "target": "20.0%"}
                ],
                "secondary": [
                    {"metric": "brand_mentions", "current": "15/month", "target": "40/month"},
                    {"metric": "website_clicks", "current": "150/month", "target": "300/month"},
                    {"metric": "content_saves", "current": "8.2%", "target": "12.0%"}
                ]
            },
            "recommendations": growth_recs[:5] if growth_recs else []
        }
        
        return growth_strategy
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch growth strategy: {str(e)}")