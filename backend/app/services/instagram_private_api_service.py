"""Instagram Private API (unofficial) integration via instagrapi.

This module intentionally supports:
- Session persistence (no repeated login)
- Dry-run mode (generate actions without posting)
- Minimum viable operations: post photo/reel, fetch recent media comments, reply

WARNING: Unofficial APIs carry account risk. Use conservative rate limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import os
import time


logger = logging.getLogger(__name__)


@dataclass
class InstagramCredentials:
    username: str
    password: str
    verification_code: Optional[str] = None


class InstagramSessionStore:
    """Very small local session store.

    Stores instagrapi settings JSON on disk. Keeps secrets out of logs.
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def session_path(self, username: str) -> Path:
        safe = "".join(c for c in username if c.isalnum() or c in ("-", "_", "."))
        return self.base_dir / f"insta_{safe}.json"

    def load(self, username: str) -> Optional[Dict[str, Any]]:
        path = self.session_path(username)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def save(self, username: str, settings_dict: Dict[str, Any]) -> None:
        path = self.session_path(username)
        path.write_text(json.dumps(settings_dict, ensure_ascii=False, indent=2), encoding="utf-8")


class InstagramPrivateAPIService:
    """Wrapper around instagrapi.Client with safe defaults."""

    def __init__(self, session_store: InstagramSessionStore, *, dry_run: bool = True):
        self.session_store = session_store
        self.dry_run = dry_run
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from instagrapi import Client  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "instagrapi is not installed. Install it in backend requirements."
                ) from e
            self._client = Client()
        return self._client

    def login(self, creds: InstagramCredentials) -> Dict[str, Any]:
        """Login using saved session if present; otherwise username/password."""
        cl = self._get_client()

        stored = self.session_store.load(creds.username)
        if stored:
            try:
                cl.set_settings(stored)
                cl.login(creds.username, creds.password, verification_code=creds.verification_code)
                self.session_store.save(creds.username, cl.get_settings())
                return {"success": True, "mode": "session"}
            except Exception as e:
                logger.warning("Session login failed; falling back to fresh login: %s", e)

        cl.login(creds.username, creds.password, verification_code=creds.verification_code)
        self.session_store.save(creds.username, cl.get_settings())
        return {"success": True, "mode": "fresh"}

    def whoami(self) -> Dict[str, Any]:
        cl = self._get_client()
        try:
            account = cl.account_info()
            return {
                "success": True,
                "username": getattr(account, "username", None),
                "pk": getattr(account, "pk", None),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_photo(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Post a photo. In dry-run, returns what would be posted."""
        image_path = os.path.abspath(image_path)
        if self.dry_run:
            return {"success": True, "dry_run": True, "action": "photo_upload", "image_path": image_path, "caption": caption}

        cl = self._get_client()
        media = cl.photo_upload(image_path, caption)
        return {"success": True, "dry_run": False, "media_pk": getattr(media, "pk", None)}

    def post_reel(self, video_path: str, caption: str, *, thumbnail_path: Optional[str] = None) -> Dict[str, Any]:
        """Post a reel/video. In dry-run, returns what would be posted."""
        video_path = os.path.abspath(video_path)
        if thumbnail_path:
            thumbnail_path = os.path.abspath(thumbnail_path)

        if self.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "action": "clip_upload",
                "video_path": video_path,
                "thumbnail_path": thumbnail_path,
                "caption": caption,
            }

        cl = self._get_client()
        media = cl.clip_upload(video_path, caption, thumbnail=thumbnail_path)
        return {"success": True, "dry_run": False, "media_pk": getattr(media, "pk", None)}

    def fetch_recent_comments(self, media_pk: int, amount: int = 25) -> Dict[str, Any]:
        """Fetch comments for a media."""
        cl = self._get_client()
        comments = cl.media_comments(media_pk, amount=amount)
        out = []
        for c in comments:
            out.append({
                "pk": getattr(c, "pk", None),
                "text": getattr(c, "text", None),
                "user": getattr(getattr(c, "user", None), "username", None),
                "created_at": getattr(c, "created_at_utc", None),
            })
        return {"success": True, "comments": out}

    def reply_to_comment(self, media_pk: int, comment_pk: int, text: str) -> Dict[str, Any]:
        """Reply to a comment. In dry-run, returns the planned reply."""
        if self.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "action": "comment_reply",
                "media_pk": media_pk,
                "comment_pk": comment_pk,
                "text": text,
            }

        cl = self._get_client()
        ok = cl.media_comment_reply(media_pk, comment_pk, text)
        return {"success": bool(ok), "dry_run": False}


class ConservativeRateLimiter:
    """Simple per-action limiter to behave more like a human."""

    def __init__(self, min_seconds_between_actions: float = 12.0):
        self.min_seconds_between_actions = float(min_seconds_between_actions)
        self._last_action_ts = 0.0

    def wait(self):
        now = time.time()
        delta = now - self._last_action_ts
        if delta < self.min_seconds_between_actions:
            time.sleep(self.min_seconds_between_actions - delta)
        self._last_action_ts = time.time()
