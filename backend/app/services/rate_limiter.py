"""Sliding-window IP rate limiter to safeguard SerpApi credit budget."""

import time
import threading
from typing import Dict, List
from fastapi import Request, HTTPException, status
from backend.app.config import settings

class SlidingWindowRateLimiter:
    def __init__(self, limit_per_minute: int = 40):
        self.limit = limit_per_minute
        self.window_seconds = 60
        self._lock = threading.Lock()
        self._requests: Dict[str, List[float]] = {}

    def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._requests.get(client_ip, [])
            # Evict timestamps older than 60s
            valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
            
            if len(valid_timestamps) >= self.limit:
                self._requests[client_ip] = valid_timestamps
                return True
                
            valid_timestamps.append(now)
            self._requests[client_ip] = valid_timestamps
            return False

rate_limiter = SlidingWindowRateLimiter(limit_per_minute=settings.RATE_LIMIT_PER_MINUTE)

def check_rate_limit(request: Request):
    """FastAPI dependency to enforce rate limits per client IP."""
    # A caller can set X-Forwarded-For directly. Only honor it when the socket
    # peer is an explicitly configured reverse proxy.
    peer_ip = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and peer_ip in settings.TRUSTED_PROXY_IPS:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = peer_ip

    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded ({settings.RATE_LIMIT_PER_MINUTE} requests/min). Please try again shortly."
        )
