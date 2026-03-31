"""
Content Autopilot Service
Autonomously generates and publishes social media content throughout the day.
Uses GymContextProvider for real gym data so every post is specific and relevant.
Configuration is persisted to autopilot_config.json so changes survive restarts.
"""

import asyncio
import json
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.gemini_ai_service import GeminiAIService
from app.services.facebook_service import FacebookService
from app.services.gym_context_provider import GymContextProvider

import logging
logger = logging.getLogger(__name__)

# ── Config file path — stored alongside the SMM backend data ──────────
def _resolve_config_dir() -> Path:
    """Find the best writable directory for autopilot config."""
    import sys
    # Frozen (PyInstaller): use AppData/Local/GymBot/data
    if getattr(sys, 'frozen', False):
        appdata = Path(os.environ.get("LOCALAPPDATA", "")) / "GymBot" / "data"
        if appdata.parent.exists():
            appdata.mkdir(parents=True, exist_ok=True)
            return appdata
    # Dev mode: use Social_Media_Management_Bot/backend/data
    here = Path(__file__).resolve().parent.parent.parent / "data"
    here.mkdir(parents=True, exist_ok=True)
    return here

_CONFIG_DIR = _resolve_config_dir()
_CONFIG_FILE = _CONFIG_DIR / "autopilot_config.json"


# ── Default themes (sales-driven, rotate through the week) ────────────
DEFAULT_DAILY_THEMES: Dict[str, List[str]] = {
    "0": [
        "$150 Gift Card Special — you GET a $150 Gift Card that covers signup, first month, 2 PT sessions, 2 body scans, and a custom meal plan. No out-of-pocket cost for all of that",
        "New week, new chapter — spotlight on a member transformation and how our training programs got them there",
        "Monday motivation: why Fond du Lac locals choose Anytime Fitness for 24/7 access and real personal training",
        "Kickstart your Monday right — walk through what a first visit looks like at our gym. We make it easy to get started",
        "Ask about our Unlimited Group Training at $175/mo — gym membership INCLUDED. Real coaching, real results, real community",
        "Meal prep Monday: simple high-protein recipe + reminder that our custom 28-day meal plans are just $50 with an Evolt 360 body scan",
    ],
    "1": [
        "FREE 6-Week Group Training Challenge — zero cost, zero contract, zero risk. Just 6 weeks of real coached sessions",
        "Training Tip Tuesday: a quick exercise form tip from our trainers, with a CTA to book a free session",
        "Unlimited Training spotlight — gym membership INCLUDED at $175/mo group or $275/mo 1-on-1, plus nutrition coaching and body scans",
        "Transformation Tuesday: side-by-side progress from one of our members — real person, real timeline, real program",
        "Did you know our $50 custom 16-week program includes a full Evolt 360 body scan? Here's what that tells you about your body",
        "What's the difference between group and 1-on-1 training? Here's a quick breakdown to help you pick the right fit",
    ],
    "2": [
        "Mid-week value stack: break down everything in the $150 Gift Card deal to show what an insane value it is",
        "Nutrition tip + upsell: quick healthy meal idea, then mention our $50 custom 28-day meal plan with Evolt 360 body scan",
        "Behind the scenes at Anytime Fitness Fond du Lac — show the gym, the equipment, the vibe, invite people to visit",
        "Hump day hustle — what does a typical group training session at our gym look like? Walk people through it",
        "Staff spotlight: meet the person behind the front desk and what makes our gym feel like community",
        "3 reasons our members say they chose Anytime Fitness over other Fond du Lac gyms — hear it from them",
    ],
    "3": [
        "Member success story / transformation — real results from our training programs, with testimonial style",
        "Training program comparison: Group Unlimited vs 1-on-1 Unlimited vs Custom Program — help people pick the right fit",
        "Throwback Thursday: before/after energy — where our members started vs where they are now",
        "The $150 Gift Card gets you: signup fee covered, first month covered, 2 PT sessions, 2 body scans, and a custom meal plan. All free.",
        "Trainer spotlight: what our coaches specialize in and why they love helping Fond du Lac get fit",
        "Quick myth-buster: '24-hour gyms are just treadmill factories' — here's what REAL personal training at Anytime Fitness looks like",
    ],
    "4": [
        "Weekend plans? Come check us out at 209 N Macy St — walk-ins welcome, ask about our $150 Gift Card to get started",
        "Friday wins: celebrate what our community accomplished this week, soft pitch the FREE 6-Week Challenge",
        "FOMO Friday: limited spots available for our FREE 6-Week Group Training Challenge — sign up before they're gone",
        "Heading into the weekend — here are 3 quick bodyweight exercises you can do anywhere. Want a real plan? We build custom 16-week programs for $50",
        "Payday Friday: investing in your health is the best money you'll ever spend. Our unlimited group training is $175/mo with membership included",
        "Friday community shoutout: tag a friend who would crush our FREE 6-Week Challenge. Accountability = results",
    ],
    "5": [
        "Saturday sweat session: group training energy at Anytime Fitness — join the community, first 6 weeks are FREE",
        "Weekend warrior workout tip + CTA: if you love working out on your own, our $50 custom 16-week program is built for you",
        "Trainer spotlight: meet one of our coaches, what they specialize in, and how to book a session",
        "Saturday vibes at the gym — 24/7 access means your schedule is YOUR schedule. No excuses, just results",
        "Weekend project: take 30 minutes for yourself today. Here's a quick full-body circuit from our trainers",
        "Don't let the weekend derail your progress — simple food swaps to stay on track + reminder about our $50 custom meal plans",
    ],
    "6": [
        "Sunday reset: plan your fitness week. Here's why having a plan matters — and we can build one for you ($50 for 16 weeks)",
        "Recovery and self-care Sunday + mention our Evolt 360 body scanner and nutrition coaching included with Unlimited Training",
        "New week starts tomorrow — if you've been thinking about joining, the $150 Gift Card deal makes it easy. Here's what you get",
        "Sunday success mindset: where do you want to be 6 weeks from now? Our FREE Group Training Challenge starts that journey",
        "Prep for Monday: set out your gym clothes, plan your meals, and book your first session. We're at 209 N Macy St — walk-ins welcome",
        "End-of-weekend reflection + CTA: the best time to start was yesterday, the next best time is tomorrow morning. $150 Gift Card makes it free to start",
    ],
}

