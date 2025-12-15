"""
Enhanced Content Processing Service
Handles video clipping, image editing, and AI content generation
"""

import os
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import shutil

import cv2
import numpy as np
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from groq import Groq

from app.models.content import Content, ContentType, ContentStatus
from app.core.config import settings


class VideoProcessingService:
    """Service for video processing and clip detection"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.upload_dir = Path(settings.UPLOAD_DIR) / "videos"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_video(
        self, 
        file_path: str, 
        content_id: str
    ) -> Dict[str, Any]:
        """
        Process video: detect scenes, extract clips, generate metadata
        
        Returns: {
            'clips': [
                {
                    'id': str,
                    'start_time': float,
                    'end_time': float,
                    'duration': int,
                    'title': str,
                    'viral_score': float,
                    'scene_description': str,
                    'aspects': ['9:16', '16:9', '1:1']
                },
                ...
            ],
            'total_duration': float,
            'analysis': {...}
        }
        """
        try:
            # Step 1: Extract metadata and audio
            metadata = self._get_video_metadata(file_path)
            audio_path = await self._extract_audio(file_path)
            
            # Step 2: Transcribe audio with Whisper
            transcript = await self._transcribe_audio(audio_path)
            
            # Step 3: Detect scenes using OpenCV
            scenes = self._detect_scenes(file_path)
            
            # Step 4: Analyze each scene with Groq
            clips = []
            for i, scene in enumerate(scenes):
                clip_analysis = await self._analyze_scene(
                    scene, 
                    transcript,
                    i
                )
                
                clip_data = {
                    'id': f"{content_id}_clip_{i}",
                    'start_time': scene['start'],
                    'end_time': scene['end'],
                    'duration': int(scene['end'] - scene['start']),
                    'title': clip_analysis.get('title', f'Clip {i+1}'),
                    'viral_score': clip_analysis.get('viral_score', 5.0),
                    'scene_description': clip_analysis.get('description', ''),
                    'aspects': ['9:16', '16:9', '1:1'],
                    'keyframes': scene.get('keyframes', []),
                }
                clips.append(clip_data)
            
            # Step 5: Generate video summary
            summary = await self._generate_video_summary(transcript, clips)
            
            return {
                'clips': clips,
                'total_duration': metadata['duration'],
                'analysis': {
                    'transcript': transcript,
                    'summary': summary,
                    'scene_count': len(scenes),
                    'recommended_clip_count': min(len(clips), 5),
                }
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")
    
    def _get_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video metadata using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'error', '-show_format', '-show_streams',
            '-print_json', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        duration = float(data['format'].get('duration', 0))
        width = int(data['streams'][0].get('width', 1920))
        height = int(data['streams'][0].get('height', 1080))
        fps = eval(data['streams'][0].get('r_frame_rate', '30/1'))
        
        return {
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps,
            'codec': data['streams'][0].get('codec_name', 'h264'),
        }
    
    async def _extract_audio(self, video_path: str) -> str:
        """Extract audio from video using FFmpeg"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_path = tmp.name
        
        cmd = [
            'ffmpeg', '-i', video_path, '-q:a', '9', '-n',
            audio_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return audio_path
    
    async def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Groq Whisper integration"""
        with open(audio_path, 'rb') as f:
            transcript_obj = self.groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), f, 'audio/wav'),
                model='whisper-large-v3-turbo',
            )
        return transcript_obj.text
    
    def _detect_scenes(self, video_path: str, threshold: float = 27.0) -> List[Dict]:
        """
        Detect scene changes in video using OpenCV
        Returns list of detected scenes with start/end times
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        scenes = []
        prev_frame = None
        scene_start = 0
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # Compare frames for scene change
                diff = cv2.absdiff(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY),
                                  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                mean_diff = np.mean(diff)
                
                if mean_diff > threshold:
                    # Scene change detected
                    scene_end = frame_idx / fps
                    if scene_end - scene_start > 2:  # Minimum clip length: 2 seconds
                        scenes.append({
                            'start': scene_start,
                            'end': scene_end,
                            'keyframes': [scene_start, (scene_start + scene_end) / 2, scene_end],
                        })
                    scene_start = scene_end
            
            prev_frame = frame.copy()
            frame_idx += 1
        
        cap.release()
        
        # Add final scene
        if frame_idx / fps - scene_start > 2:
            scenes.append({
                'start': scene_start,
                'end': frame_idx / fps,
                'keyframes': [scene_start, (scene_start + frame_idx / fps) / 2, frame_idx / fps],
            })
        
        return scenes
    
    async def _analyze_scene(
        self, 
        scene: Dict, 
        transcript: str,
        scene_idx: int
    ) -> Dict[str, Any]:
        """Analyze scene with Groq AI to determine viral potential and title"""
        prompt = f"""Analyze this video scene (#{scene_idx + 1}, from {scene['start']:.1f}s to {scene['end']:.1f}s):

Transcript excerpt: "{transcript[:500]}"

Based on the timing and transcript, determine:
1. A catchy 5-10 word title for this clip (make it viral-friendly)
2. Viral potential score (1-10, where 10 is extremely viral)
3. Best aspect ratio: vertical (9:16), horizontal (16:9), or square (1:1)
4. One sentence description of key content

Return JSON:
{{
    "title": "string",
    "viral_score": number,
    "aspect_ratio": "9:16|16:9|1:1",
    "description": "string"
}}"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # Fallback response
            return {
                'title': f'Clip {scene_idx + 1}',
                'viral_score': 5.0,
                'aspect_ratio': '9:16',
                'description': 'Video clip'
            }
    
    async def _generate_video_summary(
        self, 
        transcript: str, 
        clips: List[Dict]
    ) -> str:
        """Generate AI summary of video content"""
        prompt = f"""Summarize this video transcript in 2-3 sentences, highlighting the main topic and why it would be engaging on social media:

Transcript:
{transcript[:2000]}

Return only the summary, no JSON."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        return response.choices[0].message.content


class ImageProcessingService:
    """Service for image editing and optimization"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR) / "images"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def apply_filter(
        self,
        image_path: str,
        filter_name: str,
    ) -> str:
        """Apply trending filter to image"""
        img = cv2.imread(image_path)
        
        if filter_name == 'vintage':
            img = self._apply_vintage_filter(img)
        elif filter_name == 'neon':
            img = self._apply_neon_filter(img)
        elif filter_name == 'cinematic':
            img = self._apply_cinematic_filter(img)
        elif filter_name == 'warm':
            img = self._apply_warm_filter(img)
        elif filter_name == 'cool':
            img = self._apply_cool_filter(img)
        
        output_path = image_path.replace('.jpg', f'_{filter_name}.jpg')
        cv2.imwrite(output_path, img)
        return output_path
    
    def _apply_vintage_filter(self, img):
        """Apply vintage film filter"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img[:, :, 0] = cv2.add(img[:, :, 0], 20)  # Increase blue channel
        return img
    
    def _apply_neon_filter(self, img):
        """Apply neon/vibrant filter"""
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        a = cv2.add(a, 20)
        b = cv2.add(b, 20)
        img = cv2.merge([l, a, b])
        img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
        return cv2.convertScaleAbs(img, alpha=1.2, beta=0)
    
    def _apply_cinematic_filter(self, img):
        """Apply cinematic/desaturated look"""
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        img_hsv[:, :, 1] = img_hsv[:, :, 1] * 0.7  # Reduce saturation
        img = cv2.cvtColor(cv2.convertScaleAbs(img_hsv), cv2.COLOR_HSV2BGR)
        return img
    
    def _apply_warm_filter(self, img):
        """Apply warm color filter"""
        img[:, :, 0] = cv2.subtract(img[:, :, 0], 20)  # Reduce blue
        img[:, :, 2] = cv2.add(img[:, :, 2], 20)  # Increase red
        return img
    
    def _apply_cool_filter(self, img):
        """Apply cool color filter"""
        img[:, :, 0] = cv2.add(img[:, :, 0], 20)  # Increase blue
        img[:, :, 2] = cv2.subtract(img[:, :, 2], 20)  # Reduce red
        return img
    
    async def add_text_overlay(
        self,
        image_path: str,
        text: str,
        position: str = 'center',
        font_size: int = 48,
        color: tuple = (255, 255, 255),
    ) -> str:
        """Add text overlay to image"""
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        font = cv2.FONT_HERSHEY_BOLD
        font_scale = font_size / 30
        thickness = int(font_scale * 2)
        
        # Calculate text position
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        if position == 'center':
            x = (width - text_size[0]) // 2
            y = (height - text_size[1]) // 2
        elif position == 'bottom':
            x = (width - text_size[0]) // 2
            y = height - text_size[1] - 20
        elif position == 'top':
            x = (width - text_size[0]) // 2
            y = 20 + text_size[1]
        
        # Add text with background for better readability
        cv2.rectangle(img, (x - 5, y - text_size[1] - 5),
                     (x + text_size[0] + 5, y + 5),
                     (0, 0, 0), -1)
        cv2.putText(img, text, (x, y), font, font_scale, color, thickness)
        
        output_path = image_path.replace('.jpg', '_text.jpg')
        cv2.imwrite(output_path, img)
        return output_path
    
    async def optimize_for_platform(
        self,
        image_path: str,
        platform: str,
    ) -> str:
        """Optimize image for specific platform (resize, crop, etc)"""
        img = cv2.imread(image_path)
        
        # Platform-specific dimensions
        dimensions = {
            'instagram_post': (1080, 1080),
            'instagram_story': (1080, 1920),
            'tiktok': (1080, 1920),
            'facebook': (1200, 628),
            'twitter': (1200, 675),
        }
        
        target_width, target_height = dimensions.get(f'{platform}_post', (1080, 1080))
        
        # Resize with aspect ratio preservation
        height, width = img.shape[:2]
        aspect = width / height
        target_aspect = target_width / target_height
        
        if aspect > target_aspect:
            new_width = int(target_height * aspect)
            new_height = target_height
        else:
            new_width = target_width
            new_height = int(target_width / aspect)
        
        img = cv2.resize(img, (new_width, new_height))
        
        # Center crop to target dimensions
        x = (new_width - target_width) // 2
        y = (new_height - target_height) // 2
        img = img[y:y+target_height, x:x+target_width]
        
        output_path = image_path.replace('.jpg', f'_{platform}.jpg')
        cv2.imwrite(output_path, img)
        return output_path


def get_video_service() -> VideoProcessingService:
    return VideoProcessingService()


def get_image_service() -> ImageProcessingService:
    return ImageProcessingService()
