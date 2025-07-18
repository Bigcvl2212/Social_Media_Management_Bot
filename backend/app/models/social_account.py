"""
Social media account models for multi-platform support
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SocialPlatform(str, enum.Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


class AccountStatus(str, enum.Enum):
    """Social account connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    EXPIRED = "expired"


class SocialAccount(Base):
    """Social media account with secure credential storage"""
    
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Platform details
    platform = Column(SQLEnum(SocialPlatform), nullable=False)
    platform_user_id = Column(String, nullable=False)  # Platform-specific user ID
    username = Column(String, nullable=False)  # Display username
    display_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    
    # Connection status
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.CONNECTED)
    
    # Encrypted credentials (stored securely)
    access_token = Column(Text, nullable=True)  # Will be encrypted
    refresh_token = Column(Text, nullable=True)  # Will be encrypted
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Platform-specific settings and metadata
    platform_data = Column(JSON, nullable=True)  # Store platform-specific info
    permissions = Column(JSON, nullable=True)  # Granted permissions
    
    # Settings
    auto_post = Column(Boolean, default=True)
    auto_engage = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
    content_schedules = relationship("ContentSchedule", back_populates="social_account")
    
    def __repr__(self):
        return f"<SocialAccount(id={self.id}, platform='{self.platform}', username='{self.username}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if account is actively connected"""
        return self.status == AccountStatus.CONNECTED
    
    @property
    def needs_reauth(self) -> bool:
        """Check if account needs re-authentication"""
        return self.status in [AccountStatus.EXPIRED, AccountStatus.ERROR]