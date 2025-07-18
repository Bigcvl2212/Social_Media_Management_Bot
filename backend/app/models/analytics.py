"""
Analytics models for tracking performance and insights
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Analytics(Base):
    """Analytics data for social media posts and accounts"""
    
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    content_schedule_id = Column(Integer, ForeignKey("content_schedules.id"), nullable=True)
    
    # Post identification
    platform_post_id = Column(String, nullable=True)
    post_url = Column(String, nullable=True)
    
    # Engagement metrics
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    saves = Column(BigInteger, default=0)
    views = Column(BigInteger, default=0)
    impressions = Column(BigInteger, default=0)
    reach = Column(BigInteger, default=0)
    
    # Advanced metrics
    engagement_rate = Column(Float, default=0.0)
    click_through_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # Time-based data
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    data_date = Column(DateTime(timezone=True), nullable=False)  # Date the metrics represent
    
    # Raw platform data
    platform_data = Column(JSON, nullable=True)  # Store raw analytics data from platform
    
    # Relationships
    social_account = relationship("SocialAccount")
    content_schedule = relationship("ContentSchedule")
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, post_id='{self.platform_post_id}', likes={self.likes})>"