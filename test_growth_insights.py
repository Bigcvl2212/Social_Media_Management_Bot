"""
Simple validation test for Growth & Audience Insights features
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import AsyncSessionLocal, create_tables
from app.models.competitor_analysis import CompetitorAccount, CompetitorAnalytics
from app.models.audience_segmentation import AudienceSegment, AudienceInsight
from app.models.growth_recommendations import GrowthRecommendation
from app.models.user import User
from app.services.competitor_analysis_service import CompetitorAnalysisService
from app.services.audience_segmentation_service import AudienceSegmentationService
from app.services.growth_recommendation_service import GrowthRecommendationService

async def test_growth_insights_features():
    """Test the main functionality of the Growth & Audience Insights features"""
    
    print("🚀 Testing Growth & Audience Insights Implementation")
    print("=" * 60)
    
    try:
        # Create database tables
        print("📊 Creating database tables...")
        await create_tables()
        print("✅ Database tables created successfully")
        
        # Test database models
        print("\n📋 Testing database models...")
        
        async with AsyncSessionLocal() as db:
            # Test CompetitorAccount model
            competitor = CompetitorAccount(
                user_id=1,
                platform="instagram",
                username="test_competitor",
                display_name="Test Competitor",
                follower_count=10000
            )
            db.add(competitor)
            await db.commit()
            print("✅ CompetitorAccount model works")
            
            # Test AudienceSegment model
            segment = AudienceSegment(
                user_id=1,
                name="Test Segment",
                segment_type="demographic",
                criteria={"age_range": [18, 24]},
                audience_size=5000,
                avg_engagement_rate=7.5
            )
            db.add(segment)
            await db.commit()
            print("✅ AudienceSegment model works")
            
            # Test GrowthRecommendation model
            recommendation = GrowthRecommendation(
                user_id=1,
                recommendation_type="content",
                category="content_theme",
                title="Test Recommendation",
                description="This is a test recommendation",
                confidence_score=0.85,
                impact_score=0.75,
                difficulty_score=0.3,
                priority_score=0.8,
                recommendation_data={"test": "data"}
            )
            db.add(recommendation)
            await db.commit()
            print("✅ GrowthRecommendation model works")
        
        # Test services
        print("\n🔧 Testing services...")
        
        async with AsyncSessionLocal() as db:
            # Test CompetitorAnalysisService
            competitor_service = CompetitorAnalysisService(db)
            trends = await competitor_service.analyze_competitor_trends(1, 30)
            print(f"✅ CompetitorAnalysisService works - found {trends.get('total_competitors', 0)} competitors")
            
            # Test AudienceSegmentationService  
            audience_service = AudienceSegmentationService(db)
            segments = await audience_service.analyze_audience_segments(1)
            print(f"✅ AudienceSegmentationService works - created {len(segments)} segments")
            
            # Test GrowthRecommendationService
            growth_service = GrowthRecommendationService(db)
            recommendations = await growth_service.generate_recommendations(1)
            print(f"✅ GrowthRecommendationService works - generated {len(recommendations)} recommendations")
        
        print("\n🎉 All tests passed successfully!")
        print("=" * 60)
        print("✨ Growth & Audience Insights features are working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_growth_insights_features())
    sys.exit(0 if result else 1)