"""
User model with multi-user support and role-based access control
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for role-based access control"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base):
    """User model with authentication and role management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Authentication
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth providers
    google_id = Column(String, unique=True, nullable=True)
    microsoft_id = Column(String, unique=True, nullable=True)
    
    # Role and permissions
    role = Column(SQLEnum(UserRole), default=UserRole.EDITOR)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="created_by_user", cascade="all, delete-orphan")

    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    zapier_webhooks = relationship("ZapierWebhook", back_populates="user", cascade="all, delete-orphan")

    direct_messages = relationship("DirectMessage", back_populates="user", cascade="all, delete-orphan")
    comment_management = relationship("CommentManagement", back_populates="user", cascade="all, delete-orphan")
    moderation_rules = relationship("ModerationRule", back_populates="user", cascade="all, delete-orphan")
    moderation_logs = relationship("ModerationLog", back_populates="user", cascade="all, delete-orphan")
    automation_config = relationship("AutomationConfig", back_populates="user", cascade="all, delete-orphan")

    
    # Monetization relationships
    brand_profiles = relationship("Brand", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("Collaboration", back_populates="influencer", cascade="all, delete-orphan")
    affiliate_links = relationship("AffiliateLink", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def can_edit(self) -> bool:
        """Check if user can edit content"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN, UserRole.EDITOR]
    
    def can_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    def is_owner(self) -> bool:
        """Check if user is owner"""
        return self.role == UserRole.OWNER