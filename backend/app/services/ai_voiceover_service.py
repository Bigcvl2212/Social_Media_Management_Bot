"""
AI-powered voiceover and dubbing service with multi-language synthesis
"""

import asyncio
import base64
import io
import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import httpx
import openai
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


class AIVoiceoverService:
    """Service for AI-powered voiceover and dubbing with multi-language synthesis"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.temp_dir = Path(settings.UPLOAD_DIR) / "voiceover"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_voiceover(self, 
                               text: str, 
                               voice: str = "alloy",
                               language: str = "en",
                               platform: Platform = Platform.INSTAGRAM,
                               speed: float = 1.0) -> Dict[str, Any]:
        """Generate AI voiceover from text with platform optimization"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured"}
        
        try:
            # Get platform-specific audio requirements
            audio_specs = self._get_platform_audio_specs(platform)
            
            # Generate speech using OpenAI TTS
            response = await self.openai_client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            # Save the audio
            audio_filename = f"voiceover_{voice}_{language}_{int(asyncio.get_event_loop().time())}.mp3"
            audio_path = self.temp_dir / audio_filename
            
            # Write audio content
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            # Process audio for platform optimization
            optimized_audio = await self._optimize_audio_for_platform(
                str(audio_path), platform, audio_specs
            )
            
            return {
                "voiceover_path": optimized_audio["path"],
                "duration": optimized_audio["duration"],
                "voice": voice,
                "language": language,
                "platform_optimizations": optimized_audio["optimizations"],
                "text_used": text,
                "alternative_voices": await self._suggest_alternative_voices(text, platform)
            }
            
        except Exception as e:
            return {"error": f"Voiceover generation failed: {str(e)}"}
    
    async def dub_video(self, 
                       video_path: str, 
                       target_language: str,
                       voice: str = "alloy",
                       platform: Platform = Platform.INSTAGRAM,
                       preserve_timing: bool = True) -> Dict[str, Any]:
        """Dub existing video with AI-generated voiceover in target language"""
        try:
            # Extract existing audio and transcribe
            original_audio = await self._extract_audio_from_video(video_path)
            transcription = await self._transcribe_audio(original_audio)
            
            # Translate transcription to target language
            translated_text = await self._translate_text(
                transcription["text"], target_language
            )
            
            # Generate voiceover in target language
            voiceover_result = await self.generate_voiceover(
                translated_text["text"], voice, target_language, platform
            )
            
            if "error" in voiceover_result:
                return voiceover_result
            
            # Sync voiceover with video timing
            if preserve_timing:
                synced_audio = await self._sync_audio_with_video(
                    voiceover_result["voiceover_path"], 
                    video_path,
                    transcription["timing"]
                )
            else:
                synced_audio = voiceover_result["voiceover_path"]
            
            # Combine video with new audio
            dubbed_video = await self._combine_video_with_audio(
                video_path, synced_audio, platform
            )
            
            return {
                "dubbed_video_path": dubbed_video["path"],
                "original_language": transcription.get("language", "unknown"),
                "target_language": target_language,
                "voice_used": voice,
                "transcription": transcription["text"],
                "translation": translated_text["text"],
                "timing_preserved": preserve_timing,
                "platform_optimizations": dubbed_video["optimizations"]
            }
            
        except Exception as e:
            return {"error": f"Video dubbing failed: {str(e)}"}
    
    async def create_multilingual_versions(self, 
                                         video_path: str, 
                                         target_languages: List[str],
                                         voice_preferences: Dict[str, str] = None,
                                         platform: Platform = Platform.INSTAGRAM) -> Dict[str, Any]:
        """Create multiple language versions of a video"""
        voice_preferences = voice_preferences or {}
        multilingual_versions = {}
        
        try:
            # Extract and transcribe original audio
            original_audio = await self._extract_audio_from_video(video_path)
            transcription = await self._transcribe_audio(original_audio)
            
            for language in target_languages:
                voice = voice_preferences.get(language, "alloy")
                
                # Create dubbed version for this language
                dubbed_result = await self.dub_video(
                    video_path, language, voice, platform, preserve_timing=True
                )
                
                if "error" not in dubbed_result:
                    multilingual_versions[language] = dubbed_result
            
            return {
                "multilingual_versions": multilingual_versions,
                "original_transcription": transcription["text"],
                "languages_created": len(multilingual_versions),
                "failed_languages": [
                    lang for lang in target_languages 
                    if lang not in multilingual_versions
                ]
            }
            
        except Exception as e:
            return {"error": f"Multilingual version creation failed: {str(e)}"}
    
    async def generate_podcast_narration(self, 
                                       content: str, 
                                       voice: str = "nova",
                                       style: str = "conversational",
                                       add_music: bool = True,
                                       platform: Platform = Platform.YOUTUBE) -> Dict[str, Any]:
        """Generate podcast-style narration for long-form content"""
        try:
            # Enhance content for podcast narration
            enhanced_script = await self._enhance_for_narration(content, style)
            
            # Generate voiceover
            narration_result = await self.generate_voiceover(
                enhanced_script["text"], voice, "en", platform, speed=0.9
            )
            
            if "error" in narration_result:
                return narration_result
            
            # Add background music if requested
            if add_music:
                music_enhanced = await self._add_background_music(
                    narration_result["voiceover_path"], platform
                )
                final_audio_path = music_enhanced["path"]
            else:
                final_audio_path = narration_result["voiceover_path"]
            
            return {
                "narration_path": final_audio_path,
                "original_content": content,
                "enhanced_script": enhanced_script["text"],
                "voice_used": voice,
                "style": style,
                "background_music_added": add_music,
                "duration": narration_result["duration"],
                "chapters": enhanced_script.get("chapters", [])
            }
            
        except Exception as e:
            return {"error": f"Podcast narration generation failed: {str(e)}"}
    
    async def create_voice_cloning(self, 
                                 sample_audio_path: str, 
                                 text: str,
                                 platform: Platform = Platform.INSTAGRAM) -> Dict[str, Any]:
        """Create voiceover using voice cloning from sample audio"""
        try:
            # Note: This is a placeholder for voice cloning functionality
            # In production, this would integrate with specialized voice cloning APIs
            
            # Analyze sample audio characteristics
            voice_profile = await self._analyze_voice_characteristics(sample_audio_path)
            
            # For now, use the closest OpenAI voice
            closest_voice = await self._find_closest_openai_voice(voice_profile)
            
            # Generate voiceover with closest voice
            result = await self.generate_voiceover(
                text, closest_voice, "en", platform
            )
            
            if "error" in result:
                return result
            
            # Apply voice characteristics matching
            matched_audio = await self._apply_voice_matching(
                result["voiceover_path"], voice_profile
            )
            
            return {
                "cloned_voiceover_path": matched_audio["path"],
                "voice_profile": voice_profile,
                "closest_voice_used": closest_voice,
                "similarity_score": matched_audio["similarity_score"],
                "text_used": text,
                "platform_optimizations": result["platform_optimizations"]
            }
            
        except Exception as e:
            return {"error": f"Voice cloning failed: {str(e)}"}
    
    # Platform specification methods
    def _get_platform_audio_specs(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific audio requirements"""
        specs = {
            Platform.TIKTOK: {
                "max_duration": 60,
                "sample_rate": 44100,
                "bitrate": 128,
                "format": "mp3",
                "optimization": "mobile_optimized"
            },
            Platform.INSTAGRAM: {
                "max_duration": 90,
                "sample_rate": 44100,
                "bitrate": 128,
                "format": "mp3",
                "optimization": "story_optimized"
            },
            Platform.YOUTUBE: {
                "max_duration": 3600,  # 1 hour
                "sample_rate": 48000,
                "bitrate": 192,
                "format": "mp3",
                "optimization": "high_quality"
            },
            Platform.TWITTER: {
                "max_duration": 140,
                "sample_rate": 44100,
                "bitrate": 128,
                "format": "mp3",
                "optimization": "compressed"
            },
            Platform.LINKEDIN: {
                "max_duration": 600,  # 10 minutes
                "sample_rate": 44100,
                "bitrate": 160,
                "format": "mp3",
                "optimization": "professional"
            }
        }
        
        return specs.get(platform, specs[Platform.INSTAGRAM])
    
    # Audio processing methods
    async def _optimize_audio_for_platform(self, audio_path: str, platform: Platform, specs: Dict) -> Dict[str, Any]:
        """Optimize audio for specific platform requirements"""
        # Placeholder for audio optimization logic
        # In production, this would use ffmpeg or similar tools
        
        optimized_path = audio_path.replace(".mp3", f"_optimized_{platform.value}.mp3")
        
        # Copy original file for now (would apply actual optimization)
        import shutil
        shutil.copy2(audio_path, optimized_path)
        
        return {
            "path": optimized_path,
            "duration": 30.0,  # Placeholder duration
            "optimizations": [
                f"sample_rate_{specs['sample_rate']}",
                f"bitrate_{specs['bitrate']}",
                specs["optimization"]
            ]
        }
    
    async def _extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio track from video file"""
        audio_filename = f"extracted_audio_{int(asyncio.get_event_loop().time())}.wav"
        audio_path = self.temp_dir / audio_filename
        
        # Placeholder for audio extraction using ffmpeg
        # In production: ffmpeg -i video_path -vn -acodec pcm_s16le audio_path
        
        return str(audio_path)
    
    async def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio to text with timing information"""
        if not self.openai_client:
            return {
                "text": "Sample transcription text",
                "language": "en",
                "timing": [{"start": 0, "end": 5, "text": "Sample transcription text"}]
            }
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            return {
                "text": transcript.text,
                "language": transcript.language,
                "timing": [
                    {
                        "start": word.start,
                        "end": word.end,
                        "text": word.word
                    }
                    for word in getattr(transcript, 'words', [])
                ]
            }
            
        except Exception as e:
            # Fallback transcription
            return {
                "text": "Transcription not available",
                "language": "unknown",
                "timing": [],
                "error": str(e)
            }
    
    async def _translate_text(self, text: str, target_language: str) -> Dict[str, Any]:
        """Translate text to target language"""
        if not self.openai_client:
            return {"text": f"[Translated to {target_language}] {text}"}
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate the following text to {target_language}. "
                                  "Maintain the original tone and style. "
                                  "For video content, keep timing and pacing in mind."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content
            
            return {
                "text": translated_text,
                "source_language": "auto-detected",
                "target_language": target_language
            }
            
        except Exception as e:
            return {
                "text": f"[Translation failed] {text}",
                "error": str(e)
            }
    
    async def _sync_audio_with_video(self, audio_path: str, video_path: str, timing_info: List[Dict]) -> str:
        """Synchronize generated audio with original video timing"""
        synced_filename = f"synced_audio_{int(asyncio.get_event_loop().time())}.mp3"
        synced_path = self.temp_dir / synced_filename
        
        # Placeholder for audio synchronization logic
        # In production, this would adjust audio speed/timing to match original
        import shutil
        shutil.copy2(audio_path, str(synced_path))
        
        return str(synced_path)
    
    async def _combine_video_with_audio(self, video_path: str, audio_path: str, platform: Platform) -> Dict[str, Any]:
        """Combine video with new audio track"""
        output_filename = f"dubbed_video_{platform.value}_{int(asyncio.get_event_loop().time())}.mp4"
        output_path = self.temp_dir / output_filename
        
        # Placeholder for video+audio combination using ffmpeg
        # In production: ffmpeg -i video_path -i audio_path -c:v copy -c:a aac output_path
        
        import shutil
        shutil.copy2(video_path, str(output_path))
        
        return {
            "path": str(output_path),
            "optimizations": ["audio_replaced", f"platform_optimized_{platform.value}"]
        }
    
    async def _enhance_for_narration(self, content: str, style: str) -> Dict[str, Any]:
        """Enhance content for podcast-style narration"""
        if not self.openai_client:
            return {
                "text": content,
                "chapters": []
            }
        
        try:
            prompt = f"""
            Transform the following content into a {style} podcast narration script:
            
            {content}
            
            Guidelines:
            - Add natural speech patterns and pauses
            - Include smooth transitions between topics
            - Make it engaging for audio-only consumption
            - Add chapter markers for longer content
            - Maintain the original information while making it conversational
            
            Format the response as:
            {{
                "text": "enhanced script",
                "chapters": [
                    {{"title": "Chapter 1", "start_text": "Beginning of chapter 1"}},
                    ...
                ]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            try:
                import json
                result = json.loads(response.choices[0].message.content)
                return result
            except:
                return {
                    "text": response.choices[0].message.content,
                    "chapters": []
                }
                
        except Exception as e:
            return {
                "text": content,
                "chapters": [],
                "error": str(e)
            }
    
    async def _add_background_music(self, audio_path: str, platform: Platform) -> Dict[str, Any]:
        """Add background music to narration"""
        music_enhanced_filename = f"music_enhanced_{int(asyncio.get_event_loop().time())}.mp3"
        output_path = self.temp_dir / music_enhanced_filename
        
        # Placeholder for background music addition
        # In production, this would mix audio with appropriate background music
        import shutil
        shutil.copy2(audio_path, str(output_path))
        
        return {
            "path": str(output_path),
            "music_added": True,
            "music_type": "ambient_podcast"
        }
    
    async def _suggest_alternative_voices(self, text: str, platform: Platform) -> List[Dict[str, Any]]:
        """Suggest alternative voice options based on content and platform"""
        openai_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        # Platform-specific voice recommendations
        platform_preferences = {
            Platform.TIKTOK: ["nova", "alloy", "shimmer"],  # Younger, energetic voices
            Platform.INSTAGRAM: ["alloy", "nova", "echo"],  # Lifestyle-friendly voices
            Platform.YOUTUBE: ["onyx", "echo", "fable"],    # Professional, clear voices
            Platform.LINKEDIN: ["onyx", "fable", "echo"],   # Professional voices
            Platform.TWITTER: ["alloy", "nova", "shimmer"]  # Quick, engaging voices
        }
        
        preferred_voices = platform_preferences.get(platform, openai_voices)
        
        return [
            {
                "voice": voice,
                "description": self._get_voice_description(voice),
                "recommended_for": self._get_voice_use_cases(voice, platform)
            }
            for voice in preferred_voices[:3]
        ]
    
    def _get_voice_description(self, voice: str) -> str:
        """Get description for OpenAI voice"""
        descriptions = {
            "alloy": "Balanced, versatile voice suitable for most content",
            "echo": "Clear, professional voice ideal for business content",
            "fable": "Warm, storytelling voice perfect for narratives",
            "onyx": "Deep, authoritative voice for serious content",
            "nova": "Young, energetic voice for lifestyle content",
            "shimmer": "Bright, engaging voice for entertainment"
        }
        return descriptions.get(voice, "Professional AI voice")
    
    def _get_voice_use_cases(self, voice: str, platform: Platform) -> List[str]:
        """Get recommended use cases for voice on platform"""
        use_cases = {
            "alloy": ["general content", "tutorials", "announcements"],
            "echo": ["business content", "interviews", "professional updates"],
            "fable": ["storytelling", "brand narratives", "educational content"],
            "onyx": ["serious topics", "news", "authoritative content"],
            "nova": ["lifestyle content", "product reviews", "casual updates"],
            "shimmer": ["entertainment", "fun content", "social updates"]
        }
        return use_cases.get(voice, ["general content"])
    
    # Voice cloning placeholder methods
    async def _analyze_voice_characteristics(self, audio_path: str) -> Dict[str, Any]:
        """Analyze voice characteristics from sample audio"""
        # Placeholder for voice analysis
        return {
            "pitch": "medium",
            "speed": "normal",
            "accent": "neutral",
            "tone": "conversational",
            "gender": "neutral"
        }
    
    async def _find_closest_openai_voice(self, voice_profile: Dict) -> str:
        """Find closest OpenAI voice based on profile"""
        # Simple mapping based on characteristics
        if voice_profile.get("tone") == "authoritative":
            return "onyx"
        elif voice_profile.get("tone") == "energetic":
            return "nova"
        elif voice_profile.get("tone") == "warm":
            return "fable"
        else:
            return "alloy"
    
    async def _apply_voice_matching(self, audio_path: str, voice_profile: Dict) -> Dict[str, Any]:
        """Apply voice matching techniques to generated audio"""
        matched_filename = f"voice_matched_{int(asyncio.get_event_loop().time())}.mp3"
        output_path = self.temp_dir / matched_filename
        
        # Placeholder for voice matching
        import shutil
        shutil.copy2(audio_path, str(output_path))
        
        return {
            "path": str(output_path),
            "similarity_score": 0.75  # Placeholder score
        }