# Post styles — weighted toward promotional and value-driven to maximize conversion
DEFAULT_STYLES = ["promotional", "promotional", "value-driven", "community-story", "educational", "urgency"]

# Default: 6 posts per day, spread across 6 posting windows (CST)
DEFAULT_POSTS_PER_DAY = 6

DEFAULT_POSTING_WINDOWS = [
    {"hour": 6, "minute": 15, "label": "early morning"},
    {"hour": 8, "minute": 30, "label": "morning"},
    {"hour": 11, "minute": 0, "label": "late morning"},
    {"hour": 13, "minute": 30, "label": "early afternoon"},
    {"hour": 17, "minute": 0, "label": "evening"},
    {"hour": 20, "minute": 0, "label": "night"},
]

# Default content format weights (must sum to 1.0)
DEFAULT_FORMAT_WEIGHTS = {
    "image": 0.75,
    "text": 0.25,
    "video": 0.0,
}


def _load_config() -> Dict[str, Any]:
    """Load autopilot config from JSON file, or return defaults."""
    try:
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            logger.info(f"Loaded autopilot config from {_CONFIG_FILE}")
            return cfg
    except Exception as e:
        logger.warning(f"Could not load autopilot config: {e} — using defaults")
    return {}


def _save_config(cfg: Dict[str, Any]):
    """Persist autopilot config to JSON file."""
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        logger.info(f"Saved autopilot config to {_CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save autopilot config: {e}")


def _get_effective_config() -> Dict[str, Any]:
    """Merge saved config over defaults."""
    cfg = _load_config()
    return {
        "posts_per_day": cfg.get("posts_per_day", DEFAULT_POSTS_PER_DAY),
        "posting_windows": cfg.get("posting_windows", DEFAULT_POSTING_WINDOWS),
        "daily_themes": cfg.get("daily_themes", DEFAULT_DAILY_THEMES),
        "styles": cfg.get("styles", DEFAULT_STYLES),
        "format_weights": cfg.get("format_weights", DEFAULT_FORMAT_WEIGHTS),
        "enabled": cfg.get("enabled", True),
    }


_HISTORY_FILE = _CONFIG_DIR / "autopilot_history.json"
_DAY_QUEUE_FILE = _CONFIG_DIR / "autopilot_day_queue.json"


