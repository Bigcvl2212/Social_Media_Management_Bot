"""
Monetization models for brand collaboration, campaigns, and affiliate marketing
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from decimal import Decimal

from app.core.database import Base


class BrandType(str, enum.Enum):
    """Types of brands"""
    FASHION = "fashion"
    BEAUTY = "beauty"
    TECH = "tech"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    LIFESTYLE = "lifestyle"
    GAMING = "gaming"
    EDUCATION = "education"
    OTHER = "other"


class CampaignType(str, enum.Enum):
    """Types of campaigns"""
    SPONSORED_POST = "sponsored_post"
    PRODUCT_PLACEMENT = "product_placement"
    BRAND_AMBASSADOR = "brand_ambassador"
    AFFILIATE_MARKETING = "affiliate_marketing"
    GIVEAWAY = "giveaway"
    REVIEW = "review"
    COLLABORATION = "collaboration"


class CampaignStatus(str, enum.Enum):
    """Campaign status lifecycle"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CollaborationStatus(str, enum.Enum):
    """Collaboration status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status for campaigns"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Brand(Base):
    """Brand model for company profiles and brand information"""
    
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Brand owner/manager
    
    # Basic brand info
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    
    # Brand details
    industry = Column(SQLEnum(BrandType), nullable=False)
    company_size = Column(String, nullable=True)  # "startup", "small", "medium", "large", "enterprise"
    location = Column(String, nullable=True)
    
    # Contact information
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    
    # Social media presence
    social_media_handles = Column(JSON, nullable=True)  # {"instagram": "@brand", "twitter": "@brand"}
    
    # Verification and status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Collaboration preferences
    collaboration_budget = Column(Float, nullable=True)  # Monthly/campaign budget
    preferred_platforms = Column(JSON, nullable=True)  # ["instagram", "tiktok", "youtube"]
    target_demographics = Column(JSON, nullable=True)  # Age groups, interests, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="brand_profiles")
    campaigns = relationship("Campaign", back_populates="brand")
    collaborations = relationship("Collaboration", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', industry='{self.industry}')>"


class Campaign(Base):
    """Campaign model for sponsorship and ad campaign tracking"""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    # Campaign details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(SQLEnum(CampaignType), nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Campaign specifics
    budget = Column(Float, nullable=False)
    target_platforms = Column(JSON, nullable=False)  # ["instagram", "tiktok"]
    target_audience = Column(JSON, nullable=True)  # Demographics, interests
    
    # Content requirements
    content_requirements = Column(JSON, nullable=True)  # Post types, hashtags, mentions
    deliverables = Column(JSON, nullable=True)  # Expected deliverables
    
    # Timeline
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Performance tracking
    target_metrics = Column(JSON, nullable=True)  # Expected reach, engagement, etc.
    actual_metrics = Column(JSON, nullable=True)  # Actual performance data
    
    # Payment information
    payment_amount = Column(Float, nullable=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="campaigns")
    collaborations = relationship("Collaboration", back_populates="campaign")
    affiliate_links = relationship("AffiliateLink", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', type='{self.campaign_type}')>"


class Collaboration(Base):
    """Collaboration model for influencer/brand partnerships"""
    
    __tablename__ = "collaborations"
    
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Influencer/creator
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)  # Optional campaign link
    
    # Collaboration details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(CollaborationStatus), default=CollaborationStatus.PENDING)
    
    # Terms and deliverables
    deliverables = Column(JSON, nullable=False)  # What the influencer needs to deliver
    compensation = Column(Float, nullable=True)  # Payment amount
    compensation_type = Column(String, nullable=True)  # "fixed", "per_post", "revenue_share"
    
    # Content details
    content_requirements = Column(JSON, nullable=True)  # Specific content requirements
    platforms = Column(JSON, nullable=False)  # ["instagram", "tiktok"]
    
    # Timeline
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Content tracking
    content_ids = Column(JSON, nullable=True)  # IDs of created content
    approval_status = Column(String, default="pending")  # "pending", "approved", "rejected"
    
    # Performance and analytics
    performance_metrics = Column(JSON, nullable=True)  # Reach, engagement, conversions
    
    # Contract and legal
    contract_url = Column(String, nullable=True)
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    influencer = relationship("User", back_populates="collaborations")
    brand = relationship("Brand", back_populates="collaborations")
    campaign = relationship("Campaign", back_populates="collaborations")
    
    # Unique constraint to prevent duplicate collaborations
    __table_args__ = (UniqueConstraint('influencer_id', 'brand_id', 'campaign_id', name='unique_collaboration'),)
    
    def __repr__(self):
        return f"<Collaboration(id={self.id}, title='{self.title}', status='{self.status}')>"


class AffiliateLink(Base):
    """Affiliate link model for affiliate marketing and tracking"""
    
    __tablename__ = "affiliate_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Link owner
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)  # Associated brand
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)  # Associated campaign
    
    # Link details
    name = Column(String, nullable=False)
    original_url = Column(String, nullable=False)
    affiliate_code = Column(String, nullable=False, unique=True, index=True)
    short_url = Column(String, nullable=True, unique=True)  # Shortened tracking URL
    
    # Product/service information
    product_name = Column(String, nullable=True)
    product_description = Column(Text, nullable=True)
    product_image_url = Column(String, nullable=True)
    
    # Commission settings
    commission_rate = Column(Float, nullable=False, default=0.0)  # Percentage
    commission_type = Column(String, default="percentage")  # "percentage", "fixed", "tiered"
    commission_settings = Column(JSON, nullable=True)  # Additional commission rules
    
    # Tracking and analytics
    click_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    last_clicked = Column(DateTime(timezone=True), nullable=True)
    
    # Link configuration
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reporting and analytics
    analytics_data = Column(JSON, nullable=True)  # Detailed click/conversion data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="affiliate_links")
    brand = relationship("Brand", back_populates="affiliate_links")
    campaign = relationship("Campaign", back_populates="affiliate_links")
    
    def __repr__(self):
        return f"<AffiliateLink(id={self.id}, name='{self.name}', code='{self.affiliate_code}')>"
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate"""
        if self.click_count == 0:
            return 0.0
        return (self.conversion_count / self.click_count) * 100


# Update existing models with new relationships
def add_monetization_relationships():
    """Function to add monetization relationships to existing models"""
    from app.models.user import User
    
    # Add relationships to User model
    User.brand_profiles = relationship("Brand", back_populates="user", cascade="all, delete-orphan")
    User.collaborations = relationship("Collaboration", back_populates="influencer", cascade="all, delete-orphan") 
    User.affiliate_links = relationship("AffiliateLink", back_populates="user", cascade="all, delete-orphan")
    User.owned_brands = relationship("Brand", back_populates="user")