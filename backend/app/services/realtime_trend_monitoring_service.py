"""
Enhanced real-time trend monitoring service
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import httpx
import openai

from app.core.config import settings
from app.models.curation import TrendWatch, TrendAlert
from app.models.social_account import SocialPlatform as Platform
from app.services.trend_analysis_service import TrendAnalysisService


class RealTimeTrendMonitoringService:
    """Enhanced service for real-time trend monitoring and alerts"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.trend_service = TrendAnalysisService(db)
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def monitor_all_active_watches(self) -> Dict[str, Any]:
        """Monitor all active trend watches and generate alerts"""
        # Get all active trend watches
        query = select(TrendWatch).where(TrendWatch.is_active == True)
        result = await self.db.execute(query)
        active_watches = result.scalars().all()
        
        monitoring_results = {
            "total_watches": len(active_watches),
            "alerts_generated": 0,
            "errors": []
        }
        
        for watch in active_watches:
            try:
                alerts = await self._monitor_trend_watch(watch)
                monitoring_results["alerts_generated"] += len(alerts)
                
                # Update last check time
                watch.last_check_at = datetime.utcnow()
                
            except Exception as e:
                monitoring_results["errors"].append(f"Error monitoring watch {watch.id}: {str(e)}")
        
        await self.db.commit()
        return monitoring_results
    
    async def monitor_trending_hashtags_realtime(self, platforms: List[Platform]) -> Dict[str, Any]:
        """Monitor trending hashtags in real-time across platforms"""
        realtime_data = {}
        
        for platform in platforms:
            try:
                hashtag_data = await self._get_realtime_hashtags(platform)
                realtime_data[platform.value] = hashtag_data
            except Exception as e:
                realtime_data[platform.value] = {"error": str(e)}
        
        return {
            "timestamp": datetime.utcnow(),
            "platforms_monitored": len(platforms),
            "hashtag_data": realtime_data,
            "top_trending_global": await self._get_global_trending_hashtags(realtime_data)
        }
    
    async def monitor_trending_sounds_realtime(self, platforms: List[Platform]) -> Dict[str, Any]:
        """Monitor trending sounds/audio in real-time for TikTok and Instagram"""
        sound_platforms = [p for p in platforms if p in [Platform.TIKTOK, Platform.INSTAGRAM]]
        realtime_data = {}
        
        for platform in sound_platforms:
            try:
                sound_data = await self._get_realtime_sounds(platform)
                realtime_data[platform.value] = sound_data
            except Exception as e:
                realtime_data[platform.value] = {"error": str(e)}
        
        return {
            "timestamp": datetime.utcnow(),
            "platforms_monitored": len(sound_platforms),
            "sound_data": realtime_data,
            "cross_platform_sounds": await self._identify_cross_platform_sounds(realtime_data)
        }
    
    async def detect_viral_content_spikes(self, platform: Platform, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """Detect sudden spikes in content engagement that indicate viral potential"""
        try:
            # Get current trending content
            current_trends = await self._get_current_viral_content(platform)
            
            # Get historical baseline for comparison
            historical_baseline = await self._get_historical_engagement_baseline(platform)
            
            viral_spikes = []
            
            for content in current_trends:
                current_engagement = content.get("engagement_rate", 0)
                baseline_engagement = historical_baseline.get("average_engagement", 0.05)
                
                if current_engagement > (baseline_engagement * threshold_multiplier):
                    spike_data = {
                        "content_id": content.get("id"),
                        "title": content.get("title"),
                        "creator": content.get("creator"),
                        "platform": platform.value,
                        "current_engagement": current_engagement,
                        "baseline_engagement": baseline_engagement,
                        "spike_multiplier": current_engagement / baseline_engagement if baseline_engagement > 0 else 0,
                        "detected_at": datetime.utcnow(),
                        "estimated_reach": content.get("estimated_reach"),
                        "content_type": content.get("content_type"),
                        "hashtags": content.get("hashtags", []),
                        "viral_indicators": await self._analyze_viral_indicators(content)
                    }
                    viral_spikes.append(spike_data)
            
            return viral_spikes
            
        except Exception as e:
            return [{"error": f"Error detecting viral spikes: {str(e)}"}]
    
    async def get_real_time_platform_insights(self, platform: Platform) -> Dict[str, Any]:
        """Get comprehensive real-time insights for a platform"""
        try:
            # Gather all real-time data
            hashtags = await self._get_realtime_hashtags(platform)
            trends = await self._get_realtime_trends(platform)
            viral_content = await self.detect_viral_content_spikes(platform)
            
            # Add sounds for supported platforms
            sounds = None
            if platform in [Platform.TIKTOK, Platform.INSTAGRAM]:
                sounds = await self._get_realtime_sounds(platform)
            
            # Generate AI insights if available
            ai_insights = None
            if self.openai_client:
                ai_insights = await self._generate_platform_ai_insights(
                    platform, hashtags, trends, viral_content, sounds
                )
            
            return {
                "platform": platform.value,
                "timestamp": datetime.utcnow(),
                "trending_hashtags": hashtags,
                "trending_topics": trends,
                "viral_content_spikes": viral_content,
                "trending_sounds": sounds,
                "ai_insights": ai_insights,
                "platform_health": await self._assess_platform_health(platform),
                "optimal_posting_window": await self._get_current_optimal_posting_window(platform)
            }
            
        except Exception as e:
            return {"error": f"Error getting platform insights: {str(e)}"}
    
    async def create_smart_trend_alerts(self, user_id: int, keywords: List[str], platforms: List[Platform]) -> List[Dict[str, Any]]:
        """Create intelligent trend alerts based on user's content history and preferences"""
        alerts = []
        
        try:
            for platform in platforms:
                platform_insights = await self.get_real_time_platform_insights(platform)
                
                for keyword in keywords:
                    # Check if keyword is trending
                    trend_score = await self._calculate_keyword_trend_score(keyword, platform_insights)
                    
                    if trend_score > 7.0:  # High trend score threshold
                        alert = {
                            "keyword": keyword,
                            "platform": platform.value,
                            "trend_score": trend_score,
                            "alert_type": "high_trend_score",
                            "recommended_action": await self._generate_trend_action_recommendation(
                                keyword, platform, trend_score
                            ),
                            "optimal_content_types": await self._suggest_optimal_content_types(
                                keyword, platform
                            ),
                            "hashtag_suggestions": await self._suggest_related_hashtags(
                                keyword, platform_insights
                            ),
                            "urgency_level": "high" if trend_score > 8.5 else "medium",
                            "estimated_opportunity_window": await self._estimate_opportunity_window(
                                keyword, platform, trend_score
                            )
                        }
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            return [{"error": f"Error creating smart alerts: {str(e)}"}]
    
    # Private helper methods
    async def _monitor_trend_watch(self, watch: TrendWatch) -> List[TrendAlert]:
        """Monitor an individual trend watch and generate alerts"""
        alerts = []
        
        for platform_name in watch.platforms:
            try:
                platform = Platform(platform_name)
                platform_insights = await self.get_real_time_platform_insights(platform)
                
                for keyword in watch.keywords:
                    # Check if keyword meets alert criteria
                    trend_data = await self._analyze_keyword_trend(keyword, platform_insights)
                    
                    if trend_data["should_alert"]:
                        alert = TrendAlert(
                            trend_watch_id=watch.id,
                            trend_name=keyword,
                            platform=platform_name,
                            alert_type=trend_data["alert_type"],
                            current_volume=trend_data.get("volume"),
                            growth_rate=trend_data.get("growth_rate"),
                            trend_data=trend_data
                        )
                        
                        self.db.add(alert)
                        alerts.append(alert)
                        
                        # Update watch stats
                        watch.total_alerts_sent += 1
            
            except Exception as e:
                continue
        
        return alerts
    
    async def _get_realtime_hashtags(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get real-time trending hashtags for platform"""
        # Mock implementation - in real app would call platform APIs
        hashtags = [
            {"tag": f"#{platform.value}trending1", "volume": 150000, "growth": "+75%", "momentum": "rising"},
            {"tag": f"#{platform.value}viral", "volume": 120000, "growth": "+60%", "momentum": "stable"},
            {"tag": f"#{platform.value}challenge", "volume": 90000, "growth": "+45%", "momentum": "rising"},
            {"tag": f"#{platform.value}content", "volume": 80000, "growth": "+30%", "momentum": "stable"},
            {"tag": f"#{platform.value}creator", "volume": 70000, "growth": "+25%", "momentum": "declining"},
        ]
        
        # Add timestamp and platform-specific data
        for hashtag in hashtags:
            hashtag.update({
                "platform": platform.value,
                "last_updated": datetime.utcnow(),
                "engagement_rate": round(0.05 + (hashtag["volume"] / 1000000) * 0.03, 3),
                "trending_duration": "2-4 hours"
            })
        
        return hashtags
    
    async def _get_realtime_sounds(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get real-time trending sounds for platform"""
        if platform not in [Platform.TIKTOK, Platform.INSTAGRAM]:
            return []
        
        sounds = [
            {"name": "Viral Song 1", "artist": "Popular Artist", "usage": 80000, "growth": "+200%"},
            {"name": "Trending Audio", "artist": "Creator Name", "usage": 60000, "growth": "+150%"},
            {"name": "Original Sound", "artist": "Viral Creator", "usage": 45000, "growth": "+100%"},
        ]
        
        for sound in sounds:
            sound.update({
                "platform": platform.value,
                "last_updated": datetime.utcnow(),
                "duration": 15,  # seconds
                "genre": "pop",
                "trending_since": "2 hours ago"
            })
        
        return sounds
    
    async def _get_realtime_trends(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get real-time trending topics for platform"""
        trends = [
            {"topic": f"{platform.value} Topic 1", "volume": 200000, "growth": "+80%", "category": "technology"},
            {"topic": f"{platform.value} Topic 2", "volume": 150000, "growth": "+65%", "category": "lifestyle"},
            {"topic": f"{platform.value} Topic 3", "volume": 120000, "growth": "+50%", "category": "entertainment"},
        ]
        
        for trend in trends:
            trend.update({
                "platform": platform.value,
                "last_updated": datetime.utcnow(),
                "sentiment": "positive",
                "related_hashtags": [f"#{trend['topic'].lower().replace(' ', '')}", f"#{trend['category']}"]
            })
        
        return trends
    
    async def _get_current_viral_content(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get currently viral content for spike detection"""
        return [
            {
                "id": f"{platform.value}_viral_1",
                "title": f"Viral {platform.value} Content 1",
                "creator": "Popular Creator",
                "engagement_rate": 0.15,
                "estimated_reach": 1000000,
                "content_type": "video",
                "hashtags": ["#viral", "#trending"],
                "posted_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": f"{platform.value}_viral_2", 
                "title": f"Viral {platform.value} Content 2",
                "creator": "Rising Creator",
                "engagement_rate": 0.12,
                "estimated_reach": 800000,
                "content_type": "image",
                "hashtags": ["#fyp", "#content"],
                "posted_at": datetime.utcnow() - timedelta(hours=1)
            }
        ]
    
    async def _get_historical_engagement_baseline(self, platform: Platform) -> Dict[str, Any]:
        """Get historical engagement baseline for comparison"""
        return {
            "average_engagement": 0.05,
            "median_engagement": 0.04,
            "top_10_percent": 0.12,
            "calculated_at": datetime.utcnow(),
            "data_period": "last_30_days"
        }
    
    async def _analyze_viral_indicators(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze indicators that suggest viral potential"""
        return {
            "engagement_velocity": "high",
            "comment_sentiment": "positive",
            "share_to_view_ratio": 0.08,
            "cross_platform_mentions": True,
            "influencer_shares": 3,
            "trend_alignment": "high"
        }
    
    async def _generate_platform_ai_insights(
        self,
        platform: Platform,
        hashtags: List[Dict],
        trends: List[Dict],
        viral_content: List[Dict],
        sounds: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Generate AI insights for platform data"""
        if not self.openai_client:
            return {"message": "AI insights not available"}
        
        try:
            data_summary = {
                "platform": platform.value,
                "top_hashtags": hashtags[:3],
                "top_trends": trends[:3],
                "viral_spikes": len(viral_content),
                "trending_sounds": len(sounds) if sounds else 0
            }
            
            prompt = f"""
            Analyze this real-time social media data and provide actionable insights:
            
            {json.dumps(data_summary, indent=2)}
            
            Provide:
            1. Key opportunities for content creators
            2. Recommended content strategies
            3. Timing recommendations
            4. Risk assessment for trend participation
            5. Predicted trend longevity
            
            Format as JSON with actionable insights.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"Error generating AI insights: {str(e)}"}
    
    async def _calculate_keyword_trend_score(self, keyword: str, platform_insights: Dict) -> float:
        """Calculate trend score for a keyword based on platform insights"""
        score = 5.0  # Base score
        
        # Check hashtags
        hashtags = platform_insights.get("trending_hashtags", [])
        for hashtag in hashtags:
            if keyword.lower() in hashtag.get("tag", "").lower():
                volume = hashtag.get("volume", 0)
                score += min(3.0, volume / 50000)  # Up to 3 points for volume
        
        # Check trending topics
        trends = platform_insights.get("trending_topics", [])
        for trend in trends:
            if keyword.lower() in trend.get("topic", "").lower():
                volume = trend.get("volume", 0)
                score += min(2.0, volume / 75000)  # Up to 2 points for volume
        
        return min(10.0, score)  # Cap at 10.0
    
    async def _analyze_keyword_trend(self, keyword: str, platform_insights: Dict) -> Dict[str, Any]:
        """Analyze if a keyword trend meets alert criteria"""
        trend_score = await self._calculate_keyword_trend_score(keyword, platform_insights)
        
        return {
            "should_alert": trend_score > 7.0,
            "alert_type": "high_trend_score" if trend_score > 8.0 else "medium_trend_score",
            "trend_score": trend_score,
            "volume": int(trend_score * 10000),  # Mock volume calculation
            "growth_rate": f"+{int(trend_score * 10)}%"
        }
    
    async def _assess_platform_health(self, platform: Platform) -> Dict[str, Any]:
        """Assess overall platform health and activity"""
        return {
            "activity_level": "high",
            "content_diversity": "excellent",
            "engagement_quality": "good",
            "creator_activity": "very_active",
            "trend_velocity": "fast",
            "recommendation": "optimal_time_for_posting"
        }
    
    async def _get_current_optimal_posting_window(self, platform: Platform) -> Dict[str, Any]:
        """Get current optimal posting window for platform"""
        current_hour = datetime.utcnow().hour
        
        # Mock optimal times based on platform
        optimal_times = {
            Platform.TIKTOK: [19, 20, 21, 22],
            Platform.INSTAGRAM: [11, 12, 17, 18, 19],
            Platform.TWITTER: [9, 12, 15, 17],
            Platform.LINKEDIN: [8, 9, 12, 17, 18],
            Platform.YOUTUBE: [14, 15, 16, 20, 21]
        }
        
        platform_optimal = optimal_times.get(platform, [12, 18, 20])
        is_optimal_now = current_hour in platform_optimal
        
        return {
            "is_optimal_now": is_optimal_now,
            "current_hour": current_hour,
            "next_optimal_hour": min([h for h in platform_optimal if h > current_hour], default=platform_optimal[0]),
            "optimal_hours_today": platform_optimal,
            "recommendation": "post_now" if is_optimal_now else "wait_for_optimal_time"
        }
    
    # Additional helper methods for smart alerts
    async def _generate_trend_action_recommendation(self, keyword: str, platform: Platform, trend_score: float) -> str:
        """Generate actionable recommendation for trending keyword"""
        if trend_score > 8.5:
            return f"Create content about '{keyword}' immediately - high viral potential on {platform.value}"
        elif trend_score > 7.5:
            return f"Plan content around '{keyword}' within 6 hours - good trend momentum on {platform.value}"
        else:
            return f"Monitor '{keyword}' trend and consider content creation if growth continues"
    
    async def _suggest_optimal_content_types(self, keyword: str, platform: Platform) -> List[str]:
        """Suggest optimal content types for keyword and platform"""
        suggestions = {
            Platform.TIKTOK: ["short_video", "dance_challenge", "tutorial"],
            Platform.INSTAGRAM: ["reel", "carousel_post", "story"],
            Platform.YOUTUBE: ["short", "tutorial", "vlog"],
            Platform.TWITTER: ["thread", "image_post", "poll"],
            Platform.LINKEDIN: ["article", "carousel", "video_post"]
        }
        return suggestions.get(platform, ["video", "image", "text"])
    
    async def _suggest_related_hashtags(self, keyword: str, platform_insights: Dict) -> List[str]:
        """Suggest related hashtags based on current trends"""
        trending_hashtags = platform_insights.get("trending_hashtags", [])
        related = [hashtag["tag"] for hashtag in trending_hashtags[:5]]
        related.append(f"#{keyword.lower().replace(' ', '')}")
        return related
    
    async def _estimate_opportunity_window(self, keyword: str, platform: Platform, trend_score: float) -> str:
        """Estimate how long the trend opportunity will last"""
        if trend_score > 9.0:
            return "6-12 hours"
        elif trend_score > 8.0:
            return "12-24 hours"
        elif trend_score > 7.0:
            return "1-3 days"
        else:
            return "3-7 days"
    
    async def _get_global_trending_hashtags(self, platform_data: Dict) -> List[Dict[str, Any]]:
        """Identify globally trending hashtags across platforms"""
        all_hashtags = []
        for platform, data in platform_data.items():
            if isinstance(data, list):
                all_hashtags.extend(data)
        
        # Sort by volume and return top global trends
        sorted_hashtags = sorted(all_hashtags, key=lambda x: x.get("volume", 0), reverse=True)
        return sorted_hashtags[:10]
    
    async def _identify_cross_platform_sounds(self, sound_data: Dict) -> List[Dict[str, Any]]:
        """Identify sounds trending across multiple platforms"""
        cross_platform_sounds = []
        
        # Compare sounds across platforms to find cross-platform trends
        # This is a simplified implementation
        for platform, sounds in sound_data.items():
            if isinstance(sounds, list):
                for sound in sounds[:3]:  # Top 3 from each platform
                    sound["cross_platform_potential"] = "high"
                    cross_platform_sounds.append(sound)
        
        return cross_platform_sounds