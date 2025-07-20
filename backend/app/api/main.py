"""
Main API router combining all endpoints
"""

from fastapi import APIRouter


from app.api.routes import auth, users, social_accounts, content, analytics, upload, monetization


from app.api.routes import (
    auth, users, social_accounts, content, analytics, upload,
    competitor_analysis, audience_insights, growth_recommendations
)

from app.api.routes import auth, users, social_accounts, content, analytics, upload, accessibility



api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["social-accounts"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])

api_router.include_router(monetization.router, tags=["monetization"])



# Growth & Audience Insights routes
api_router.include_router(competitor_analysis.router, prefix="/analytics/competitors", tags=["competitor-analysis"])
api_router.include_router(audience_insights.router, prefix="/analytics/audience", tags=["audience-insights"])
api_router.include_router(growth_recommendations.router, prefix="/analytics/recommendations", tags=["growth-recommendations"])

api_router.include_router(accessibility.router, prefix="/accessibility", tags=["accessibility"])


