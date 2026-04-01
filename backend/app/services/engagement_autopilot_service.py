"""
Engagement Autopilot — auto-reply to comments, auto-DM new followers,
auto-like community posts, flag negative comments for human review.
Uses Brand DNA style prompt to keep replies on-brand.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(settings.UPLOAD_DIR) / "engagement_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_INDEX_PATH = _DATA_DIR / "engagement_index.json"


class EngagementAutopilotService:
    """Autonomous engagement: comment replies, DM welcomes, community interaction."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=api_key)
        self._data = self._load_data()

    # ════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ════════════════════════════════════════════════════════════════

    def _load_data(self) -> Dict[str, Any]:
        if _INDEX_PATH.exists():
            try:
                return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt engagement data, starting fresh")
        return {
            "config": {
                "auto_reply_enabled": False,
                "auto_dm_enabled": False,
                "auto_like_enabled": False,
                "flag_negative": True,
                "reply_delay_seconds": 30,
                "dm_welcome_message": "",
                "max_replies_per_hour": 20,
                "max_dms_per_hour": 10,
            },
            "rules": [],
            "history": [],
            "flagged": [],
            "stats": {
                "total_replies": 0,
                "total_dms": 0,
                "total_likes": 0,
                "total_flagged": 0,
                "last_run": None,
            },
        }

    def _save_data(self) -> None:
        _INDEX_PATH.write_text(
            json.dumps(self._data, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  CONFIG
    # ════════════════════════════════════════════════════════════════

    def get_config(self) -> Dict[str, Any]:
        return self._data["config"]

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        cfg = self._data["config"]
        for key in ("auto_reply_enabled", "auto_dm_enabled", "auto_like_enabled",
                     "flag_negative", "reply_delay_seconds", "dm_welcome_message",
                     "max_replies_per_hour", "max_dms_per_hour"):
            if key in updates:
                cfg[key] = updates[key]
        self._save_data()
        return cfg

    # ════════════════════════════════════════════════════════════════
    #  RULES — keyword/trigger-based engagement rules
    # ════════════════════════════════════════════════════════════════

    def get_rules(self) -> List[Dict[str, Any]]:
        return self._data["rules"]

    def add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Add an engagement rule.

        rule: {
            "trigger": "keyword" | "new_follower" | "first_comment" | "question" | "negative",
            "keywords": ["word1", "word2"],  # for keyword triggers
            "action": "reply" | "dm" | "like" | "flag",
            "template": "response template with {name} placeholders",
            "ai_generate": true/false  # use AI to generate response
        }
        """
        rule_id = f"rule_{len(self._data['rules']) + 1}_{datetime.utcnow().strftime('%H%M%S')}"
        rule_rec = {
            "id": rule_id,
            "trigger": rule.get("trigger", "keyword"),
            "keywords": rule.get("keywords", []),
            "action": rule.get("action", "reply"),
            "template": rule.get("template", ""),
            "ai_generate": rule.get("ai_generate", True),
            "enabled": True,
            "created_at": datetime.utcnow().isoformat(),
            "times_triggered": 0,
        }
        self._data["rules"].append(rule_rec)
        self._save_data()
        return rule_rec

    def delete_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self._data["rules"]):
            if r["id"] == rule_id:
                self._data["rules"].pop(i)
                self._save_data()
                return True
        return False

    def toggle_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        for r in self._data["rules"]:
            if r["id"] == rule_id:
                r["enabled"] = not r.get("enabled", True)
                self._save_data()
                return r
        return None

    # ════════════════════════════════════════════════════════════════
    #  PROCESS COMMENTS — analyze and auto-respond
    # ════════════════════════════════════════════════════════════════

    async def process_comments(self, comments: List[Dict[str, Any]],
                                brand_prompt: str = "") -> Dict[str, Any]:
        """Process a batch of comments and generate responses.

        comments: list of {id, message, from_name, post_id, created_time}
        brand_prompt: Brand DNA style prompt for on-brand replies
        """
        cfg = self._data["config"]
        results = {"replied": [], "flagged": [], "skipped": [], "errors": []}

        for comment in comments:
            msg = comment.get("message", "")
            from_name = comment.get("from_name", "someone")
            comment_id = comment.get("id", "")

            # Check if already processed
            if any(h.get("comment_id") == comment_id for h in self._data["history"][-500:]):
                results["skipped"].append({"id": comment_id, "reason": "already_processed"})
                continue

            # Sentiment and intent analysis
            analysis = await self._analyze_comment(msg, from_name)

            # Flag negative comments
            if cfg.get("flag_negative") and analysis.get("sentiment") == "negative":
                flag_rec = {
                    "comment_id": comment_id,
                    "message": msg,
                    "from_name": from_name,
                    "sentiment": "negative",
                    "flagged_at": datetime.utcnow().isoformat(),
                    "reason": analysis.get("reason", "Negative sentiment detected"),
                }
                self._data["flagged"].append(flag_rec)
                self._data["stats"]["total_flagged"] += 1
                results["flagged"].append(flag_rec)
                continue

            # Generate reply if auto_reply is enabled
            if cfg.get("auto_reply_enabled"):
                reply = await self._generate_reply(msg, from_name, analysis, brand_prompt)
                reply_rec = {
                    "comment_id": comment_id,
                    "original": msg,
                    "from_name": from_name,
                    "reply": reply,
                    "sentiment": analysis.get("sentiment"),
                    "intent": analysis.get("intent"),
                    "generated_at": datetime.utcnow().isoformat(),
                    "posted": False,  # actual posting done by caller
                }
                self._data["history"].append(reply_rec)
                self._data["stats"]["total_replies"] += 1
                results["replied"].append(reply_rec)

        # Trim history to last 1000
        if len(self._data["history"]) > 1000:
            self._data["history"] = self._data["history"][-1000:]
        if len(self._data["flagged"]) > 500:
            self._data["flagged"] = self._data["flagged"][-500:]

        self._data["stats"]["last_run"] = datetime.utcnow().isoformat()
        self._save_data()
        return results

    async def _analyze_comment(self, message: str, from_name: str) -> Dict[str, Any]:
        """Quick AI analysis of a comment's sentiment and intent."""
        prompt = f"""Analyze this social media comment. Return JSON only:
{{
  "sentiment": "positive" | "neutral" | "negative",
  "intent": "praise" | "question" | "complaint" | "interest" | "spam" | "general",
  "reason": "brief explanation",
  "needs_response": true/false
}}

Comment by {from_name}: "{message}"
Return ONLY the JSON."""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=200),
            )
            result = self._extract_json(response.text or "")
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Comment analysis failed: {e}")
        return {"sentiment": "neutral", "intent": "general", "needs_response": True}

    async def _generate_reply(self, message: str, from_name: str,
                               analysis: Dict, brand_prompt: str) -> str:
        """Generate an on-brand reply to a comment."""
        intent = analysis.get("intent", "general")

        prompt = f"""{brand_prompt}

You are replying to a comment on your social media post.
Keep replies SHORT (1-2 sentences max), friendly, and on-brand.
Don't be generic — reference what they said.
Don't use excessive emojis unless the brand style says to.

Comment by {from_name}: "{message}"
Comment intent: {intent}

Reply:"""

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=150),
            )
            return (response.text or "").strip().strip('"')
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
            return ""

    # ════════════════════════════════════════════════════════════════
    #  DM WELCOME — generate welcome messages for new followers
    # ════════════════════════════════════════════════════════════════

    async def generate_welcome_dm(self, follower_name: str,
                                   brand_prompt: str = "") -> Dict[str, Any]:
        """Generate a personalized welcome DM for a new follower."""
        cfg = self._data["config"]
        template = cfg.get("dm_welcome_message", "")

        if template:
            # Use template with name substitution
            dm_text = template.replace("{name}", follower_name)
        else:
            # AI generated
            prompt = f"""{brand_prompt}

Generate a SHORT welcome DM (2-3 sentences) for a new follower named {follower_name}.
Be warm, personal, and invite them to check out your content or visit.
Don't be salesy. Don't use excessive emojis.

Message:"""
            try:
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=200),
                )
                dm_text = (response.text or "").strip().strip('"')
            except Exception as e:
                logger.error(f"Welcome DM generation failed: {e}")
                dm_text = f"Hey {follower_name}! Welcome to the page! 💪"

        self._data["stats"]["total_dms"] += 1
        self._save_data()

        return {"follower": follower_name, "message": dm_text}

    # ════════════════════════════════════════════════════════════════
    #  STATS / HISTORY / FLAGGED
    # ════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        return self._data["stats"]

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self._data["history"][-limit:]))

    def get_flagged(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self._data["flagged"][-limit:]))

    def dismiss_flagged(self, comment_id: str) -> bool:
        for i, f in enumerate(self._data["flagged"]):
            if f.get("comment_id") == comment_id:
                self._data["flagged"].pop(i)
                self._save_data()
                return True
        return False

    # ════════════════════════════════════════════════════════════════
    #  UTILITY
    # ════════════════════════════════════════════════════════════════

    @staticmethod
    def _extract_json(text: str):
        text = text.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass
        return None
