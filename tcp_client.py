import socket
import logging
import time
import ssl
import asyncio
from ssl_cache import check_ssl_cache, update_ssl_cache, clear_ssl_cache
from device_performance_cache import update_device_performance, get_dynamic_timeout, get_dynamic_retries, clear_performance_cache
from coap_client import get_firmware_version_coap
from coap_client import get_device_status_coap

# Setup logging
logging.basicConfig(filename='firmware_query.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(ip, protocol, error, severity="ERROR"):
    """Log errors with additional information about the device type and severity."""
    logging.log(getattr(logging, severity), f"[{protocol}] Error for {ip}: {error}")


def probe_ssl_support(ip, port, timeout=5):
    """
    Probe a device to determine if it supports SSL.
    Returns True if SSL is supported, False otherwise.
    """
    try:
        # Try creating an SSL connection to the device
        context = ssl.create_default_context()
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=ip):
                return True
    except ssl.SSLError:
        # SSL not supported
        return False
    except socket.error:
        # General connection error (couldn't connect)
        return False

# Send request to get firmware version with support for device-specific protocols, retry logic, SSL detection, and timing metrics
def get_firmware_version(ip, config, protocol="generic"):
    commands = {
        "generic": "GET_FIRMWARE",
        "deviceA": "FETCH_FW_VER",
        "deviceB": "QUERY_FW"
    }

    # Check if CoAP is enabled for the device
    if config['tcp_settings'].get('use_coap', False):
        print(f"Querying {ip} for firmware using CoAP...")
        return asyncio.run(get_firmware_version_coap(ip))
    
    command = commands.get(protocol, "GET_FIRMWARE")
    port = config['tcp_settings']['port']
    retries = config['tcp_settings']['retries']
    ssl_probe_enabled = config['tcp_settings'].get('enable_ssl_probe', False)  # Optional SSL probing

    # Check if the SSL status is cached
    ssl_supported = check_ssl_cache(ip)

    if ssl_supported is None and ssl_probe_enabled:
        # If no cache entry exists, probe for SSL support
        ssl_supported = probe_ssl_support(ip, port)
        update_ssl_cache(ip, ssl_supported)  # Update the cache with the result
        logging.info(f"SSL support for {ip}: {'enabled' if ssl_supported else 'disabled'}")

    use_ssl = ssl_supported if ssl_supported is not None else config['tcp_settings'].get('use_ssl', False)

    # Use dynamic timeouts and retries
    timeout = get_dynamic_timeout(ip)
    retries = get_dynamic_retries(ip)

    backoff_factor = 2  # For exponential backoff in retry logic

    for attempt in range(retries):
        start_time = time.time()  # Start timing
        try:
            # Create a socket connection
            sock = socket.create_connection((ip, port), timeout=5)

            if use_ssl:
                try:
                    # Attempt to wrap the socket with SSL
                    context = ssl.create_default_context()
                    sock = context.wrap_socket(sock, server_hostname=ip)
                except ssl.SSLError as ssl_error:
                    # Fallback to non-SSL if SSL fails
                    log_error(ip, protocol, ssl_error, severity="WARNING")
                    logging.warning(f"SSL handshake failed for {ip}, falling back to non-SSL: {str(ssl_error)}")

            # Send the protocol-specific command to query the firmware version
            sock.sendall(command.encode())

            # Receive and return the response
            firmware_version = sock.recv(1024).decode()

            # Measure elapsed time
            elapsed_time = time.time() - start_time

            # Update performance cache
            update_device_performance(ip, elapsed_time)

            # Log successful query with timing information
            logging.info(f"Successfully received firmware version from {ip}: {firmware_version} in {elapsed_time:.2f} seconds")
            sock.close()
            return firmware_version

        except socket.timeout:
            # Handle timeout specifically (e.g., quick retry)
            log_error(ip, protocol, "Timeout occurred", severity="WARNING")
            logging.warning(f"Timeout occurred for {ip}, retrying...")
            time.sleep(1)  # Retry sooner after timeout

        except ConnectionRefusedError:
            # Handle connection refused differently (e.g., log and do not retry)
            log_error(ip, protocol, e, severity="ERROR")
            logging.error(f"Connection refused by {ip}, aborting further retries.")
            return None

        except (socket.error, ssl.SSLError) as e:
            # Handle other socket or SSL errors (e.g., retry after a delay)
            log_error(ip, protocol, e, severity="WARNING")
            backoff_time = backoff_factor ** attempt  # Exponential backoff
            logging.warning(f"Error occurred for {ip}: {str(e)}, retrying after delay.")
            time.sleep(2)

        if attempt == retries - 1:
            # Log final failure after retries with timing information
            elapsed_time = time.time() - start_time
            log_error(ip, protocol, f"Failed after {retries} attempts", severity="ERROR")
            logging.error(f"Failed to retrieve firmware version from {ip} after {retries} attempts in {elapsed_time:.2f} seconds.")
            return None

def get_device_status(ip, config):
    """Query the device status using CoAP if enabled, otherwise fallback to TCP."""
    
    # Check if CoAP is enabled in the configuration
    if config['tcp_settings'].get('use_coap', False):
        print(f"Querying {ip} for status using CoAP...")
        try:
            return asyncio.run(get_device_status_coap(ip))  # Call CoAP client to fetch status
        except Exception as e:
            print(f"Failed to query {ip} using CoAP: {str(e)}")
    
    # Fallback to another method (e.g., TCP) if CoAP is not enabled or fails
    print(f"CoAP not enabled for {ip}. Falling back to TCP-based status query...")
    return get_device_status_tcp(ip)

def get_device_status_tcp(ip):
    """Fallback function to query status over TCP."""
    # Simulate a TCP-based status query (this should be your existing or custom logic)
    print(f"Querying {ip} for status using TCP...")
    # Example placeholder logic
    try:
        # Implement your TCP logic here, e.g., send a request via TCP
        return "Device status via TCP: online"
    except Exception as e:
        print(f"Failed to query {ip} using TCP: {str(e)}")
        return None

def clear_caches():
    """Manual function to clear all caches."""
    clear_ssl_cache()
    clear_performance_cache()