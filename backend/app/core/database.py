"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
if "sqlite" in settings.DATABASE_URL:
    # SQLite configuration
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.DEBUG,
        future=True
    )

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.models.user import User
            from app.models.social_account import SocialAccount
            from app.models.content import Content, ContentSchedule
            from app.models.analytics import Analytics
            from app.models.competitor_analysis import CompetitorAccount, CompetitorAnalytics, CompetitorContent
            from app.models.audience_segmentation import AudienceSegment, AudienceInsight, EngagementPattern
            from app.models.growth_recommendations import GrowthRecommendation, ContentRecommendation, TimingRecommendation, HashtagRecommendation
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise