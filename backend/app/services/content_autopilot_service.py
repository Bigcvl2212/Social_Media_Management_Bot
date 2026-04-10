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
import re
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


# ── Default themes (topic directions — NO hardcoded prices/phone/address) ──
# All gym-specific facts (prices, phone, address, promotions, website) are
# injected at generation time by GymContextProvider from gym_profile.json.
# Themes describe the *topic direction* only.  The AI prompt instructs the
# model to pull real facts from the GYM CONTEXT block and NEVER fabricate.
DEFAULT_DAILY_THEMES: Dict[str, List[str]] = {
    "0": [
        "Highlight our top signup promotion — break down the EXACT dollar value of each item included so prospects can see the value. Use ONLY the promotions listed in the GYM CONTEXT",
        "New week kickoff: Walk through what a FIRST VISIT looks like — the tour, the body scan, the initial consult, the plan. Make it feel easy and welcoming so people who are nervous about joining feel comfortable",
        "Monday motivation — share a specific, science-backed benefit of morning workouts (cortisol regulation, EPOC effect, or circadian rhythm alignment). Tie it to 24/7 key fob access",
        "Meal prep Monday: give a specific high-protein recipe with macros (grams of protein, carbs, fat). If we offer custom meal plans, mention them using ONLY the pricing from GYM CONTEXT",
        "Spotlight our group training program — explain what a group session looks like: the structure (warm-up, strength block, conditioning, cooldown), the coaching style, and why it works better than working out alone. Use ONLY real pricing from GYM CONTEXT",
        "The science of consistency: explain why training 3x per week for 12 weeks beats 6x per week for 3 weeks. Reference muscle protein synthesis windows and progressive overload. CTA: our trainers build programs designed for long-term consistency",
    ],
    "1": [
        "Promote our free trial or challenge program — explain what happens during the program: the assessments, the programming, the support. Use ONLY promotions from GYM CONTEXT",
        "Training Tip Tuesday: teach ONE specific exercise with proper form cues — e.g., Romanian deadlift (hinge at hips, bar stays close, feel hamstrings stretch, squeeze glutes at top). Give 3 actionable cues",
        "Training program spotlight — compare our group vs 1-on-1 options with membership included. Use ONLY real pricing from GYM CONTEXT. Do a cost comparison vs paying for gym + separate trainer elsewhere",
        "Transformation spotlight: describe the JOURNEY — what kind of program, how many weeks, what changed, what was hard. Use ANONYMOUS language only (no names). Focus on the process, not just the before/after",
        "Body composition scanning: explain what it measures (skeletal muscle mass, visceral fat, body water, segmental analysis) and why that's more useful than a bathroom scale",
        "What's the difference between group and 1-on-1 training? Break down both: group = accountability + community + structured programming. 1-on-1 = fully customized. Help people pick the right fit",
    ],
    "2": [
        "Mid-week value stack: break down every item in our top signup promotion with its individual retail value. Use ONLY the promotions from GYM CONTEXT",
        "Nutrition deep-dive: explain ONE specific concept (e.g., protein timing, caloric surplus vs deficit, hydration and performance) with real numbers. If we offer meal plans, mention using ONLY GYM CONTEXT pricing",
        "Behind the scenes at our gym — describe the equipment: free weight area, cable machines, cardio floor, functional training zone. Paint a picture so people can visualize training here",
        "Walk through an actual group training session structure: 10-min warm-up, 25-min strength block, 15-min conditioning, 5-min cooldown. Show people what they're signing up for",
        "3 reasons our members choose us over other gyms — focus on SPECIFIC differentiators: 24/7 access, personal training, body scanning, and community feel",
        "Exercise science breakdown: explain ONE training principle (e.g., progressive overload, mind-muscle connection, time under tension, or periodization) and how our trainers apply it",
    ],
    "3": [
        "Anonymous member transformation — describe the starting point, the program, the timeline, and the results WITHOUT using any names. Focus on relatable obstacles they overcame",
        "Training program comparison — break down who each training option is best for. Use ONLY real pricing and program names from GYM CONTEXT",
        "Throwback Thursday: describe a specific type of progress — someone who couldn't do a pull-up and now does sets of 5, or someone who hated mornings and now trains at 5 AM. Keep it anonymous but relatable",
        "Deep dive on our top signup promotion: walk through exactly what's included and what happens at each step. Use ONLY the promotion details from GYM CONTEXT",
        "Trainer expertise spotlight: describe what our coaching staff specializes in — strength training, functional fitness, weight loss programming, nutrition coaching. No names, just expertise and results",
        "Myth-buster: pick a specific fitness myth (e.g., 'lifting heavy makes women bulky', 'you need to do cardio to lose fat') and explain the actual science. Position our trainers as the experts",
    ],
    "4": [
        "Weekend plans? Come check us out — walk-ins welcome. Describe what a walk-in experience looks like: free tour, no pressure, see the facility, ask questions. Use ONLY the address and phone from GYM CONTEXT for the CTA",
        "Friday wins: celebrate weekly progress — explain why tracking small wins (1 more rep, 5 more lbs, better sleep) compounds into massive results. Our trainers track everything for you",
        "FOMO Friday: promote our free trial or challenge — explain what makes it different from a typical free trial. Real coaching, real programming, real community. Use ONLY GYM CONTEXT details",
        "Weekend workout guide: give 4-5 specific bodyweight exercises with sets/reps. Then CTA: want a REAL customized plan? Reference our custom program option using ONLY GYM CONTEXT pricing",
        "Break down the cost of fitness vs the cost of NOT investing in your health. Use our ACTUAL training pricing from GYM CONTEXT — calculate the daily cost",
        "Community callout: we're built for hardworking people — factory workers, nurses, teachers, parents. Our 24/7 access and flexible training schedules fit real lives and real schedules",
    ],
    "5": [
        "Saturday sweat session: describe the energy of a weekend group training class — the camaraderie, the accountability, the post-workout feeling. If we have a free challenge, mention it from GYM CONTEXT",
        "Weekend warrior tip: give a specific recovery protocol — foam rolling sequence, stretching routine, or active recovery workout with sets/reps. Explain WHY recovery matters",
        "Coach expertise feature: describe a specific training methodology our coaches use (e.g., periodized strength training, HIIT programming, functional movement screening). Show expertise, not just enthusiasm",
        "24/7 access deep-dive: paint specific scenarios — single parent training at 5 AM, night shift worker lifting at midnight, college student on a lunch break. Our gym fits YOUR schedule",
        "Weekend full-body circuit: give a specific circuit workout (5 exercises, 3 rounds, specific reps) people can try this weekend. CTA: our trainers build these for you daily",
        "Nutrition for the weekend: give specific tips for staying on track (protein targets, meal timing, hydration goals). If we offer meal plans, mention using ONLY GYM CONTEXT pricing",
    ],
    "6": [
        "Sunday reset: explain how to plan a fitness week — pick 3-4 training days, prep meals, set sleep schedule. Give actual structure, not just 'plan ahead'",
        "Recovery science: explain a specific recovery concept (sleep and muscle protein synthesis, deload weeks, active recovery vs passive rest) with real data",
        "New week starts tomorrow — if you've been thinking about joining, highlight our best signup deal from GYM CONTEXT. Walk through the process: walk in, sign up, start training",
        "Sunday success mindset: explain the compound effect of small daily actions — 1%% better each day = 37x improvement in a year. Tie it to our challenge or training programs from GYM CONTEXT",
        "Prep for Monday: give specific actionable steps — lay out gym clothes, prep 3 meals, fill water bottle, set alarm 30 min earlier. Make it tactical, not motivational fluff",
        "End-of-weekend reflection: the best investment is in yourself. Recap our training options using ONLY the real pricing from GYM CONTEXT. Something for every budget",
    ],
}

# Post styles — varied to keep the feed fresh and engaging
DEFAULT_STYLES = ["promotional", "value-driven", "educational", "authority", "curiosity-hook", "urgency"]

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


# ── Post-generation sanitizer ─────────────────────────────────────────
# Catches AI-fabricated names and low-quality patterns before publishing.
# The AI *will* invent member names despite being told not to. This is
# the last-resort safety net — it must be aggressive, not surgical.

_FAKE_NAMES = (
    "Sarah", "Mike", "Jessica", "Brandon", "Ashley", "Chris", "Lisa",
    "Dave", "Jen", "Amanda", "Josh", "Emily", "Matt", "Rachel", "Tyler",
    "Nicole", "Kevin", "Megan", "Laura", "Brian", "Katie", "Dan",
    "Stephanie", "Andrew", "Heather", "Jason", "Maria", "Ryan", "Kelly",
    "Amy", "Steve", "Tanya", "Tony", "Brittany", "Samantha", "Derek",
    "Tiffany", "Travis", "Lindsey", "Chad", "Missy", "Mark", "John",
    "Jennifer", "David", "Linda", "Robert", "Michelle", "James", "Karen",
    "Alex", "Taylor", "Jordan", "Morgan", "Jamie", "Casey", "Pat",
    "Kim", "Cody", "Becky", "Greg", "Tom", "Jake", "Luke", "Zach",
)

