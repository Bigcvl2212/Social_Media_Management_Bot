"""Smoke test runner for InstagramPrivateAPIService.

This does NOT post by default. Use DRY_RUN=0 to actually post.

Env vars:
- IG_USERNAME
- IG_PASSWORD
- IG_2FA_CODE (optional)
- DRY_RUN (default 1)

Usage (PowerShell):
  $env:IG_USERNAME="..."; $env:IG_PASSWORD="..."; python .\scripts\instagram_smoke_test.py
"""

import os
import sys

# Make `app` importable when running from backend/
HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(HERE, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.instagram_private_api_service import (
    InstagramCredentials,
    InstagramPrivateAPIService,
    InstagramSessionStore,
)


def main() -> int:
    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    code = os.environ.get("IG_2FA_CODE")
    dry_run = os.environ.get("DRY_RUN", "1").strip() != "0"

    if not username or not password:
        print("Missing IG_USERNAME/IG_PASSWORD env vars")
        return 2

    store = InstagramSessionStore(base_dir=os.path.join(BACKEND_DIR, "var", "sessions"))
    svc = InstagramPrivateAPIService(store, dry_run=dry_run)

    print(f"Logging in as {username} (dry_run={dry_run})")
    print(svc.login(InstagramCredentials(username=username, password=password, verification_code=code)))
    print("whoami:", svc.whoami())

    # No posting here by default; just prove auth + session persistence.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
