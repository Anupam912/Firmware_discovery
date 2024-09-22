# IoT Device Management & Firmware Query System

This project provides a system to remotely query the firmware version and status of devices in your network, using both TCP/IP and CoAP protocols. It is designed for use with constrained IoT devices and supports features like CoAP-based device discovery, device health checks, and firmware management.

## Features

- **Query Firmware Versions**: Query devices using both TCP and CoAP protocols to retrieve firmware versions.
- **Device Discovery**: Discover CoAP-enabled devices using multicast.
- **Device Status Monitoring**: Query the status (e.g., uptime, CPU load) of devices using CoAP or TCP.
- **CoAP and TCP Fallback**: Automatically fallback to TCP queries if CoAP is not supported.
- **SSL Support**: Secure communications using SSL/TLS.
- **Caching and Rate Limiting**: Device query results and SSL status are cached to optimize performance.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [Features Overview](#features-overview)
5. [Testing](#testing)

---

## Installation

### Prerequisites

- Python 3.7+
- Virtual Environment (recommended)
- Install required Python packages:

```bash
pip install -r requirements.txt
# Create virtual environment
python3 -m venv venv
# Activate virtual environment (Linux/macOS)
source venv/bin/activate
# Activate virtual environment (Windows)
venv\Scripts\activate
```

## Usage

Querying Firmware Versions

1. Edit Configuration: Update your config.json file to define your network, devices, and query preferences (TCP, CoAP, SSL).

2. Run the Main Script:

```bash
python main.py
```

### CoAP-Specific Functionality

#### CoAP-based device discovery

```bash
python coap_discovery.py
CoAP-based firmware query:
```

```bash
python coap_client.py
```

### Configuration

config.json Example:

```json
{
    "network": {
        "cidr": "192.168.1.0/24"
    },
    "devices": {
        "192.168.1.": "deviceA",
        "192.168.2.": "deviceB",
        "default": "generic"
    },
    "tcp_settings": {
        "port": 12345,
        "retries": 3,
        "use_ssl": true,
        "use_coap": true,    
        "rate_limit_delay": 0.5
    }
}
```

- CIDR: Define the network range for device scanning.
- use_coap: Toggle CoAP queries on or off.
- use_ssl: Enable SSL/TLS communication.
- rate_limit_delay: Delay between successive queries to avoid overwhelming the network.

## Features Overview

1. Firmware Querying:

    - Uses both CoAP and TCP to query the firmware version of devices.
    - Fallback to TCP if CoAP is not supported by a device.

2. Device Discovery:

    - Discovers CoAP-enabled devices using multicast.
    - Collects device information such as firmware version and status.

3. SSL Support:

    - Queries devices securely over SSL.
    - Cache SSL status to optimize performance by avoiding repeated SSL probing.

4. Error Handling and Retry Mechanism:

    - Implements retry logic with exponential backoff for handling network errors.
    - Skips devices with persistent errors to avoid getting stuck on unresponsive devices.

## Testing

### Unit Tests

Tests can be run using unittest for your device query system. Make sure to activate the virtual environment before running tests.

```bash
# Run tests
python -m unittest discover -s tests
```

Ensure that your tests are located inside the tests/ directory, and include test cases for CoAP, TCP, caching, and SSL functionality.

```python
import unittest
from tcp_client import get_firmware_version

class TestDeviceQuery(unittest.TestCase):

    def test_get_firmware_version_tcp(self):
        # Simulate TCP query test
        result = get_firmware_version('192.168.1.100', config)
        self.assertIsNotNone(result)
```
