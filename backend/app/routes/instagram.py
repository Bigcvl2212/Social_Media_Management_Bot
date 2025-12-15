"""Instagram autopilot endpoints (instagrapi-based).

These endpoints are intentionally minimal and safe:
- Defaults to dry-run from settings
- Never returns credentials
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.services.instagram_autopilot_service import AutopilotConfig, InstagramAutopilotService
from app.services.instagram_private_api_service import InstagramCredentials


router = APIRouter(prefix=f"{settings.API_V1_STR}/instagram", tags=["instagram"])


def _require_creds() -> InstagramCredentials:
    if not settings.IG_USERNAME or not settings.IG_PASSWORD:
        raise HTTPException(status_code=400, detail="IG_USERNAME/IG_PASSWORD not configured")
    return InstagramCredentials(
        username=settings.IG_USERNAME,
        password=settings.IG_PASSWORD,
        verification_code=settings.IG_2FA_CODE,
    )


@router.get("/status")
def status():
    creds = _require_creds()
    cfg = AutopilotConfig(dry_run=settings.IG_DRY_RUN)
    svc = InstagramAutopilotService(creds, session_dir=settings.IG_SESSION_DIR, config=cfg)
    return svc.start()


@router.post("/run-once")
def run_once():
    creds = _require_creds()
    cfg = AutopilotConfig(dry_run=settings.IG_DRY_RUN)
    svc = InstagramAutopilotService(creds, session_dir=settings.IG_SESSION_DIR, config=cfg)
    start = svc.start()
    if not start.get("success"):
        return start

    # Placeholder reply generator: do not auto-reply yet.
    # We will wire AI reply generation in the next step.
    def reply_generator(_comment):
        return None

    return svc.run_once(reply_generator)
