from network_scanner import scan_network
from tcp_client import get_firmware_version
from packet_sniffer import start_packet_sniffing
from config_loader import load_config
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from coap_discovery import discover_coap_devices
from tcp_client import get_device_status
import time


# Setup logging
logging.basicConfig(filename='firmware_query.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def determine_protocol(device_ip, config):
    for ip_prefix, protocol in config['devices'].items():
        if device_ip.startswith(ip_prefix):
            return protocol
    return config['devices']['default']

def query_device(device_ip, config):
    protocol = determine_protocol(device_ip, config)
    print(f"Querying {device_ip} for firmware version (Protocol: {protocol})...")
    firmware_version = get_firmware_version(device_ip, config, protocol=protocol)

    if firmware_version:
        print(f"Device {device_ip} Firmware Version: {firmware_version}")
        logging.info(f"Device {device_ip} Firmware Version: {firmware_version}")
    else:
        print(f"Could not retrieve firmware version from {device_ip}")
        logging.warning(f"Could not retrieve firmware version from {device_ip}")

def main():
    # Load configuration file
    config = load_config('config.json')
    
    network_cidr = config['network']['cidr']  # Get CIDR from config
    print("Scanning network for devices...")

    # Perform CoAP device discovery
    print("Discovering CoAP devices...")
    discovered_devices = asyncio.run(discover_coap_devices())
    print(f"Discovered devices: {discovered_devices}")
    
    # Step 1: Scan network for active devices
    devices = scan_network(network_cidr)
    logging.info(f"Network scan completed. Active devices found: {devices}")

    # For each discovered device, query its status
    for device_ip in devices:
        print(f"Querying status for device: {device_ip}")
        
        # Call the get_device_status function
        status = get_device_status(device_ip, config)
        
        # Print or log the device status
        if status:
            print(f"Device {device_ip} Status: {status}")
        else:
            print(f"Failed to retrieve status for device {device_ip}")

    # Step 2: Query firmware versions with rate-limiting
    rate_limit_delay = config['tcp_settings'].get('rate_limit_delay', 0.5)  # Delay between requests, in seconds

    with ThreadPoolExecutor() as executor:
        for device_ip in devices:
            executor.submit(query_device, device_ip, config)
            time.sleep(rate_limit_delay)  # Rate limiting to prevent network overload

    # Optional: Start packet sniffing in a separate thread
    print("Starting packet sniffing for network analysis...")
    start_packet_sniffing(interface="eth0")

if __name__ == "__main__":
    main()
