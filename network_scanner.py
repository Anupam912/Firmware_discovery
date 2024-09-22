import socket
import ipaddress
import threading

# Scan the network to find active devices
def is_device_alive(ip):
    try:
        socket.create_connection((ip, 80), timeout=2)
        return True
    except:
        return False

def scan_network(network_cidr):
    active_devices = []
    network = ipaddress.IPv4Network(network_cidr)
    threads = []

    for ip in network:
        thread = threading.Thread(target=lambda: active_devices.append(str(ip)) if is_device_alive(str(ip)) else None)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return active_devices
