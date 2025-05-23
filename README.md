
# PyWall: Network Security Script

## Overview

**PyWall** is a network security script designed to monitor your local network, block unauthorized devices, and provide mechanisms for unblocking trusted devices. It operates in two modes: **Smart Mode** and **Strict Mode**, catering to different levels of network protection.

### Features

- **Smart Mode**: Automatically detects and blocks unknown devices based on IP and MAC addresses.
- **Strict Mode**: Blocks all devices in the network, maintaining a whitelist of safe devices.
- **ARP Cache Management**: Clears ARP cache before each scan to ensure accurate device detection.
- **Block and Safe Lists**: Maintains records of blocked and trusted devices.
- **Temporary Unblocking**: Allows temporary unblocking of devices for a limited time (30 minutes).
- **Comprehensive Firewall Rules**: Blocks all traffic (TCP/UDP and ICMP) for unauthorized devices.

## Setup

### Requirements

- **Administrator Privileges**: Necessary for modifying ARP cache and firewall settings.
- **Python 3.x**: Ensure Python 3.x is installed on your system.
- **Windows OS**: Utilizes `netsh` commands specific to Windows for firewall management.
- **Windows Firewall**: Configures Windows Firewall to block or unblock IP addresses.

## Getting Started

### 1. Download the Project

Clone or download the repository to your local machine:

```bash
git clone https://github.com/CEHCVKR/PyWall.git
cd PyWall
```

### 2. Run the Main Script

Execute the `PyWall.py` script to initiate network scanning. The script continuously scans the local network for new devices and blocks any unauthorized devices.

```bash
python PyWall.py
```

#### Modes:

- **Smart Mode**: Default mode that blocks only unknown devices, allowing trusted devices.
- **Strict Mode**: Blocks all devices except those explicitly marked as trusted.

To enable **Strict Mode**, set the `MODE` variable to `"STRICT"` in `PyWall.py`.

## How It Works

1. **Network Scanning**: The script pings all devices in the subnet and builds an ARP table.
2. **Device Detection**: It checks the MAC addresses of connected devices.
   - If a device is not in the safe list, it gets blocked.
3. **Firewall Rules**:
   - Adds rules to block all traffic (TCP/UDP and ICMP) for unauthorized devices.
4. **Lists Management**:
   - **Blocked List** (`blocked_devices.txt`): Records of blocked devices.
   - **Safe List** (`safe_devices.txt`): Records of trusted devices.

## Unblocking Devices

To unblock a device, use the `PyWall_Unblock.py` script. This script allows you to unblock specific devices and add them to the safe list.

Run the script:

```bash
python PyWall_Unblock.py
```

The script will display a list of blocked devices. You can choose devices to unblock by their index.

## Use Cases

- **Unauthorized Device Detection**: Automatically identifies and blocks unauthorized devices on your network.
- **Enhanced Network Security**: Strengthens network security by allowing only trusted devices.
- **ARP Table Management**: Utilizes ARP table entries for accurate device identification.
- **Firewall Management**: Manages firewall rules to block or unblock devices effectively.

## Configuration

### `PyWall.py` Configuration

- **MODE**: Set to `"SMART"` or `"STRICT"` based on desired security level.
- **BLOCKED_FILE**: File path for storing blocked devices (`blocked_devices.txt`).
- **SAFE_DEVICES_FILE**: File path for storing safe devices (`safe_devices.txt`).
- **known_macs**: Set of MAC addresses for known, trusted devices.

### `PyWall_Unblock.py` Configuration

- **BLOCKED_FILE**: File path for blocked devices.
- **SAFE_DEVICES_FILE**: File path for safe devices.

## Notes

- **Run as Administrator**: Required for actions like modifying ARP cache or adding firewall rules.
- **Regular Scanning**: The script scans the network every 5 seconds by default. You can modify this interval in the code.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Chinnapareddy Venkata Karthik Reddy**

- LinkedIn: [https://www.linkedin.com/in/cvkr/](https://www.linkedin.com/in/cvkr/)
- GitHub: [https://github.com/CEHCVKR](https://github.com/CEHCVKR)
