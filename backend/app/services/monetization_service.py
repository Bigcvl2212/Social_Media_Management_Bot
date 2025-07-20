"""
Monetization service for handling brand collaboration, campaigns, and affiliate marketing
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import string
from urllib.parse import urljoin

from app.models.monetization import Brand, Campaign, Collaboration, AffiliateLink
from app.models.monetization import BrandType, CampaignType, CampaignStatus, CollaborationStatus, PaymentStatus
from app.schemas.monetization import (
    BrandCreate, BrandUpdate, CampaignCreate, CampaignUpdate,
    CollaborationCreate, CollaborationUpdate, AffiliateLinkCreate, AffiliateLinkUpdate,
    BrandMarketplaceFilter, CampaignMarketplaceFilter
)


class MonetizationService:
    """Service for handling monetization features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Brand Management
    def create_brand(self, brand_data: BrandCreate, user_id: int) -> Brand:
        """Create a new brand profile"""
        brand = Brand(
            user_id=user_id,
            **brand_data.dict()
        )
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand
    
    def get_brand(self, brand_id: int, user_id: Optional[int] = None) -> Optional[Brand]:
        """Get a brand by ID"""
        query = self.db.query(Brand).filter(Brand.id == brand_id)
        if user_id:
            query = query.filter(Brand.user_id == user_id)
        return query.first()
    
    def get_brands(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Get brands with optional user filter"""
        query = self.db.query(Brand)
        if user_id:
            query = query.filter(Brand.user_id == user_id)
        return query.filter(Brand.is_active == True).offset(skip).limit(limit).all()
    
    def update_brand(self, brand_id: int, brand_data: BrandUpdate, user_id: int) -> Optional[Brand]:
        """Update a brand profile"""
        brand = self.db.query(Brand).filter(
            and_(Brand.id == brand_id, Brand.user_id == user_id)
        ).first()
        
        if not brand:
            return None
        
        update_data = brand_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        
        self.db.commit()
        self.db.refresh(brand)
        return brand
    
    def delete_brand(self, brand_id: int, user_id: int) -> bool:
        """Soft delete a brand"""
        brand = self.db.query(Brand).filter(
            and_(Brand.id == brand_id, Brand.user_id == user_id)
        ).first()
        
        if not brand:
            return False
        
        brand.is_active = False
        self.db.commit()
        return True
    
    def search_brands(self, filters: BrandMarketplaceFilter, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Search brands in marketplace with filters"""
        query = self.db.query(Brand).filter(Brand.is_active == True)
        
        if filters.industry:
            query = query.filter(Brand.industry.in_(filters.industry))
        
        if filters.company_size:
            query = query.filter(Brand.company_size.in_(filters.company_size))
        
        if filters.location:
            query = query.filter(Brand.location.ilike(f"%{filters.location}%"))
        
        if filters.min_budget is not None:
            query = query.filter(Brand.collaboration_budget >= filters.min_budget)
        
        if filters.max_budget is not None:
            query = query.filter(Brand.collaboration_budget <= filters.max_budget)
        
        if filters.verified_only:
            query = query.filter(Brand.is_verified == True)
        
        return query.offset(skip).limit(limit).all()
    
    # Campaign Management
    def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(**campaign_data.dict())
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get a campaign by ID"""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    def get_campaigns(self, brand_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get campaigns with optional brand filter"""
        query = self.db.query(Campaign)
        if brand_id:
            query = query.filter(Campaign.brand_id == brand_id)
        return query.order_by(desc(Campaign.created_at)).offset(skip).limit(limit).all()
    
    def update_campaign(self, campaign_id: int, campaign_data: CampaignUpdate, user_id: int) -> Optional[Campaign]:
        """Update a campaign (only brand owner can update)"""
        campaign = self.db.query(Campaign).join(Brand).filter(
            and_(Campaign.id == campaign_id, Brand.user_id == user_id)
        ).first()
        
        if not campaign:
            return None
        
        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def search_campaigns(self, filters: CampaignMarketplaceFilter, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Search campaigns in marketplace with filters"""
        query = self.db.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE)
        
        if filters.campaign_type:
            query = query.filter(Campaign.campaign_type.in_(filters.campaign_type))
        
        if filters.platforms:
            # Check if any of the filter platforms match campaign target platforms
            for platform in filters.platforms:
                query = query.filter(Campaign.target_platforms.contains(platform))
        
        if filters.min_budget is not None:
            query = query.filter(Campaign.budget >= filters.min_budget)
        
        if filters.max_budget is not None:
            query = query.filter(Campaign.budget <= filters.max_budget)
        
        if filters.industry:
            query = query.join(Brand).filter(Brand.industry.in_(filters.industry))
        
        return query.order_by(desc(Campaign.created_at)).offset(skip).limit(limit).all()
    
    # Collaboration Management
    def create_collaboration(self, collaboration_data: CollaborationCreate) -> Collaboration:
        """Create a new collaboration"""
        collaboration = Collaboration(**collaboration_data.dict())
        self.db.add(collaboration)
        self.db.commit()
        self.db.refresh(collaboration)
        return collaboration
    
    def get_collaboration(self, collaboration_id: int) -> Optional[Collaboration]:
        """Get a collaboration by ID"""
        return self.db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    
    def get_collaborations(self, user_id: Optional[int] = None, brand_id: Optional[int] = None, 
                          skip: int = 0, limit: int = 100) -> List[Collaboration]:
        """Get collaborations with filters"""
        query = self.db.query(Collaboration)
        
        if user_id:
            query = query.filter(Collaboration.influencer_id == user_id)
        
        if brand_id:
            query = query.filter(Collaboration.brand_id == brand_id)
        
        return query.order_by(desc(Collaboration.created_at)).offset(skip).limit(limit).all()
    
    def update_collaboration(self, collaboration_id: int, collaboration_data: CollaborationUpdate, 
                           user_id: int) -> Optional[Collaboration]:
        """Update a collaboration"""
        collaboration = self.db.query(Collaboration).filter(
            and_(
                Collaboration.id == collaboration_id,
                or_(
                    Collaboration.influencer_id == user_id,
                    Collaboration.brand.has(Brand.user_id == user_id)
                )
            )
        ).first()
        
        if not collaboration:
            return None
        
        update_data = collaboration_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collaboration, field, value)
        
        self.db.commit()
        self.db.refresh(collaboration)
        return collaboration
    
    def accept_collaboration(self, collaboration_id: int, user_id: int) -> Optional[Collaboration]:
        """Accept a collaboration (influencer only)"""
        collaboration = self.db.query(Collaboration).filter(
            and_(
                Collaboration.id == collaboration_id,
                Collaboration.influencer_id == user_id,
                Collaboration.status == CollaborationStatus.PENDING
            )
        ).first()
        
        if not collaboration:
            return None
        
        collaboration.status = CollaborationStatus.ACCEPTED
        collaboration.terms_accepted = True
        collaboration.terms_accepted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(collaboration)
        return collaboration
    
    # Affiliate Link Management
    def generate_affiliate_code(self, length: int = 8, max_retries: int = 100) -> str:
        """Generate a unique affiliate code with a retry limit"""
        for _ in range(max_retries):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
            existing = self.db.query(AffiliateLink).filter(AffiliateLink.affiliate_code == code).first()
            if not existing:
                return code
        raise RuntimeError("Failed to generate a unique affiliate code after maximum retries")
    
    def create_affiliate_link(self, link_data: AffiliateLinkCreate, user_id: int) -> AffiliateLink:
        """Create a new affiliate link"""
        affiliate_code = self.generate_affiliate_code()
        
        link = AffiliateLink(
            user_id=user_id,
            affiliate_code=affiliate_code,
            **link_data.dict()
        )
        
        # Generate short URL (would integrate with URL shortening service)
        link.short_url = f"https://short.ly/{affiliate_code}"
        
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def get_affiliate_link(self, link_id: int, user_id: Optional[int] = None) -> Optional[AffiliateLink]:
        """Get an affiliate link by ID"""
        query = self.db.query(AffiliateLink).filter(AffiliateLink.id == link_id)
        if user_id:
            query = query.filter(AffiliateLink.user_id == user_id)
        return query.first()
    
    def get_affiliate_links(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AffiliateLink]:
        """Get user's affiliate links"""
        return self.db.query(AffiliateLink).filter(
            AffiliateLink.user_id == user_id
        ).order_by(desc(AffiliateLink.created_at)).offset(skip).limit(limit).all()
    
    def update_affiliate_link(self, link_id: int, link_data: AffiliateLinkUpdate, 
                            user_id: int) -> Optional[AffiliateLink]:
        """Update an affiliate link"""
        link = self.db.query(AffiliateLink).filter(
            and_(AffiliateLink.id == link_id, AffiliateLink.user_id == user_id)
        ).first()
        
        if not link:
            return None
        
        update_data = link_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(link, field, value)
        
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def track_click(self, affiliate_code: str, referrer: Optional[str] = None) -> bool:
        """Track a click on an affiliate link"""
        link = self.db.query(AffiliateLink).filter(
            and_(
                AffiliateLink.affiliate_code == affiliate_code,
                AffiliateLink.is_active == True
            )
        ).first()
        
        if not link:
            return False
        
        # Check if link has expired
        if link.expires_at and link.expires_at < datetime.utcnow():
            return False
        
        # Update click tracking
        link.click_count += 1
        link.last_clicked = datetime.utcnow()
        
        # Update analytics data
        if not link.analytics_data:
            link.analytics_data = {"daily_clicks": {}, "referrers": {}}
        
        today = datetime.utcnow().date().isoformat()
        if today not in link.analytics_data["daily_clicks"]:
            link.analytics_data["daily_clicks"][today] = 0
        link.analytics_data["daily_clicks"][today] += 1
        
        if referrer:
            if referrer not in link.analytics_data["referrers"]:
                link.analytics_data["referrers"][referrer] = 0
            link.analytics_data["referrers"][referrer] += 1
        
        self.db.commit()
        return True
    
    def track_conversion(self, affiliate_code: str, conversion_value: float = 0.0) -> bool:
        """Track a conversion for an affiliate link"""
        link = self.db.query(AffiliateLink).filter(
            AffiliateLink.affiliate_code == affiliate_code
        ).first()
        
        if not link:
            return False
        
        # Update conversion tracking
        link.conversion_count += 1
        
        # Calculate earnings based on commission
        if link.commission_type == "percentage":
            earnings = conversion_value * (link.commission_rate / 100)
        elif link.commission_type == "fixed":
            earnings = link.commission_rate
        else:  # tiered or other custom logic
            earnings = conversion_value * (link.commission_rate / 100)
        
        link.total_earnings += earnings
        
        self.db.commit()
        return True
    
    # Analytics and Reporting
    def get_monetization_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get monetization dashboard data for a user"""
        # Get total earnings from affiliate links
        total_earnings = self.db.query(AffiliateLink).filter(
            AffiliateLink.user_id == user_id
        ).with_entities(AffiliateLink.total_earnings).all()
        total_earnings = sum(earnings[0] or 0 for earnings in total_earnings)
        
        # Get collaboration counts
        active_collaborations = self.db.query(Collaboration).filter(
            and_(
                Collaboration.influencer_id == user_id,
                Collaboration.status.in_([CollaborationStatus.ACCEPTED, CollaborationStatus.IN_PROGRESS])
            )
        ).count()
        
        pending_collaborations = self.db.query(Collaboration).filter(
            and_(
                Collaboration.influencer_id == user_id,
                Collaboration.status == CollaborationStatus.PENDING
            )
        ).count()
        
        # Get affiliate link stats
        active_links = self.db.query(AffiliateLink).filter(
            and_(AffiliateLink.user_id == user_id, AffiliateLink.is_active == True)
        ).count()
        
        total_clicks = self.db.query(AffiliateLink).filter(
            AffiliateLink.user_id == user_id
        ).with_entities(AffiliateLink.click_count).all()
        total_clicks = sum(clicks[0] or 0 for clicks in total_clicks)
        
        total_conversions = self.db.query(AffiliateLink).filter(
            AffiliateLink.user_id == user_id
        ).with_entities(AffiliateLink.conversion_count).all()
        total_conversions = sum(conversions[0] or 0 for conversions in total_conversions)
        
        return {
            "total_earnings": total_earnings,
            "active_collaborations": active_collaborations,
            "pending_collaborations": pending_collaborations,
            "active_affiliate_links": active_links,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        }
    
    def get_affiliate_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get affiliate link analytics for a user"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        links = self.db.query(AffiliateLink).filter(
            and_(
                AffiliateLink.user_id == user_id,
                AffiliateLink.created_at >= since_date
            )
        ).all()
        
        analytics = {
            "total_links": len(links),
            "total_clicks": sum(link.click_count for link in links),
            "total_conversions": sum(link.conversion_count for link in links),
            "total_earnings": sum(link.total_earnings for link in links),
            "top_performing_links": sorted(
                [{"id": link.id, "name": link.name, "clicks": link.click_count, "earnings": link.total_earnings}
                 for link in links],
                key=lambda x: x["earnings"],
                reverse=True
            )[:5]
        }
        
        return analytics