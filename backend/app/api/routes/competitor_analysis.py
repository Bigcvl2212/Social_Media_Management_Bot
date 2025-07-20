"""
Competitor analysis API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.competitor_analysis_service import CompetitorAnalysisService

router = APIRouter()

# Pydantic models for request/response
class AddCompetitorRequest(BaseModel):
    platform: str
    username: str
    display_name: Optional[str] = None

class CompetitorResponse(BaseModel):
    id: int
    platform: str
    username: str
    display_name: Optional[str]
    follower_count: int
    following_count: int
    post_count: int
    is_active: bool
    created_at: str
    last_analyzed: Optional[str]

class CompetitorAnalyticsResponse(BaseModel):
    competitor_id: int
    follower_count: int
    engagement_rate: float
    posting_frequency: float
    follower_growth: int
    popular_hashtags: Optional[List[Dict[str, Any]]]
    content_themes: Optional[List[Dict[str, Any]]]
    recorded_at: str

class CompetitorTrendsResponse(BaseModel):
    total_competitors: int
    platform_distribution: Dict[str, int]
    growth_leaders: List[Dict[str, Any]]
    engagement_leaders: List[Dict[str, Any]]
    trending_hashtags: List[Dict[str, Any]]
    optimal_posting_times: List[Dict[str, Any]]
    content_themes: List[Dict[str, Any]]
    analysis_period: Dict[str, str]

@router.post("/competitors", response_model=Dict[str, Any])
async def add_competitor(
    request: AddCompetitorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new competitor to track"""
    try:
        service = CompetitorAnalysisService(db)
        competitor = await service.add_competitor(
            user_id=current_user.id,
            platform=request.platform,
            username=request.username,
            display_name=request.display_name
        )
        
        return {
            "id": competitor.id,
            "platform": competitor.platform,
            "username": competitor.username,
            "display_name": competitor.display_name,
            "follower_count": competitor.follower_count,
            "following_count": competitor.following_count,
            "post_count": competitor.post_count,
            "is_active": competitor.is_active,
            "created_at": competitor.created_at.isoformat(),
            "last_analyzed": competitor.last_analyzed.isoformat() if competitor.last_analyzed else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add competitor: {str(e)}")

@router.get("/competitors", response_model=List[Dict[str, Any]])
async def get_competitors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all competitors for the current user"""
    try:
        service = CompetitorAnalysisService(db)
        competitors = await service.get_user_competitors(current_user.id)
        
        result = []
        for competitor in competitors:
            result.append({
                "id": competitor.id,
                "platform": competitor.platform,
                "username": competitor.username,
                "display_name": competitor.display_name,
                "follower_count": competitor.follower_count,
                "following_count": competitor.following_count,
                "post_count": competitor.post_count,
                "is_active": competitor.is_active,
                "created_at": competitor.created_at.isoformat(),
                "last_analyzed": competitor.last_analyzed.isoformat() if competitor.last_analyzed else None
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitors: {str(e)}")

@router.get("/competitors/{competitor_id}/analytics")
async def get_competitor_analytics(
    competitor_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific competitor"""
    try:
        service = CompetitorAnalysisService(db)
        analytics = await service.get_competitor_analytics(competitor_id, days)
        
        result = []
        for analytic in analytics:
            result.append({
                "competitor_id": analytic.competitor_account_id,
                "follower_count": analytic.follower_count,
                "following_count": analytic.following_count,
                "post_count": analytic.post_count,
                "avg_likes": analytic.avg_likes,
                "avg_comments": analytic.avg_comments,
                "avg_shares": analytic.avg_shares,
                "engagement_rate": analytic.engagement_rate,
                "follower_growth": analytic.follower_growth,
                "posting_frequency": analytic.posting_frequency,
                "popular_hashtags": analytic.popular_hashtags,
                "content_themes": analytic.content_themes,
                "recorded_at": analytic.recorded_at.isoformat(),
                "data_date": analytic.data_date.isoformat()
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitor analytics: {str(e)}")

@router.get("/competitors/{competitor_id}/insights")
async def get_competitor_insights(
    competitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed insights for a specific competitor"""
    try:
        service = CompetitorAnalysisService(db)
        insights = await service.get_competitor_insights(competitor_id)
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitor insights: {str(e)}")

@router.get("/trends", response_model=CompetitorTrendsResponse)
async def get_competitor_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trends analysis across all competitors"""
    try:
        service = CompetitorAnalysisService(db)
        trends = await service.analyze_competitor_trends(current_user.id, days)
        return trends
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitor trends: {str(e)}")

@router.delete("/competitors/{competitor_id}")
async def remove_competitor(
    competitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a competitor from tracking"""
    try:
        service = CompetitorAnalysisService(db)
        success = await service.remove_competitor(current_user.id, competitor_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        return {"message": "Competitor removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove competitor: {str(e)}")

@router.get("/dashboard")
async def get_competitor_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get competitor analysis dashboard data"""
    try:
        service = CompetitorAnalysisService(db)
        
        # Get basic competitor stats
        competitors = await service.get_user_competitors(current_user.id)
        trends = await service.analyze_competitor_trends(current_user.id, 30)
        
        # Calculate summary metrics
        total_competitors = len(competitors)
        active_competitors = len([c for c in competitors if c.is_active])
        
        # Get top performing competitor
        top_competitor = None
        if trends.get("engagement_leaders"):
            top_competitor = trends["engagement_leaders"][0]
        
        return {
            "summary": {
                "total_competitors": total_competitors,
                "active_competitors": active_competitors,
                "platforms_tracked": len(trends.get("platform_distribution", {})),
                "last_updated": competitors[0].last_analyzed.isoformat() if competitors and competitors[0].last_analyzed else None
            },
            "top_performer": top_competitor,
            "platform_distribution": trends.get("platform_distribution", {}),
            "trending_hashtags": trends.get("trending_hashtags", [])[:5],  # Top 5
            "growth_opportunities": [
                {
                    "title": "Hashtag Optimization",
                    "description": "Top competitors are using hashtags you're not utilizing",
                    "action": "Analyze trending hashtags from successful competitors"
                },
                {
                    "title": "Posting Schedule",
                    "description": "Competitors post during high-engagement windows",
                    "action": "Align your posting schedule with peak competitor activity"
                },
                {
                    "title": "Content Themes",
                    "description": "Emerging content themes showing strong performance",
                    "action": "Experiment with trending content themes in your niche"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitor dashboard: {str(e)}")