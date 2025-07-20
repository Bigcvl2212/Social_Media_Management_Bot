"""
Growth recommendations models for AI-generated suggestions and insights
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, BigInteger, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class GrowthRecommendation(Base):
    """AI-generated recommendations for growth and content optimization"""
    
    __tablename__ = "growth_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)  # Specific to one account or general
    
    # Recommendation metadata
    recommendation_type = Column(String, nullable=False)  # content, timing, hashtag, engagement, growth_strategy
    category = Column(String, nullable=False)  # posting_schedule, content_theme, hashtag_strategy, audience_targeting
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # AI confidence and scoring
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0 - How confident the AI is
    impact_score = Column(Float, default=0.0)  # 0.0 to 1.0 - Expected impact on growth
    difficulty_score = Column(Float, default=0.0)  # 0.0 to 1.0 - How difficult to implement
    priority_score = Column(Float, default=0.0)  # 0.0 to 1.0 - Overall priority (computed)
    
    # Recommendation details
    recommendation_data = Column(JSON, nullable=False)  # Specific recommendation details
    supporting_evidence = Column(JSON, nullable=True)  # Data that supports this recommendation
    expected_outcomes = Column(JSON, nullable=True)  # [{"metric": "engagement_rate", "improvement": 15.2}]
    
    # Implementation guidance
    actionable_steps = Column(JSON, nullable=True)  # [{"step": 1, "action": "...", "estimated_time": "15 min"}]
    required_resources = Column(JSON, nullable=True)  # ["content_creation", "scheduling_tool"]
    estimated_effort = Column(String, nullable=True)  # low, medium, high
    estimated_time = Column(String, nullable=True)  # "2 weeks", "1 month"
    
    # Context and basis
    data_sources = Column(JSON, nullable=True)  # What data was used to generate this
    analysis_period = Column(JSON, nullable=True)  # {"start": "2024-01-01", "end": "2024-01-31"}
    target_metrics = Column(JSON, nullable=True)  # ["engagement_rate", "follower_growth"]
    
    # Status tracking
    status = Column(String, default="active")  # active, implemented, dismissed, expired
    is_personalized = Column(Boolean, default=True)
    is_urgent = Column(Boolean, default=False)
    
    # Implementation tracking
    implementation_date = Column(DateTime(timezone=True), nullable=True)
    implementation_notes = Column(Text, nullable=True)
    actual_outcomes = Column(JSON, nullable=True)  # Track actual results
    effectiveness_score = Column(Float, nullable=True)  # How effective it was (post-implementation)
    
    # Validity
    valid_until = Column(DateTime(timezone=True), nullable=True)
    refresh_after = Column(DateTime(timezone=True), nullable=True)  # When to regenerate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    social_account = relationship("SocialAccount")
    
    def __repr__(self):
        return f"<GrowthRecommendation(id={self.id}, type='{self.recommendation_type}', priority={self.priority_score})>"


class ContentRecommendation(Base):
    """Specific content-focused recommendations"""
    
    __tablename__ = "content_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    growth_recommendation_id = Column(Integer, ForeignKey("growth_recommendations.id"), nullable=False)
    
    # Content specifics
    content_type = Column(String, nullable=False)  # video, image, text, carousel, story
    content_theme = Column(String, nullable=True)  # lifestyle, educational, behind_scenes
    content_format = Column(String, nullable=True)  # tutorial, showcase, testimonial
    
    # Content elements
    suggested_captions = Column(JSON, nullable=True)  # Multiple caption options
    recommended_hashtags = Column(JSON, nullable=True)  # [{"hashtag": "#fashion", "relevance": 0.9}]
    visual_guidelines = Column(JSON, nullable=True)  # Colors, composition, style
    posting_tips = Column(JSON, nullable=True)  # Specific posting advice
    
    # Performance prediction
    predicted_engagement = Column(Float, default=0.0)
    predicted_reach = Column(BigInteger, default=0)
    best_posting_time = Column(JSON, nullable=True)  # {"hour": 14, "day": "tuesday"}
    
    # Content inspiration
    trending_topics = Column(JSON, nullable=True)
    competitor_insights = Column(JSON, nullable=True)  # What competitors are doing well
    seasonal_relevance = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    growth_recommendation = relationship("GrowthRecommendation")
    
    def __repr__(self):
        return f"<ContentRecommendation(id={self.id}, type='{self.content_type}', theme='{self.content_theme}')>"


class TimingRecommendation(Base):
    """Optimal timing recommendations for posting"""
    
    __tablename__ = "timing_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    growth_recommendation_id = Column(Integer, ForeignKey("growth_recommendations.id"), nullable=False)
    
    # Timing specifics
    recommendation_scope = Column(String, nullable=False)  # daily, weekly, monthly, seasonal
    time_zone = Column(String, nullable=False)
    
    # Optimal times
    optimal_hours = Column(JSON, nullable=False)  # [{"hour": 14, "score": 0.95, "audience_activity": 0.85}]
    optimal_days = Column(JSON, nullable=False)  # [{"day": "tuesday", "score": 0.90}]
    optimal_frequency = Column(JSON, nullable=True)  # {"posts_per_day": 2, "posts_per_week": 7}
    
    # Audience behavior insights
    audience_activity_pattern = Column(JSON, nullable=True)
    peak_engagement_windows = Column(JSON, nullable=True)
    low_activity_periods = Column(JSON, nullable=True)  # When NOT to post
    
    # Platform-specific insights
    platform_trends = Column(JSON, nullable=True)
    algorithm_considerations = Column(JSON, nullable=True)
    competition_analysis = Column(JSON, nullable=True)  # When competitors post
    
    # Performance metrics
    expected_engagement_lift = Column(Float, default=0.0)
    expected_reach_improvement = Column(Float, default=0.0)
    confidence_level = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    growth_recommendation = relationship("GrowthRecommendation")
    
    def __repr__(self):
        return f"<TimingRecommendation(id={self.id}, scope='{self.recommendation_scope}')>"


class HashtagRecommendation(Base):
    """Hashtag strategy recommendations"""
    
    __tablename__ = "hashtag_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    growth_recommendation_id = Column(Integer, ForeignKey("growth_recommendations.id"), nullable=False)
    
    # Hashtag strategy
    strategy_type = Column(String, nullable=False)  # trending, niche, branded, seasonal
    hashtag_mix = Column(JSON, nullable=False)  # [{"category": "trending", "count": 5, "hashtags": [...]}]
    
    # Recommended hashtags
    primary_hashtags = Column(JSON, nullable=False)  # Main hashtags for reach
    secondary_hashtags = Column(JSON, nullable=True)  # Supporting hashtags
    niche_hashtags = Column(JSON, nullable=True)  # Targeted, specific hashtags
    trending_hashtags = Column(JSON, nullable=True)  # Currently trending
    
    # Performance data
    hashtag_performance = Column(JSON, nullable=True)  # Historical performance of suggested hashtags
    competitor_hashtags = Column(JSON, nullable=True)  # What competitors use successfully
    opportunity_hashtags = Column(JSON, nullable=True)  # Underutilized but promising
    
    # Strategy guidance
    usage_guidelines = Column(JSON, nullable=True)  # How to use these hashtags
    rotation_schedule = Column(JSON, nullable=True)  # When to rotate hashtags
    avoid_hashtags = Column(JSON, nullable=True)  # Hashtags to avoid
    
    # Expected outcomes
    expected_reach_increase = Column(Float, default=0.0)
    expected_engagement_lift = Column(Float, default=0.0)
    discovery_potential = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    growth_recommendation = relationship("GrowthRecommendation")
    
    def __repr__(self):
        return f"<HashtagRecommendation(id={self.id}, strategy='{self.strategy_type}')>"