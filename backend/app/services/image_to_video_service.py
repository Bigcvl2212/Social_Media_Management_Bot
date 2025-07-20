"""
Enhanced image-to-video generation service with advanced AI capabilities
"""

import asyncio
import base64
import io
import json
import os
import tempfile
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import httpx
import openai
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
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


class ImageToVideoService:
    """Enhanced service for AI-powered image-to-video generation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.temp_dir = Path(settings.UPLOAD_DIR) / "image_to_video"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_video_from_image(self, 
                                    image_path: str, 
                                    motion_prompt: str,
                                    platform: Platform = Platform.INSTAGRAM,
                                    duration: int = 15,
                                    style: str = "cinematic") -> Dict[str, Any]:
        """Create video from single image with AI-generated motion"""
        try:
            # Get platform specifications
            video_specs = self._get_platform_video_specs(platform)
            duration = min(duration, video_specs["max_duration"])
            
            # Load and prepare image
            image = Image.open(image_path)
            prepared_image = await self._prepare_image_for_video(image, video_specs, style)
            
            # Generate motion sequence based on prompt
            motion_sequence = await self._generate_motion_sequence(
                motion_prompt, duration, style, platform
            )
            
            # Create video frames with motion effects
            video_frames = await self._apply_motion_to_image(
                prepared_image, motion_sequence, video_specs
            )
            
            # Render final video
            video_path = await self._render_video_from_frames(
                video_frames, video_specs, platform, style
            )
            
            # Add audio if requested
            enhanced_video = await self._enhance_video_with_audio(
                video_path, motion_prompt, platform, style
            )
            
            return {
                "video_path": enhanced_video["path"],
                "motion_prompt": motion_prompt,
                "duration": duration,
                "style": style,
                "platform_optimizations": video_specs,
                "motion_effects": motion_sequence["effects"],
                "audio_added": enhanced_video["audio_added"],
                "thumbnail": await self._generate_video_thumbnail(enhanced_video["path"])
            }
            
        except Exception as e:
            return {"error": f"Image-to-video creation failed: {str(e)}"}
    
    async def create_slideshow_video(self, 
                                   image_paths: List[str], 
                                   transition_style: str = "smooth",
                                   platform: Platform = Platform.INSTAGRAM,
                                   duration_per_image: float = 3.0,
                                   add_music: bool = True) -> Dict[str, Any]:
        """Create slideshow video from multiple images"""
        try:
            video_specs = self._get_platform_video_specs(platform)
            total_duration = len(image_paths) * duration_per_image
            
            if total_duration > video_specs["max_duration"]:
                duration_per_image = video_specs["max_duration"] / len(image_paths)
                total_duration = video_specs["max_duration"]
            
            # Process all images
            processed_images = []
            for image_path in image_paths:
                image = Image.open(image_path)
                processed = await self._prepare_image_for_video(image, video_specs, "slideshow")
                processed_images.append(processed)
            
            # Generate transitions between images
            transitions = await self._generate_image_transitions(
                processed_images, transition_style, duration_per_image
            )
            
            # Create video frames
            video_frames = await self._create_slideshow_frames(
                processed_images, transitions, video_specs
            )
            
            # Render video
            video_path = await self._render_video_from_frames(
                video_frames, video_specs, platform, "slideshow"
            )
            
            # Add background music if requested
            if add_music:
                music_enhanced = await self._add_slideshow_music(video_path, platform, total_duration)
                final_video_path = music_enhanced["path"]
            else:
                final_video_path = video_path
            
            return {
                "slideshow_video_path": final_video_path,
                "image_count": len(image_paths),
                "duration_per_image": duration_per_image,
                "total_duration": total_duration,
                "transition_style": transition_style,
                "music_added": add_music,
                "thumbnail": await self._generate_video_thumbnail(final_video_path)
            }
            
        except Exception as e:
            return {"error": f"Slideshow creation failed: {str(e)}"}
    
    async def create_text_to_image_video(self, 
                                       text_prompt: str, 
                                       motion_description: str,
                                       platform: Platform = Platform.INSTAGRAM,
                                       style: str = "realistic",
                                       duration: int = 15) -> Dict[str, Any]:
        """Create video by first generating image from text, then animating it"""
        try:
            # Generate base image from text
            image_result = await self._generate_image_from_text(text_prompt, platform, style)
            
            if "error" in image_result:
                return image_result
            
            # Create video from generated image
            video_result = await self.create_video_from_image(
                image_result["image_path"],
                motion_description,
                platform,
                duration,
                style
            )
            
            if "error" in video_result:
                return video_result
            
            return {
                "text_to_video_path": video_result["video_path"],
                "text_prompt": text_prompt,
                "motion_description": motion_description,
                "generated_image_path": image_result["image_path"],
                "style": style,
                "duration": duration,
                "creation_steps": [
                    "text_to_image",
                    "image_to_video", 
                    "motion_application",
                    "platform_optimization"
                ]
            }
            
        except Exception as e:
            return {"error": f"Text-to-image-video creation failed: {str(e)}"}
    
    async def create_parallax_video(self, 
                                  image_path: str, 
                                  depth_layers: int = 3,
                                  platform: Platform = Platform.INSTAGRAM,
                                  movement_speed: str = "slow") -> Dict[str, Any]:
        """Create parallax motion video effect from single image"""
        try:
            if not CV2_AVAILABLE:
                return {"error": "Parallax video creation requires OpenCV"}
            
            # Load image
            image = cv2.imread(image_path)
            height, width = image.shape[:2]
            
            # Get platform specs
            video_specs = self._get_platform_video_specs(platform)
            
            # Create depth layers
            layers = await self._create_depth_layers(image, depth_layers)
            
            # Generate parallax motion
            parallax_frames = await self._generate_parallax_motion(
                layers, movement_speed, video_specs
            )
            
            # Render final video
            video_path = await self._render_video_from_frames(
                parallax_frames, video_specs, platform, "parallax"
            )
            
            return {
                "parallax_video_path": video_path,
                "depth_layers": depth_layers,
                "movement_speed": movement_speed,
                "original_image": image_path,
                "platform_optimizations": video_specs["optimizations"]
            }
            
        except Exception as e:
            return {"error": f"Parallax video creation failed: {str(e)}"}
    
    async def create_morph_video(self, 
                               start_image_path: str, 
                               end_image_path: str,
                               steps: int = 30,
                               platform: Platform = Platform.INSTAGRAM) -> Dict[str, Any]:
        """Create morphing video between two images"""
        try:
            if not CV2_AVAILABLE:
                return {"error": "Morph video creation requires OpenCV"}
            
            # Load images
            start_img = cv2.imread(start_image_path)
            end_img = cv2.imread(end_image_path)
            
            # Get platform specs
            video_specs = self._get_platform_video_specs(platform)
            
            # Resize images to match
            target_size = video_specs["dimensions"]
            start_img = cv2.resize(start_img, target_size)
            end_img = cv2.resize(end_img, target_size)
            
            # Generate morph frames
            morph_frames = await self._generate_morph_frames(start_img, end_img, steps)
            
            # Render video
            video_path = await self._render_video_from_frames(
                morph_frames, video_specs, platform, "morph"
            )
            
            return {
                "morph_video_path": video_path,
                "start_image": start_image_path,
                "end_image": end_image_path,
                "morph_steps": steps,
                "duration": len(morph_frames) / video_specs["fps"]
            }
            
        except Exception as e:
            return {"error": f"Morph video creation failed: {str(e)}"}
    
    async def create_zoom_effect_video(self, 
                                     image_path: str, 
                                     zoom_type: str = "zoom_in",
                                     focus_point: Tuple[float, float] = (0.5, 0.5),
                                     platform: Platform = Platform.INSTAGRAM,
                                     duration: int = 10) -> Dict[str, Any]:
        """Create zoom effect video from static image"""
        try:
            if not CV2_AVAILABLE:
                return {"error": "Zoom effect video creation requires OpenCV"}
            
            # Load image
            image = cv2.imread(image_path)
            video_specs = self._get_platform_video_specs(platform)
            
            # Generate zoom frames
            zoom_frames = await self._generate_zoom_frames(
                image, zoom_type, focus_point, duration, video_specs
            )
            
            # Render video
            video_path = await self._render_video_from_frames(
                zoom_frames, video_specs, platform, "zoom_effect"
            )
            
            return {
                "zoom_video_path": video_path,
                "zoom_type": zoom_type,
                "focus_point": focus_point,
                "duration": duration,
                "frame_count": len(zoom_frames)
            }
            
        except Exception as e:
            return {"error": f"Zoom effect video creation failed: {str(e)}"}
    
    # Platform specifications
    def _get_platform_video_specs(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific video specifications"""
        specs = {
            Platform.TIKTOK: {
                "dimensions": (1080, 1920),
                "max_duration": 60,
                "fps": 30,
                "format": "mp4",
                "optimizations": ["mobile_first", "vertical_focus", "quick_loading"]
            },
            Platform.INSTAGRAM: {
                "dimensions": (1080, 1920),  # Reels format
                "max_duration": 90,
                "fps": 30,
                "format": "mp4",
                "optimizations": ["aesthetic_quality", "smooth_motion", "engaging_start"]
            },
            Platform.YOUTUBE: {
                "dimensions": (1080, 1920),  # Shorts format
                "max_duration": 60,
                "fps": 30,
                "format": "mp4",
                "optimizations": ["high_quality", "retention_focused", "thumbnail_friendly"]
            },
            Platform.TWITTER: {
                "dimensions": (1280, 720),
                "max_duration": 140,
                "fps": 30,
                "format": "mp4",
                "optimizations": ["fast_loading", "clear_messaging", "loop_friendly"]
            },
            Platform.LINKEDIN: {
                "dimensions": (1920, 1080),
                "max_duration": 600,
                "fps": 25,
                "format": "mp4",
                "optimizations": ["professional_quality", "business_focused", "clear_audio"]
            }
        }
        
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    # Image processing methods
    async def _prepare_image_for_video(self, image: Image.Image, video_specs: Dict, style: str) -> Image.Image:
        """Prepare image for video creation with platform optimization"""
        # Resize to video dimensions
        target_size = video_specs["dimensions"]
        
        # Maintain aspect ratio and crop/pad as needed
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        else:
            # Image is taller, crop height
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        
        # Resize to exact dimensions
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Apply style-specific enhancements
        if style == "cinematic":
            image = self._apply_cinematic_look(image)
        elif style == "vibrant":
            image = self._apply_vibrant_enhancement(image)
        elif style == "vintage":
            image = self._apply_vintage_filter(image)
        
        return image
    
    def _apply_cinematic_look(self, image: Image.Image) -> Image.Image:
        """Apply cinematic color grading and effects"""
        # Slight saturation increase
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # Slight contrast increase
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Slight warmth
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _apply_vibrant_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply vibrant color enhancement"""
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image
    
    def _apply_vintage_filter(self, image: Image.Image) -> Image.Image:
        """Apply vintage film look"""
        # Reduce saturation slightly
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.8)
        
        # Add warm tone
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.95)
        
        return image
    
    # Motion generation methods
    async def _generate_motion_sequence(self, motion_prompt: str, duration: int, style: str, platform: Platform) -> Dict[str, Any]:
        """Generate motion sequence instructions from prompt"""
        if not self.openai_client:
            return {
                "effects": ["zoom_in", "pan_right"],
                "timing": [{"effect": "zoom_in", "start": 0, "end": duration//2}],
                "style": style
            }
        
        try:
            prompt = f"""
            Create a motion sequence for a {duration}-second video based on this description: "{motion_prompt}"
            
            Platform: {platform.value}
            Style: {style}
            
            Generate a sequence of motion effects with timing. Choose from:
            - zoom_in, zoom_out
            - pan_left, pan_right, pan_up, pan_down
            - rotate_cw, rotate_ccw
            - fade_in, fade_out
            - shake, smooth_motion
            
            Return as JSON with effects, timing, and transitions.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            try:
                motion_data = json.loads(response.choices[0].message.content)
                return motion_data
            except:
                # Fallback motion sequence
                return {
                    "effects": ["zoom_in", "pan_right"],
                    "timing": [
                        {"effect": "zoom_in", "start": 0, "end": duration//2},
                        {"effect": "pan_right", "start": duration//2, "end": duration}
                    ],
                    "style": style
                }
                
        except Exception as e:
            return {
                "effects": ["zoom_in"],
                "timing": [{"effect": "zoom_in", "start": 0, "end": duration}],
                "style": style,
                "error": str(e)
            }
    
    async def _apply_motion_to_image(self, image: Image.Image, motion_sequence: Dict, video_specs: Dict) -> List:
        """Apply motion effects to create video frames"""
        if not CV2_AVAILABLE:
            # Return static frames
            cv_image = np.array(image)
            frame_count = int(video_specs["fps"] * 15)  # 15 second default
            return [cv_image] * frame_count
        
        frames = []
        fps = video_specs["fps"]
        
        # Convert PIL to OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        height, width = cv_image.shape[:2]
        
        # Process each motion effect
        for motion in motion_sequence.get("timing", []):
            effect = motion["effect"]
            start_time = motion["start"]
            end_time = motion["end"]
            duration = end_time - start_time
            effect_frames = int(fps * duration)
            
            if effect == "zoom_in":
                frames.extend(self._create_zoom_frames(cv_image, effect_frames, "in"))
            elif effect == "zoom_out":
                frames.extend(self._create_zoom_frames(cv_image, effect_frames, "out"))
            elif effect.startswith("pan_"):
                direction = effect.split("_")[1]
                frames.extend(self._create_pan_frames(cv_image, effect_frames, direction))
            else:
                # Default: static frames
                frames.extend([cv_image] * effect_frames)
        
        return frames
    
    def _create_zoom_frames(self, image, frame_count: int, direction: str) -> List:
        """Create zoom effect frames"""
        frames = []
        height, width = image.shape[:2]
        
        if direction == "in":
            zoom_factors = np.linspace(1.0, 1.5, frame_count)
        else:
            zoom_factors = np.linspace(1.5, 1.0, frame_count)
        
        for zoom in zoom_factors:
            # Calculate crop size
            crop_height = int(height / zoom)
            crop_width = int(width / zoom)
            
            # Center crop
            start_y = (height - crop_height) // 2
            start_x = (width - crop_width) // 2
            
            cropped = image[start_y:start_y + crop_height, start_x:start_x + crop_width]
            zoomed = cv2.resize(cropped, (width, height))
            frames.append(zoomed)
        
        return frames
    
    def _create_pan_frames(self, image, frame_count: int, direction: str) -> List:
        """Create panning effect frames"""
        frames = []
        height, width = image.shape[:2]
        
        # Scale image up for panning
        scale_factor = 1.2
        scaled_image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)))
        scaled_height, scaled_width = scaled_image.shape[:2]
        
        if direction == "right":
            x_positions = np.linspace(0, scaled_width - width, frame_count).astype(int)
            y_pos = (scaled_height - height) // 2
            for x in x_positions:
                cropped = scaled_image[y_pos:y_pos + height, x:x + width]
                frames.append(cropped)
        elif direction == "left":
            x_positions = np.linspace(scaled_width - width, 0, frame_count).astype(int)
            y_pos = (scaled_height - height) // 2
            for x in x_positions:
                cropped = scaled_image[y_pos:y_pos + height, x:x + width]
                frames.append(cropped)
        # Add other directions as needed
        
        return frames
    
    # Advanced video creation methods
    async def _generate_image_from_text(self, text_prompt: str, platform: Platform, style: str) -> Dict[str, Any]:
        """Generate image from text using AI"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured"}
        
        try:
            # Get platform image specs
            video_specs = self._get_platform_video_specs(platform)
            dimensions = video_specs["dimensions"]
            
            # Enhance prompt for video creation
            enhanced_prompt = f"""
            {text_prompt}
            
            Style: {style}, high quality, video-ready composition
            Optimized for {platform.value}
            Clear focal point, good for motion effects
            """
            
            # Generate image
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=self._get_dalle_size(dimensions),
                quality="hd",
                n=1
            )
            
            # Download and save image
            image_url = response.data[0].url
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                image_data = response.content
            
            # Save image
            filename = f"generated_{platform.value}_{int(asyncio.get_event_loop().time())}.jpg"
            image_path = self.temp_dir / filename
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            return {
                "image_path": str(image_path),
                "text_prompt": text_prompt,
                "enhanced_prompt": enhanced_prompt
            }
            
        except Exception as e:
            return {"error": f"Image generation failed: {str(e)}"}
    
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
    
    # Advanced motion effects
    async def _create_depth_layers(self, image, layer_count: int) -> List:
        """Create depth layers for parallax effect"""
        if not CV2_AVAILABLE:
            return [image] * layer_count
        
        layers = []
        
        # Foreground layer (original)
        layers.append(image)
        
        # Middle layers (slightly blurred)
        for i in range(1, layer_count - 1):
            blur_amount = i * 2
            blurred = cv2.GaussianBlur(image, (blur_amount * 2 + 1, blur_amount * 2 + 1), blur_amount)
            layers.append(blurred)
        
        # Background layer (most blurred)
        if layer_count > 1:
            bg_blur = layer_count * 3
            background = cv2.GaussianBlur(image, (bg_blur * 2 + 1, bg_blur * 2 + 1), bg_blur)
            layers.append(background)
        
        return layers
    
    async def _generate_parallax_motion(self, layers: List, speed: str, video_specs: Dict) -> List:
        """Generate parallax motion frames"""
        if not CV2_AVAILABLE:
            return layers[:1] * 30  # Return static frames
        
        frames = []
        frame_count = video_specs["fps"] * 10  # 10 seconds
        
        speed_multiplier = {"slow": 0.5, "medium": 1.0, "fast": 2.0}.get(speed, 1.0)
        
        for frame_idx in range(frame_count):
            composite_frame = np.zeros_like(layers[0])
            
            for layer_idx, layer in enumerate(layers):
                # Calculate movement offset for this layer
                movement_factor = (layer_idx + 1) * speed_multiplier
                offset_x = int((frame_idx * movement_factor) % layer.shape[1])
                
                # Create shifted version of layer
                shifted_layer = np.roll(layer, offset_x, axis=1)
                
                # Blend layers
                if layer_idx == 0:
                    composite_frame = shifted_layer
                else:
                    alpha = 0.7 ** layer_idx
                    composite_frame = cv2.addWeighted(composite_frame, 1, shifted_layer, alpha, 0)
            
            frames.append(composite_frame)
        
        return frames
    
    async def _generate_morph_frames(self, start_img, end_img, steps: int) -> List:
        """Generate morphing frames between two images"""
        if not CV2_AVAILABLE:
            return [start_img, end_img]
        
        frames = []
        
        for i in range(steps):
            alpha = i / (steps - 1)
            morphed = cv2.addWeighted(start_img, 1 - alpha, end_img, alpha, 0)
            frames.append(morphed)
        
        return frames
    
    async def _generate_zoom_frames(self, image, zoom_type: str, focus_point: Tuple[float, float], duration: int, video_specs: Dict) -> List:
        """Generate zoom effect frames"""
        if not CV2_AVAILABLE:
            return [image] * 30
        
        frames = []
        frame_count = video_specs["fps"] * duration
        height, width = image.shape[:2]
        
        # Calculate focus point in pixels
        focus_x = int(focus_point[0] * width)
        focus_y = int(focus_point[1] * height)
        
        if zoom_type == "zoom_in":
            zoom_factors = np.linspace(1.0, 2.0, frame_count)
        else:
            zoom_factors = np.linspace(2.0, 1.0, frame_count)
        
        for zoom in zoom_factors:
            # Calculate crop size
            crop_width = int(width / zoom)
            crop_height = int(height / zoom)
            
            # Calculate crop position centered on focus point
            start_x = max(0, min(width - crop_width, focus_x - crop_width // 2))
            start_y = max(0, min(height - crop_height, focus_y - crop_height // 2))
            
            # Crop and resize
            cropped = image[start_y:start_y + crop_height, start_x:start_x + crop_width]
            zoomed = cv2.resize(cropped, (width, height))
            frames.append(zoomed)
        
        return frames
    
    # Video rendering methods
    async def _render_video_from_frames(self, frames: List, video_specs: Dict, platform: Platform, style: str) -> str:
        """Render final video from frames"""
        if not CV2_AVAILABLE or not frames:
            # Create placeholder video file
            placeholder_path = self.temp_dir / f"placeholder_{platform.value}_{int(asyncio.get_event_loop().time())}.mp4"
            placeholder_path.touch()
            return str(placeholder_path)
        
        output_filename = f"video_{platform.value}_{style}_{int(asyncio.get_event_loop().time())}.mp4"
        output_path = self.temp_dir / output_filename
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = video_specs["fps"]
        dimensions = video_specs["dimensions"]
        
        out = cv2.VideoWriter(str(output_path), fourcc, fps, dimensions)
        
        for frame in frames:
            # Ensure frame is correct size
            if frame.shape[:2] != (dimensions[1], dimensions[0]):
                frame = cv2.resize(frame, dimensions)
            out.write(frame)
        
        out.release()
        
        return str(output_path)
    
    # Audio enhancement methods
    async def _enhance_video_with_audio(self, video_path: str, motion_prompt: str, platform: Platform, style: str) -> Dict[str, Any]:
        """Add appropriate audio to generated video"""
        # For now, return the video without audio enhancement
        # In production, this would add background music or sound effects
        return {
            "path": video_path,
            "audio_added": False,
            "audio_type": None
        }
    
    async def _add_slideshow_music(self, video_path: str, platform: Platform, duration: float) -> Dict[str, Any]:
        """Add background music to slideshow video"""
        # Placeholder for music addition
        # In production, this would use ffmpeg to add background music
        return {
            "path": video_path,
            "music_added": True,
            "music_type": "ambient_slideshow"
        }
    
    async def _generate_video_thumbnail(self, video_path: str) -> str:
        """Generate thumbnail for video"""
        thumbnail_filename = f"thumbnail_{int(asyncio.get_event_loop().time())}.jpg"
        thumbnail_path = self.temp_dir / thumbnail_filename
        
        if CV2_AVAILABLE:
            # Extract first frame as thumbnail
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(str(thumbnail_path), frame)
            cap.release()
        else:
            # Create placeholder thumbnail
            thumbnail_path.touch()
        
        return str(thumbnail_path)
    
    # Slideshow-specific methods
    async def _generate_image_transitions(self, images: List[Image.Image], style: str, duration: float) -> List[Dict[str, Any]]:
        """Generate transition effects between images"""
        transitions = []
        
        for i in range(len(images) - 1):
            if style == "smooth":
                transitions.append({
                    "type": "crossfade",
                    "duration": 0.5,
                    "from_image": i,
                    "to_image": i + 1
                })
            elif style == "dynamic":
                transitions.append({
                    "type": "slide",
                    "duration": 0.3,
                    "direction": "left" if i % 2 == 0 else "right",
                    "from_image": i,
                    "to_image": i + 1
                })
            else:
                transitions.append({
                    "type": "fade",
                    "duration": 0.2,
                    "from_image": i,
                    "to_image": i + 1
                })
        
        return transitions
    
    async def _create_slideshow_frames(self, images: List[Image.Image], transitions: List[Dict], video_specs: Dict) -> List:
        """Create frames for slideshow video with transitions"""
        if not CV2_AVAILABLE:
            # Convert PIL images to numpy arrays for fallback
            return [np.array(img) for img in images]
        
        frames = []
        fps = video_specs["fps"]
        
        for i, image in enumerate(images):
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Add static frames for this image (3 seconds)
            static_frames = int(fps * 3)
            frames.extend([cv_image] * static_frames)
            
            # Add transition frames if not last image
            if i < len(transitions):
                transition = transitions[i]
                transition_frames = self._create_transition_frames(
                    cv_image, 
                    cv2.cvtColor(np.array(images[i + 1]), cv2.COLOR_RGB2BGR),
                    transition,
                    fps
                )
                frames.extend(transition_frames)
        
        return frames
    
    def _create_transition_frames(self, img1, img2, transition: Dict, fps: int) -> List:
        """Create transition frames between two images"""
        if not CV2_AVAILABLE:
            return [img1, img2]
        
        frame_count = int(fps * transition["duration"])
        frames = []
        
        if transition["type"] == "crossfade":
            for i in range(frame_count):
                alpha = i / (frame_count - 1)
                blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
                frames.append(blended)
        elif transition["type"] == "slide":
            # Simple slide transition (placeholder)
            for i in range(frame_count):
                alpha = i / (frame_count - 1)
                blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
                frames.append(blended)
        else:
            # Default fade
            for i in range(frame_count):
                alpha = i / (frame_count - 1)
                blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
                frames.append(blended)
        
        return frames