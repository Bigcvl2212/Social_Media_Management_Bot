"""
Rate limiting middleware for the Social Media Management Bot API.

Implements configurable rate limiting to prevent API abuse and ensure
fair usage across all users and applications.
"""

import time
import os
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import json
import hashlib
from app.core.config import settings


class RateLimiter:
    """
    Redis-based rate limiter with support for multiple rate limit tiers.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize rate limiter with Redis client."""
        self.redis_available = True
        if redis_client is None:
            try:
                redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
            except (redis.RedisError, ConnectionError, AttributeError):
                # Redis not available - disable rate limiting
                self.redis_available = False
                self.redis_client = None
        else:
            self.redis_client = redis_client
    
    def _get_client_id(self, request: Request) -> str:
        """
        Generate a unique client identifier based on IP and user info.
        """
        # Try to get user ID from request (if authenticated)
        user_id = getattr(request.state, "user_id", None)
        
        # Get client IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Create unique identifier
        if user_id:
            identifier = f"user:{user_id}"
        else:
            identifier = f"ip:{client_ip}"
        
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _get_rate_limit_for_user(self, request: Request) -> Tuple[int, int]:
        """
        Determine rate limit based on user tier.
        Returns (requests_per_hour, window_size_seconds)
        """
        # Default rate limit
        default_limit = settings.API_RATE_LIMIT_DEFAULT
        window_size = 3600  # 1 hour in seconds
        
        # Check if user is authenticated and has premium/enterprise tier
        user_tier = getattr(request.state, "user_tier", "default")
        
        if user_tier == "enterprise":
            return settings.API_RATE_LIMIT_ENTERPRISE, window_size
        elif user_tier == "premium":
            return settings.API_RATE_LIMIT_PREMIUM, window_size
        else:
            return default_limit, window_size
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limits.
        Returns True if allowed, raises HTTPException if rate limited.
        """
        # If Redis is not available, allow all requests
        if not self.redis_available or self.redis_client is None:
            return True
            
        client_id = self._get_client_id(request)
        requests_per_hour, window_size = self._get_rate_limit_for_user(request)
        
        # Redis key for this client
        key = f"rate_limit:{client_id}"
        
        try:
            # Get current request count
            current_requests = self.redis_client.get(key)
            
            if current_requests is None:
                # First request - set counter
                self.redis_client.setex(key, window_size, 1)
                return True
            
            current_requests = int(current_requests)
            
            if current_requests >= requests_per_hour:
                # Rate limit exceeded
                ttl = self.redis_client.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": requests_per_hour,
                        "window": f"{window_size // 3600} hour(s)",
                        "retry_after": ttl,
                        "message": f"You have exceeded the rate limit of {requests_per_hour} requests per hour. Please try again in {ttl} seconds."
                    },
                    headers={"Retry-After": str(ttl)}
                )
            
            # Increment counter
            self.redis_client.incr(key)
            
            # Add rate limit headers to response (will be added by middleware)
            request.state.rate_limit_remaining = requests_per_hour - current_requests - 1
            request.state.rate_limit_limit = requests_per_hour
            request.state.rate_limit_reset = int(time.time()) + self.redis_client.ttl(key)
            
            return True
            
        except redis.RedisError as e:
            # If Redis is unavailable, log error but allow request
            # This ensures the API remains functional even if rate limiting fails
            print(f"Rate limiting error: {e}")
            return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware to apply rate limiting to all requests.
    """
    # Skip rate limiting entirely in test environment
    if os.getenv('TESTING') or os.getenv('PYTEST_CURRENT_TEST'):
        response = await call_next(request)
        return response
    
    # Skip rate limiting for health checks and static files
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/static"]
    
    if any(request.url.path.startswith(path) for path in skip_paths):
        response = await call_next(request)
        return response
    
    # Check rate limit
    try:
        await rate_limiter.check_rate_limit(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=e.detail,
            headers=e.headers
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to response
    if hasattr(request.state, "rate_limit_remaining"):
        response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
    
    return response


class RateLimitConfig:
    """Configuration class for rate limiting settings."""
    
    @staticmethod
    def get_rate_limits() -> Dict[str, Dict[str, int]]:
        """Get all configured rate limits."""
        return {
            "default": {
                "requests_per_hour": settings.API_RATE_LIMIT_DEFAULT,
                "description": "Default rate limit for unauthenticated users"
            },
            "premium": {
                "requests_per_hour": settings.API_RATE_LIMIT_PREMIUM,
                "description": "Premium user rate limit"
            },
            "enterprise": {
                "requests_per_hour": getattr(settings, "API_RATE_LIMIT_ENTERPRISE", 50000),
                "description": "Enterprise user rate limit"
            }
        }
    
    @staticmethod
    def get_rate_limit_info() -> Dict[str, any]:
        """Get rate limiting information for API documentation."""
        return {
            "enabled": True,
            "window": "1 hour",
            "tiers": RateLimitConfig.get_rate_limits(),
            "headers": {
                "X-RateLimit-Limit": "Maximum requests per window",
                "X-RateLimit-Remaining": "Remaining requests in current window",
                "X-RateLimit-Reset": "Unix timestamp when window resets"
            },
            "error_response": {
                "status_code": 429,
                "structure": {
                    "error": "Rate limit exceeded",
                    "limit": "Number of requests allowed per window",
                    "window": "Time window duration",
                    "retry_after": "Seconds until requests are allowed again",
                    "message": "Human-readable error message"
                }
            }
        }