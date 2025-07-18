"""
Advanced AI-powered content generation service for images, videos, and text
"""

import asyncio
import base64
import io
import json
import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import httpx
import openai
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available, video processing features will be limited")
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.content import Content, ContentType, ContentStatus
from app.models.social_account import SocialPlatform as Platform


class ContentGenerationService:
    """Service for AI-powered content generation across all media types"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.temp_dir = Path(settings.UPLOAD_DIR) / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_text_content(self, 
                                  prompt: str, 
                                  platform: Platform, 
                                  content_type: str = "post",
                                  style: str = "engaging",
                                  target_audience: str = None) -> Dict[str, Any]:
        """Generate AI-powered text content optimized for specific platforms"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured"}
        
        try:
            platform_specs = self._get_text_specifications(platform, content_type)
            
            system_prompt = f"""
            You are an expert social media content creator specializing in {platform.value}.
            Create {content_type} content that is {style} and optimized for {platform.value}.
            
            Platform requirements:
            - Character limit: {platform_specs['char_limit']}
            - Style: {platform_specs['style']}
            - Key features: {platform_specs['features']}
            - Best practices: {platform_specs['best_practices']}
            
            Target audience: {target_audience or 'General social media users'}
            """
            
            user_prompt = f"""
            Create compelling {content_type} content about: {prompt}
            
            Provide:
            1. Main content text
            2. Alternative versions (3 variations)
            3. Recommended hashtags
            4. Call-to-action suggestions
            5. Engagement hooks
            6. Best posting time recommendations
            
            Format as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except:
                # Fallback parsing
                result = self._parse_text_response(content, platform)
            
            # Add platform-specific optimizations
            result["platform_optimizations"] = await self._optimize_text_for_platform(result, platform)
            
            return result
            
        except Exception as e:
            return {"error": f"Text generation failed: {str(e)}"}
    
    async def generate_image_content(self, 
                                   prompt: str, 
                                   platform: Platform,
                                   style: str = "modern",
                                   dimensions: tuple = None) -> Dict[str, Any]:
        """Generate AI-powered images with platform-specific optimizations"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured"}
        
        try:
            # Get platform-specific image requirements
            image_specs = self._get_image_specifications(platform)
            dimensions = dimensions or image_specs['dimensions']
            
            # Enhanced prompt for better results
            enhanced_prompt = f"""
            {prompt}
            
            Style: {style}, high quality, professional, {image_specs['style']}
            Optimized for {platform.value} social media
            Clean composition, vibrant colors, engaging visual
            """
            
            # Generate image with DALL-E
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=self._get_dalle_size(dimensions),
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and process the image
            processed_image = await self._download_and_process_image(
                image_url, dimensions, platform, style
            )
            
            return {
                "original_url": image_url,
                "processed_image_path": processed_image["path"],
                "dimensions": processed_image["dimensions"],
                "platform_optimizations": processed_image["optimizations"],
                "variations": await self._generate_image_variations(processed_image["path"], platform)
            }
            
        except Exception as e:
            return {"error": f"Image generation failed: {str(e)}"}
    
    async def generate_video_content(self, 
                                   concept: str, 
                                   platform: Platform,
                                   duration: int = None,
                                   style: str = "dynamic") -> Dict[str, Any]:
        """Generate AI-powered video content with platform optimization"""
        if not CV2_AVAILABLE:
            return {"error": "Video generation requires OpenCV which is not available"}
        
        try:
            # Get platform video specifications
            video_specs = self._get_video_specifications(platform)
            duration = duration or video_specs['default_duration']
            
            # For now, we'll create a sophisticated animated video from images
            # In production, this could integrate with video generation APIs
            
            # Generate multiple related images for video frames
            frames = await self._generate_video_frames(concept, platform, duration, style)
            
            # Create video from frames with effects
            video_path = await self._create_video_from_frames(
                frames, duration, video_specs, style
            )
            
            # Add platform-specific optimizations
            optimized_video = await self._optimize_video_for_platform(video_path, platform)
            
            return {
                "video_path": optimized_video["path"],
                "duration": optimized_video["duration"],
                "dimensions": optimized_video["dimensions"],
                "platform_optimizations": optimized_video["optimizations"],
                "thumbnail": optimized_video["thumbnail"],
                "alternative_versions": optimized_video["variations"]
            }
            
        except Exception as e:
            return {"error": f"Video generation failed: {str(e)}"}
    
    async def generate_meme_content(self, 
                                  text: str, 
                                  template: str = "auto",
                                  platform: Platform = Platform.INSTAGRAM) -> Dict[str, Any]:
        """Generate meme content with text overlay"""
        try:
            # Create or select meme template
            template_image = await self._get_meme_template(template)
            
            # Add text with optimal styling
            meme_image = await self._add_meme_text(template_image, text, platform)
            
            # Apply platform-specific optimizations
            optimized_meme = await self._optimize_meme_for_platform(meme_image, platform)
            
            return {
                "meme_path": optimized_meme["path"],
                "template_used": template,
                "text_applied": text,
                "platform_optimizations": optimized_meme["optimizations"]
            }
            
        except Exception as e:
            return {"error": f"Meme generation failed: {str(e)}"}
    
    async def generate_carousel_content(self, 
                                      topic: str, 
                                      platform: Platform,
                                      slide_count: int = 5) -> Dict[str, Any]:
        """Generate carousel/slideshow content for educational or storytelling"""
        try:
            # Generate content structure
            carousel_structure = await self._generate_carousel_structure(topic, slide_count, platform)
            
            # Generate individual slides
            slides = []
            for i, slide_data in enumerate(carousel_structure["slides"]):
                slide_image = await self._generate_carousel_slide(
                    slide_data, i + 1, slide_count, platform
                )
                slides.append(slide_image)
            
            return {
                "slides": slides,
                "cover_image": slides[0] if slides else None,
                "structure": carousel_structure,
                "platform_optimizations": self._get_carousel_optimizations(platform)
            }
            
        except Exception as e:
            return {"error": f"Carousel generation failed: {str(e)}"}
    
    async def generate_story_content(self, 
                                   content: str, 
                                   platform: Platform,
                                   interactive: bool = True) -> Dict[str, Any]:
        """Generate story content with interactive elements"""
        try:
            story_specs = self._get_story_specifications(platform)
            
            # Generate story frames
            story_frames = await self._generate_story_frames(content, story_specs, interactive)
            
            # Add interactive elements based on platform
            if interactive:
                story_frames = await self._add_story_interactions(story_frames, platform)
            
            return {
                "frames": story_frames,
                "duration_per_frame": story_specs["frame_duration"],
                "interactive_elements": story_frames[0].get("interactions", []) if story_frames else [],
                "platform_optimizations": story_specs["optimizations"]
            }
            
        except Exception as e:
            return {"error": f"Story generation failed: {str(e)}"}
    
    # Helper methods for content specifications
    def _get_text_specifications(self, platform: Platform, content_type: str) -> Dict[str, Any]:
        """Get text content specifications for each platform"""
        specs = {
            Platform.TIKTOK: {
                "char_limit": 2200,
                "style": "casual, trendy, hashtag-heavy",
                "features": ["trending hashtags", "challenges", "sounds"],
                "best_practices": ["hook in first line", "use trending sounds", "call-to-action"]
            },
            Platform.INSTAGRAM: {
                "char_limit": 2200,
                "style": "visual-first, storytelling, authentic",
                "features": ["hashtags", "mentions", "story integration"],
                "best_practices": ["strong first line", "storytelling", "community engagement"]
            },
            Platform.YOUTUBE: {
                "char_limit": 5000,
                "style": "descriptive, SEO-focused, informative",
                "features": ["timestamps", "links", "SEO optimization"],
                "best_practices": ["keyword optimization", "clear structure", "engagement hooks"]
            },
            Platform.TWITTER: {
                "char_limit": 280,
                "style": "concise, conversational, timely",
                "features": ["threads", "hashtags", "mentions"],
                "best_practices": ["clear message", "engagement", "trending topics"]
            },
            Platform.LINKEDIN: {
                "char_limit": 3000,
                "style": "professional, insightful, industry-focused",
                "features": ["professional networks", "industry hashtags", "thought leadership"],
                "best_practices": ["value-driven", "professional tone", "industry insights"]
            }
        }
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    def _get_image_specifications(self, platform: Platform) -> Dict[str, Any]:
        """Get image specifications for each platform"""
        specs = {
            Platform.TIKTOK: {
                "dimensions": (1080, 1920),  # 9:16
                "style": "vibrant, eye-catching, mobile-optimized"
            },
            Platform.INSTAGRAM: {
                "dimensions": (1080, 1080),  # 1:1 for posts, 1080x1920 for stories
                "style": "aesthetic, high-quality, brand-consistent"
            },
            Platform.YOUTUBE: {
                "dimensions": (1920, 1080),  # 16:9 for thumbnails
                "style": "bright, clear text, compelling visuals"
            },
            Platform.TWITTER: {
                "dimensions": (1200, 675),  # 16:9
                "style": "informative, clear, engaging"
            },
            Platform.LINKEDIN: {
                "dimensions": (1200, 627),  # ~1.91:1
                "style": "professional, clean, business-focused"
            }
        }
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    def _get_video_specifications(self, platform: Platform) -> Dict[str, Any]:
        """Get video specifications for each platform"""
        specs = {
            Platform.TIKTOK: {
                "dimensions": (1080, 1920),
                "default_duration": 15,
                "max_duration": 60,
                "fps": 30,
                "style": "fast-paced, trendy, effects-heavy"
            },
            Platform.INSTAGRAM: {
                "dimensions": (1080, 1920),  # Reels
                "default_duration": 30,
                "max_duration": 90,
                "fps": 30,
                "style": "polished, aesthetic, engaging"
            },
            Platform.YOUTUBE: {
                "dimensions": (1080, 1920),  # Shorts
                "default_duration": 30,
                "max_duration": 60,
                "fps": 30,
                "style": "informative, high-quality, engaging"
            },
            Platform.TWITTER: {
                "dimensions": (1280, 720),
                "default_duration": 30,
                "max_duration": 140,
                "fps": 30,
                "style": "informative, timely, engaging"
            },
            Platform.LINKEDIN: {
                "dimensions": (1920, 1080),
                "default_duration": 60,
                "max_duration": 600,
                "fps": 25,
                "style": "professional, informative, value-driven"
            }
        }
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    def _get_dalle_size(self, dimensions: tuple) -> str:
        """Convert dimensions to DALL-E supported sizes"""
        width, height = dimensions
        ratio = width / height
        
        if abs(ratio - 1) < 0.1:  # Square
            return "1024x1024"
        elif ratio > 1.5:  # Landscape
            return "1792x1024"
        else:  # Portrait
            return "1024x1792"
    
    async def _download_and_process_image(self, url: str, dimensions: tuple, platform: Platform, style: str) -> Dict[str, Any]:
        """Download and process AI-generated image"""
        try:
            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                image_data = response.content
            
            # Open with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Resize to target dimensions
            image = image.resize(dimensions, Image.Resampling.LANCZOS)
            
            # Apply platform-specific enhancements
            enhanced_image = await self._enhance_image_for_platform(image, platform, style)
            
            # Save processed image
            filename = f"generated_{platform.value}_{int(asyncio.get_event_loop().time())}.jpg"
            file_path = self.temp_dir / filename
            enhanced_image.save(file_path, "JPEG", quality=95)
            
            return {
                "path": str(file_path),
                "dimensions": dimensions,
                "optimizations": ["resized", "enhanced", "quality_optimized"]
            }
            
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
    
    async def _enhance_image_for_platform(self, image: Image.Image, platform: Platform, style: str) -> Image.Image:
        """Apply platform-specific image enhancements"""
        enhanced = image.copy()
        
        if platform == Platform.TIKTOK:
            # Increase saturation and contrast for TikTok
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.1)
            
        elif platform == Platform.INSTAGRAM:
            # Apply subtle filter for Instagram aesthetic
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.05)
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.1)
            
        elif platform == Platform.LINKEDIN:
            # Keep professional and clean
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)
        
        return enhanced
    
    async def _generate_image_variations(self, image_path: str, platform: Platform) -> List[Dict[str, Any]]:
        """Generate platform-specific variations of the image"""
        variations = []
        
        try:
            original = Image.open(image_path)
            
            # Different aspect ratios for the platform
            platform_variations = self._get_platform_variations(platform)
            
            for variation in platform_variations:
                var_image = original.copy()
                var_image = var_image.resize(variation["dimensions"], Image.Resampling.LANCZOS)
                
                # Save variation
                filename = f"variation_{variation['name']}_{int(asyncio.get_event_loop().time())}.jpg"
                var_path = self.temp_dir / filename
                var_image.save(var_path, "JPEG", quality=95)
                
                variations.append({
                    "name": variation["name"],
                    "path": str(var_path),
                    "dimensions": variation["dimensions"],
                    "use_case": variation["use_case"]
                })
                
        except Exception as e:
            print(f"Error generating variations: {e}")
        
        return variations
    
    def _get_platform_variations(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get different format variations for each platform"""
        variations = {
            Platform.INSTAGRAM: [
                {"name": "post", "dimensions": (1080, 1080), "use_case": "feed_post"},
                {"name": "story", "dimensions": (1080, 1920), "use_case": "story"},
                {"name": "reel", "dimensions": (1080, 1920), "use_case": "reel_cover"}
            ],
            Platform.TIKTOK: [
                {"name": "video_cover", "dimensions": (1080, 1920), "use_case": "video_thumbnail"}
            ],
            Platform.YOUTUBE: [
                {"name": "thumbnail", "dimensions": (1280, 720), "use_case": "video_thumbnail"},
                {"name": "short_cover", "dimensions": (1080, 1920), "use_case": "short_thumbnail"}
            ],
            Platform.TWITTER: [
                {"name": "post", "dimensions": (1200, 675), "use_case": "tweet_image"}
            ],
            Platform.LINKEDIN: [
                {"name": "post", "dimensions": (1200, 627), "use_case": "post_image"}
            ]
        }
        
        return variations.get(platform, [])
    
    # Placeholder methods for video generation (would integrate with video AI services)
    async def _generate_video_frames(self, concept: str, platform: Platform, duration: int, style: str) -> List[str]:
        """Generate frames for video creation"""
        # This would generate multiple related images for video frames
        return [f"frame_{i}.jpg" for i in range(duration)]
    
    async def _create_video_from_frames(self, frames: List[str], duration: int, specs: Dict, style: str) -> str:
        """Create video from generated frames"""
        # Placeholder for video creation logic using OpenCV or similar
        filename = f"generated_video_{int(asyncio.get_event_loop().time())}.mp4"
        return str(self.temp_dir / filename)
    
    async def _optimize_video_for_platform(self, video_path: str, platform: Platform) -> Dict[str, Any]:
        """Optimize video for specific platform requirements"""
        return {
            "path": video_path,
            "duration": 30,
            "dimensions": (1080, 1920),
            "optimizations": ["platform_optimized"],
            "thumbnail": video_path.replace(".mp4", "_thumb.jpg"),
            "variations": []
        }
    
    # Meme generation methods
    async def _get_meme_template(self, template: str) -> Image.Image:
        """Get or create meme template"""
        if template == "auto":
            # Create a simple template
            img = Image.new('RGB', (800, 600), color='white')
            return img
        else:
            # Load specific template (placeholder)
            img = Image.new('RGB', (800, 600), color='lightgray')
            return img
    
    async def _add_meme_text(self, template: Image.Image, text: str, platform: Platform) -> Image.Image:
        """Add text to meme template with optimal styling"""
        img = template.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add text with outline for better readability
        x, y = img.size[0] // 2, img.size[1] // 2
        
        # Draw text outline
        for adj in range(-2, 3):
            for adj2 in range(-2, 3):
                draw.text((x + adj, y + adj2), text, font=font, fill='black', anchor='mm')
        
        # Draw main text
        draw.text((x, y), text, font=font, fill='white', anchor='mm')
        
        return img
    
    async def _optimize_meme_for_platform(self, meme_image: Image.Image, platform: Platform) -> Dict[str, Any]:
        """Optimize meme for platform requirements"""
        specs = self._get_image_specifications(platform)
        optimized = meme_image.resize(specs["dimensions"], Image.Resampling.LANCZOS)
        
        filename = f"meme_{platform.value}_{int(asyncio.get_event_loop().time())}.jpg"
        file_path = self.temp_dir / filename
        optimized.save(file_path, "JPEG", quality=95)
        
        return {
            "path": str(file_path),
            "optimizations": ["resized", "quality_optimized"]
        }
    
    # Carousel generation methods
    async def _generate_carousel_structure(self, topic: str, slide_count: int, platform: Platform) -> Dict[str, Any]:
        """Generate structure for carousel content"""
        if not self.openai_client:
            return {"slides": [{"title": f"Slide {i+1}", "content": topic} for i in range(slide_count)]}
        
        try:
            prompt = f"""
            Create a {slide_count}-slide carousel about "{topic}" for {platform.value}.
            
            For each slide provide:
            1. Title
            2. Main content/message
            3. Visual description
            4. Key points (bullet format)
            
            Make it engaging and educational. Format as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"slides": [{"title": f"Slide {i+1}", "content": topic} for i in range(slide_count)]}
    
    async def _generate_carousel_slide(self, slide_data: Dict, slide_num: int, total_slides: int, platform: Platform) -> Dict[str, Any]:
        """Generate individual carousel slide"""
        # Create slide image with text overlay
        specs = self._get_image_specifications(platform)
        img = Image.new('RGB', specs["dimensions"], color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Add slide number indicator
        draw.text((50, 50), f"{slide_num}/{total_slides}", fill='gray')
        
        # Add title and content (simplified)
        title = slide_data.get("title", f"Slide {slide_num}")
        draw.text((specs["dimensions"][0]//2, 200), title, fill='black', anchor='mm')
        
        filename = f"carousel_slide_{slide_num}_{int(asyncio.get_event_loop().time())}.jpg"
        file_path = self.temp_dir / filename
        img.save(file_path, "JPEG", quality=95)
        
        return {
            "slide_number": slide_num,
            "path": str(file_path),
            "data": slide_data
        }
    
    def _get_carousel_optimizations(self, platform: Platform) -> List[str]:
        """Get carousel-specific optimizations for platform"""
        optimizations = {
            Platform.INSTAGRAM: ["square_format", "swipe_indicator", "brand_consistent"],
            Platform.LINKEDIN: ["professional_design", "value_focused", "clear_progression"],
            Platform.FACEBOOK: ["engaging_covers", "clear_navigation", "mobile_optimized"]
        }
        
        return optimizations.get(platform, ["engaging_design", "clear_navigation"])
    
    # Story generation methods
    def _get_story_specifications(self, platform: Platform) -> Dict[str, Any]:
        """Get story specifications for platform"""
        specs = {
            Platform.INSTAGRAM: {
                "dimensions": (1080, 1920),
                "frame_duration": 15,
                "max_frames": 10,
                "optimizations": ["stickers", "polls", "questions", "music"]
            },
            Platform.FACEBOOK: {
                "dimensions": (1080, 1920),
                "frame_duration": 15,
                "max_frames": 10,
                "optimizations": ["reactions", "polls", "text_overlay"]
            }
        }
        
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    async def _generate_story_frames(self, content: str, specs: Dict, interactive: bool) -> List[Dict[str, Any]]:
        """Generate story frames"""
        frames = []
        
        # Create basic story frame
        img = Image.new('RGB', specs["dimensions"], color='#667eea')
        draw = ImageDraw.Draw(img)
        draw.text((specs["dimensions"][0]//2, specs["dimensions"][1]//2), content, fill='white', anchor='mm')
        
        filename = f"story_frame_{int(asyncio.get_event_loop().time())}.jpg"
        file_path = self.temp_dir / filename
        img.save(file_path, "JPEG", quality=95)
        
        frames.append({
            "path": str(file_path),
            "duration": specs["frame_duration"],
            "interactive": interactive
        })
        
        return frames
    
    async def _add_story_interactions(self, frames: List[Dict], platform: Platform) -> List[Dict[str, Any]]:
        """Add interactive elements to story frames"""
        for frame in frames:
            if platform == Platform.INSTAGRAM:
                frame["interactions"] = ["poll", "question_sticker", "music"]
            elif platform == Platform.FACEBOOK:
                frame["interactions"] = ["reaction", "poll"]
        
        return frames
    
    def _parse_text_response(self, content: str, platform: Platform) -> Dict[str, Any]:
        """Parse AI text response when JSON parsing fails"""
        lines = content.split('\n')
        result = {
            "main_content": content[:200] + "..." if len(content) > 200 else content,
            "alternatives": [content],
            "hashtags": ["#content", f"#{platform.value}"],
            "cta": "Engage with this post!",
            "hooks": ["Check this out!"],
            "posting_time": "Peak hours for your audience"
        }
        
        return result
    
    async def _optimize_text_for_platform(self, content: Dict, platform: Platform) -> Dict[str, Any]:
        """Add platform-specific text optimizations"""
        optimizations = {
            "character_count": len(content.get("main_content", "")),
            "hashtag_count": len(content.get("hashtags", [])),
            "platform_best_practices": self._get_text_specifications(platform, "post")["best_practices"],
            "engagement_features": ["call_to_action", "question", "hashtags"]
        }
        
        return optimizations