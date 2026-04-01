"""
Facebook / Instagram API Setup — Automated OAuth Flow
=====================================================
Run this script, click "Allow" in the browser, and it handles:
  1. OAuth authorization (opens browser)
  2. Exchanges code for user access token
  3. Lists your Facebook Pages
  4. Gets Page access token
  5. Extends to long-lived (60-day) token
  6. Finds linked Instagram Business Account
  7. Subscribes page to leadgen webhooks
  8. Saves everything to backend/.env

Usage:
    python fb_setup.py
"""

import http.server
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / "backend" / ".env"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"

# ── Permissions ──────────────────────────────────────────────────
# Only request scopes that have been activated in the Meta Developer
# portal under Use Cases.  Start with the basics; the script will
# tell you which ones are missing so you can add them later.
#
# To add more: activate the permission in the portal first, then
# uncomment the line here and re-run this script.
SCOPES = [
    "public_profile",
    "email",
    "business_management",
    # "instagram_basic",  # Needs Instagram use case activated separately
    "pages_show_list",
    "pages_manage_posts",
    "pages_manage_metadata",
    "pages_manage_engagement",
    "pages_read_engagement",
    "pages_read_user_content",
    "read_insights",
]


def _load_env(path: Path) -> dict:
    """Read .env file into a dict."""
    env = {}
    if not path.exists():
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env


def _save_env_value(path: Path, key: str, value: str):
    """Update or append a key=value in .env file."""
    lines = []
    found = False
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped == f"{key}=":
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def _graph_api(endpoint: str, params: dict = None, method: str = "GET") -> dict:
    """Call Facebook Graph API v21.0."""
    base = "https://graph.facebook.com/v21.0"
    url = f"{base}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"\n  ERROR {e.code}: {body}")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"error": {"message": body, "code": e.code}}


def _exchange_code_for_token(app_id: str, app_secret: str, code: str) -> str:
    """Exchange the OAuth code for a short-lived user access token."""
    data = _graph_api("oauth/access_token", {
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })
    if "access_token" in data:
        return data["access_token"]
    print(f"\n  Token exchange failed: {data}")
    sys.exit(1)


def _extend_token(app_id: str, app_secret: str, short_token: str) -> str:
    """Exchange a short-lived token for a 60-day long-lived token."""
    data = _graph_api("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    })
    if "access_token" in data:
        expires = data.get("expires_in", "unknown")
        print(f"  Token extended — expires in {expires} seconds (~{int(expires)//86400} days)" if isinstance(expires, int) else f"  Token extended — expires: {expires}")
        return data["access_token"]
    print(f"\n  Token extension failed: {data}")
    return short_token  # Fall back to short-lived


def _get_pages(user_token: str) -> list:
    """Get list of Facebook Pages the user manages."""
    data = _graph_api("me/accounts", {"access_token": user_token, "limit": 100})
    return data.get("data", [])


def _get_instagram_account(page_id: str, page_token: str) -> str | None:
    """Get the Instagram Business Account linked to a Facebook Page."""
    data = _graph_api(page_id, {
        "fields": "instagram_business_account",
        "access_token": page_token,
    })
    ig = data.get("instagram_business_account")
    return ig.get("id") if ig else None


def _get_long_lived_page_token(page_id: str, user_long_token: str) -> str:
    """Get a page token that never expires (derived from long-lived user token)."""
    data = _graph_api(f"{page_id}", {
        "fields": "access_token",
        "access_token": user_long_token,
    })
    return data.get("access_token", "")


def _subscribe_page_to_leadgen(page_id: str, page_token: str) -> bool:
    """Subscribe the page to leadgen webhooks."""
    data = _graph_api(f"{page_id}/subscribed_apps", {
        "subscribed_fields": "leadgen",
        "access_token": page_token,
    }, method="POST")
    return data.get("success", False)


# ─── OAuth callback server ──────────────────────────────────────────
_auth_code = None
_server_done = threading.Event()


class _OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
            <h1 style="color:#22c55e;">&#10004; Authorization Successful!</h1>
            <p>You can close this tab and go back to VS Code.</p>
            <script>setTimeout(function(){window.close()},3000);</script>
            </body></html>""")
            _server_done.set()
        elif "error" in params:
            error_msg = params.get("error_description", params.get("error", ["Unknown"]))[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
            <h1 style="color:#ef4444;">&#10008; Authorization Failed</h1>
            <p>{error_msg}</p>
            </body></html>""".encode())
            _server_done.set()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress server logs


def _run_oauth_server():
    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _OAuthHandler)
    server.timeout = 120
    while not _server_done.is_set():
        server.handle_request()