def _load_history() -> List[Dict[str, Any]]:
    """Load publish history from disk."""
    try:
        if _HISTORY_FILE.exists():
            with open(_HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load autopilot history: {e}")
    return []


def _save_history(history: List[Dict[str, Any]]):
    """Persist publish history to disk. Keep last 100 entries."""
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_HISTORY_FILE, "w") as f:
            json.dump(history[-100:], f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save autopilot history: {e}")


def _load_day_queue() -> Dict[str, Any]:
    """Load the pre-generated day queue from disk."""
    try:
        if _DAY_QUEUE_FILE.exists():
            with open(_DAY_QUEUE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load day queue: {e}")
    return {}


def _save_day_queue(queue: Dict[str, Any]):
    """Persist day queue to disk."""
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_DAY_QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save day queue: {e}")


class ContentAutopilotService:
    """Generates and publishes gym-specific content on autopilot."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.gemini = GeminiAIService()
        self.fb = FacebookService()
        self._running = False
        self._config = _get_effective_config()
        self._enabled = self._config["enabled"]
        self._history: List[Dict[str, Any]] = _load_history()
        self._used_topics_today: List[str] = []
        self._last_topic_date: str = ""
        self._fired_windows_today: set = set()  # tracks which HH:MM windows already fired today
        self._last_check_date: str = ""
        self._day_queue: Dict[str, Any] = _load_day_queue()  # pre-generated posts keyed by date

    # ── Lifecycle ────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        # Single interval job that checks every 60s if a window is due
        self.scheduler.add_job(
            self._check_windows,
            trigger=IntervalTrigger(seconds=60),
            id="autopilot_checker",
            replace_existing=True,
        )
        self.scheduler.start()
        self._running = True
        windows = self._config["posting_windows"]
        logger.info(
            f"Content autopilot started — {len(windows)} posts/day at "
            + ", ".join(f"{w['hour']:02d}:{w['minute']:02d}" for w in windows)
        )

    async def _check_windows(self):
        """Called every 60s. Fires _autopilot_tick if a posting window is due."""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # Reset fired windows at midnight
        if self._last_check_date != today_str:
            self._fired_windows_today = set()
            self._last_check_date = today_str

        for window in self._config["posting_windows"]:
            key = f"{window['hour']:02d}:{window['minute']:02d}"
            if key in self._fired_windows_today:
                continue
            # Fire if current time is within 2 minutes past the window
            window_time = now.replace(hour=window["hour"], minute=window["minute"], second=0, microsecond=0)
            diff = (now - window_time).total_seconds()
            if 0 <= diff < 120:  # within 0-2 minutes of the window
                self._fired_windows_today.add(key)
                logger.info(f"Autopilot window {key} ({window.get('label','')}) is due — triggering")
                await self._autopilot_tick(window_label=window.get("label", key))

    def _apply_schedule(self):
        """Reset fired windows so schedule changes take effect immediately."""
        self._fired_windows_today = set()

    def reload_config(self):
        """Reload config from disk and reschedule jobs."""
        self._config = _get_effective_config()
        self._enabled = self._config["enabled"]
        if self._running:
            self._apply_schedule()
        windows = self._config["posting_windows"]
        logger.info(
            f"Autopilot config reloaded — {len(windows)} posts/day at "
            + ", ".join(f"{w['hour']:02d}:{w['minute']:02d}" for w in windows)
        )

    def stop(self):
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Content autopilot stopped")

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        self._config["enabled"] = value
        _save_config(self._config)
        logger.info(f"Content autopilot {'ENABLED' if value else 'DISABLED'}")

    def get_status(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        todays_posts = [h for h in self._history if h.get("date") == today_str]
        return {
            "running": self._running,
            "enabled": self._enabled,
            "posts_per_day": len(self._config["posting_windows"]),
            "posting_windows": self._config["posting_windows"],
            "format_weights": self._config["format_weights"],
            "styles": self._config["styles"],
            "config_file": str(_CONFIG_FILE),
            "posts_today": todays_posts,
            "total_posts_today": len(todays_posts),
        }

    def get_full_config(self) -> Dict[str, Any]:
        """Return the full editable config (themes, schedule, weights, styles)."""
        return dict(self._config)

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge partial updates into the config, persist, and reschedule."""
        allowed_keys = {"posts_per_day", "posting_windows", "daily_themes",
                        "styles", "format_weights", "enabled"}
        for key, value in updates.items():
            if key in allowed_keys:
                self._config[key] = value
        self._enabled = self._config.get("enabled", True)
        _save_config(self._config)
        if self._running:
            self._apply_schedule()
        logger.info(f"Autopilot config updated: {list(updates.keys())}")
        return self._config

    # ── Core Loop ────────────────────────────────────────────

    async def _autopilot_tick(self, window_label: str = ""):
        """Called by the scheduler at each posting window."""
        if not self._enabled:
            logger.debug(f"Autopilot tick skipped (disabled) — {window_label}")
            return

        logger.info(f"Autopilot tick: {window_label}")
        try:
            # Check if there's a pre-generated post in the day queue for this window
            today_date = datetime.now().strftime("%Y-%m-%d")
            queued_post = self._pop_queued_post(today_date, window_label)
            if queued_post:
                result = await self._publish_queued_post(queued_post)
            else:
                result = await self.generate_and_publish()
            logger.info(f"Autopilot published: {result.get('post_id', 'unknown')} — {window_label}")
        except Exception as e:
            logger.error(f"Autopilot tick failed ({window_label}): {e}")

    def _pop_queued_post(self, date: str, window_label: str) -> Optional[Dict[str, Any]]:
        """Pop a pre-generated post from the day queue for the given window."""
        if not self._day_queue or self._day_queue.get("date") != date:
            return None
        posts = self._day_queue.get("posts", [])
        for post in posts:
            if post.get("window_label") == window_label and post.get("status") == "queued":
                post["status"] = "publishing"
                _save_day_queue(self._day_queue)
                return post
        return None

    async def _publish_queued_post(self, queued: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a pre-generated post from the day queue to Facebook."""
        full_text = queued["full_text"]
        content_format = queued.get("format", "text")
        media_path = queued.get("media_path")

        post_result: Dict[str, Any] = {}
        if content_format == "image" and media_path:
            post_result = await self.fb.post_photo(image_path=media_path, caption=full_text)
        elif content_format == "video" and media_path:
            post_result = await self.fb.post_video(video_path=media_path, description=full_text)
        else:
            post_result = await self.fb.post_text(message=full_text)

        # Update queue entry status
        queued["status"] = "published"
        queued["post_id"] = post_result.get("id") or post_result.get("post_id")
        queued["published_at"] = datetime.now(timezone.utc).isoformat()
        _save_day_queue(self._day_queue)

        # Record in history
        record = {
            "post_id": queued["post_id"],
            "topic": queued.get("topic", ""),
            "style": queued.get("style", ""),
            "format": content_format,
            "text": full_text[:300],
            "had_media": media_path is not None,
            "published_at": queued["published_at"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
        }
        self._history.append(record)
        _save_history(self._history)
        return record

    async def generate_and_publish(self, force_topic: Optional[str] = None) -> Dict[str, Any]:
        """Generate a gym-specific post and publish it to Facebook."""

        # Pick topic and style from config — avoid repeating today's topics
        today = str(datetime.now().weekday())
        today_date = datetime.now().strftime("%Y-%m-%d")

        # Reset used topics if it's a new day
        if self._last_topic_date != today_date:
            self._used_topics_today = []
            self._last_topic_date = today_date

        themes = self._config.get("daily_themes", DEFAULT_DAILY_THEMES)
        topics = themes.get(today, themes.get("0", DEFAULT_DAILY_THEMES["0"]))

        if force_topic:
            topic = force_topic
        else:
            # Pick a topic NOT already used today
            available = [t for t in topics if t not in self._used_topics_today]
            if not available:
                # All used, reset and reuse (shouldn't happen with 6 topics / 6 windows)
                available = topics
                self._used_topics_today = []
            topic = random.choice(available)
            self._used_topics_today.append(topic)

        styles = self._config.get("styles", DEFAULT_STYLES)
        style = random.choice(styles)

        # Content format based on configurable weights
        weights = self._config.get("format_weights", DEFAULT_FORMAT_WEIGHTS)
        roll = random.random()
        image_threshold = weights.get("image", 0.55)
        text_threshold = image_threshold + weights.get("text", 0.25)
        if roll < image_threshold:
            content_format = "image"
        elif roll < text_threshold:
            content_format = "text"
        else:
            content_format = "video"

        logger.info(f"Generating: topic='{topic}', style='{style}', format={content_format}")

        # Generate text (gym context is injected automatically via GymContextProvider)
        text_result = await self.gemini.generate_post_text(
            topic=topic,
            style=style,
            platform="facebook",
        )

        post_text = text_result.get("emoji_enhanced") or text_result.get("main_text", "")
        hashtags = text_result.get("hashtags", [])
        cta = text_result.get("call_to_action", "")

        # Combine text + hashtags + CTA
        full_text = post_text
        if cta:
            full_text += f"\n\n{cta}"
        if hashtags:
            full_text += "\n\n" + " ".join(f"#{h.lstrip('#')}" for h in hashtags)

        # Generate and post
        post_result: Dict[str, Any] = {}
        media_path = None

        if content_format == "image":
            # Extract the headline from generated text so the image matches
            headline = text_result.get("headline", "")
            img_prompt = (
                f"Marketing graphic for Anytime Fitness Fond du Lac. "
                f"Topic: {topic}. "
                "Anytime Fitness branded — purple (#6A2C91) and white color scheme. "
                "209 N Macy St, Fond du Lac at the bottom."
            )
            img_result = await self.gemini.generate_image(
                prompt=img_prompt,
                aspect_ratio="1:1",
                style="professional marketing graphic",
                headline_overlay=headline or topic[:60],
            )
            if img_result.get("status") == "success":
                media_path = img_result["filepath"]
                post_result = await self.fb.post_photo(
                    image_path=media_path,
                    caption=full_text,
                )
            else:
                logger.warning(f"Image gen failed, posting text only: {img_result.get('error')}")
                post_result = await self.fb.post_text(message=full_text)

        elif content_format == "video":
            # Generate a short promo video with the same headline as the text
            headline = text_result.get("headline", topic[:60])
            vid_prompt = (
                f"Short promotional ad for Anytime Fitness Fond du Lac. "
                f"Main message: {headline}. "
                f"Topic details: {topic}. "
                "TV-commercial quality with energetic music and gym footage."
            )
            vid_result = await self.gemini.generate_extended_video(
                prompt=vid_prompt,
                target_duration=30,
                aspect_ratio="16:9",
            )
            if vid_result.get("status") == "success":
                media_path = vid_result["filepath"]
                post_result = await self.fb.post_video(
                    video_path=media_path,
                    description=full_text,
                )
            else:
                logger.warning(f"Video gen failed, posting text only: {vid_result.get('error')}")
                post_result = await self.fb.post_text(message=full_text)

        else:
            post_result = await self.fb.post_text(message=full_text)

        # Record in history
        record = {
            "post_id": post_result.get("id") or post_result.get("post_id"),
            "topic": topic,
            "style": style,
            "format": content_format,
            "text": full_text[:300],
            "had_media": media_path is not None,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
        }
        self._history.append(record)
        _save_history(self._history)

        return {
            "post_id": record["post_id"],
            "topic": topic,
            "style": style,
            "format": content_format,
            "text": full_text[:200],
            "had_image": media_path is not None,
            "published_at": record["published_at"],
            "fb_result": post_result,
        }

    # ── Manual trigger (for API) ─────────────────────────────

    async def trigger_now(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Manually trigger a single autopilot post right now."""
        return await self.generate_and_publish(force_topic=topic)

    def get_history(self, limit: int = 20, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return publish history, optionally filtered by date (YYYY-MM-DD)."""
        if date:
            filtered = [h for h in self._history if h.get("date") == date]
        else:
            filtered = list(self._history)
        return filtered[-limit:]

    # ── Day Queue — generate all posts up front ──────────────

    def get_day_queue(self) -> Dict[str, Any]:
        """Return the current day queue."""
        return dict(self._day_queue) if self._day_queue else {}

    async def generate_day_queue(self) -> Dict[str, Any]:
        """Generate all posts for today up front and store them in the day queue.
        Each post gets AI-generated text + image/video. Posts publish at their
        scheduled window times. Returns the full queue for preview."""

        today_date = datetime.now().strftime("%Y-%m-%d")
        today_weekday = str(datetime.now().weekday())
        windows = self._config["posting_windows"]
        themes = self._config.get("daily_themes", DEFAULT_DAILY_THEMES)
        topics = themes.get(today_weekday, themes.get("0", DEFAULT_DAILY_THEMES["0"]))
        styles = self._config.get("styles", DEFAULT_STYLES)
        weights = self._config.get("format_weights", DEFAULT_FORMAT_WEIGHTS)

        # Shuffle topics so each window gets a unique one
        available_topics = list(topics)
        random.shuffle(available_topics)

        posts = []
        for i, window in enumerate(windows):
            topic = available_topics[i % len(available_topics)]
            style = styles[i % len(styles)]

            # Content format based on weights
            roll = random.random()
            image_threshold = weights.get("image", 0.55)
            text_threshold = image_threshold + weights.get("text", 0.25)
            if roll < image_threshold:
                content_format = "image"
            elif roll < text_threshold:
                content_format = "text"
            else:
                content_format = "video"

            window_key = f"{window['hour']:02d}:{window['minute']:02d}"
            window_label = window.get("label", window_key)

            logger.info(f"Generating queue post {i+1}/{len(windows)}: "
                        f"window={window_key}, topic='{topic[:50]}...', format={content_format}")

            try:
                # Generate text
                text_result = await self.gemini.generate_post_text(
                    topic=topic, style=style, platform="facebook",
                )
                post_text = text_result.get("emoji_enhanced") or text_result.get("main_text", "")
                hashtags = text_result.get("hashtags", [])
                cta = text_result.get("call_to_action", "")

                full_text = post_text
                if cta:
                    full_text += f"\n\n{cta}"
                if hashtags:
                    full_text += "\n\n" + " ".join(f"#{h.lstrip('#')}" for h in hashtags)

                # Generate media if needed
                media_path = None
                if content_format == "image":
                    headline = text_result.get("headline", "")
                    img_prompt = (
                        f"Marketing graphic for Anytime Fitness Fond du Lac. "
                        f"Topic: {topic}. "
                        "Anytime Fitness branded — purple (#6A2C91) and white color scheme. "
                        "209 N Macy St, Fond du Lac at the bottom."
                    )
                    img_result = await self.gemini.generate_image(
                        prompt=img_prompt, aspect_ratio="1:1",
                        style="professional marketing graphic",
                        headline_overlay=headline or topic[:60],
                    )
                    if img_result.get("status") == "success":
                        media_path = img_result["filepath"]
                    else:
                        logger.warning(f"Image gen failed for window {window_key}, will post text only")
                        content_format = "text"

                elif content_format == "video":
                    headline = text_result.get("headline", topic[:60])
                    vid_prompt = (
                        f"Short promotional ad for Anytime Fitness Fond du Lac. "
                        f"Main message: {headline}. Topic details: {topic}. "
                        "TV-commercial quality with energetic music and gym footage."
                    )
                    vid_result = await self.gemini.generate_extended_video(
                        prompt=vid_prompt, target_duration=30, aspect_ratio="16:9",
                    )
                    if vid_result.get("status") == "success":
                        media_path = vid_result["filepath"]
                    else:
                        logger.warning(f"Video gen failed for window {window_key}, will post text only")
                        content_format = "text"

                # Build a URL-safe media reference for the frontend
                media_url = None
                if media_path:
                    media_filename = os.path.basename(media_path)
                    media_url = f"/uploads/generated/{media_filename}"

                posts.append({
                    "window_key": window_key,
                    "window_label": window_label,
                    "window_hour": window["hour"],
                    "window_minute": window["minute"],
                    "topic": topic,
                    "style": style,
                    "format": content_format,
                    "full_text": full_text,
                    "text_preview": full_text[:500],
                    "media_path": media_path,
                    "media_url": media_url,
                    "status": "queued",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                })
                logger.info(f"✅ Queue post {i+1} generated ({content_format}) for {window_key}")

            except Exception as e:
                logger.error(f"Failed to generate queue post for {window_key}: {e}")
                posts.append({
                    "window_key": window_key,
                    "window_label": window_label,
                    "window_hour": window["hour"],
                    "window_minute": window["minute"],
                    "topic": topic,
                    "style": style,
                    "format": "text",
                    "full_text": f"[Generation failed: {e}]",
                    "text_preview": f"[Generation failed: {e}]",
                    "media_path": None,
                    "status": "failed",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                })

        self._day_queue = {
            "date": today_date,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total": len(posts),
            "posts": posts,
        }
        _save_day_queue(self._day_queue)
        logger.info(f"✅ Day queue generated: {len(posts)} posts for {today_date}")
        return self._day_queue
