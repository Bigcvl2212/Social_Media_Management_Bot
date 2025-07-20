"""
Competitor analysis models for tracking and analyzing competitor performance
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, BigInteger, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class CompetitorAccount(Base):
    """Competitor social media accounts to track"""
    
    __tablename__ = "competitor_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User who added this competitor
    
    # Account identification
    platform = Column(String, nullable=False)  # instagram, twitter, tiktok, etc.
    username = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    profile_url = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Account metadata
    description = Column(Text, nullable=True)
    follower_count = Column(BigInteger, default=0)
    following_count = Column(BigInteger, default=0)
    post_count = Column(BigInteger, default=0)
    
    # Tracking settings
    is_active = Column(Boolean, default=True)
    track_frequency = Column(String, default="daily")  # daily, weekly, monthly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_analyzed = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    analytics = relationship("CompetitorAnalytics", back_populates="competitor_account")
    
    def __repr__(self):
        return f"<CompetitorAccount(id={self.id}, platform='{self.platform}', username='{self.username}')>"


class CompetitorAnalytics(Base):
    """Analytics data for competitor accounts"""
    
    __tablename__ = "competitor_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_account_id = Column(Integer, ForeignKey("competitor_accounts.id"), nullable=False)
    
    # Metrics snapshot
    follower_count = Column(BigInteger, default=0)
    following_count = Column(BigInteger, default=0)
    post_count = Column(BigInteger, default=0)
    
    # Engagement metrics (calculated from recent posts)
    avg_likes = Column(Float, default=0.0)
    avg_comments = Column(Float, default=0.0)
    avg_shares = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    
    # Growth metrics
    follower_growth = Column(BigInteger, default=0)  # Change since last snapshot
    following_growth = Column(BigInteger, default=0)
    post_growth = Column(BigInteger, default=0)
    
    # Content analysis
    posting_frequency = Column(Float, default=0.0)  # Posts per day
    optimal_posting_times = Column(JSON, nullable=True)  # [{"hour": 10, "day": "monday", "score": 0.85}]
    popular_hashtags = Column(JSON, nullable=True)  # [{"hashtag": "#fashion", "count": 15, "engagement": 1250}]
    content_themes = Column(JSON, nullable=True)  # [{"theme": "lifestyle", "percentage": 45.2}]
    
    # Platform-specific data
    platform_data = Column(JSON, nullable=True)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    data_date = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    competitor_account = relationship("CompetitorAccount", back_populates="analytics")
    
    def __repr__(self):
        return f"<CompetitorAnalytics(id={self.id}, competitor_id={self.competitor_account_id}, followers={self.follower_count})>"


class CompetitorContent(Base):
    """Individual content posts from competitors for detailed analysis"""
    
    __tablename__ = "competitor_content"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_account_id = Column(Integer, ForeignKey("competitor_accounts.id"), nullable=False)
    
    # Content identification
    platform_post_id = Column(String, nullable=False)
    post_url = Column(String, nullable=True)
    content_type = Column(String, nullable=False)  # image, video, text, carousel
    
    # Content metadata
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # ["#fashion", "#style"]
    mentions = Column(JSON, nullable=True)  # ["@username1", "@username2"]
    
    # Performance metrics
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    views = Column(BigInteger, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Analysis data
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    content_themes = Column(JSON, nullable=True)
    visual_elements = Column(JSON, nullable=True)  # colors, objects detected, etc.
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=False)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    competitor_account = relationship("CompetitorAccount")
    
    def __repr__(self):
        return f"<CompetitorContent(id={self.id}, post_id='{self.platform_post_id}', likes={self.likes})>"