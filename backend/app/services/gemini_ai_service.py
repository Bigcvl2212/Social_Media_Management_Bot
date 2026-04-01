"""
Gemini AI Content Generation Service
Uses Google Gemini for text, Gemini Flash Image for images, and Veo 3 for video.
"""

import asyncio
import io
import json
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types
from PIL import Image

from app.core.config import settings
from app.services.gym_context_provider import GymContextProvider

import re
import urllib.request
import urllib.error
import logging
logger = logging.getLogger(__name__)


def _save_video(video, filepath: str, client=None) -> None:
    """Save a Video object to disk, handling local bytes and authenticated remote downloads."""
    if video.video_bytes:
        Path(filepath).write_bytes(video.video_bytes)
    elif video.uri:
        logger.info(f"Downloading remote video from URI: {video.uri[:80]}...")

        # Veo download URIs are gated; prefer authenticated SDK download.
        if client is not None:
            sdk_download_errors = []
            for file_ref in (video, getattr(video, "name", None)):
                if not file_ref:
                    continue
                try:
                    data = client.files.download(file=file_ref)
                    if data:
                        Path(filepath).write_bytes(data)
                        return
                except Exception as sdk_err:
                    sdk_download_errors.append(str(sdk_err))
            if sdk_download_errors:
                logger.warning(
                    "SDK download failed, falling back to urllib: %s",
                    " | ".join(sdk_download_errors),
                )

        req = urllib.request.Request(video.uri, headers={"User-Agent": "GymBot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                Path(filepath).write_bytes(resp.read())
        except urllib.error.HTTPError as http_err:
            raise RuntimeError(
                f"Video download forbidden/unavailable (HTTP {http_err.code}). "
                "This usually means the temporary Veo URI expired before download."
            ) from http_err
    else:
        raise RuntimeError("Video has neither bytes nor URI — cannot save")


def _extract_json(raw: str):
    """Robustly extract a JSON object or array from raw LLM text."""
    text = raw.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Regex: find outermost {...} or [...]
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        m = re.search(pattern, text)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return None


class GeminiAIService:
    """AI content generation powered by Google Gemini, Imagen, and Veo3."""

    # ── Models ──────────────────────────────────────────────
    TEXT_MODEL = "gemini-2.5-flash-lite"
    IMAGE_MODEL = "gemini-2.5-flash-image"
    VIDEO_MODEL = "veo-3.1-generate-preview"
    MAX_VIDEOS_PER_DAY = 2

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        self.client = genai.Client(api_key=api_key)
        self.output_dir = Path(settings.UPLOAD_DIR) / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._video_count_today = 0
        self._video_count_date = datetime.utcnow().date()

    # ════════════════════════════════════════════════════════
    #  TEXT GENERATION
    # ════════════════════════════════════════════════════════

    async def generate_post_text(
        self,
        topic: str,
        style: str = "engaging",
        platform: str = "facebook",
        target_audience: str = "local gym members and prospects in Fond du Lac, WI",
        include_hashtags: bool = True,
        include_cta: bool = True,
    ) -> Dict[str, Any]:
        """Generate a complete social-media post (text + hashtags + CTA)."""

        gym_block = GymContextProvider.get_prompt_block()

        user_prompt = f"""You are a TOP-TIER paid social media manager for a local gym. Your job is to
create content that SELLS memberships and training packages. Every post must drive action.

You write for Anytime Fitness in Fond du Lac, WI. You know the local community.
Your audience: {target_audience}.

{gym_block}

STYLE: {style}
PLATFORM: {platform}
TOPIC: {topic}

=== CRITICAL RULES (follow ALL of these) ===
1. ACCURACY: Only state facts from the gym context above. NEVER invent prices, offers, or details.
2. PROMO CORRECTNESS:
   - The $150 Gift Card IS the deal. The customer GETS a $150 Gift Card that PAYS FOR everything:
     signup fee, first month, 2 PT sessions, 2 Evolt 360 body scans, and a 28-day meal plan.
     The customer does NOT pay $150 out of pocket — the Gift Card covers all of it.
     They just commit to an 18-month membership at $35/month.
     NEVER write "for only $150" or "just $150" or "all this for $150" or "for $150" — the Gift Card IS the payment, not the customer's wallet.
     WRONG examples (NEVER write these): "All this for just $150", "for only $150", "Get started for $150", "Only $150 gets you"
     CORRECT examples: "Grab your $150 Gift Card", "Get a $150 Gift Card loaded with", "Your $150 Gift Card covers", "This Gift Card is packed with"
     The customer receives the gift card. The gift card pays for the services. The customer's only cost is $35/mo.
   - The FREE 6-Week Challenge is completely free — no money, no contract. Say that clearly.
   - Unlimited Training INCLUDES the gym membership. Don't list membership as a separate cost.
3. SALES PSYCHOLOGY: Use urgency, social proof, value stacking, and benefit-driven language.
   - Lead with the RESULT/BENEFIT, not the feature. ("Get a complete fitness jumpstart" not "Buy a gift card")
   - Stack the value: list what they get, then reveal the price to make it feel like a steal.
   - Create urgency: "limited spots", "this month only", "don't wait".
   - Social proof: "our members love...", "join hundreds of Fond du Lac residents who...".
4. TONE: Confident but approachable. Like a friend who happens to run the best gym in town.
   Not corporate. Not cheesy. Not desperate. Professional but warm.
5. CTA: Every post MUST end with a clear next step — visit, call, DM, or link.
   Include the address (209 N Macy St) or phone in the CTA.
6. LENGTH: {platform} posts perform best at 100-200 words. Not too short, not a wall of text.
7. HASHTAGS: Use 3-5 LOCAL + niche hashtags (e.g. #FondDuLacFitness not just #Fitness).

Return a JSON object:
{{
  "headline": "Short 5-8 word headline that captures the main offer. This will be displayed on the image graphic, so it MUST match what the post is selling.",
  "main_text": "The full post body (100-200 words, with line breaks for readability)",
  "hashtags": ["FondDuLacFitness", "AnytimeFitnessFDL", ...],
  "call_to_action": "Clear action step with address or phone",
  "emoji_enhanced": "main_text with strategic emoji placement (not overdone)",
  "posting_tips": "One tip about optimal posting for this content type"
}}"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.TEXT_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                max_output_tokens=2048,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        raw = response.text.strip()
        result = _extract_json(raw)
        if result is None:
            result = {"main_text": raw, "hashtags": [], "call_to_action": "", "posting_tips": ""}

        if not include_hashtags:
            result["hashtags"] = []
        if not include_cta:
            result["call_to_action"] = ""

        # Ensure expected keys exist
        result.setdefault("variations", [])
        result.setdefault("headline", "")
        result.setdefault("emoji_enhanced", result.get("main_text", ""))
        result["generated_at"] = datetime.utcnow().isoformat()
        result["model"] = self.TEXT_MODEL
        return result

    async def generate_caption(
        self,
        description: str,
        platform: str = "facebook",
    ) -> Dict[str, str]:
        """Quick caption generation for an existing image/video."""

        prompt = f"""Write a short, engaging {platform} caption for this content: {description}
Return JSON: {{"caption": "...", "hashtags": ["..."], "cta": "..."}}"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=512,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        result = _extract_json(response.text)
        if result is None:
            return {"caption": response.text.strip(), "hashtags": [], "cta": ""}
        return result

    async def generate_ad_copy(
        self,
        objective: str,
        offer: str = "",
        target_audience: str = "local fitness enthusiasts",
        tone: str = "motivational",
    ) -> Dict[str, Any]:
        """Generate Facebook ad copy variants (headline + primary text + description)."""

        gym_block = GymContextProvider.get_prompt_block()

        prompt = f"""You are a direct-response copywriter specializing in local fitness advertising.
Your ads convert cold audiences into gym visits. You write for Anytime Fitness Fond du Lac.

{gym_block}

=== AD BRIEF ===
Objective: {objective}
Offer: {offer or 'Pick the most compelling current promotion from above'}
Audience: {target_audience}
Tone: {tone}

=== COPYWRITING RULES ===
1. ACCURACY: Only reference real offers/prices from the gym context. Never invent.
2. PROMO CORRECTNESS:
   - $150 Gift Card = given to the customer. It PAYS FOR signup + first month + 2 PT + 2 scans + meal plan.
     Customer pays nothing upfront — the Gift Card covers it. They commit to 18mo @ $35/mo.
     NEVER say "for $150" or "only $150" — the Gift Card IS the payment.
   - FREE 6-Week Challenge = truly free, no money, no contract.
   - Unlimited Training INCLUDES gym membership.
3. HEADLINE: Interrupt the scroll. Use numbers, questions, or bold claims. Max 40 chars.
4. PRIMARY TEXT: Hook → Value stack → CTA. Lead with the result. Max 125 chars.
5. DESCRIPTION: Reinforce urgency or social proof. Max 30 chars.
6. Each variant should use a different angle: fear-of-missing-out, value, transformation, social proof.

Return JSON:
{{
  "variants": [
    {{
      "headline": "max 40 chars - scroll-stopping",
      "primary_text": "max 125 chars - benefit-driven with specific offer",
      "description": "max 30 chars - urgency or proof",
      "cta_type": "SIGN_UP|LEARN_MORE|GET_OFFER|BOOK_NOW"
    }}
  ]
}}
Generate 3 variants with different psychological angles."""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=1024,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        result = _extract_json(response.text)
        if result is None:
            raw = response.text.strip()
            return {"variants": [{"headline": raw[:40], "primary_text": raw[:125], "description": "", "cta_type": "LEARN_MORE"}]}
        return result

    async def generate_comment_reply(
        self,
        comment_text: str,
        post_context: str = "",
        tone: str = "friendly and helpful",
    ) -> str:
        """Generate a reply to a Facebook comment."""

        gym_block = GymContextProvider.get_prompt_block()

        prompt = f"""You are the social media manager for Anytime Fitness Fond du Lac, replying to a
Facebook comment. You represent the gym — be warm, knowledgeable, and always move toward a sale.

{gym_block}

Post context: {post_context}
Comment: "{comment_text}"
Tone: {tone}

RULES:
- Reply naturally in 1-3 sentences. Sound human, not corporate.
- If they ask about pricing/programs, give SPECIFIC real details from the gym context above.
  Use exact prices and offer names. Never say "check our website" — give the answer.
- ACCURACY: The $150 Gift Card is given to the customer — it PAYS FOR signup + first month +
  2 PT + 2 scans + meal plan. Customer pays nothing upfront; the Gift Card covers it all.
  They commit to 18mo at $35/mo. NEVER say "for $150" as if the customer pays.
- Always try to move them toward action: "DM us to grab a spot", "Stop by 209 N Macy St",
  "Call us at [phone] and we'll get you set up".
- If it's a compliment, thank them genuinely and mention the community.
- No hashtags. No emojis overload. Professional and real.

Return ONLY the reply text, no JSON."""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=256, thinking_config=types.ThinkingConfig(thinking_budget=0)),
        )
        return response.text.strip()

    # ════════════════════════════════════════════════════════
    #  IMAGE GENERATION (Gemini Flash Image / Imagen 3)
    # ════════════════════════════════════════════════════════

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        style: str = "photorealistic",
        filename: Optional[str] = None,
        headline_overlay: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an image using Gemini Flash Image model.
        
        Args:
            headline_overlay: If provided, the image MUST display this exact text
                            as the bold headline overlay. Ensures image matches the post text.
        """

        ctx = GymContextProvider.get_context()
        gym_name = ctx.get("gym_name", "Anytime Fitness")
        gym_address = ctx.get("gym_address", "")

        headline_instruction = ""
        if headline_overlay:
            headline_instruction = (
                f"CRITICAL — The bold text overlay on this image MUST say EXACTLY: \"{headline_overlay}\". "
                "Use these EXACT words as the main headline. Do NOT invent a different headline or slogan. "
                "Do NOT add words like 'JOIN FOR $1' or any other text that is not in the headline above. "
                "This ensures the image matches the accompanying post text. "
                "SPELLING: Double-check every word. Common mistakes to avoid: "
                "'MEMBERSHIP' not 'MENBRESHIP', 'Fond du Lac' not 'Fond Dac' or 'Fond DAC'. "
            )

        full_prompt = (
            f"Professional social media marketing graphic for {gym_name}. "
            f"Style: {style}. "
            f"Content theme: {prompt}. "
            f"{headline_instruction}"
            "DESIGN REQUIREMENTS: "
            "- Clean, modern fitness marketing design with Anytime Fitness purple (#6A2C91) and white color scheme. "
            "- Bold, readable text overlay is REQUIRED — include the headline text prominently on the image. "
            f"- If the prompt mentions a specific offer or price, display it prominently as text on the image. "
            "- Professional gym photography feel: well-lit, high contrast, energetic. "
            "- People should look real, diverse, and genuinely engaged in fitness activities. "
            "- Include the Anytime Fitness logo or branding elements. "
            f"- Location text at bottom: {gym_address}. "
            "- This should look like it was created by a paid graphic designer, not AI-generated stock art. "
            "- Layout: clean composition with space for text, not cluttered. "
            "- SPELLING ACCURACY: Every word on the image must be spelled correctly. "
            "  'MEMBERSHIP' not 'MENBRESHIP'. 'Fond du Lac' not 'Fond Dac'. 'Anytime Fitness' exactly. "
            "  Double-check all text before finalizing."
        )

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.IMAGE_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )

        # Extract and save the image
        if not response.candidates or not response.candidates[0].content.parts:
            return {"status": "failed", "error": "No image generated"}

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img = Image.open(io.BytesIO(part.inline_data.data))
                if not filename:
                    filename = f"img_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = self.output_dir / filename
                img.save(str(filepath))
                return {
                    "status": "success",
                    "filepath": str(filepath),
                    "filename": filename,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": aspect_ratio,
                    "model": self.IMAGE_MODEL,
                    "generated_at": datetime.utcnow().isoformat(),
                }

        return {"status": "failed", "error": "No image data in response"}

    # ════════════════════════════════════════════════════════
    #  VIDEO GENERATION (Veo 3)
    # ════════════════════════════════════════════════════════

    def _check_video_budget(self) -> bool:
        """Return True if we haven't exceeded the daily video generation cap."""
        today = datetime.utcnow().date()
        if self._video_count_date != today:
            self._video_count_today = 0
            self._video_count_date = today
        return self._video_count_today < self.MAX_VIDEOS_PER_DAY

    def _record_video_gen(self):
        """Increment daily video generation counter."""
        today = datetime.utcnow().date()
        if self._video_count_date != today:
            self._video_count_today = 0
            self._video_count_date = today
        self._video_count_today += 1
        logger.info(f"Video gen #{self._video_count_today}/{self.MAX_VIDEOS_PER_DAY} today")

    async def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 8,
        resolution: str = "1080p",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a video using Veo 3.  Returns path to saved .mp4."""
        if not self._check_video_budget():
            return {"status": "failed", "error": f"Daily video limit ({self.MAX_VIDEOS_PER_DAY}) reached — videos cost ~$12 each. Try again tomorrow."}

        ctx = GymContextProvider.get_context()
        gym_name = ctx.get("gym_name", "Anytime Fitness")
        gym_address = ctx.get("gym_address", "")

        full_prompt = (
            f"TV-COMMERCIAL QUALITY fitness advertisement for {gym_name}. "
            f"Content: {prompt}. "
            "PRODUCTION REQUIREMENTS: "
            "- Cinematic quality: professional lighting, smooth camera movements (dolly, crane, or steadicam feel). "
            "- Color grading: warm, energetic tones with Anytime Fitness purple accent lighting. "
            "- Pacing: dynamic cuts between scenes, building energy. "
            "- People: real-looking diverse adults actively working out, high-fiving trainers, or achieving goals. "
            "- Environment: modern, clean gym interior with equipment, purple branding visible. "
            "- Emotion: convey transformation, community, and confidence — not just exercise footage. "
            "- Audio: upbeat motivational background music with professional voiceover energy. "
            f"- End card: {gym_name} logo with '{gym_address}' text. "
            "- This should look like a local TV commercial or paid Facebook video ad, not a generic fitness clip. "
            "- Show real results: before/after energy, member testimonials vibe, trainers coaching with enthusiasm."
        )

        try:
            operation = await asyncio.to_thread(
                self.client.models.generate_videos,
                model=self.VIDEO_MODEL,
                prompt=full_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    duration_seconds=duration_seconds,
                    resolution=resolution,
                    number_of_videos=1,
                    person_generation="allow_all",
                ),
            )

            # Poll for completion (video gen is async on Google's side)
            while True:
                op_status = await asyncio.to_thread(self.client.operations.get, operation)
                if op_status.done:
                    break
                await asyncio.sleep(10)

            result = op_status.result
            if not result or not result.generated_videos:
                return {"status": "failed", "error": "No video generated"}

            if not filename:
                filename = f"vid_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = self.output_dir / filename
            _save_video(result.generated_videos[0].video, str(filepath), client=self.client)

            return {
                "status": "success",
                "filepath": str(filepath),
                "filename": filename,
                "duration_seconds": duration_seconds,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "model": self.VIDEO_MODEL,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Veo3 video generation failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def generate_video_from_image(
        self,
        image_path: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 8,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Animate an existing image into a video using Veo 3."""

        try:
            operation = await asyncio.to_thread(
                self.client.models.generate_videos,
                model=self.VIDEO_MODEL,
                prompt=prompt,
                image=types.Image.from_file(location=image_path),
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    duration_seconds=duration_seconds,
                    resolution="1080p",
                ),
            )

            while True:
                op_status = await asyncio.to_thread(self.client.operations.get, operation)
                if op_status.done:
                    break
                await asyncio.sleep(10)

            result = op_status.result
            if not result or not result.generated_videos:
                return {"status": "failed", "error": "No video generated"}

            if not filename:
                filename = f"vid_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = self.output_dir / filename
            _save_video(result.generated_videos[0].video, str(filepath), client=self.client)

            return {
                "status": "success",
                "filepath": str(filepath),
                "filename": filename,
                "model": self.VIDEO_MODEL,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Veo3 image-to-video failed: {e}")
            return {"status": "failed", "error": str(e)}

    # ════════════════════════════════════════════════════════
    #  EXTENDED VIDEO (chained Veo extensions for 30-60s)
    # ════════════════════════════════════════════════════════

    async def _plan_video_scenes(
        self,
        topic: str,
        total_seconds: int,
        num_segments: int,
    ) -> List[str]:
        """Use Gemini to plan a coherent multi-segment video storyboard.

        Returns a list of scene prompts, one per segment. The first is 8 seconds,
        each subsequent extension is 7 seconds. Every prompt builds on the previous
        to create a single cohesive narrative arc.
        """
        ctx = GymContextProvider.get_context()
        gym_name = ctx.get("gym_name", "Anytime Fitness")
        gym_address = ctx.get("gym_address", "209 N Macy St, Fond du Lac, WI")
        gym_block = GymContextProvider.get_prompt_block()

        planning_prompt = f"""You are a professional VIDEO DIRECTOR creating a TV-commercial storyboard
for {gym_name} located at {gym_address}.

{gym_block}

VIDEO CONCEPT / TOPIC: {topic}
TOTAL DURATION: ~{total_seconds} seconds
SEGMENTS: {num_segments} (first segment is 8 seconds, each extension segment is 7 seconds)

Create a storyboard with EXACTLY {num_segments} scene descriptions. Each scene MUST:
1. Flow naturally from the previous scene — this is ONE continuous video, not separate clips.
2. Build a narrative arc: HOOK (grab attention) → BUILD (stack value/emotion) → CLIMAX (peak energy) → CTA (clear call to action on the final segment).
3. Include specific camera directions (dolly in, wide shot, close-up, tracking shot, etc.).
4. Include specific audio/sound cues (upbeat music builds, voiceover tone, gym sounds, dialogue in quotes).
5. Reference REAL gym details — actual prices, actual programs, actual address. No made-up details.
6. Scene 1 must hook the viewer in the first 2 seconds — dramatic visual, bold statement, or surprising moment.
7. The FINAL scene MUST include the gym name, address, and a clear CTA (call, visit, sign up).
8. People should look real, diverse, energetic — members working out, trainers coaching, high-fives, sweat, determination.
9. Each scene prompt must be self-contained but reference continuity ("continuing from the previous shot...", "the camera pulls back to reveal...", etc.)
10. Maintain consistent color grading throughout: warm energetic tones with Anytime Fitness purple accent lighting.
11. CRITICAL AUDIO TIMING: ALL voiceover, narration, and dialogue MUST COMPLETE within each segment's time window. Segment 1 = 8 seconds max of audio. Each extension segment = 7 seconds max of audio. NEVER let a sentence run past the segment boundary.
12. End each segment's audio with a natural pause or breath — do NOT start a new sentence in the last 1.5 seconds of any segment. Plan speech to wrap up cleanly 1-2 seconds before the segment ends.
13. Use music and ambient sound to fill the last 1-2 seconds of each segment where narration has ended. This creates a clean seam between segments.

$150 GIFT CARD RULES (if the topic involves this promo):
- The customer GETS a $150 Gift Card. They do NOT pay $150.
- CORRECT: "Grab your $150 Gift Card", "Your $150 Gift Card covers..."
- WRONG: "for only $150", "just $150", "all this for $150"

Return ONLY a JSON array of {num_segments} strings. Each string is a detailed scene prompt.
Example format: ["Scene 1 prompt...", "Scene 2 prompt...", "Scene 3 prompt..."]
No markdown fences. No commentary. Just the JSON array."""

        try:
            resp = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.TEXT_MODEL,
                contents=planning_prompt,
            )
            scenes = _extract_json(resp.text)
            if isinstance(scenes, list) and len(scenes) == num_segments:
                return scenes
            # Fallback: if AI returns wrong count, pad or trim
            if isinstance(scenes, list):
                while len(scenes) < num_segments:
                    scenes.append(scenes[-1])
                return scenes[:num_segments]
        except Exception as e:
            logger.error(f"Scene planning failed: {e}")

        # Hard fallback: generic scene breakdown
        fallback = []
        for i in range(num_segments):
            if i == 0:
                fallback.append(
                    f"Opening hook: dramatic wide shot of {gym_name} exterior at golden hour, "
                    f"camera pushes through the doors into a bustling gym. Upbeat music kicks in. "
                    f"Topic: {topic}"
                )
            elif i == num_segments - 1:
                fallback.append(
                    f"Closing CTA: camera pulls back to reveal the full gym. "
                    f"Bold text overlay: {gym_name} - {gym_address}. "
                    f"Voiceover: 'Visit us today.' Upbeat music crescendo and fade."
                )
            else:
                fallback.append(
                    f"Continuation scene {i+1}: energetic gym footage supporting '{topic}'. "
                    f"Members working out, trainers coaching, smooth camera movement. "
                    f"Building energy and emotion toward the finale."
                )
        return fallback

    async def generate_extended_video(
        self,
        prompt: str,
        target_duration: int = 30,
        aspect_ratio: str = "16:9",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a longer video (30-60s) by chaining Veo 3.1 extensions.

        Workflow:
        1. Plan scene-by-scene storyboard via Gemini text model.
        2. Generate initial 8-second clip at 720p (required for extension).
        3. Extend in 7-second increments, each with a scene-specific prompt.
        4. Return the final combined video.

        Constraints (Veo 3.1 API):
        - Extension only works at 720p.
        - Each extension adds 7 seconds.
        - Max ~148 seconds total (20 extensions).
        - The final video is a single stitched file returned by the API.
        """
        # Clamp duration to API limits
        target_duration = max(15, min(target_duration, 141))

        if not self._check_video_budget():
            return {"status": "failed", "error": f"Daily video limit ({self.MAX_VIDEOS_PER_DAY}) reached \u2014 videos cost ~$12 each. Try again tomorrow."}

        # Calculate segments: first clip = 8s, each extension = 7s
        extensions_needed = max(1, (target_duration - 8 + 6) // 7)  # round up
        num_segments = 1 + extensions_needed  # initial + extensions
        actual_duration = 8 + (extensions_needed * 7)

        logger.info(
            f"Extended video: {target_duration}s requested → {num_segments} segments "
            f"({extensions_needed} extensions) → ~{actual_duration}s actual"
        )

        # Step 1: Plan the storyboard
        logger.info("Step 1/3: Planning storyboard...")
        scenes = await self._plan_video_scenes(prompt, actual_duration, num_segments)
        logger.info(f"Storyboard planned: {len(scenes)} scenes")

        ctx = GymContextProvider.get_context()
        gym_name = ctx.get("gym_name", "Anytime Fitness")
        gym_address = ctx.get("gym_address", "")

        # Step 2: Generate initial 8-second clip at 720p
        logger.info("Step 2/3: Generating initial 8-second clip...")
        initial_prompt = (
            f"TV-COMMERCIAL QUALITY fitness video for {gym_name}. "
            f"SCENE 1 of {num_segments}: {scenes[0]} "
            "PRODUCTION: cinematic lighting, smooth camera movement, warm energetic tones, "
            "Anytime Fitness purple accents, real-looking diverse people, modern gym interior. "
            "This is the OPENING of a longer commercial — hook the viewer immediately. "
            "CRITICAL AUDIO RULE: All voiceover and narration in this 8-second segment "
            "MUST complete by the 6.5-second mark. End with a natural pause or music swell — "
            "do NOT let any sentence run past the segment boundary."
        )

        try:
            operation = await asyncio.to_thread(
                self.client.models.generate_videos,
                model=self.VIDEO_MODEL,
                prompt=initial_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    duration_seconds=8,
                    resolution="720p",
                    number_of_videos=1,
                    person_generation="allow_all",
                ),
            )

            while True:
                op_status = await asyncio.to_thread(self.client.operations.get, operation)
                if op_status.done:
                    break
                await asyncio.sleep(10)

            result = op_status.result
            if not result or not result.generated_videos:
                return {"status": "failed", "error": "Initial video generation failed — no video returned"}

            current_video = result.generated_videos[0].video
            logger.info("Initial 8-second clip generated successfully")

        except Exception as e:
            logger.error(f"Initial video generation failed: {e}")
            return {"status": "failed", "error": f"Initial generation failed: {e}"}

        # Step 3: Chain extensions
        logger.info(f"Step 3/3: Chaining {extensions_needed} extensions...")
        extensions_completed = 0
        for i in range(extensions_needed):
            scene_idx = i + 1
            scene_prompt = scenes[scene_idx] if scene_idx < len(scenes) else scenes[-1]

            is_final = (i == extensions_needed - 1)
            continuity_note = (
                "This is the FINAL scene — end with a strong call to action, "
                f"gym name ({gym_name}), and address ({gym_address})."
                if is_final
                else f"This is scene {scene_idx + 1} of {num_segments} — "
                     "maintain visual continuity from the previous shot."
            )

            ext_prompt = (
                f"CONTINUATION of a TV commercial for {gym_name}. "
                f"{continuity_note} "
                f"SCENE {scene_idx + 1}: {scene_prompt} "
                "Maintain the same cinematic style, color grading, and energy level. "
                "Smooth transition from the previous segment. "
                "CRITICAL AUDIO RULE: All narration and dialogue in this 7-second segment "
                "MUST complete by the 5.5-second mark. End with a natural pause — "
                "do NOT leave any sentence unfinished. Use music or ambient gym sounds "
                "to fill the final 1-2 seconds cleanly."
            )

            extension_ok = False
            for attempt in range(1, 4):
                try:
                    if attempt > 1:
                        wait_s = attempt * 5
                        logger.info(
                            f"Retrying extension {scene_idx + 1}/{num_segments} in {wait_s}s "
                            f"(attempt {attempt}/3)..."
                        )
                        await asyncio.sleep(wait_s)

                    logger.info(
                        f"Extending: segment {scene_idx + 1}/{num_segments} "
                        f"(attempt {attempt}/3)..."
                    )
                    ext_operation = await asyncio.to_thread(
                        self.client.models.generate_videos,
                        model=self.VIDEO_MODEL,
                        prompt=ext_prompt,
                        video=current_video,
                        config=types.GenerateVideosConfig(
                            aspect_ratio=aspect_ratio,
                            duration_seconds=8,
                            resolution="720p",
                            number_of_videos=1,
                            person_generation="allow_all",
                        ),
                    )

                    while True:
                        ext_status = await asyncio.to_thread(
                            self.client.operations.get, ext_operation
                        )
                        if ext_status.done:
                            break
                        await asyncio.sleep(10)

                    ext_result = ext_status.result
                    if not ext_result or not ext_result.generated_videos:
                        logger.warning(
                            f"Extension {scene_idx + 1} returned no video — "
                            f"stopping at ~{8 + i * 7}s"
                        )
                        break

                    # The API returns the FULL combined video (original + extension)
                    current_video = ext_result.generated_videos[0].video
                    extensions_completed += 1
                    extension_ok = True
                    logger.info(
                        f"Extension {scene_idx + 1}/{num_segments} complete — "
                        f"video now ~{8 + (i + 1) * 7}s"
                    )
                    break

                except Exception as e:
                    err_text = str(e).lower()
                    needs_processing = "must be a video that was generated by veo" in err_text or "has been processed" in err_text
                    if attempt < 3 and needs_processing:
                        continue

                    logger.warning(
                        f"Extension {scene_idx + 1} failed: {e} — "
                        f"returning video at ~{8 + i * 7}s"
                    )
                    break

            if not extension_ok:
                break

        # Save the final combined video
        if not filename:
            filename = f"vid_ext_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
        filepath = self.output_dir / filename
        try:
            _save_video(current_video, str(filepath), client=self.client)
        except Exception as e:
            logger.error(f"Final video save failed: {e}")
            return {
                "status": "failed",
                "error": f"Video generated but could not be downloaded/saved: {e}",
            }

        final_duration = min(actual_duration, 8 + (extensions_completed * 7))
        self._record_video_gen()
        logger.info(f"Extended video saved: {filepath} (~{final_duration}s)")

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filename,
            "duration_seconds": actual_duration,
            "segments": num_segments,
            "extensions_completed": extensions_completed,
            "resolution": "720p",
            "aspect_ratio": aspect_ratio,
            "model": self.VIDEO_MODEL,
            "storyboard": scenes,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ════════════════════════════════════════════════════════
    #  CONTENT STRATEGY / CALENDAR SUGGESTIONS
    # ════════════════════════════════════════════════════════

    async def generate_content_calendar(
        self,
        days: int = 7,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a week's worth of content ideas for the gym."""

        areas = focus_areas or [
            "$150 Gift Card Special promotion",
            "FREE 6-Week Group Training Challenge",
            "member transformation / success story",
            "training program spotlight (unlimited group or 1-on-1)",
            "local community tie-in (Fond du Lac events, seasonal)",
            "trainer spotlight / behind-the-scenes",
            "nutrition tip with meal plan upsell",
        ]

        gym_block = GymContextProvider.get_prompt_block()

        prompt = f"""You are a paid social media strategist creating a {days}-day content calendar
for Anytime Fitness Fond du Lac's Facebook page. Your goal: drive memberships and training signups.

{gym_block}

=== CALENDAR STRATEGY ===
Every post must tie back to a SALE or engagement goal. Mix content types:
- 40% promotional (directly selling an offer with specific pricing)
- 30% value/educational (tips that position the gym as expert, with soft CTA)
- 20% social proof (transformations, member stories, community)
- 10% engagement (questions, polls, local tie-ins)

Focus areas: {', '.join(areas)}

=== ACCURACY RULES ===
- $150 Gift Card = given to the customer. It COVERS signup + first month + 2 PT + 2 scans + meal plan.
  Customer pays nothing upfront — the Gift Card IS the payment. They commit to 18mo at $35/mo.
  NEVER say "for $150" or "only $150".
- FREE 6-Week Challenge = completely free, no contract.
- Unlimited Training INCLUDES membership ($175/mo group, $275/mo 1-on-1).
- Always include the real address: 209 N Macy St, Fond du Lac.

For each day return:
- post_type: text | image | video
- topic: specific, sales-oriented topic
- caption_idea: a compelling caption concept (not generic)
- best_time: posting time in CST
- content_prompt: detailed prompt to generate the image/video (include text overlay instructions,
  specific offer amounts, and visual direction)
- sales_goal: what this post is designed to achieve (e.g. "drive DMs for gift card deal")

Return JSON: {{"calendar": [{{"day": 1, "post_type": "...", "topic": "...", "caption_idea": "...", "best_time": "...", "content_prompt": "...", "sales_goal": "..."}}]}}"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=4096, thinking_config=types.ThinkingConfig(thinking_budget=0)),
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        if raw.startswith("json"):
            raw = raw[4:]
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            return {"calendar": [], "raw": raw}
