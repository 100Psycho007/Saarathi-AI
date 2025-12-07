"""
Simple in-memory rate limiter for API endpoints.
Tracks requests per IP address within a time window.
"""

import time
from typing import Dict

# { ip: [timestamps...] }
_requests_per_ip: Dict[str, list[float]] = {}

# Allow 20 requests per 60 seconds
WINDOW_SECONDS = 60
MAX_REQUESTS = 20


def check_rate_limit(ip: str) -> bool:
    """
    Check if the given IP is within rate limits.
    
    Args:
        ip: Client IP address
        
    Returns:
        True if request is allowed, False if rate limit exceeded
    """
    now = time.time()
    arr = _requests_per_ip.get(ip, [])
    
    # Keep only recent timestamps within the window
    arr = [t for t in arr if now - t < WINDOW_SECONDS]
    
    if len(arr) >= MAX_REQUESTS:
        _requests_per_ip[ip] = arr
        return False
    
    arr.append(now)
    _requests_per_ip[ip] = arr
    return True
