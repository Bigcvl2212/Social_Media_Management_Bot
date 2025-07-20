"""
Enhanced AI meme generator with trending analysis and brand relevance
"""

import asyncio
import base64
import io
import json
import os
import random
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import httpx
import openai
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.content import Content, ContentType, ContentStatus
from app.models.social_account import SocialPlatform as Platform


class EnhancedMemeGeneratorService:
    """Enhanced AI-powered meme generator with trending analysis and brand relevance"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.temp_dir = Path(settings.UPLOAD_DIR) / "memes"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize meme templates and trending data
        self._trending_formats = {}
        self._brand_voice_cache = {}
    
    async def generate_trending_meme(self, 
                                   topic: str, 
                                   brand_voice: str = "casual",
                                   platform: Platform = Platform.INSTAGRAM,
                                   target_audience: str = "general",
                                   include_brand_elements: bool = True) -> Dict[str, Any]:
        """Generate meme using current trending formats and topics"""
        try:
            # Get current trending meme formats
            trending_formats = await self._get_trending_meme_formats(platform)
            
            # Analyze topic for meme potential
            topic_analysis = await self._analyze_topic_for_memes(topic, platform, target_audience)
            
            # Select best trending format for the topic
            selected_format = await self._select_optimal_format(
                trending_formats, topic_analysis, brand_voice
            )
            
            # Generate meme text using AI
            meme_text = await self._generate_meme_text(
                topic, selected_format, brand_voice, platform, target_audience
            )
            
            # Create meme image
            meme_image = await self._create_meme_image(
                selected_format, meme_text, platform, include_brand_elements
            )
            
            # Add viral enhancement effects
            enhanced_meme = await self._enhance_for_virality(
                meme_image["path"], platform, topic_analysis
            )
            
            return {
                "meme_path": enhanced_meme["path"],
                "format_used": selected_format["name"],
                "text_content": meme_text,
                "viral_score": enhanced_meme["viral_score"],
                "trending_relevance": topic_analysis["trending_score"],
                "brand_alignment": await self._calculate_brand_alignment(meme_text, brand_voice),
                "platform_optimizations": enhanced_meme["optimizations"],
                "alternative_versions": await self._generate_alternative_versions(
                    selected_format, topic, brand_voice, platform
                )
            }
            
        except Exception as e:
            return {"error": f"Trending meme generation failed: {str(e)}"}
    
    async def generate_brand_relevant_memes(self, 
                                          brand_info: Dict[str, Any], 
                                          current_trends: List[str],
                                          platform: Platform = Platform.INSTAGRAM,
                                          count: int = 5) -> Dict[str, Any]:
        """Generate multiple brand-relevant memes based on current trends"""
        try:
            memes = []
            
            for trend in current_trends[:count]:
                # Analyze trend for brand relevance
                relevance_analysis = await self._analyze_brand_trend_relevance(
                    brand_info, trend, platform
                )
                
                if relevance_analysis["relevance_score"] > 0.6:
                    # Generate brand-aligned meme
                    meme_result = await self._generate_brand_aligned_meme(
                        trend, brand_info, platform, relevance_analysis
                    )
                    
                    if "error" not in meme_result:
                        memes.append(meme_result)
            
            # Rank memes by potential impact
            ranked_memes = await self._rank_memes_by_impact(memes, brand_info, platform)
            
            return {
                "brand_memes": ranked_memes,
                "brand_info": brand_info,
                "trends_analyzed": len(current_trends),
                "memes_created": len(memes),
                "top_recommendation": ranked_memes[0] if ranked_memes else None
            }
            
        except Exception as e:
            return {"error": f"Brand meme generation failed: {str(e)}"}
    
    async def create_meme_series(self, 
                               theme: str, 
                               series_count: int = 3,
                               platform: Platform = Platform.INSTAGRAM,
                               brand_voice: str = "casual") -> Dict[str, Any]:
        """Create a series of related memes around a theme"""
        try:
            # Develop series concept
            series_concept = await self._develop_meme_series_concept(
                theme, series_count, platform, brand_voice
            )
            
            meme_series = []
            
            for i, concept in enumerate(series_concept["concepts"]):
                # Generate individual meme
                meme_result = await self.generate_trending_meme(
                    concept["topic"], 
                    brand_voice, 
                    platform,
                    concept.get("target_audience", "general")
                )
                
                if "error" not in meme_result:
                    meme_result["series_position"] = i + 1
                    meme_result["series_theme"] = theme
                    meme_result["concept"] = concept
                    meme_series.append(meme_result)
            
            return {
                "meme_series": meme_series,
                "series_theme": theme,
                "series_concept": series_concept,
                "posting_schedule": await self._suggest_series_posting_schedule(
                    meme_series, platform
                ),
                "engagement_strategy": await self._develop_series_engagement_strategy(
                    meme_series, platform
                )
            }
            
        except Exception as e:
            return {"error": f"Meme series creation failed: {str(e)}"}
    
    async def generate_reactive_meme(self, 
                                   current_event: str, 
                                   brand_perspective: str,
                                   platform: Platform = Platform.TWITTER,
                                   urgency: str = "high") -> Dict[str, Any]:
        """Generate reactive meme for current events or trending topics"""
        try:
            # Analyze event for meme potential and brand safety
            event_analysis = await self._analyze_event_for_memes(
                current_event, brand_perspective, platform
            )
            
            if event_analysis["brand_safety_score"] < 0.7:
                return {"error": "Event not suitable for brand meme creation due to safety concerns"}
            
            # Get real-time trending formats
            trending_formats = await self._get_realtime_trending_formats(platform)
            
            # Generate reactive meme content
            reactive_content = await self._generate_reactive_meme_content(
                current_event, brand_perspective, event_analysis, urgency
            )
            
            # Create meme with urgency optimizations
            meme_result = await self._create_urgent_meme(
                reactive_content, trending_formats[0], platform
            )
            
            # Add real-time optimization
            optimized_meme = await self._optimize_for_real_time_sharing(
                meme_result["path"], platform, urgency
            )
            
            return {
                "reactive_meme_path": optimized_meme["path"],
                "event_referenced": current_event,
                "brand_perspective": brand_perspective,
                "urgency_level": urgency,
                "time_sensitivity": event_analysis["time_sensitivity"],
                "viral_potential": event_analysis["viral_potential"],
                "optimal_posting_time": "immediate" if urgency == "high" else "within_1_hour"
            }
            
        except Exception as e:
            return {"error": f"Reactive meme generation failed: {str(e)}"}
    
    async def analyze_meme_performance_potential(self, 
                                               meme_concept: str, 
                                               platform: Platform = Platform.INSTAGRAM) -> Dict[str, Any]:
        """Analyze potential performance of a meme concept before creation"""
        try:
            # Analyze current meme trends
            trend_analysis = await self._analyze_current_meme_trends(platform)
            
            # Assess concept against trending patterns
            concept_score = await self._score_meme_concept(
                meme_concept, trend_analysis, platform
            )
            
            # Predict engagement potential
            engagement_prediction = await self._predict_meme_engagement(
                meme_concept, concept_score, platform
            )
            
            # Generate improvement suggestions
            improvements = await self._suggest_concept_improvements(
                meme_concept, concept_score, platform
            )
            
            return {
                "concept": meme_concept,
                "performance_score": concept_score["overall_score"],
                "trend_alignment": concept_score["trend_score"],
                "originality_score": concept_score["originality_score"],
                "engagement_prediction": engagement_prediction,
                "improvement_suggestions": improvements,
                "recommended_formats": concept_score["recommended_formats"],
                "optimal_timing": engagement_prediction["best_posting_time"]
            }
            
        except Exception as e:
            return {"error": f"Meme performance analysis failed: {str(e)}"}
    
    # Trending analysis methods
    async def _get_trending_meme_formats(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get currently trending meme formats for platform"""
        # In production, this would connect to trending APIs or analyze recent content
        
        trending_formats = {
            Platform.TIKTOK: [
                {
                    "name": "drake_pointing",
                    "popularity": 0.9,
                    "format_type": "choice_comparison",
                    "template": "drake_template.jpg",
                    "description": "Drake pointing meme for comparing two options"
                },
                {
                    "name": "distracted_boyfriend",
                    "popularity": 0.8,
                    "format_type": "distraction",
                    "template": "distracted_boyfriend.jpg",
                    "description": "Distracted boyfriend meme for showing preference"
                },
                {
                    "name": "woman_yelling_cat",
                    "popularity": 0.85,
                    "format_type": "reaction",
                    "template": "woman_cat.jpg",
                    "description": "Woman yelling at cat reaction meme"
                }
            ],
            Platform.INSTAGRAM: [
                {
                    "name": "this_is_fine",
                    "popularity": 0.87,
                    "format_type": "situation_commentary",
                    "template": "this_is_fine.jpg",
                    "description": "This is fine dog meme for ironic situations"
                },
                {
                    "name": "expanding_brain",
                    "popularity": 0.82,
                    "format_type": "progression",
                    "template": "expanding_brain.jpg",
                    "description": "Expanding brain meme for showing progression"
                }
            ],
            Platform.TWITTER: [
                {
                    "name": "hot_takes",
                    "popularity": 0.9,
                    "format_type": "opinion",
                    "template": "hot_takes.jpg",
                    "description": "Hot takes format for controversial opinions"
                }
            ]
        }
        
        return trending_formats.get(platform, trending_formats[Platform.INSTAGRAM])
    
    async def _analyze_topic_for_memes(self, topic: str, platform: Platform, audience: str) -> Dict[str, Any]:
        """Analyze topic for meme creation potential"""
        if not self.openai_client:
            return {
                "trending_score": 0.7,
                "humor_potential": 0.8,
                "relatability": 0.75,
                "meme_angles": ["general humor", "relatable content"]
            }
        
        try:
            prompt = f"""
            Analyze this topic for meme creation potential: "{topic}"
            
            Platform: {platform.value}
            Target audience: {audience}
            
            Provide analysis on:
            1. Current trending relevance (0-1 score)
            2. Humor potential (0-1 score) 
            3. Relatability factor (0-1 score)
            4. Potential meme angles and approaches
            5. Recommended meme formats
            6. Timing considerations
            
            Return as JSON format.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except:
                return {
                    "trending_score": 0.7,
                    "humor_potential": 0.8,
                    "relatability": 0.75,
                    "meme_angles": ["general humor", "relatable content"],
                    "recommended_formats": ["reaction", "commentary"]
                }
                
        except Exception as e:
            return {
                "trending_score": 0.5,
                "humor_potential": 0.6,
                "relatability": 0.5,
                "error": str(e)
            }
    
    async def _select_optimal_format(self, trending_formats: List[Dict], topic_analysis: Dict, brand_voice: str) -> Dict[str, Any]:
        """Select the optimal meme format based on analysis"""
        if not trending_formats:
            return {
                "name": "custom_text",
                "popularity": 0.5,
                "format_type": "text_overlay",
                "template": None
            }
        
        # Score each format based on compatibility
        format_scores = []
        
        for format_info in trending_formats:
            score = format_info["popularity"]
            
            # Adjust score based on topic analysis
            if format_info["format_type"] in topic_analysis.get("recommended_formats", []):
                score += 0.2
            
            # Adjust for brand voice compatibility
            voice_compatibility = self._calculate_format_voice_compatibility(format_info, brand_voice)
            score *= voice_compatibility
            
            format_scores.append((score, format_info))
        
        # Return highest scoring format
        format_scores.sort(key=lambda x: x[0], reverse=True)
        return format_scores[0][1]
    
    def _calculate_format_voice_compatibility(self, format_info: Dict, brand_voice: str) -> float:
        """Calculate how well a meme format aligns with brand voice"""
        voice_format_compatibility = {
            "professional": {
                "choice_comparison": 0.8,
                "progression": 0.9,
                "situation_commentary": 0.7,
                "reaction": 0.6
            },
            "casual": {
                "reaction": 0.9,
                "distraction": 0.8,
                "situation_commentary": 0.8,
                "choice_comparison": 0.7
            },
            "humorous": {
                "reaction": 0.95,
                "situation_commentary": 0.9,
                "distraction": 0.85,
                "choice_comparison": 0.8
            },
            "educational": {
                "progression": 0.9,
                "choice_comparison": 0.8,
                "situation_commentary": 0.7,
                "reaction": 0.6
            }
        }
        
        format_type = format_info.get("format_type", "reaction")
        return voice_format_compatibility.get(brand_voice, {}).get(format_type, 0.7)
    
    # Meme text generation
    async def _generate_meme_text(self, topic: str, format_info: Dict, brand_voice: str, platform: Platform, audience: str) -> Dict[str, Any]:
        """Generate meme text content using AI"""
        if not self.openai_client:
            return {
                "top_text": f"When you think about {topic}",
                "bottom_text": "It's actually pretty interesting",
                "format_specific": {}
            }
        
        try:
            prompt = f"""
            Create meme text for the "{format_info['name']}" format about: {topic}
            
            Format type: {format_info['format_type']}
            Brand voice: {brand_voice}
            Platform: {platform.value}
            Target audience: {audience}
            
            Requirements:
            - Match the meme format structure
            - Use appropriate {brand_voice} tone
            - Make it relatable to {audience}
            - Keep text concise and punchy
            - Ensure it's {platform.value}-appropriate
            
            Return structured text for the meme format.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            # Parse meme text based on format
            meme_text = self._parse_meme_text_for_format(
                response.choices[0].message.content, format_info
            )
            
            return meme_text
            
        except Exception as e:
            return {
                "top_text": f"When {topic}",
                "bottom_text": "Happens",
                "error": str(e)
            }
    
    def _parse_meme_text_for_format(self, ai_response: str, format_info: Dict) -> Dict[str, Any]:
        """Parse AI response into format-specific meme text structure"""
        format_type = format_info.get("format_type", "reaction")
        
        if format_type == "choice_comparison":
            # Drake format: two options
            lines = ai_response.split('\n')
            return {
                "top_text": lines[0] if lines else "Option 1",
                "bottom_text": lines[1] if len(lines) > 1 else "Option 2",
                "format_specific": {
                    "rejection_text": lines[0] if lines else "Not this",
                    "approval_text": lines[1] if len(lines) > 1 else "This instead"
                }
            }
        elif format_type == "progression":
            # Expanding brain format: multiple levels
            lines = ai_response.split('\n')
            return {
                "format_specific": {
                    "level_1": lines[0] if lines else "Basic level",
                    "level_2": lines[1] if len(lines) > 1 else "Intermediate level",
                    "level_3": lines[2] if len(lines) > 2 else "Advanced level",
                    "level_4": lines[3] if len(lines) > 3 else "Galaxy brain level"
                }
            }
        else:
            # Standard top/bottom text format
            lines = ai_response.split('\n')
            return {
                "top_text": lines[0] if lines else ai_response[:50],
                "bottom_text": lines[1] if len(lines) > 1 else ""
            }
    
    # Meme image creation
    async def _create_meme_image(self, format_info: Dict, meme_text: Dict, platform: Platform, include_brand: bool) -> Dict[str, Any]:
        """Create the meme image with text overlay"""
        try:
            # Get or create base template
            template_image = await self._get_meme_template(format_info, platform)
            
            # Add text overlays
            meme_with_text = await self._add_text_to_template(
                template_image, meme_text, format_info, platform
            )
            
            # Add brand elements if requested
            if include_brand:
                branded_meme = await self._add_brand_elements(meme_with_text, platform)
            else:
                branded_meme = meme_with_text
            
            # Save final meme
            filename = f"meme_{format_info['name']}_{int(asyncio.get_event_loop().time())}.jpg"
            meme_path = self.temp_dir / filename
            branded_meme.save(meme_path, "JPEG", quality=95)
            
            return {
                "path": str(meme_path),
                "format": format_info["name"],
                "dimensions": branded_meme.size
            }
            
        except Exception as e:
            return {"error": f"Meme image creation failed: {str(e)}"}
    
    async def _get_meme_template(self, format_info: Dict, platform: Platform) -> Image.Image:
        """Get or generate meme template image"""
        template_name = format_info.get("template")
        
        if template_name and template_name != "custom_text":
            # Try to load existing template
            template_path = Path(__file__).parent.parent / "assets" / "meme_templates" / template_name
            if template_path.exists():
                return Image.open(template_path)
        
        # Generate basic template based on format
        specs = self._get_platform_image_specs(platform)
        width, height = specs["dimensions"]
        
        if format_info["format_type"] == "choice_comparison":
            # Create two-panel template (Drake style)
            template = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(template)
            
            # Draw dividing line
            draw.line([(0, height//2), (width, height//2)], fill='black', width=2)
            
            # Add placeholder areas
            draw.rectangle([10, 10, width//2-10, height//2-10], outline='gray', width=2)
            draw.rectangle([10, height//2+10, width//2-10, height-10], outline='gray', width=2)
            
        elif format_info["format_type"] == "progression":
            # Create four-panel template (Brain expanding style)
            template = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(template)
            
            # Draw grid
            draw.line([(width//2, 0), (width//2, height)], fill='black', width=2)
            draw.line([(0, height//2), (width, height//2)], fill='black', width=2)
            
        else:
            # Standard template with top and bottom text areas
            template = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(template)
            
            # Add gradient or pattern
            for y in range(height):
                color_intensity = int(255 * (y / height))
                draw.line([(0, y), (width, y)], fill=(color_intensity, color_intensity, 255))
        
        return template
    
    async def _add_text_to_template(self, template: Image.Image, meme_text: Dict, format_info: Dict, platform: Platform) -> Image.Image:
        """Add text overlays to meme template"""
        img = template.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font_size = self._calculate_font_size(img.size, platform)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        format_type = format_info.get("format_type", "reaction")
        
        if format_type == "choice_comparison" and "format_specific" in meme_text:
            # Drake-style format
            self._add_choice_comparison_text(img, draw, meme_text["format_specific"], font)
        elif format_type == "progression" and "format_specific" in meme_text:
            # Brain expanding format
            self._add_progression_text(img, draw, meme_text["format_specific"], font)
        else:
            # Standard top/bottom format
            self._add_standard_meme_text(img, draw, meme_text, font)
        
        return img
    
    def _add_standard_meme_text(self, img: Image.Image, draw: ImageDraw.Draw, meme_text: Dict, font):
        """Add standard top and bottom text to meme"""
        width, height = img.size
        
        # Add top text
        if meme_text.get("top_text"):
            top_text = meme_text["top_text"].upper()
            self._draw_outlined_text(draw, top_text, (width//2, height//8), font, anchor="mm")
        
        # Add bottom text
        if meme_text.get("bottom_text"):
            bottom_text = meme_text["bottom_text"].upper()
            self._draw_outlined_text(draw, bottom_text, (width//2, height*7//8), font, anchor="mm")
    
    def _add_choice_comparison_text(self, img: Image.Image, draw: ImageDraw.Draw, text_data: Dict, font):
        """Add text for choice comparison format (Drake style)"""
        width, height = img.size
        
        # Rejection text (top)
        if text_data.get("rejection_text"):
            self._draw_outlined_text(
                draw, text_data["rejection_text"], 
                (width*3//4, height//4), font, anchor="mm"
            )
        
        # Approval text (bottom)
        if text_data.get("approval_text"):
            self._draw_outlined_text(
                draw, text_data["approval_text"], 
                (width*3//4, height*3//4), font, anchor="mm"
            )
    
    def _add_progression_text(self, img: Image.Image, draw: ImageDraw.Draw, text_data: Dict, font):
        """Add text for progression format (Expanding brain style)"""
        width, height = img.size
        
        positions = [
            (width*3//4, height//4),      # Top right
            (width*3//4, height*3//4),    # Bottom right
            (width//4, height//4),        # Top left
            (width//4, height*3//4)       # Bottom left
        ]
        
        levels = ["level_1", "level_2", "level_3", "level_4"]
        
        for i, level in enumerate(levels):
            if text_data.get(level) and i < len(positions):
                self._draw_outlined_text(
                    draw, text_data[level], 
                    positions[i], font, anchor="mm"
                )
    
    def _draw_outlined_text(self, draw: ImageDraw.Draw, text: str, position: tuple, font, anchor="mm"):
        """Draw text with black outline for better readability"""
        x, y = position
        
        # Draw outline
        for adj_x in range(-2, 3):
            for adj_y in range(-2, 3):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill='black', anchor=anchor)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill='white', anchor=anchor)
    
    def _calculate_font_size(self, image_size: tuple, platform: Platform) -> int:
        """Calculate appropriate font size based on image dimensions"""
        width, height = image_size
        base_size = min(width, height) // 20
        
        # Platform-specific adjustments
        if platform == Platform.TIKTOK:
            return max(40, base_size)
        elif platform == Platform.INSTAGRAM:
            return max(36, base_size)
        else:
            return max(32, base_size)
    
    def _get_platform_image_specs(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific image specifications for memes"""
        specs = {
            Platform.TIKTOK: {"dimensions": (1080, 1080)},  # Square for TikTok
            Platform.INSTAGRAM: {"dimensions": (1080, 1080)},  # Square for posts
            Platform.TWITTER: {"dimensions": (1200, 675)},  # 16:9 for Twitter
            Platform.LINKEDIN: {"dimensions": (1200, 627)},  # Professional format
            Platform.YOUTUBE: {"dimensions": (1280, 720)}  # 16:9 for thumbnails
        }
        
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    # Brand alignment methods
    async def _calculate_brand_alignment(self, meme_text: Dict, brand_voice: str) -> float:
        """Calculate how well the meme aligns with brand voice"""
        if not self.openai_client:
            return 0.75  # Default alignment score
        
        try:
            # Combine all text content
            all_text = " ".join([
                meme_text.get("top_text", ""),
                meme_text.get("bottom_text", ""),
                str(meme_text.get("format_specific", {}))
            ])
            
            prompt = f"""
            Analyze this meme text for brand voice alignment:
            
            Text: "{all_text}"
            Target brand voice: {brand_voice}
            
            Rate alignment from 0.0 to 1.0 where:
            - 1.0 = Perfect alignment with brand voice
            - 0.0 = Completely misaligned
            
            Consider tone, messaging, appropriateness, and brand consistency.
            Return only a number between 0.0 and 1.0.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except:
                return 0.75
                
        except Exception:
            return 0.75
    
    # Enhancement and optimization
    async def _enhance_for_virality(self, meme_path: str, platform: Platform, topic_analysis: Dict) -> Dict[str, Any]:
        """Enhance meme for viral potential"""
        try:
            # Apply platform-specific optimizations
            img = Image.open(meme_path)
            
            # Enhance colors for platform
            if platform == Platform.TIKTOK:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.2)
            elif platform == Platform.INSTAGRAM:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
            
            # Save enhanced version
            enhanced_path = meme_path.replace(".jpg", "_enhanced.jpg")
            img.save(enhanced_path, "JPEG", quality=95)
            
            # Calculate viral score
            viral_score = self._calculate_viral_score(topic_analysis, platform)
            
            return {
                "path": enhanced_path,
                "viral_score": viral_score,
                "optimizations": ["color_enhanced", f"platform_optimized_{platform.value}"]
            }
            
        except Exception as e:
            return {
                "path": meme_path,
                "viral_score": 0.5,
                "error": str(e)
            }
    
    def _calculate_viral_score(self, topic_analysis: Dict, platform: Platform) -> float:
        """Calculate potential viral score for meme"""
        base_score = 0.5
        
        # Add trending relevance
        base_score += topic_analysis.get("trending_score", 0) * 0.3
        
        # Add humor potential
        base_score += topic_analysis.get("humor_potential", 0) * 0.2
        
        # Add relatability
        base_score += topic_analysis.get("relatability", 0) * 0.2
        
        # Platform-specific bonus
        platform_bonus = {
            Platform.TIKTOK: 0.1,
            Platform.TWITTER: 0.08,
            Platform.INSTAGRAM: 0.06
        }.get(platform, 0.05)
        
        base_score += platform_bonus
        
        return min(1.0, base_score)
    
    # Alternative versions and brand methods (placeholder implementations)
    async def _generate_alternative_versions(self, format_info: Dict, topic: str, brand_voice: str, platform: Platform) -> List[Dict[str, Any]]:
        """Generate alternative versions of the meme"""
        # Placeholder for alternative version generation
        return [
            {"version": "alternative_1", "style": "more_casual"},
            {"version": "alternative_2", "style": "more_professional"}
        ]
    
    async def _analyze_brand_trend_relevance(self, brand_info: Dict, trend: str, platform: Platform) -> Dict[str, Any]:
        """Analyze how relevant a trend is to the brand"""
        # Placeholder implementation
        return {
            "relevance_score": 0.75,
            "brand_safety": 0.9,
            "audience_alignment": 0.8
        }
    
    async def _generate_brand_aligned_meme(self, trend: str, brand_info: Dict, platform: Platform, relevance: Dict) -> Dict[str, Any]:
        """Generate a meme that aligns with brand and trend"""
        # Use the main meme generation with brand context
        return await self.generate_trending_meme(
            trend, 
            brand_info.get("voice", "casual"), 
            platform,
            brand_info.get("target_audience", "general"),
            include_brand_elements=True
        )
    
    async def _rank_memes_by_impact(self, memes: List[Dict], brand_info: Dict, platform: Platform) -> List[Dict[str, Any]]:
        """Rank memes by potential impact"""
        # Sort by viral score and brand alignment
        return sorted(memes, key=lambda x: x.get("viral_score", 0) * x.get("brand_alignment", 0), reverse=True)
    
    async def _add_brand_elements(self, meme_image: Image.Image, platform: Platform) -> Image.Image:
        """Add subtle brand elements to meme"""
        # Placeholder for brand element addition
        # In production, this would add watermarks, logos, or brand colors
        return meme_image
    
    # Additional helper methods would be implemented here for the remaining functionality
    async def _develop_meme_series_concept(self, theme: str, count: int, platform: Platform, brand_voice: str) -> Dict[str, Any]:
        """Develop concept for meme series"""
        return {
            "concepts": [
                {"topic": f"{theme} - part {i+1}", "target_audience": "general"} 
                for i in range(count)
            ]
        }
    
    async def _suggest_series_posting_schedule(self, meme_series: List[Dict], platform: Platform) -> Dict[str, Any]:
        """Suggest optimal posting schedule for meme series"""
        return {
            "frequency": "daily",
            "optimal_times": ["12:00", "18:00", "20:00"]
        }
    
    async def _develop_series_engagement_strategy(self, meme_series: List[Dict], platform: Platform) -> Dict[str, Any]:
        """Develop engagement strategy for meme series"""
        return {
            "hashtags": ["#memeseries", "#trending"],
            "engagement_tactics": ["ask_questions", "encourage_shares"]
        }
    
    # Additional methods for reactive memes, event analysis, etc. would be implemented similarly
    
    async def _analyze_current_meme_trends(self, platform: Platform) -> Dict[str, Any]:
        """Analyze current meme trends for platform"""
        return {
            "trends": ["viral_formats", "trending_topics"],
            "popular_formats": ["drake", "expanding_brain", "woman_yelling_cat"]
        }
    
    async def _score_meme_concept(self, concept: str, trends: Dict, platform: Platform) -> Dict[str, Any]:
        """Score meme concept against current trends"""
        return {
            "overall_score": 0.8,
            "trend_score": 0.7,
            "originality_score": 0.9,
            "recommended_formats": ["drake", "expanding_brain"]
        }
    
    async def _predict_meme_engagement(self, concept: str, score: Dict, platform: Platform) -> Dict[str, Any]:
        """Predict engagement for meme concept"""
        return {
            "engagement_score": 0.75,
            "best_posting_time": "evening",
            "viral_potential": 0.8
        }
    
    async def _suggest_concept_improvements(self, concept: str, score: Dict, platform: Platform) -> List[str]:
        """Suggest improvements for meme concept"""
        return ["add more humor", "use trending format", "improve timing"]