# Match any fake name as a standalone word (case-sensitive, must be capitalised)
_FAKE_NAME_RE = re.compile(
    r'\b(?:' + '|'.join(_FAKE_NAMES) + r')(?:\'s)?\b'
)

# "Meet Sarah," / "Meet Sarah!" / "Meet Sarah." / "Meet Sarah —"
_MEET_NAME_RE = re.compile(
    r'\b[Mm]eet\s+(?:' + '|'.join(_FAKE_NAMES) + r')(?:\'s)?[,\.!\s—\-]',
)

_ANON_REPLACEMENTS = [
    "One of our members",
    "A Fond Du Lac local who trains here",
    "A busy parent in our community",
    "One of our regulars",
    "A member who started right where you are",
    "Someone from the neighborhood",
    "A local who decided to make a change",
]


def sanitize_post_text(text: str) -> str:
    """Remove fabricated member names and replace with anonymous references."""
    if not text:
        return text

    sanitized = text
    changed = False

    # Pass 1: "Meet [Name]" → "Meet one of our members"
    def _replace_meet(m):
        tail_char = m.group(0)[-1]  # keep trailing punctuation
        return "Meet " + random.choice(_ANON_REPLACEMENTS).lower() + tail_char
    sanitized = _MEET_NAME_RE.sub(_replace_meet, sanitized)

    # Pass 2: standalone name or name's → anonymous reference
    def _replace_name(m):
        return random.choice(_ANON_REPLACEMENTS).lower()
    sanitized = _FAKE_NAME_RE.sub(_replace_name, sanitized)

    # Pass 3: fix capitalisation after sentence boundaries
    def _cap_after_boundary(m):
        return m.group(0)[:-1] + m.group(0)[-1].upper()
    sanitized = re.sub(r'(?:^|[.!?]\s+|[\n])\s*[a-z]', _cap_after_boundary, sanitized)

    # Pass 4: fix double-space artifacts from replacements
    sanitized = re.sub(r'  +', ' ', sanitized)

    if sanitized != text:
        changed = True
        logger.warning("Sanitizer removed fabricated member name(s) from post text")

    return sanitized


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
        full_text = sanitize_post_text(queued["full_text"])
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

        # Sanitize: strip fabricated names before publishing
        full_text = sanitize_post_text(full_text)

        # Generate and post
        post_result: Dict[str, Any] = {}
        media_path = None

        # Pull gym name + address from GymContextProvider for media prompts
        _gym_ctx = GymContextProvider.get_context()
        _gym_label = _gym_ctx.get("gym_name", "the gym")
        _gym_addr = _gym_ctx.get("gym_address", "")
        _addr_line = f"Include gym address: {_gym_addr} at the bottom. " if _gym_addr else ""

        if content_format == "image":
            # Extract the headline from generated text so the image matches
            headline = text_result.get("headline", "")
            img_prompt = (
                f"High-end social media marketing graphic for {_gym_label}. "
                f"Topic: {topic}. "
                "Style: clean modern fitness design, bold typography, professional layout. "
                "Brand colors: Anytime Fitness purple (#6A2C91) and white. "
                f"{_addr_line}"
                "NO stock photo people. Use clean geometric shapes, gradients, and bold text. "
                "Make it look like a paid agency designed it — not a Canva template."
            )
            img_result = await self.gemini.generate_image(
                prompt=img_prompt,
                aspect_ratio="1:1",
                style="premium fitness brand marketing graphic",
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
                f"Short promotional ad for {_gym_label}. "
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

                # Sanitize: strip fabricated names before queuing
                full_text = sanitize_post_text(full_text)

                # Generate media if needed
                media_path = None
                # Pull gym name + address from GymContextProvider for media prompts
                _gctx = GymContextProvider.get_context()
                _glabel = _gctx.get("gym_name", "the gym")
                _gaddr = _gctx.get("gym_address", "")
                _gaddr_line = f"Include gym address: {_gaddr} at the bottom. " if _gaddr else ""

                if content_format == "image":
                    headline = text_result.get("headline", "")
                    img_prompt = (
                        f"High-end social media marketing graphic for {_glabel}. "
                        f"Topic: {topic}. "
                        "Style: clean modern fitness design, bold typography, professional layout. "
                        "Brand colors: Anytime Fitness purple (#6A2C91) and white. "
                        f"{_gaddr_line}"
                        "NO stock photo people. Use clean geometric shapes, gradients, and bold text. "
                        "Make it look like a paid agency designed it — not a Canva template."
                    )
                    img_result = await self.gemini.generate_image(
                        prompt=img_prompt, aspect_ratio="1:1",
                        style="premium fitness brand marketing graphic",
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
                        f"Short promotional ad for {_glabel}. "
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