# ─── Main flow ──────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Facebook / Instagram API Setup")
    print("=" * 60)

    # Load credentials
    env = _load_env(ENV_FILE)
    app_id = env.get("FACEBOOK_APP_ID", "")
    app_secret = env.get("FACEBOOK_APP_SECRET", "")

    if not app_id or not app_secret:
        print("\n  Missing FACEBOOK_APP_ID or FACEBOOK_APP_SECRET in backend/.env")
        sys.exit(1)

    print(f"\n  App ID: {app_id[:6]}...{app_id[-4:]}")
    print(f"  Redirect URI: {REDIRECT_URI}")
    print(f"  Scopes: {len(SCOPES)} permissions requested")

    # ── Step 1: Start local server and open browser ──
    print("\n[1/7] Opening browser for Facebook authorization...")
    print("      >>> Click 'Continue as [Your Name]' then 'Allow' <<<\n")

    server_thread = threading.Thread(target=_run_oauth_server, daemon=True)
    server_thread.start()

    auth_url = (
        f"https://www.facebook.com/v21.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope={','.join(SCOPES)}&"
        f"response_type=code"
    )

    # Try multiple methods to open the browser on Windows
    opened = False
    try:
        os.startfile(auth_url)  # Windows-native, most reliable
        opened = True
    except Exception:
        try:
            webbrowser.open(auth_url)
            opened = True
        except Exception:
            pass

    if not opened:
        print("\n  Could not open browser automatically.")

    print(f"\n  If the browser didn't open, copy this URL and paste it:\n")
    print(f"  {auth_url}\n")

    # Wait for callback
    _server_done.wait(timeout=120)
    if not _auth_code:
        print("\n  Timed out waiting for authorization. Try again.")
        sys.exit(1)

    print("  Authorization code received!")

    # ── Step 2: Exchange code for token ──
    print("\n[2/7] Exchanging code for access token...")
    short_token = _exchange_code_for_token(app_id, app_secret, _auth_code)
    print(f"  Got short-lived token: {short_token[:15]}...")

    # ── Step 3: Extend to long-lived token ──
    print("\n[3/7] Extending to long-lived token (60 days)...")
    long_token = _extend_token(app_id, app_secret, short_token)

    # ── Step 4: Get Pages ──
    print("\n[4/7] Fetching your Facebook Pages...")
    pages = _get_pages(long_token)
    if not pages:
        print("  No pages found! Make sure your Facebook account manages a Page.")
        sys.exit(1)

    print(f"  Found {len(pages)} page(s):\n")
    for i, page in enumerate(pages):
        print(f"    [{i + 1}] {page['name']}  (ID: {page['id']})")

    # Select page
    if len(pages) == 1:
        selected = pages[0]
        print(f"\n  Auto-selecting: {selected['name']}")
    else:
        while True:
            choice = input(f"\n  Select page number [1-{len(pages)}]: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(pages):
                selected = pages[int(choice) - 1]
                break
            print("  Invalid choice, try again.")

    page_id = selected["id"]
    page_name = selected["name"]

    # ── Step 5: Get never-expiring Page token ──
    print(f"\n[5/7] Getting permanent Page access token for '{page_name}'...")
    page_token = _get_long_lived_page_token(page_id, long_token)
    if not page_token:
        print("  Failed to get page token!")
        sys.exit(1)
    print(f"  Page token: {page_token[:15]}...")

    # ── Step 6: Find Instagram Business Account ──
    print(f"\n[6/7] Looking for Instagram Business Account linked to '{page_name}'...")
    ig_id = _get_instagram_account(page_id, page_token)
    if ig_id:
        print(f"  Instagram Business Account ID: {ig_id}")
    else:
        print("  No Instagram Business Account linked to this page.")
        print("  (You can link one later in Facebook Page Settings → Instagram)")

    # ── Step 7: Subscribe to leadgen webhooks ──
    print(f"\n[7/7] Subscribing '{page_name}' to lead ad webhooks...")
    if _subscribe_page_to_leadgen(page_id, page_token):
        print("  Subscribed to leadgen events!")
    else:
        print("  Could not subscribe (may need App Review for leads_retrieval).")
        print("  We'll set up the webhook endpoint regardless — you can subscribe later.")

    # ── Save to .env ──
    print("\n" + "=" * 60)
    print("  Saving credentials to backend/.env ...")
    _save_env_value(ENV_FILE, "FACEBOOK_PAGE_ID", page_id)
    _save_env_value(ENV_FILE, "FACEBOOK_PAGE_ACCESS_TOKEN", page_token)
    if ig_id:
        _save_env_value(ENV_FILE, "INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id)

    # ── Summary ──
    print("\n  SETUP COMPLETE!")
    print("=" * 60)
    print(f"  Page:           {page_name}")
    print(f"  Page ID:        {page_id}")
    print(f"  Page Token:     {page_token[:20]}...  (never expires)")
    print(f"  Instagram ID:   {ig_id or 'Not linked'}")
    print(f"  Lead Webhooks:  Subscribed")
    print(f"  Saved to:       {ENV_FILE}")
    print("=" * 60)
    print("\n  NEXT STEPS:")
    print("  1. Regenerate your App Secret in Meta Developer portal")
    print("     (Settings → Basic → Reset) since it was in chat")
    print("  2. Update FACEBOOK_APP_SECRET in backend/.env with the new one")
    print("  3. The lead ads webhook endpoint is ready — I'll wire it up next")
    print()


if __name__ == "__main__":
    main()
