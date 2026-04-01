"""
Main API router combining all endpoints
"""

from fastapi import APIRouter

from app.api.routes import (
    auth, users, social_accounts, analytics, upload, monetization,
    automation, integrations, campaigns, api_management, zapier, admin,
    competitor_analysis, audience_insights, growth_recommendations,
    facebook, facebook_ads, leads, webhooks, scheduler, messenger,
    content, gym_context, autopilot, clip_studio,
    brand_dna, content_vault, engagement, remix, growth, competitor_spy,
)

api_router = APIRouter()

# Core routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["social-accounts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(monetization.router, tags=["monetization"])

# Integration routes
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(api_management.router, prefix="/api", tags=["api-management"])
api_router.include_router(zapier.router, prefix="/zapier", tags=["zapier"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation"])

# Analytics routes
api_router.include_router(competitor_analysis.router, prefix="/analytics/competitors", tags=["competitor-analysis"])
api_router.include_router(audience_insights.router, prefix="/analytics/audience", tags=["audience-insights"])
api_router.include_router(growth_recommendations.router, prefix="/analytics/recommendations", tags=["growth-recommendations"])

# Facebook / Gym Bot services
api_router.include_router(facebook.router, prefix="/facebook", tags=["facebook"])
api_router.include_router(facebook_ads.router, prefix="/facebook-ads", tags=["facebook-ads"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(messenger.router, prefix="/messenger", tags=["messenger"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(gym_context.router, prefix="/gym-context", tags=["gym-context"])
api_router.include_router(autopilot.router, prefix="/autopilot", tags=["autopilot"])
api_router.include_router(clip_studio.router, prefix="/clip-studio", tags=["clip-studio"])

# New feature routes
api_router.include_router(brand_dna.router, prefix="/brand-dna", tags=["brand-dna"])
api_router.include_router(content_vault.router, prefix="/content-vault", tags=["content-vault"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["engagement"])
api_router.include_router(remix.router, prefix="/remix", tags=["remix"])
api_router.include_router(growth.router, prefix="/growth", tags=["growth"])
api_router.include_router(competitor_spy.router, prefix="/competitor-spy", tags=["competitor-spy"])


