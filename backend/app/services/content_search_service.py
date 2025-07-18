"""
Advanced content search and ideation service with AI-powered trend analysis
"""

import asyncio
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime, timedelta
import json
import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.content import Content, ContentType
from app.models.social_account import SocialAccount, SocialPlatform as Platform


class ContentSearchService:
    """Service for intelligent content search, ideation, and trend analysis"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def search_trending_topics(self, platform: Platform, region: str = "global") -> List[Dict[str, Any]]:
        """Search for trending topics on specific platforms"""
        trends = []
        
        try:
            if platform == Platform.TWITTER:
                trends.extend(await self._get_twitter_trends(region))
            elif platform == Platform.TIKTOK:
                trends.extend(await self._get_tiktok_trends(region))
            elif platform == Platform.INSTAGRAM:
                trends.extend(await self._get_instagram_trends(region))
            elif platform == Platform.YOUTUBE:
                trends.extend(await self._get_youtube_trends(region))
            elif platform == Platform.LINKEDIN:
                trends.extend(await self._get_linkedin_trends(region))
            
            # Add AI-powered trend enhancement
            if self.openai_client and trends:
                enhanced_trends = await self._enhance_trends_with_ai(trends, platform)
                return enhanced_trends
                
        except Exception as e:
            print(f"Error fetching trends for {platform}: {e}")
        
        return trends
    
    async def generate_content_ideas(self, topic: str, platform: Platform, target_audience: str = None) -> List[Dict[str, Any]]:
        """Generate AI-powered content ideas based on topics and platform"""
        if not self.openai_client:
            return []
        
        try:
            platform_specs = self._get_platform_specifications(platform)
            
            prompt = f"""
            Generate 10 creative and viral content ideas for {platform.value} about '{topic}'.
            
            Platform specifications:
            - Max duration: {platform_specs['max_duration']}
            - Optimal dimensions: {platform_specs['dimensions']}
            - Key features: {platform_specs['features']}
            - Best practices: {platform_specs['best_practices']}
            
            Target audience: {target_audience or 'General audience'}
            
            For each idea, provide:
            1. Content type (video, image, carousel, etc.)
            2. Hook/opening line
            3. Key talking points
            4. Visual elements suggestions
            5. Hashtag recommendations
            6. Call-to-action
            7. Virality score prediction (1-10)
            
            Format as JSON array.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            # Try to parse JSON, fall back to structured text if needed
            try:
                ideas = json.loads(content)
            except:
                ideas = self._parse_text_ideas(content)
            
            return ideas
            
        except Exception as e:
            print(f"Error generating content ideas: {e}")
            return []
    
    async def search_viral_content(self, platform: Platform, timeframe: int = 7) -> List[Dict[str, Any]]:
        """Search for viral content patterns on platforms"""
        viral_content = []
        
        try:
            # Get viral metrics thresholds for each platform
            thresholds = self._get_viral_thresholds(platform)
            
            if platform == Platform.TIKTOK:
                viral_content.extend(await self._get_viral_tiktok_content(timeframe, thresholds))
            elif platform == Platform.INSTAGRAM:
                viral_content.extend(await self._get_viral_instagram_content(timeframe, thresholds))
            elif platform == Platform.YOUTUBE:
                viral_content.extend(await self._get_viral_youtube_content(timeframe, thresholds))
            elif platform == Platform.TWITTER:
                viral_content.extend(await self._get_viral_twitter_content(timeframe, thresholds))
            
            # Analyze patterns with AI
            if self.openai_client and viral_content:
                patterns = await self._analyze_viral_patterns(viral_content, platform)
                return {
                    "viral_content": viral_content,
                    "patterns": patterns,
                    "recommendations": await self._generate_viral_recommendations(patterns, platform)
                }
                
        except Exception as e:
            print(f"Error searching viral content: {e}")
        
        return viral_content
    
    async def suggest_hashtags(self, content_description: str, platform: Platform) -> List[str]:
        """AI-powered hashtag suggestions based on content and platform"""
        if not self.openai_client:
            return []
        
        try:
            platform_hashtag_rules = self._get_hashtag_rules(platform)
            
            prompt = f"""
            Generate optimal hashtags for {platform.value} content: "{content_description}"
            
            Platform rules:
            - Max hashtags: {platform_hashtag_rules['max_count']}
            - Character limit: {platform_hashtag_rules['char_limit']}
            - Style: {platform_hashtag_rules['style']}
            
            Mix of:
            - 3-5 trending/popular hashtags
            - 3-5 niche/specific hashtags  
            - 2-3 branded/unique hashtags
            
            Return as JSON array of strings.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            try:
                hashtags = json.loads(content)
            except:
                # Extract hashtags from text
                hashtags = [tag.strip() for tag in content.split() if tag.startswith('#')]
            
            return hashtags[:platform_hashtag_rules['max_count']]
            
        except Exception as e:
            print(f"Error generating hashtags: {e}")
            return []
    
    async def analyze_competitor_content(self, competitor_handles: List[str], platform: Platform) -> Dict[str, Any]:
        """Analyze competitor content strategies"""
        analysis = {
            "posting_frequency": {},
            "content_types": {},
            "engagement_patterns": {},
            "hashtag_strategies": {},
            "recommendations": []
        }
        
        try:
            for handle in competitor_handles:
                competitor_data = await self._get_competitor_data(handle, platform)
                if competitor_data:
                    analysis["posting_frequency"][handle] = competitor_data.get("posting_frequency")
                    analysis["content_types"][handle] = competitor_data.get("content_types")
                    analysis["engagement_patterns"][handle] = competitor_data.get("engagement_patterns")
                    analysis["hashtag_strategies"][handle] = competitor_data.get("hashtags")
            
            # Generate AI insights
            if self.openai_client and any(analysis.values()):
                insights = await self._generate_competitor_insights(analysis, platform)
                analysis["recommendations"] = insights
                
        except Exception as e:
            print(f"Error analyzing competitors: {e}")
        
        return analysis
    
    # Platform-specific trend fetching methods
    async def _get_twitter_trends(self, region: str) -> List[Dict[str, Any]]:
        """Fetch Twitter/X trending topics"""
        # Placeholder for Twitter API integration
        return [
            {"topic": "AI Technology", "volume": 50000, "growth": "+25%"},
            {"topic": "Digital Marketing", "volume": 30000, "growth": "+15%"},
            {"topic": "Remote Work", "volume": 25000, "growth": "+10%"}
        ]
    
    async def _get_tiktok_trends(self, region: str) -> List[Dict[str, Any]]:
        """Fetch TikTok trending topics and sounds"""
        return [
            {"topic": "Dance Challenge", "volume": 1000000, "growth": "+300%", "type": "challenge"},
            {"topic": "Life Hack", "volume": 500000, "growth": "+150%", "type": "educational"},
            {"topic": "Food Review", "volume": 750000, "growth": "+200%", "type": "entertainment"}
        ]
    
    async def _get_instagram_trends(self, region: str) -> List[Dict[str, Any]]:
        """Fetch Instagram trending topics and hashtags"""
        return [
            {"topic": "Wellness Wednesday", "volume": 200000, "growth": "+50%", "type": "lifestyle"},
            {"topic": "Before After", "volume": 150000, "growth": "+75%", "type": "transformation"},
            {"topic": "Behind The Scenes", "volume": 180000, "growth": "+60%", "type": "authentic"}
        ]
    
    async def _get_youtube_trends(self, region: str) -> List[Dict[str, Any]]:
        """Fetch YouTube trending topics"""
        return [
            {"topic": "Tutorial Tuesday", "volume": 300000, "growth": "+40%", "type": "educational"},
            {"topic": "Product Review", "volume": 250000, "growth": "+30%", "type": "review"},
            {"topic": "Day in Life", "volume": 400000, "growth": "+80%", "type": "vlog"}
        ]
    
    async def _get_linkedin_trends(self, region: str) -> List[Dict[str, Any]]:
        """Fetch LinkedIn trending professional topics"""
        return [
            {"topic": "Leadership", "volume": 80000, "growth": "+20%", "type": "professional"},
            {"topic": "Industry Insights", "volume": 60000, "growth": "+35%", "type": "business"},
            {"topic": "Career Development", "volume": 70000, "growth": "+25%", "type": "career"}
        ]
    
    async def _enhance_trends_with_ai(self, trends: List[Dict], platform: Platform) -> List[Dict]:
        """Enhance trend data with AI insights"""
        try:
            prompt = f"""
            Analyze these trending topics for {platform.value} and enhance each with:
            1. Content angle suggestions
            2. Target audience insights
            3. Optimal posting times
            4. Content format recommendations
            5. Engagement tactics
            
            Trends: {json.dumps(trends)}
            
            Return enhanced JSON with additional fields.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            
            enhanced = json.loads(response.choices[0].message.content)
            return enhanced
            
        except Exception as e:
            print(f"Error enhancing trends: {e}")
            return trends
    
    def _get_platform_specifications(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific content specifications"""
        specs = {
            Platform.TIKTOK: {
                "max_duration": "60 seconds",
                "dimensions": "9:16 vertical",
                "features": ["effects", "filters", "sounds", "text_overlay"],
                "best_practices": ["hook_in_3s", "trending_sounds", "hashtag_challenges"]
            },
            Platform.INSTAGRAM: {
                "max_duration": "90 seconds (Reels)",
                "dimensions": "9:16 (Reels), 1:1 (Posts)",
                "features": ["reels", "stories", "carousel", "igtv"],
                "best_practices": ["high_quality_visuals", "story_engagement", "reel_trends"]
            },
            Platform.YOUTUBE: {
                "max_duration": "60 seconds (Shorts)",
                "dimensions": "9:16 (Shorts), 16:9 (regular)",
                "features": ["shorts", "long_form", "live", "community"],
                "best_practices": ["strong_thumbnails", "seo_titles", "engagement_hooks"]
            },
            Platform.TWITTER: {
                "max_duration": "140 seconds",
                "dimensions": "16:9 or 1:1",
                "features": ["threads", "spaces", "polls", "moments"],
                "best_practices": ["timely_content", "hashtag_strategy", "engagement"]
            },
            Platform.LINKEDIN: {
                "max_duration": "30 minutes",
                "dimensions": "16:9 or 1:1",
                "features": ["articles", "polls", "documents", "events"],
                "best_practices": ["professional_tone", "industry_insights", "networking"]
            }
        }
        
        return specs.get(platform, {})
    
    def _get_viral_thresholds(self, platform: Platform) -> Dict[str, int]:
        """Get viral content thresholds for each platform"""
        thresholds = {
            Platform.TIKTOK: {"views": 100000, "likes": 10000, "shares": 1000},
            Platform.INSTAGRAM: {"likes": 10000, "comments": 500, "saves": 1000},
            Platform.YOUTUBE: {"views": 50000, "likes": 1000, "comments": 100},
            Platform.TWITTER: {"likes": 5000, "retweets": 1000, "replies": 500},
            Platform.LINKEDIN: {"likes": 1000, "comments": 100, "shares": 200}
        }
        
        return thresholds.get(platform, {})
    
    def _get_hashtag_rules(self, platform: Platform) -> Dict[str, Any]:
        """Get hashtag best practices for each platform"""
        rules = {
            Platform.TIKTOK: {"max_count": 5, "char_limit": 100, "style": "trending_focused"},
            Platform.INSTAGRAM: {"max_count": 30, "char_limit": 2200, "style": "mix_popular_niche"},
            Platform.YOUTUBE: {"max_count": 15, "char_limit": 500, "style": "seo_focused"},
            Platform.TWITTER: {"max_count": 3, "char_limit": 280, "style": "conversation_starters"},
            Platform.LINKEDIN: {"max_count": 5, "char_limit": 3000, "style": "professional_industry"}
        }
        
        return rules.get(platform, {"max_count": 10, "char_limit": 500, "style": "balanced"})
    
    def _parse_text_ideas(self, text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated text into structured content ideas"""
        # Basic parsing logic for when JSON parsing fails
        ideas = []
        lines = text.split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_idea:
                    ideas.append(current_idea)
                current_idea = {"title": line, "type": "mixed", "virality_score": 7}
            elif line and current_idea:
                if "hook" in line.lower():
                    current_idea["hook"] = line
                elif "hashtag" in line.lower():
                    current_idea["hashtags"] = line
                elif "call" in line.lower() and "action" in line.lower():
                    current_idea["cta"] = line
        
        if current_idea:
            ideas.append(current_idea)
        
        return ideas[:10]  # Limit to 10 ideas
    
    # Placeholder methods for viral content analysis
    async def _get_viral_tiktok_content(self, timeframe: int, thresholds: Dict) -> List[Dict]:
        return [{"title": "Dance trend", "views": 2000000, "engagement_rate": 0.15}]
    
    async def _get_viral_instagram_content(self, timeframe: int, thresholds: Dict) -> List[Dict]:
        return [{"title": "Reel trend", "likes": 50000, "engagement_rate": 0.12}]
    
    async def _get_viral_youtube_content(self, timeframe: int, thresholds: Dict) -> List[Dict]:
        return [{"title": "Short tutorial", "views": 500000, "engagement_rate": 0.08}]
    
    async def _get_viral_twitter_content(self, timeframe: int, thresholds: Dict) -> List[Dict]:
        return [{"title": "Thread tips", "retweets": 5000, "engagement_rate": 0.10}]
    
    async def _analyze_viral_patterns(self, content: List[Dict], platform: Platform) -> Dict:
        return {"common_themes": ["trending_audio", "quick_hooks"], "optimal_length": "15-30s"}
    
    async def _generate_viral_recommendations(self, patterns: Dict, platform: Platform) -> List[str]:
        return ["Use trending audio", "Hook viewers in first 3 seconds", "Include clear call-to-action"]
    
    async def _get_competitor_data(self, handle: str, platform: Platform) -> Dict:
        return {"posting_frequency": "2x daily", "content_types": ["video", "image"], "engagement_patterns": "peak_evening"}
    
    async def _generate_competitor_insights(self, analysis: Dict, platform: Platform) -> List[str]:
        return ["Post during peak hours", "Focus on video content", "Engage with trending topics"]