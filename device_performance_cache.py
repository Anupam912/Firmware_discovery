import time

device_performance_cache = {}

def update_device_performance(ip, response_time):
    """Update the performance metrics for the device."""
    if ip not in device_performance_cache:
        device_performance_cache[ip] = {
            'response_times': [],
            'average_response_time': None,
            'last_updated': time.time()
        }
    
    device_performance_cache[ip]['response_times'].append(response_time)
    
    # Update the average response time
    avg_response_time = sum(device_performance_cache[ip]['response_times']) / len(device_performance_cache[ip]['response_times'])
    device_performance_cache[ip]['average_response_time'] = avg_response_time

    # Update the last updated timestamp
    device_performance_cache[ip]['last_updated'] = time.time()


def get_dynamic_timeout(ip):
    """Get a dynamic timeout based on the device's average response time."""
    device_data = device_performance_cache.get(ip)
    if device_data:
        # Invalidate cache if older than 1 day
        if time.time() - device_data['last_updated'] > 86400:
            return 5  # Default timeout if the cache is stale
        if device_data['average_response_time']:
            return device_data['average_response_time'] * 2  # Use 2x the average response time as timeout
    return 5  # Default timeout if no historical data is available

def get_dynamic_retries(ip):
    """Get dynamic retry limits based on device performance."""
    device_data = device_performance_cache.get(ip)
    if device_data:
        # Invalidate cache if older than 1 day
        if time.time() - device_data['last_updated'] > 86400:
            return 3  # Default retries if the cache is stale
        if device_data['average_response_time']:
            if device_data['average_response_time'] > 2:  # If response time is slow
                return 2  # Reduce retries for slow devices
    return 3  # Default retry limit

def clear_performance_cache():
    """Clear the entire device performance cache manually."""
    device_performance_cache.clear()
    print("Device performance cache cleared.")
