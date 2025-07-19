"""
ClubOS API Configuration Constants
"""

# ClubOS API Configuration
CLUBOS_BASE_URL = "https://anytime.club-os.com"
CLUBOS_LOGIN_URL = f"{CLUBOS_BASE_URL}/action/Authentication/log-in"
CLUBOS_DASHBOARD_URL = f"{CLUBOS_BASE_URL}/action/Dashboard"
CLUBOS_MEMBER_PROFILE_URL = f"{CLUBOS_BASE_URL}/action/Dashboard/member"
CLUBOS_API_SEND_MESSAGE_URL = f"{CLUBOS_BASE_URL}/action/Api/send-message"
CLUBOS_API_FOLLOW_UP_URL = f"{CLUBOS_BASE_URL}/action/Api/follow-up"

# Default Headers for Browser-like Requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# API Request Headers
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Cache-Control': 'no-cache'
}

# Message Types
MESSAGE_TYPE_SMS = "sms"
MESSAGE_TYPE_EMAIL = "email"

# Default Member ID for Testing (Jeremy Mayo)
DEFAULT_MEMBER_ID = "187032782"

# Session Configuration
SESSION_TIMEOUT = 300  # 5 minutes
REQUEST_TIMEOUT = 30   # 30 seconds

# Authentication Patterns
AUTH_SUCCESS_INDICATORS = [
    "dashboard",
    "member",
    "profile"
]

# Error Patterns
ERROR_PATTERNS = [
    "Something isn't right",
    "unauthorized",
    "invalid",
    "error"
]