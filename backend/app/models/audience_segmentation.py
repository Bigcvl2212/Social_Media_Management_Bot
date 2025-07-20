"""
Audience segmentation models for analyzing user demographics and engagement patterns
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, BigInteger, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class AudienceSegment(Base):
    """Audience segments based on demographics, interests, and behavior"""
    
    __tablename__ = "audience_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)  # Specific to one account or all
    
    # Segment identification
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    segment_type = Column(String, nullable=False)  # demographic, behavioral, geographic, psychographic
    
    # Segment criteria (JSON structure for flexible criteria)
    criteria = Column(JSON, nullable=False)  # {"age_range": [18, 34], "interests": ["fashion"], "engagement_level": "high"}
    
    # Segment metrics
    audience_size = Column(BigInteger, default=0)
    percentage_of_total = Column(Float, default=0.0)
    
    # Engagement metrics for this segment
    avg_engagement_rate = Column(Float, default=0.0)
    avg_likes_per_post = Column(Float, default=0.0)
    avg_comments_per_post = Column(Float, default=0.0)
    avg_shares_per_post = Column(Float, default=0.0)
    
    # Behavioral patterns
    most_active_hours = Column(JSON, nullable=True)  # [{"hour": 14, "activity_score": 0.85}]
    most_active_days = Column(JSON, nullable=True)  # [{"day": "tuesday", "activity_score": 0.75}]
    content_preferences = Column(JSON, nullable=True)  # [{"content_type": "video", "preference_score": 0.90}]
    
    # Demographics (if available from platform)
    age_distribution = Column(JSON, nullable=True)  # [{"age_range": "18-24", "percentage": 35.2}]
    gender_distribution = Column(JSON, nullable=True)  # [{"gender": "female", "percentage": 62.1}]
    location_distribution = Column(JSON, nullable=True)  # [{"country": "US", "percentage": 45.3, "city": "New York"}]
    
    # Interests and behavior
    top_interests = Column(JSON, nullable=True)  # [{"interest": "fashion", "score": 0.85}]
    brand_affinity = Column(JSON, nullable=True)  # [{"brand": "nike", "affinity_score": 0.75}]
    
    # Segment status
    is_active = Column(Boolean, default=True)
    last_calculated = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    social_account = relationship("SocialAccount")
    insights = relationship("AudienceInsight", back_populates="segment")
    
    def __repr__(self):
        return f"<AudienceSegment(id={self.id}, name='{self.name}', size={self.audience_size})>"


class AudienceInsight(Base):
    """Specific insights and analytics for audience segments"""
    
    __tablename__ = "audience_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("audience_segments.id"), nullable=False)
    
    # Insight metadata
    insight_type = Column(String, nullable=False)  # engagement_pattern, content_preference, optimal_timing, growth_opportunity
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Insight data
    insight_data = Column(JSON, nullable=False)  # Flexible structure for different insight types
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    impact_score = Column(Float, default=0.0)  # Expected impact on engagement/growth
    
    # Actionability
    actionable = Column(Boolean, default=True)
    recommended_actions = Column(JSON, nullable=True)  # [{"action": "post_at_time", "params": {"hour": 14}}]
    
    # Validity period
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime(timezone=True), nullable=True)
    result_metrics = Column(JSON, nullable=True)  # Track results if implemented
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    segment = relationship("AudienceSegment", back_populates="insights")
    
    def __repr__(self):
        return f"<AudienceInsight(id={self.id}, type='{self.insight_type}', confidence={self.confidence_score})>"


class EngagementPattern(Base):
    """Detailed engagement patterns for audience analysis"""
    
    __tablename__ = "engagement_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)
    
    # Pattern identification
    pattern_type = Column(String, nullable=False)  # hourly, daily, weekly, content_type, hashtag
    pattern_name = Column(String, nullable=False)
    
    # Pattern data
    pattern_data = Column(JSON, nullable=False)  # Flexible structure for different pattern types
    strength = Column(Float, default=0.0)  # How strong/consistent this pattern is (0.0 to 1.0)
    
    # Performance metrics
    avg_engagement_rate = Column(Float, default=0.0)
    avg_reach = Column(BigInteger, default=0)
    total_interactions = Column(BigInteger, default=0)
    
    # Sample size and confidence
    sample_size = Column(Integer, default=0)  # Number of data points used
    confidence_level = Column(Float, default=0.0)  # Statistical confidence
    
    # Time period analysis
    analysis_start_date = Column(DateTime(timezone=True), nullable=False)
    analysis_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Pattern evolution
    trend_direction = Column(String, nullable=True)  # increasing, decreasing, stable
    trend_strength = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When pattern should be recalculated
    
    # Relationships
    user = relationship("User")
    social_account = relationship("SocialAccount")
    
    def __repr__(self):
        return f"<EngagementPattern(id={self.id}, type='{self.pattern_type}', strength={self.strength})>"