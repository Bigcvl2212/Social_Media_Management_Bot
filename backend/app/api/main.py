"""
Main API router combining all endpoints
"""

from fastapi import APIRouter

from app.api.routes import auth, users, social_accounts, content, analytics, upload, monetization

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["social-accounts"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(monetization.router, tags=["monetization"])