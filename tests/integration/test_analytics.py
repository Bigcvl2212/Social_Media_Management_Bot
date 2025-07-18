"""
Integration tests for analytics retrieval and reporting functionality.

Tests analytics data collection, reporting, insights generation, and dashboard features.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class TestAnalyticsRetrieval:
    """Test suite for analytics data retrieval and processing."""

    @pytest.mark.asyncio
    async def test_instagram_analytics_retrieval(self, test_config: Dict[str, Any], sample_analytics_data: Dict[str, Any]):
        """Test retrieving analytics data from Instagram."""
        analytics_data = sample_analytics_data["instagram"]
        
        print("✓ Testing Instagram analytics retrieval")
        
        # Mock analytics request
        analytics_request = {
            "platform": "instagram",
            "account_id": "test_instagram_123",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "metrics": ["followers", "engagement", "reach", "impressions", "profile_views"]
        }
        
        # Mock Instagram analytics response
        analytics_response = {
            "platform": "instagram",
            "account_id": "test_instagram_123",
            "account_name": "@test_account",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "summary": {
                "followers": analytics_data["followers"],
                "following": analytics_data["following"],
                "posts": analytics_data["posts"],
                "engagement_rate": analytics_data["engagement_rate"],
                "reach": analytics_data["reach"],
                "impressions": analytics_data["impressions"]
            },
            "growth": {
                "followers_change": 125,
                "followers_change_percent": 11.1,
                "engagement_rate_change": 0.3,
                "reach_change": 450
            },
            "top_posts": [
                {
                    "post_id": "ig_post_123",
                    "content": "Amazing sunset photo 🌅",
                    "likes": 89,
                    "comments": 12,
                    "shares": 5,
                    "reach": 567,
                    "engagement_rate": 18.7
                },
                {
                    "post_id": "ig_post_124",
                    "content": "Daily motivation quote ✨",
                    "likes": 76,
                    "comments": 8,
                    "shares": 3,
                    "reach": 445,
                    "engagement_rate": 19.6
                }
            ]
        }
        
        # Assertions
        assert analytics_response["platform"] == "instagram"
        assert analytics_response["summary"]["followers"] == analytics_data["followers"]
        assert analytics_response["summary"]["engagement_rate"] == analytics_data["engagement_rate"]
        assert "growth" in analytics_response
        assert len(analytics_response["top_posts"]) > 0
        
        # Check growth metrics
        assert analytics_response["growth"]["followers_change"] > 0
        assert "followers_change_percent" in analytics_response["growth"]
        
        print("✓ Instagram analytics retrieval test passed")

    @pytest.mark.asyncio
    async def test_twitter_analytics_retrieval(self, test_config: Dict[str, Any], sample_analytics_data: Dict[str, Any]):
        """Test retrieving analytics data from Twitter."""
        analytics_data = sample_analytics_data["twitter"]
        
        print("✓ Testing Twitter analytics retrieval")
        
        # Mock Twitter analytics request
        analytics_request = {
            "platform": "twitter",
            "account_id": "test_twitter_456",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "metrics": ["followers", "tweets", "engagement", "impressions", "mentions"]
        }
        
        # Mock Twitter analytics response
        analytics_response = {
            "platform": "twitter",
            "account_id": "test_twitter_456",
            "account_name": "@test_twitter",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "summary": {
                "followers": analytics_data["followers"],
                "following": analytics_data["following"],
                "tweets": analytics_data["tweets"],
                "engagement_rate": analytics_data["engagement_rate"],
                "total_retweets": analytics_data["retweets"],
                "total_likes": analytics_data["likes"]
            },
            "growth": {
                "followers_change": 67,
                "followers_change_percent": 8.1,
                "tweet_impressions": 15420,
                "profile_visits": 234
            },
            "top_tweets": [
                {
                    "tweet_id": "tw_123456",
                    "content": "Just launched our new feature! 🚀 #ProductLaunch",
                    "retweets": 23,
                    "likes": 89,
                    "replies": 12,
                    "impressions": 1250,
                    "engagement_rate": 9.9
                },
                {
                    "tweet_id": "tw_123457",
                    "content": "Threading some insights about social media automation 🧵",
                    "retweets": 18,
                    "likes": 67,
                    "replies": 8,
                    "impressions": 980,
                    "engagement_rate": 9.5
                }
            ]
        }
        
        # Assertions
        assert analytics_response["platform"] == "twitter"
        assert analytics_response["summary"]["followers"] == analytics_data["followers"]
        assert analytics_response["summary"]["engagement_rate"] == analytics_data["engagement_rate"]
        assert "growth" in analytics_response
        assert len(analytics_response["top_tweets"]) > 0
        
        # Check Twitter-specific metrics
        assert "tweet_impressions" in analytics_response["growth"]
        assert "profile_visits" in analytics_response["growth"]
        
        print("✓ Twitter analytics retrieval test passed")

    @pytest.mark.asyncio
    async def test_tiktok_analytics_retrieval(self, test_config: Dict[str, Any], sample_analytics_data: Dict[str, Any]):
        """Test retrieving analytics data from TikTok."""
        analytics_data = sample_analytics_data["tiktok"]
        
        print("✓ Testing TikTok analytics retrieval")
        
        # Mock TikTok analytics request
        analytics_request = {
            "platform": "tiktok",
            "account_id": "test_tiktok_789",
            "date_range": {
                "start_date": "2024-01-01", 
                "end_date": "2024-01-31"
            },
            "metrics": ["followers", "videos", "views", "likes", "shares", "engagement"]
        }
        
        # Mock TikTok analytics response
        analytics_response = {
            "platform": "tiktok",
            "account_id": "test_tiktok_789",
            "account_name": "@test_tiktok",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "summary": {
                "followers": analytics_data["followers"],
                "following": analytics_data["following"],
                "videos": analytics_data["videos"],
                "total_views": analytics_data["views"],
                "total_likes": analytics_data["likes"],
                "engagement_rate": analytics_data["engagement_rate"]
            },
            "growth": {
                "followers_change": 420,
                "followers_change_percent": 14.0,
                "video_views": 125000,
                "average_watch_time": 18.5  # seconds
            },
            "top_videos": [
                {
                    "video_id": "tt_video_001",
                    "description": "Trending dance challenge! 💃 #DanceChallenge #Viral",
                    "views": 25000,
                    "likes": 2100,
                    "comments": 189,
                    "shares": 156,
                    "engagement_rate": 9.8,
                    "duration": 15
                },
                {
                    "video_id": "tt_video_002", 
                    "description": "Quick productivity tips for creators 📱 #ProductivityTips",
                    "views": 18500,
                    "likes": 1650,
                    "comments": 123,
                    "shares": 98,
                    "engagement_rate": 10.1,
                    "duration": 30
                }
            ]
        }
        
        # Assertions
        assert analytics_response["platform"] == "tiktok"
        assert analytics_response["summary"]["followers"] == analytics_data["followers"]
        assert analytics_response["summary"]["total_views"] == analytics_data["views"]
        assert "growth" in analytics_response
        assert len(analytics_response["top_videos"]) > 0
        
        # Check TikTok-specific metrics
        assert "average_watch_time" in analytics_response["growth"]
        for video in analytics_response["top_videos"]:
            assert "duration" in video
            assert "views" in video
            
        print("✓ TikTok analytics retrieval test passed")

    @pytest.mark.asyncio
    async def test_cross_platform_analytics_comparison(self, test_config: Dict[str, Any], sample_analytics_data: Dict[str, Any]):
        """Test cross-platform analytics comparison and aggregation."""
        print("✓ Testing cross-platform analytics comparison")
        
        # Mock cross-platform analytics request
        comparison_request = {
            "platforms": ["instagram", "twitter", "tiktok"],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "metrics": ["followers", "engagement_rate", "growth", "reach"]
        }
        
        # Mock cross-platform comparison response
        comparison_response = {
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "platforms": {
                "instagram": {
                    "followers": sample_analytics_data["instagram"]["followers"],
                    "engagement_rate": sample_analytics_data["instagram"]["engagement_rate"],
                    "reach": sample_analytics_data["instagram"]["reach"],
                    "growth_rate": 11.1
                },
                "twitter": {
                    "followers": sample_analytics_data["twitter"]["followers"],
                    "engagement_rate": sample_analytics_data["twitter"]["engagement_rate"],
                    "reach": 15420,  # tweet impressions
                    "growth_rate": 8.1
                },
                "tiktok": {
                    "followers": sample_analytics_data["tiktok"]["followers"],
                    "engagement_rate": sample_analytics_data["tiktok"]["engagement_rate"],
                    "reach": sample_analytics_data["tiktok"]["views"],
                    "growth_rate": 14.0
                }
            },
            "totals": {
                "total_followers": 5562,  # Sum across platforms
                "average_engagement_rate": 4.9,  # Weighted average
                "total_reach": 142870,  # Sum of reach across platforms
                "overall_growth_rate": 11.1  # Weighted average
            },
            "insights": {
                "best_performing_platform": "tiktok",
                "highest_engagement": "tiktok",
                "fastest_growing": "tiktok",
                "recommendations": [
                    "Focus more content creation on TikTok due to highest engagement",
                    "Improve Twitter engagement through more interactive content",
                    "Leverage Instagram's strong reach for brand awareness"
                ]
            }
        }
        
        # Assertions
        assert "platforms" in comparison_response
        assert "totals" in comparison_response
        assert "insights" in comparison_response
        assert len(comparison_response["platforms"]) == 3
        
        # Check totals calculation
        expected_followers = (
            sample_analytics_data["instagram"]["followers"] +
            sample_analytics_data["twitter"]["followers"] +
            sample_analytics_data["tiktok"]["followers"]
        )
        assert comparison_response["totals"]["total_followers"] == expected_followers
        
        # Check insights
        assert comparison_response["insights"]["best_performing_platform"] in ["instagram", "twitter", "tiktok"]
        assert len(comparison_response["insights"]["recommendations"]) > 0
        
        print("✓ Cross-platform analytics comparison test passed")


class TestAnalyticsReporting:
    """Test suite for analytics reporting and dashboard functionality."""

    @pytest.mark.asyncio
    async def test_dashboard_overview_generation(self, test_config: Dict[str, Any]):
        """Test generation of analytics dashboard overview."""
        print("✓ Testing dashboard overview generation")
        
        # Mock dashboard request
        dashboard_request = {
            "user_id": 1,
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "include_predictions": True,
            "include_recommendations": True
        }
        
        # Mock dashboard overview response
        dashboard_response = {
            "user_id": 1,
            "generated_at": "2024-01-31T23:59:59Z",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "summary": {
                "total_followers": 5562,
                "total_posts": 366,
                "total_engagement": 3428,
                "average_engagement_rate": 4.9,
                "total_reach": 142870,
                "growth_rate": 11.1
            },
            "platform_breakdown": {
                "instagram": {
                    "percentage_of_followers": 22.5,
                    "percentage_of_engagement": 35.2,
                    "top_content_type": "image"
                },
                "twitter": {
                    "percentage_of_followers": 16.0,
                    "percentage_of_engagement": 28.8,
                    "top_content_type": "text"
                },
                "tiktok": {
                    "percentage_of_followers": 61.5,
                    "percentage_of_engagement": 36.0,
                    "top_content_type": "video"
                }
            },
            "trends": {
                "followers_trend": "increasing",
                "engagement_trend": "stable",
                "posting_frequency_trend": "increasing",
                "best_posting_times": {
                    "instagram": ["08:00", "12:00", "18:00"],
                    "twitter": ["09:00", "13:00", "17:00"],
                    "tiktok": ["19:00", "21:00", "22:00"]
                }
            },
            "predictions": {
                "followers_next_month": 6200,
                "engagement_rate_forecast": 5.2,
                "recommended_posting_frequency": {
                    "instagram": 5,  # posts per week
                    "twitter": 12,   # posts per week
                    "tiktok": 4     # posts per week
                }
            },
            "recommendations": [
                "Increase TikTok posting frequency to capitalize on high engagement",
                "Post Instagram content during peak hours: 8AM, 12PM, 6PM",
                "Create more video content across all platforms",
                "Engage more with comments to boost engagement rate"
            ]
        }
        
        # Assertions
        assert dashboard_response["user_id"] == 1
        assert "summary" in dashboard_response
        assert "platform_breakdown" in dashboard_response
        assert "trends" in dashboard_response
        assert "predictions" in dashboard_response
        assert "recommendations" in dashboard_response
        
        # Check summary totals
        assert dashboard_response["summary"]["total_followers"] > 0
        assert dashboard_response["summary"]["average_engagement_rate"] > 0
        
        # Check platform breakdown adds up to 100%
        total_percentage = sum([
            platform["percentage_of_followers"] 
            for platform in dashboard_response["platform_breakdown"].values()
        ])
        assert abs(total_percentage - 100.0) < 0.1  # Allow for rounding
        
        # Check predictions are forward-looking
        assert dashboard_response["predictions"]["followers_next_month"] >= dashboard_response["summary"]["total_followers"]
        
        print("✓ Dashboard overview generation test passed")

    @pytest.mark.asyncio
    async def test_custom_analytics_report_generation(self, test_config: Dict[str, Any]):
        """Test generation of custom analytics reports."""
        print("✓ Testing custom analytics report generation")
        
        # Mock custom report request
        report_request = {
            "report_name": "Monthly Performance Report",
            "user_id": 1,
            "platforms": ["instagram", "twitter"],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "metrics": [
                "followers_growth",
                "engagement_analysis",
                "content_performance",
                "optimal_timing",
                "competitor_comparison"
            ],
            "format": "detailed",
            "include_visualizations": True
        }
        
        # Mock custom report response
        report_response = {
            "report_id": "report_123456",
            "report_name": "Monthly Performance Report",
            "user_id": 1,
            "generated_at": "2024-01-31T23:59:59Z",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "platforms": ["instagram", "twitter"],
            "sections": {
                "followers_growth": {
                    "instagram": {
                        "start_followers": 1125,
                        "end_followers": 1250,
                        "growth": 125,
                        "growth_rate": 11.1,
                        "growth_trend": "steady_increase"
                    },
                    "twitter": {
                        "start_followers": 825,
                        "end_followers": 892,
                        "growth": 67,
                        "growth_rate": 8.1,
                        "growth_trend": "moderate_increase"
                    }
                },
                "engagement_analysis": {
                    "instagram": {
                        "average_engagement_rate": 4.2,
                        "best_performing_content_type": "carousel",
                        "peak_engagement_times": ["08:00", "12:00", "18:00"],
                        "engagement_trend": "increasing"
                    },
                    "twitter": {
                        "average_engagement_rate": 3.8,
                        "best_performing_content_type": "thread",
                        "peak_engagement_times": ["09:00", "13:00", "17:00"],
                        "engagement_trend": "stable"
                    }
                },
                "content_performance": {
                    "total_posts": 45,
                    "instagram_posts": 20,
                    "twitter_posts": 25,
                    "top_performing_hashtags": ["#SocialMedia", "#Marketing", "#Automation"],
                    "content_mix_recommendation": {
                        "images": 40,
                        "videos": 35,
                        "text": 25
                    }
                }
            },
            "visualizations": {
                "followers_growth_chart": "chart_data_base64_string",
                "engagement_trends_chart": "chart_data_base64_string",
                "content_performance_pie_chart": "chart_data_base64_string"
            },
            "key_insights": [
                "Instagram shows stronger growth rate than Twitter",
                "Carousel posts on Instagram drive 40% more engagement",
                "Twitter threads perform better than single tweets",
                "Morning posts (8-9 AM) consistently perform best"
            ],
            "action_items": [
                "Increase carousel content on Instagram",
                "Create more Twitter threads",
                "Focus posting during 8-9 AM window",
                "Use top-performing hashtags more frequently"
            ]
        }
        
        # Assertions
        assert report_response["report_name"] == "Monthly Performance Report"
        assert "sections" in report_response
        assert "visualizations" in report_response
        assert "key_insights" in report_response
        assert "action_items" in report_response
        
        # Check sections are present
        assert "followers_growth" in report_response["sections"]
        assert "engagement_analysis" in report_response["sections"]
        assert "content_performance" in report_response["sections"]
        
        # Check insights and action items
        assert len(report_response["key_insights"]) > 0
        assert len(report_response["action_items"]) > 0
        
        print("✓ Custom analytics report generation test passed")

    @pytest.mark.asyncio
    async def test_automated_insights_generation(self, test_config: Dict[str, Any]):
        """Test automated AI-powered insights generation."""
        print("✓ Testing automated insights generation")
        
        # Mock insights generation request
        insights_request = {
            "user_id": 1,
            "analysis_type": "comprehensive",
            "lookback_period": 30,  # days
            "include_predictions": True,
            "include_recommendations": True,
            "competitor_analysis": True
        }
        
        # Mock AI-generated insights response
        insights_response = {
            "user_id": 1,
            "generated_at": "2024-01-31T23:59:59Z",
            "analysis_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "performance_score": 78,  # Out of 100
            "growth_trajectory": "positive",
            "key_insights": {
                "audience_behavior": [
                    "Your audience is most active on weekdays between 8-10 AM",
                    "Video content receives 45% more engagement than static posts",
                    "Posts with 3-5 hashtags perform better than those with more"
                ],
                "content_patterns": [
                    "Motivational content consistently drives high engagement",
                    "Behind-the-scenes content increases follower retention by 23%",
                    "User-generated content has 67% higher share rate"
                ],
                "platform_specific": {
                    "instagram": [
                        "Stories with polls increase profile visits by 34%",
                        "Reels posted between 7-9 PM get maximum visibility"
                    ],
                    "twitter": [
                        "Threads perform 3x better than single tweets",
                        "Adding images to tweets increases engagement by 150%"
                    ],
                    "tiktok": [
                        "15-30 second videos have highest completion rate",
                        "Trending sounds increase reach by 89%"
                    ]
                }
            },
            "predictions": {
                "30_day_forecast": {
                    "followers_growth": 15.5,  # percentage
                    "engagement_rate": 5.1,
                    "optimal_posting_frequency": {
                        "instagram": 6,
                        "twitter": 14,
                        "tiktok": 5
                    }
                },
                "growth_opportunities": [
                    {
                        "platform": "tiktok",
                        "opportunity": "viral_potential",
                        "confidence": 0.87,
                        "description": "High likelihood of viral content based on current trends"
                    },
                    {
                        "platform": "instagram",
                        "opportunity": "reels_expansion",
                        "confidence": 0.75,
                        "description": "Reels content shows strong growth potential"
                    }
                ]
            },
            "recommendations": {
                "immediate": [
                    "Increase video content production by 25%",
                    "Post Instagram Reels during 7-9 PM window",
                    "Create Twitter threads for complex topics"
                ],
                "short_term": [
                    "Develop series-based content for better audience retention",
                    "Collaborate with micro-influencers for expanded reach",
                    "Implement user-generated content campaigns"
                ],
                "long_term": [
                    "Build a YouTube presence to complement existing platforms",
                    "Develop platform-specific content strategies",
                    "Invest in professional video production equipment"
                ]
            },
            "competitive_analysis": {
                "position": "above_average",
                "growth_rate_vs_competitors": 2.3,  # multiplier
                "engagement_rate_vs_industry": 1.8,  # multiplier
                "areas_for_improvement": [
                    "Increase posting consistency",
                    "Improve hashtag strategy",
                    "Enhance visual content quality"
                ]
            }
        }
        
        # Assertions
        assert insights_response["user_id"] == 1
        assert insights_response["performance_score"] >= 0 and insights_response["performance_score"] <= 100
        assert insights_response["growth_trajectory"] in ["positive", "negative", "stable"]
        
        # Check key insights structure
        assert "audience_behavior" in insights_response["key_insights"]
        assert "content_patterns" in insights_response["key_insights"]
        assert "platform_specific" in insights_response["key_insights"]
        
        # Check predictions
        assert "30_day_forecast" in insights_response["predictions"]
        assert "growth_opportunities" in insights_response["predictions"]
        
        # Check recommendations categories
        assert "immediate" in insights_response["recommendations"]
        assert "short_term" in insights_response["recommendations"]
        assert "long_term" in insights_response["recommendations"]
        
        # Check competitive analysis
        assert "position" in insights_response["competitive_analysis"]
        assert "growth_rate_vs_competitors" in insights_response["competitive_analysis"]
        
        print("✓ Automated insights generation test passed")


class TestAnalyticsIntegration:
    """Test suite for analytics integration with other system components."""

    @pytest.mark.asyncio
    async def test_analytics_export_functionality(self, test_config: Dict[str, Any]):
        """Test exporting analytics data to various formats."""
        print("✓ Testing analytics export functionality")
        
        # Mock export request
        export_request = {
            "user_id": 1,
            "platforms": ["instagram", "twitter", "tiktok"],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            "format": "csv",  # Options: csv, json, pdf, xlsx
            "include_charts": True,
            "metrics": ["followers", "engagement", "reach", "growth"]
        }
        
        # Mock export response
        export_response = {
            "export_id": "export_789012",
            "user_id": 1,
            "format": "csv",
            "status": "completed",
            "file_url": "https://app.example.com/exports/analytics_2024-01.csv",
            "file_size": "2.3 MB",
            "expires_at": "2024-02-07T23:59:59Z",  # 7 days from generation
            "generated_at": "2024-01-31T23:59:59Z",
            "includes": {
                "summary_data": True,
                "detailed_metrics": True,
                "charts": True,
                "insights": True
            }
        }
        
        # Assertions
        assert export_response["status"] == "completed"
        assert export_response["format"] == "csv"
        assert "file_url" in export_response
        assert "expires_at" in export_response
        assert export_response["includes"]["charts"] is True
        
        print("✓ Analytics export functionality test passed")

    @pytest.mark.asyncio
    async def test_real_time_analytics_monitoring(self, test_config: Dict[str, Any]):
        """Test real-time analytics monitoring and alerts."""
        print("✓ Testing real-time analytics monitoring")
        
        # Mock real-time monitoring setup
        monitoring_request = {
            "user_id": 1,
            "platforms": ["instagram", "twitter", "tiktok"],
            "alerts": [
                {
                    "metric": "engagement_rate",
                    "threshold": 10.0,  # Alert if engagement rate exceeds 10%
                    "condition": "greater_than"
                },
                {
                    "metric": "followers_growth_rate",
                    "threshold": 20.0,  # Alert if daily growth rate exceeds 20%
                    "condition": "greater_than"
                },
                {
                    "metric": "negative_sentiment",
                    "threshold": 15.0,  # Alert if negative sentiment exceeds 15%
                    "condition": "greater_than"
                }
            ],
            "notification_methods": ["email", "webhook"]
        }
        
        # Mock real-time alert response
        alert_response = {
            "alert_id": "alert_345678",
            "user_id": 1,
            "triggered_at": "2024-01-31T14:30:00Z",
            "metric": "engagement_rate",
            "platform": "tiktok",
            "threshold": 10.0,
            "actual_value": 15.7,
            "post_id": "tt_viral_001",
            "alert_level": "high",
            "message": "TikTok post engagement rate (15.7%) exceeded threshold (10.0%)",
            "suggested_actions": [
                "Monitor comments for sentiment analysis",
                "Prepare follow-up content to capitalize on engagement",
                "Consider promoting similar content"
            ]
        }
        
        # Mock monitoring dashboard response
        monitoring_dashboard = {
            "user_id": 1,
            "last_updated": "2024-01-31T23:59:59Z",
            "active_alerts": 3,
            "platforms_monitored": 3,
            "current_metrics": {
                "instagram": {
                    "live_engagement_rate": 4.5,
                    "hourly_followers_change": 5,
                    "recent_posts_performance": "above_average"
                },
                "twitter": {
                    "live_engagement_rate": 3.9,
                    "hourly_followers_change": 2,
                    "recent_posts_performance": "average"
                },
                "tiktok": {
                    "live_engagement_rate": 15.7,  # High engagement
                    "hourly_followers_change": 25,   # High growth
                    "recent_posts_performance": "excellent"
                }
            },
            "trending_content": [
                {
                    "platform": "tiktok",
                    "post_id": "tt_viral_001",
                    "engagement_velocity": "viral",
                    "current_views": 50000,
                    "growth_rate": 200  # views per hour
                }
            ]
        }
        
        # Assertions
        assert alert_response["user_id"] == 1
        assert alert_response["actual_value"] > alert_response["threshold"]
        assert alert_response["alert_level"] in ["low", "medium", "high"]
        assert len(alert_response["suggested_actions"]) > 0
        
        assert monitoring_dashboard["active_alerts"] >= 0
        assert "current_metrics" in monitoring_dashboard
        assert "trending_content" in monitoring_dashboard
        
        print("✓ Real-time analytics monitoring test passed")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])