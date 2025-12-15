"""Autonomous Instagram autopilot: posting + engagement loops.

This is designed to run as a background task/worker.
For safety, default behavior is dry-run unless explicitly disabled.

Responsibilities:
- Log in with session persistence
- Poll recent comments on recent media
- Draft or send replies (AI-generated outside this module)

This keeps platform risk low: conservative rate limiting and small batches.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, List, Optional
import logging

from app.services.instagram_private_api_service import (
    ConservativeRateLimiter,
    InstagramCredentials,
    InstagramPrivateAPIService,
    InstagramSessionStore,
)


logger = logging.getLogger(__name__)


@dataclass
class AutopilotConfig:
    dry_run: bool = True
    min_seconds_between_actions: float = 15.0
    poll_interval_seconds: float = 45.0
    recent_media_limit: int = 5
    comments_per_media: int = 20


class InstagramAutopilotService:
    """Runs simple engagement automation using instagrapi."""

    def __init__(
        self,
        creds: InstagramCredentials,
        session_dir: str,
        config: Optional[AutopilotConfig] = None,
    ):
        self.creds = creds
        self.config = config or AutopilotConfig()
        self._store = InstagramSessionStore(session_dir)
        self._ig = InstagramPrivateAPIService(self._store, dry_run=self.config.dry_run)
        self._limiter = ConservativeRateLimiter(self.config.min_seconds_between_actions)

    def start(self) -> Dict[str, Any]:
        login = self._ig.login(self.creds)
        who = self._ig.whoami()
        if not who.get("success"):
            return {"success": False, "error": who.get("error"), "login": login}
        return {"success": True, "login": login, "whoami": who}

    def run_once(
        self,
        reply_generator: Callable[[Dict[str, Any]], Optional[str]],
    ) -> Dict[str, Any]:
        """One cycle: fetch recent media, poll comments, optionally reply.

        reply_generator receives a comment dict and returns reply text or None.
        """
        cl = self._ig._get_client()  # intentional: single client for this cycle

        media_list = cl.user_medias(cl.user_id, amount=self.config.recent_media_limit)
        results: List[Dict[str, Any]] = []

        for media in media_list:
            media_pk = getattr(media, "pk", None)
            if not media_pk:
                continue

            comments = self._ig.fetch_recent_comments(media_pk, amount=self.config.comments_per_media)
            if not comments.get("success"):
                results.append({"media_pk": media_pk, "success": False, "error": comments.get("error")})
                continue

            handled: List[Dict[str, Any]] = []
            for c in comments.get("comments", []):
                # naive filter: skip empty
                if not c.get("text"):
                    continue

                reply_text = reply_generator(c)
                if not reply_text:
                    continue

                self._limiter.wait()
                res = self._ig.reply_to_comment(media_pk=int(media_pk), comment_pk=int(c["pk"]), text=reply_text)
                handled.append({"comment_pk": c.get("pk"), "reply": reply_text, "result": res})

            results.append({"media_pk": media_pk, "success": True, "handled": handled})

        return {"success": True, "dry_run": self.config.dry_run, "results": results}
