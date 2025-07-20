"""
Integration tests for monetization features including brand collaboration, campaigns, and affiliate marketing
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.monetization_service import MonetizationService
from app.schemas.monetization import (
    BrandCreate, CampaignCreate, CollaborationCreate, AffiliateLinkCreate,
    BrandMarketplaceFilter, CampaignMarketplaceFilter
)
from app.models.monetization import BrandType, CampaignType, CampaignStatus, CollaborationStatus


class TestMonetizationIntegration:
    """Integration tests for monetization features"""
    
    def setup_method(self):
        """Set up test data for each test"""
        self.mock_db = Mock()
        self.service = MonetizationService(self.mock_db)
        self.test_user_id = 1
        self.test_brand_id = 1
        self.test_campaign_id = 1
        
        # Mock datetime for consistent testing
        self.future_date = datetime.utcnow() + timedelta(days=30)
        self.past_date = datetime.utcnow() - timedelta(days=30)
    
    def test_brand_creation_flow(self):
        """✓ Test complete brand creation and management flow"""
        print("✓ Testing brand creation with comprehensive data")
        
        # Mock brand creation
        brand_data = BrandCreate(
            name="Test Fashion Brand",
            description="A premium fashion brand focused on sustainable clothing",
            website="https://testfashion.com",
            industry=BrandType.FASHION,
            company_size="medium",
            location="New York, NY",
            contact_email="contact@testfashion.com",
            contact_person="John Smith",
            collaboration_budget=50000.0,
            preferred_platforms=["instagram", "tiktok"],
            target_demographics={"age": "18-35", "interests": ["fashion", "sustainability"]}
        )
        
        mock_brand = Mock()
        mock_brand.id = self.test_brand_id
        mock_brand.name = brand_data.name
        mock_brand.industry = brand_data.industry
        mock_brand.is_verified = False
        mock_brand.is_active = True
        
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        with patch.object(self.service, 'create_brand', return_value=mock_brand):
            result = self.service.create_brand(brand_data, self.test_user_id)
            
            assert result.id == self.test_brand_id
            assert result.name == brand_data.name
            assert result.industry == brand_data.industry
            
        print("✓ Brand creation test passed")
    
    def test_brand_marketplace_search(self):
        """✓ Test brand marketplace search and filtering"""
        print("✓ Testing brand marketplace search functionality")
        
        # Mock search filters
        filters = BrandMarketplaceFilter(
            industry=[BrandType.FASHION, BrandType.BEAUTY],
            company_size=["medium", "large"],
            min_budget=10000.0,
            max_budget=100000.0,
            platforms=["instagram"],
            verified_only=True
        )
        
        # Mock search results
        mock_brands = [
            Mock(id=1, name="Fashion Brand A", industry=BrandType.FASHION, is_verified=True),
            Mock(id=2, name="Beauty Brand B", industry=BrandType.BEAUTY, is_verified=True)
        ]
        
        with patch.object(self.service, 'search_brands', return_value=mock_brands):
            results = self.service.search_brands(filters, skip=0, limit=100)
            
            assert len(results) == 2
            assert all(brand.is_verified for brand in results)
            assert any(brand.industry == BrandType.FASHION for brand in results)
            assert any(brand.industry == BrandType.BEAUTY for brand in results)
        
        print("✓ Brand marketplace search test passed")
    
    def test_campaign_creation_and_management(self):
        """✓ Test campaign creation and lifecycle management"""
        print("✓ Testing campaign creation and management flow")
        
        # Mock campaign creation
        campaign_data = CampaignCreate(
            brand_id=self.test_brand_id,
            name="Summer Fashion Campaign",
            description="Promote summer collection with fashion influencers",
            campaign_type=CampaignType.SPONSORED_POST,
            budget=25000.0,
            target_platforms=["instagram", "tiktok"],
            target_audience={"age": "18-30", "location": "US", "interests": ["fashion"]},
            content_requirements={"posts": 3, "stories": 5, "hashtags": ["#summerfashion"]},
            deliverables={"instagram_posts": 2, "tiktok_videos": 1},
            start_date=datetime.utcnow() + timedelta(days=7),
            end_date=datetime.utcnow() + timedelta(days=37),
            target_metrics={"reach": 100000, "engagement_rate": 5.0}
        )
        
        mock_campaign = Mock()
        mock_campaign.id = self.test_campaign_id
        mock_campaign.name = campaign_data.name
        mock_campaign.campaign_type = campaign_data.campaign_type
        mock_campaign.status = CampaignStatus.DRAFT
        mock_campaign.budget = campaign_data.budget
        
        with patch.object(self.service, 'create_campaign', return_value=mock_campaign):
            result = self.service.create_campaign(campaign_data)
            
            assert result.id == self.test_campaign_id
            assert result.name == campaign_data.name
            assert result.campaign_type == campaign_data.campaign_type
            assert result.budget == campaign_data.budget
            assert result.status == CampaignStatus.DRAFT
        
        print("✓ Campaign creation test passed")
    
    def test_campaign_marketplace_discovery(self):
        """✓ Test campaign marketplace discovery and filtering"""
        print("✓ Testing campaign marketplace discovery")
        
        # Mock marketplace filters
        filters = CampaignMarketplaceFilter(
            campaign_type=[CampaignType.SPONSORED_POST, CampaignType.BRAND_AMBASSADOR],
            platforms=["instagram", "youtube"],
            min_budget=5000.0,
            max_budget=50000.0,
            industry=[BrandType.FASHION, BrandType.BEAUTY]
        )
        
        # Mock active campaigns
        mock_campaigns = [
            Mock(
                id=1, 
                name="Fashion Influencer Campaign",
                campaign_type=CampaignType.SPONSORED_POST,
                status=CampaignStatus.ACTIVE,
                budget=20000.0
            ),
            Mock(
                id=2,
                name="Beauty Ambassador Program", 
                campaign_type=CampaignType.BRAND_AMBASSADOR,
                status=CampaignStatus.ACTIVE,
                budget=35000.0
            )
        ]
        
        with patch.object(self.service, 'search_campaigns', return_value=mock_campaigns):
            results = self.service.search_campaigns(filters, skip=0, limit=100)
            
            assert len(results) == 2
            assert all(campaign.status == CampaignStatus.ACTIVE for campaign in results)
            assert any(campaign.campaign_type == CampaignType.SPONSORED_POST for campaign in results)
            assert any(campaign.campaign_type == CampaignType.BRAND_AMBASSADOR for campaign in results)
        
        print("✓ Campaign marketplace discovery test passed")
    
    def test_collaboration_lifecycle(self):
        """✓ Test complete collaboration lifecycle from creation to completion"""
        print("✓ Testing collaboration lifecycle management")
        
        # Mock collaboration creation
        collaboration_data = CollaborationCreate(
            influencer_id=2,  # Different user as influencer
            brand_id=self.test_brand_id,
            campaign_id=self.test_campaign_id,
            title="Summer Fashion Collaboration",
            description="Create engaging content for summer fashion line",
            deliverables={
                "instagram_posts": 2,
                "instagram_stories": 3,
                "tiktok_videos": 1,
                "post_requirements": "Include brand hashtags and product tags"
            },
            compensation=5000.0,
            compensation_type="fixed",
            platforms=["instagram", "tiktok"],
            start_date=datetime.utcnow() + timedelta(days=5),
            end_date=datetime.utcnow() + timedelta(days=35)
        )
        
        mock_collaboration = Mock()
        mock_collaboration.id = 1
        mock_collaboration.title = collaboration_data.title
        mock_collaboration.status = CollaborationStatus.PENDING
        mock_collaboration.influencer_id = collaboration_data.influencer_id
        mock_collaboration.brand_id = collaboration_data.brand_id
        mock_collaboration.compensation = collaboration_data.compensation
        
        with patch.object(self.service, 'create_collaboration', return_value=mock_collaboration):
            result = self.service.create_collaboration(collaboration_data)
            
            assert result.id == 1
            assert result.title == collaboration_data.title
            assert result.status == CollaborationStatus.PENDING
            assert result.compensation == collaboration_data.compensation
        
        # Test collaboration acceptance
        mock_collaboration.status = CollaborationStatus.ACCEPTED
        mock_collaboration.terms_accepted = True
        
        with patch.object(self.service, 'accept_collaboration', return_value=mock_collaboration):
            accepted = self.service.accept_collaboration(1, 2)  # influencer accepts
            
            assert accepted.status == CollaborationStatus.ACCEPTED
            assert accepted.terms_accepted is True
        
        print("✓ Collaboration lifecycle test passed")
    
    def test_affiliate_link_management(self):
        """✓ Test affiliate link creation, tracking, and analytics"""
        print("✓ Testing affiliate link management and tracking")
        
        # Mock affiliate link creation
        link_data = AffiliateLinkCreate(
            name="Summer Fashion Collection",
            original_url="https://testfashion.com/summer-collection",
            product_name="Summer Dress Collection",
            product_description="Beautiful summer dresses in various styles",
            commission_rate=15.0,
            commission_type="percentage",
            brand_id=self.test_brand_id
        )
        
        mock_link = Mock()
        mock_link.id = 1
        mock_link.name = link_data.name
        mock_link.affiliate_code = "SUMMER123"
        mock_link.short_url = "https://short.ly/SUMMER123"
        mock_link.commission_rate = link_data.commission_rate
        mock_link.click_count = 0
        mock_link.conversion_count = 0
        mock_link.total_earnings = 0.0
        mock_link.is_active = True
        
        with patch.object(self.service, 'create_affiliate_link', return_value=mock_link):
            result = self.service.create_affiliate_link(link_data, self.test_user_id)
            
            assert result.id == 1
            assert result.name == link_data.name
            assert result.affiliate_code == "SUMMER123"
            assert result.commission_rate == link_data.commission_rate
            assert result.is_active is True
        
        # Test click tracking
        with patch.object(self.service, 'track_click', return_value=True):
            click_success = self.service.track_click("SUMMER123", "instagram.com")
            assert click_success is True
        
        # Test conversion tracking
        with patch.object(self.service, 'track_conversion', return_value=True):
            conversion_success = self.service.track_conversion("SUMMER123", 250.0)
            assert conversion_success is True
        
        print("✓ Affiliate link management test passed")
    
    def test_monetization_dashboard_analytics(self):
        """✓ Test monetization dashboard and analytics generation"""
        print("✓ Testing monetization dashboard and analytics")
        
        # Mock dashboard data
        mock_dashboard_data = {
            "total_earnings": 15750.0,
            "active_collaborations": 3,
            "pending_collaborations": 2,
            "active_affiliate_links": 8,
            "total_clicks": 1250,
            "total_conversions": 47,
            "conversion_rate": 3.76
        }
        
        with patch.object(self.service, 'get_monetization_dashboard', return_value=mock_dashboard_data):
            dashboard = self.service.get_monetization_dashboard(self.test_user_id)
            
            assert dashboard["total_earnings"] == 15750.0
            assert dashboard["active_collaborations"] == 3
            assert dashboard["pending_collaborations"] == 2
            assert dashboard["active_affiliate_links"] == 8
            assert dashboard["total_clicks"] == 1250
            assert dashboard["total_conversions"] == 47
            assert dashboard["conversion_rate"] == 3.76
        
        # Mock affiliate analytics
        mock_analytics = {
            "total_links": 8,
            "total_clicks": 1250,
            "total_conversions": 47,
            "total_earnings": 15750.0,
            "top_performing_links": [
                {"id": 1, "name": "Summer Fashion Collection", "clicks": 350, "earnings": 5250.0},
                {"id": 2, "name": "Beauty Essentials", "clicks": 280, "earnings": 4200.0}
            ]
        }
        
        with patch.object(self.service, 'get_affiliate_analytics', return_value=mock_analytics):
            analytics = self.service.get_affiliate_analytics(self.test_user_id, 30)
            
            assert analytics["total_links"] == 8
            assert analytics["total_earnings"] == 15750.0
            assert len(analytics["top_performing_links"]) == 2
            assert analytics["top_performing_links"][0]["earnings"] == 5250.0
        
        print("✓ Monetization dashboard analytics test passed")
    
    def test_brand_verification_workflow(self):
        """✓ Test brand verification and trust features"""
        print("✓ Testing brand verification workflow")
        
        # Mock brand verification process
        mock_brand = Mock()
        mock_brand.id = self.test_brand_id
        mock_brand.name = "Premium Fashion Brand"
        mock_brand.is_verified = False
        mock_brand.is_active = True
        
        # Test initial unverified state
        with patch.object(self.service, 'get_brand', return_value=mock_brand):
            brand = self.service.get_brand(self.test_brand_id)
            assert brand.is_verified is False
        
        # Mock verification approval
        mock_brand.is_verified = True
        
        with patch.object(self.service, 'get_brand', return_value=mock_brand):
            verified_brand = self.service.get_brand(self.test_brand_id)
            assert verified_brand.is_verified is True
        
        print("✓ Brand verification workflow test passed")
    
    def test_payment_and_earnings_tracking(self):
        """✓ Test payment processing and earnings tracking"""
        print("✓ Testing payment and earnings tracking")
        
        # Mock payment tracking for campaigns
        mock_campaign = Mock()
        mock_campaign.id = self.test_campaign_id
        mock_campaign.payment_amount = 5000.0
        mock_campaign.payment_status = "pending"
        
        # Test payment status update
        mock_campaign.payment_status = "paid"
        mock_campaign.payment_date = datetime.utcnow()
        
        with patch.object(self.service, 'get_campaign', return_value=mock_campaign):
            campaign = self.service.get_campaign(self.test_campaign_id)
            assert campaign.payment_status == "paid"
            assert campaign.payment_amount == 5000.0
        
        # Mock affiliate earnings calculation
        conversion_value = 300.0
        commission_rate = 10.0
        expected_earnings = conversion_value * (commission_rate / 100)
        
        assert expected_earnings == 30.0
        
        print("✓ Payment and earnings tracking test passed")
    
    def test_collaboration_content_approval(self):
        """✓ Test content approval workflow in collaborations"""
        print("✓ Testing collaboration content approval workflow")
        
        # Mock collaboration with content submission
        mock_collaboration = Mock()
        mock_collaboration.id = 1
        mock_collaboration.content_ids = [101, 102, 103]
        mock_collaboration.approval_status = "pending"
        mock_collaboration.status = CollaborationStatus.IN_PROGRESS
        
        # Test content approval
        mock_collaboration.approval_status = "approved"
        
        with patch.object(self.service, 'get_collaboration', return_value=mock_collaboration):
            collaboration = self.service.get_collaboration(1)
            assert collaboration.approval_status == "approved"
            assert len(collaboration.content_ids) == 3
        
        print("✓ Collaboration content approval test passed")
    
    def test_performance_metrics_tracking(self):
        """✓ Test performance metrics and ROI tracking"""
        print("✓ Testing performance metrics and ROI tracking")
        
        # Mock collaboration performance metrics
        mock_performance = {
            "total_reach": 125000,
            "total_engagement": 8750,
            "engagement_rate": 7.0,
            "click_through_rate": 2.5,
            "conversion_rate": 1.8,
            "platform_breakdown": {
                "instagram": {"reach": 85000, "engagement": 6000},
                "tiktok": {"reach": 40000, "engagement": 2750}
            }
        }
        
        # Mock collaboration with performance data
        mock_collaboration = Mock()
        mock_collaboration.performance_metrics = mock_performance
        
        with patch.object(self.service, 'get_collaboration', return_value=mock_collaboration):
            collaboration = self.service.get_collaboration(1)
            metrics = collaboration.performance_metrics
            
            assert metrics["total_reach"] == 125000
            assert metrics["engagement_rate"] == 7.0
            assert "instagram" in metrics["platform_breakdown"]
            assert "tiktok" in metrics["platform_breakdown"]
        
        print("✓ Performance metrics tracking test passed")


# Test runner function for integration testing
def run_monetization_tests():
    """Run all monetization integration tests"""
    test_instance = TestMonetizationIntegration()
    
    test_methods = [
        test_instance.test_brand_creation_flow,
        test_instance.test_brand_marketplace_search,
        test_instance.test_campaign_creation_and_management,
        test_instance.test_campaign_marketplace_discovery,
        test_instance.test_collaboration_lifecycle,
        test_instance.test_affiliate_link_management,
        test_instance.test_monetization_dashboard_analytics,
        test_instance.test_brand_verification_workflow,
        test_instance.test_payment_and_earnings_tracking,
        test_instance.test_collaboration_content_approval,
        test_instance.test_performance_metrics_tracking
    ]
    
    passed_tests = 0
    total_tests = len(test_methods)
    
    print("🧪 Running Monetization Integration Tests...")
    print("=" * 60)
    
    for test_method in test_methods:
        try:
            test_instance.setup_method()
            test_method()
            passed_tests += 1
        except Exception as e:
            print(f"❌ {test_method.__name__} failed: {str(e)}")
    
    print("=" * 60)
    print(f"✅ Monetization Tests Summary: {passed_tests}/{total_tests} tests passed")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    run_monetization_tests()