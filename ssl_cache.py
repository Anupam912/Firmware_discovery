import time

ssl_support_cache = {}

def check_ssl_cache(ip):
    """Check if the SSL support status for the device is already cached and still valid."""
    entry = ssl_support_cache.get(ip)
    if entry:
        cache_timestamp, ssl_supported = entry
        # Invalidate cache if older than 1 day (86400 seconds)
        if time.time() - cache_timestamp > 86400:
            return None
        return ssl_supported
    return None

def update_ssl_cache(ip, ssl_supported):
    """Update the SSL support cache with the result and the current timestamp."""
    ssl_support_cache[ip] = (time.time(), ssl_supported)

def clear_ssl_cache():
    """Clear the entire SSL cache manually."""
    ssl_support_cache.clear()
    print("SSL support cache cleared.")