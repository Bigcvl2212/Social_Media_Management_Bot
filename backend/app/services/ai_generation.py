"""
AI Content Generation Service
Generates videos, images, and text from prompts using OpenAI and Groq
"""

import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import openai
from groq import Groq

from app.core.config import settings


class AIContentGenerationService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    # ==================== TEXT GENERATION ====================
    
    async def generate_captions(
        self,
        content_description: str,
        platform: str,
        hashtags: bool = True,
    ) -> Dict[str, str]:
        """Generate platform-optimized captions using Groq"""
        
        prompt = f"""Create an engaging caption for a {platform} post about: {content_description}

Requirements:
- Hook with first 3 words to grab attention
- 3-5 sentences of engaging content
- Include value (education, entertainment, or inspiration)
- Include call-to-action
{f"- Include trending hashtags (max 10)" if hashtags else ""}
- Optimized for {platform} algorithm

Return JSON:
{{
    "caption": "string",
    "hashtags": ["string"],
    "posting_tips": "string"
}}"""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_script(
        self,
        topic: str,
        duration_seconds: int,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """Generate video script from topic"""
        
        words_per_second = 2.5
        target_words = int(duration_seconds * words_per_second)
        
        prompt = f"""Write a {duration_seconds}-second video script for social media about: {topic}

Style: {style}
Target word count: approximately {target_words} words
Format: [TIME] SPEAKER: TEXT

Requirements:
- Hook in first 5 seconds (make them stop scrolling)
- Clear message/value proposition
- Call-to-action at end
- Include text overlay suggestions [TEXT OVERLAY: ...]
- Natural, conversational tone
- Optimized for platforms: TikTok, Instagram Reels, YouTube Shorts

Generate professional, engaging script with proper timing."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        
        script_text = response.choices[0].message.content
        
        return {
            'script': script_text,
            'duration': duration_seconds,
            'topic': topic,
            'style': style,
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    # ==================== VIDEO GENERATION ====================
    
    async def generate_video_from_script(
        self,
        script: str,
        duration_seconds: int,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generate video from script using OpenAI Video Generation
        Note: This requires access to OpenAI's video generation API
        """
        
        # Extract key visual descriptions from script
        visual_prompt = await self._extract_visual_descriptions(script)
        
        # Generate video using OpenAI API (if available)
        try:
            response = await self.openai_client.video.generations.create(
                model="gpt-4-vision",
                prompt=visual_prompt,
                duration=min(duration_seconds, 60),  # Max 60 seconds
                quality="hd",
                style=style,
            )
            
            return {
                'video_url': response.data[0].url if response.data else None,
                'script': script,
                'status': 'generated',
                'generated_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            # Fallback: Return script with metadata
            return {
                'script': script,
                'status': 'script_ready',
                'note': 'Video generation requires additional setup',
                'generated_at': datetime.utcnow().isoformat(),
            }
    
    async def generate_video_from_audio(
        self,
        audio_path: str,
        audio_description: str,
        duration_seconds: int,
    ) -> Dict[str, Any]:
        """Generate video from audio file (podcast, voiceover, music)"""
        
        # Transcribe audio to understand content
        with open(audio_path, 'rb') as audio_file:
            transcript_response = self.groq_client.audio.transcriptions.create(
                file=(audio_path, audio_file, 'audio/mpeg'),
                model="whisper-large-v3-turbo",
            )
        
        transcript = transcript_response.text
        
        # Generate visual descriptions matching audio
        visual_prompt = f"""Create vivid visual descriptions for a {duration_seconds}-second video to accompany this audio:

Audio description: {audio_description}
Transcript: {transcript[:500]}

Provide 5-7 specific visual scenes that would complement the audio,
with timings and detailed descriptions suitable for video generation."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": visual_prompt}],
            temperature=0.8,
        )
        
        visual_descriptions = response.choices[0].message.content
        
        return {
            'audio_path': audio_path,
            'transcript': transcript,
            'visual_descriptions': visual_descriptions,
            'duration': duration_seconds,
            'status': 'ready_for_generation',
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    # ==================== IMAGE GENERATION ====================
    
    async def generate_image_from_prompt(
        self,
        prompt: str,
        style: str = "professional",
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        """Generate image from text prompt using DALL-E"""
        
        full_prompt = f"""{prompt}

Style: {style}
High quality, professional, trending on social media
Suitable for content marketing and social posts"""
        
        try:
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size=size,
                quality="hd",
                n=1,
            )
            
            return {
                'image_url': response.data[0].url,
                'prompt': prompt,
                'style': style,
                'status': 'generated',
                'generated_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    # ==================== CONTENT IDEAS ====================
    
    async def generate_content_ideas(
        self,
        topic: str,
        platform: str,
        count: int = 5,
    ) -> Dict[str, Any]:
        """Generate viral content ideas for a specific topic and platform"""
        
        prompt = f"""Generate {count} viral content ideas for {platform} about: {topic}

For each idea, provide:
1. Hook/Title (5-10 words, attention-grabbing)
2. Content type (video, image, carousel, reel)
3. Duration/Format (if applicable)
4. Key message
5. Trending elements to include
6. Estimated viral score (1-10)

Platform-specific optimization:
- TikTok: Trending sounds, quick cuts, hooks in first 3 seconds
- Instagram: Aesthetic, storytelling, relatable content
- YouTube: Educational, SEO-optimized titles, thumbnails
- Twitter/X: Timely, conversational, thread-able

Return JSON array of 5 ideas."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            response_format={"type": "json_object"}
        )
        
        ideas = json.loads(response.choices[0].message.content)
        
        return {
            'topic': topic,
            'platform': platform,
            'ideas': ideas if isinstance(ideas, list) else ideas.get('ideas', []),
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    # ==================== TRENDING ANALYSIS ====================
    
    async def analyze_trending_topics(
        self,
        platform: str,
        region: str = "global",
    ) -> Dict[str, Any]:
        """Analyze trending topics for a specific platform"""
        
        prompt = f"""What are the top 10 trending topics and hashtags on {platform} right now in {region}?

For each trend, provide:
1. Topic/Hashtag
2. Current momentum (rising, stable, declining)
3. Best content types (video, image, text, etc)
4. Estimated engagement potential (low/medium/high)
5. Recommended video length/format
6. Content angle suggestions

Return JSON with trending_topics array."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def predict_viral_potential(
        self,
        content_description: str,
        platform: str,
        target_audience: str = "general",
    ) -> Dict[str, Any]:
        """Predict viral potential of content idea"""
        
        prompt = f"""Analyze the viral potential of this content idea:

Platform: {platform}
Target Audience: {target_audience}
Content: {content_description}

Provide:
1. Viral Score (1-10)
2. Key viral factors present
3. Potential issues that could limit reach
4. Optimization recommendations (3-5)
5. Best posting time
6. Estimated reach (conservative/mid/optimistic)
7. Engagement predictions

Return JSON with detailed analysis."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    # ==================== HELPERS ====================
    
    async def _extract_visual_descriptions(self, script: str) -> str:
        """Extract visual descriptions from script for video generation"""
        
        prompt = f"""From this script, extract key visual scenes and create detailed descriptions:

Script:
{script}

Create a comprehensive visual prompt that describes:
1. Main visual elements
2. Scene transitions
3. Color palette and mood
4. Camera movements
5. Text overlays
6. Overall aesthetic

Make it suitable for AI video generation."""
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        
        return response.choices[0].message.content


# Service instance
ai_generation_service = AIContentGenerationService()
