"""
Content curation and inspiration board models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class CurationCollectionType(str, enum.Enum):
    """Types of curation collections"""
    INSPIRATION_BOARD = "inspiration_board"
    TEMPLATE_COLLECTION = "template_collection"
    TREND_WATCHLIST = "trend_watchlist"
    CONTENT_IDEAS = "content_ideas"


class CurationItemType(str, enum.Enum):
    """Types of items that can be curated"""
    TREND = "trend"
    HASHTAG = "hashtag"
    AUDIO_TRACK = "audio_track"
    CONTENT_IDEA = "content_idea"
    TEMPLATE = "template"
    INSPIRATION_POST = "inspiration_post"
    COMPETITOR_CONTENT = "competitor_content"


class CurationItemStatus(str, enum.Enum):
    """Status of curated items"""
    SAVED = "saved"
    IN_PROGRESS = "in_progress"
    USED = "used"
    ARCHIVED = "archived"


class CurationCollection(Base):
    """Collections for organizing curated content and ideas"""
    
    __tablename__ = "curation_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Collection details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    collection_type = Column(SQLEnum(CurationCollectionType), nullable=False)
    
    # Collection settings
    is_public = Column(Boolean, default=False)
    color_theme = Column(String, nullable=True)  # For UI organization
    tags = Column(JSON, nullable=True)  # Array of tags for filtering
    
    # Auto-curation settings
    auto_curate_trends = Column(Boolean, default=False)
    auto_curate_keywords = Column(JSON, nullable=True)  # Keywords to auto-monitor
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="curation_collections")
    items = relationship("CurationItem", back_populates="collection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CurationCollection(id={self.id}, name='{self.name}', type='{self.collection_type}')>"


class CurationItem(Base):
    """Individual items saved to curation collections"""
    
    __tablename__ = "curation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("curation_collections.id"), nullable=False)
    
    # Item details
    item_type = Column(SQLEnum(CurationItemType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(CurationItemStatus), default=CurationItemStatus.SAVED)
    
    # Content metadata
    source_url = Column(String, nullable=True)  # Original URL if from external source
    source_platform = Column(String, nullable=True)  # Platform where content was found
    thumbnail_url = Column(String, nullable=True)
    
    # Item-specific data
    item_data = Column(JSON, nullable=True)  # Store type-specific data
    """
    Examples of item_data:
    - Trend: {"volume": 1000000, "growth_rate": "+50%", "hashtags": ["#ai", "#tech"]}
    - Hashtag: {"usage_count": 500000, "engagement_rate": 0.08, "trending_score": 8.5}
    - Audio: {"duration": 30, "artist": "Artist Name", "usage_count": 100000}
    - Content Idea: {"content_type": "video", "estimated_time": "5 min", "difficulty": "easy"}
    - Template: {"platform": "instagram", "dimensions": "1080x1080", "elements": [...]}
    """
    
    # User annotations
    user_notes = Column(Text, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 star rating
    user_tags = Column(JSON, nullable=True)  # User-defined tags
    
    # AI analysis
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights about the item
    viral_potential_score = Column(Integer, nullable=True)  # AI predicted viral score 1-10
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    collection = relationship("CurationCollection", back_populates="items")
    
    def __repr__(self):
        return f"<CurationItem(id={self.id}, title='{self.title}', type='{self.item_type}')>"


class TrendWatch(Base):
    """Real-time trend monitoring and alerts"""
    
    __tablename__ = "trend_watches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Watch configuration
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Monitoring criteria
    keywords = Column(JSON, nullable=False)  # Keywords to monitor
    platforms = Column(JSON, nullable=False)  # Platforms to monitor
    regions = Column(JSON, nullable=True)  # Geographic regions to monitor
    
    # Alert settings
    is_active = Column(Boolean, default=True)
    alert_threshold = Column(Integer, default=1000)  # Minimum volume for alert
    notification_frequency = Column(String, default="daily")  # hourly, daily, weekly
    
    # Monitoring results
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    total_alerts_sent = Column(Integer, default=0)
    
    # Auto-curation settings
    auto_save_to_collection_id = Column(Integer, ForeignKey("curation_collections.id"), nullable=True)
    auto_save_threshold = Column(Integer, default=5000)  # Auto-save if trend volume exceeds this
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trend_watches")
    auto_save_collection = relationship("CurationCollection", foreign_keys=[auto_save_to_collection_id])
    alerts = relationship("TrendAlert", back_populates="trend_watch", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TrendWatch(id={self.id}, name='{self.name}', active={self.is_active})>"


class TrendAlert(Base):
    """Individual trend alerts generated by monitoring"""
    
    __tablename__ = "trend_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    trend_watch_id = Column(Integer, ForeignKey("trend_watches.id"), nullable=False)
    
    # Alert details
    trend_name = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # "new_trend", "volume_spike", "growth_surge"
    
    # Trend data
    current_volume = Column(Integer, nullable=True)
    growth_rate = Column(String, nullable=True)
    trend_data = Column(JSON, nullable=True)  # Full trend data snapshot
    
    # Alert status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    auto_saved_to_collection = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    trend_watch = relationship("TrendWatch", back_populates="alerts")
    
    def __repr__(self):
        return f"<TrendAlert(id={self.id}, trend='{self.trend_name}', platform='{self.platform}')>"