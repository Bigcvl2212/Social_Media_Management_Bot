"""
Content models for content management and scheduling
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ContentType(str, enum.Enum):
    """Types of content supported"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class ContentStatus(str, enum.Enum):
    """Content status lifecycle"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class ScheduleStatus(str, enum.Enum):
    """Schedule status for automated posting"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Content(Base):
    """Content model for storing and managing media content"""
    
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic content info
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT)
    
    # File information
    file_path = Column(String, nullable=True)  # Path to original file
    thumbnail_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # For videos, in seconds
    
    # AI-generated content
    ai_generated = Column(Boolean, default=False)
    ai_metadata = Column(JSON, nullable=True)  # Store AI processing info
    
    # Content metadata
    tags = Column(JSON, nullable=True)  # Array of tags
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    mentions = Column(JSON, nullable=True)  # Array of mentions
    
    # Platform-specific variations
    platform_variants = Column(JSON, nullable=True)  # Different versions for different platforms
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by_user = relationship("User", back_populates="content")
    schedules = relationship("ContentSchedule", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"


class ContentSchedule(Base):
    """Scheduled content posting to social media platforms"""
    
    __tablename__ = "content_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Scheduling details
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.PENDING)
    
    # Platform-specific content
    caption = Column(Text, nullable=True)
    platform_specific_data = Column(JSON, nullable=True)  # Platform-specific options
    
    # Posting results
    posted_at = Column(DateTime(timezone=True), nullable=True)
    platform_post_id = Column(String, nullable=True)  # ID from social platform
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", back_populates="schedules")
    social_account = relationship("SocialAccount", back_populates="content_schedules")
    
    def __repr__(self):
        return f"<ContentSchedule(id={self.id}, content_id={self.content_id}, scheduled_time='{self.scheduled_time}')>"