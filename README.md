
# PyWall: Network Security Script

## Overview

PyWall is a network security script designed to monitor your local network, block unauthorized devices, and provide mechanisms for unblocking trusted devices. It works in two modes, **Smart Mode** and **Strict Mode**, for different network protection levels.

### Features:
- **Smart Mode**: Automatically detects and blocks unknown devices based on IP and MAC address.
- **Strict Mode**: Blocks all devices in the network and maintains a list of safe devices.
- **ARP Cache Management**: Clears ARP cache before each scan to ensure fresh device detection.
- **Block and Safe Lists**: Keeps track of blocked devices and safe devices that won't be blocked.
- **Temporary Unblocking**: Allows temporary unblocking for a limited time (30 minutes).

---

## Setup

### Requirements
- **Admin Privileges**: To modify the ARP cache and firewall settings, the script must be run as an administrator.
- **Python 3.x**: Make sure Python 3.x is installed on your system.
- **Windows OS**: The script uses `netsh` commands specific to Windows to block/unblock IP addresses.
- **Firewall**: The script configures Windows Firewall to block IPs.

---

## Getting Started

### 1. Download the Project
Clone or download the repository to your local machine.

```bash
git clone https://github.com/CEHCVKR/PyWall.git
cd PyWall
```

### 2. Run the Script (Main Script)
Run the `PyWall.py` script to start the network scanning process. It will continuously scan the local network for new devices and block any unknown devices.

```bash
python PyWall.py
```

#### Modes:
- **Smart Mode**: The default mode that only blocks unknown devices while allowing trusted devices.
- **Strict Mode**: Blocks all devices in the network and only allows trusted devices.

To use **Strict Mode**, change the `MODE` variable to `"STRICT"` in `PyWall.py`.

---

## How It Works

1. **Scanning**: The script scans the network by pinging all devices in the subnet and building an ARP table.
2. **Device Detection**: It checks the MAC addresses of devices connected to the network.
   - If a device is unknown (not in the safe list), it gets blocked.
3. **Lists**:
   - **Blocked List** (`blocked_devices.txt`): Contains the devices that have been blocked.
   - **Safe List** (`safe_devices.txt`): Contains the devices that are trusted and will not be blocked.

---

## Unblocking Devices

To unblock a device, use the `PyWall_Unblock.py` script. This will allow you to unblock a specific device for communication by adding it to the safe list.

Run the script:

```bash
python PyWall_Unblock.py
```

The script will display a list of blocked devices, and you can choose the devices you want to unblock by their index.

---

## Use Cases

- **Unknown Device Detection**: Automatically detects and blocks unauthorized devices from accessing your network.
- **Network Protection**: Enhances network security by blocking devices that are not part of the trusted list.
- **ARP Table Management**: Uses ARP table entries to identify devices, ensuring that only authorized devices are allowed.
- **Firewall Management**: Blocks or unblocks devices by adding or removing firewall rules.

---

## Configuration

### `main.py` Configuration
- **MODE**: Set to `"SMART"` or `"STRICT"` depending on your desired level of security.
- **BLOCKED_FILE**: The file that holds blocked devices' details (`blocked_devices.txt`).
- **SAFE_DEVICES_FILE**: The file that holds the safe devices' details (`safe_devices.txt`).
- **known_macs**: A set of MAC addresses for known, trusted devices (e.g., your own devices, routers).

### `unblock.py` Configuration
- **BLOCKED_FILE**: The file that holds blocked devices' details.
- **SAFE_DEVICES_FILE**: The file to add devices to the safe list.

---

## Notes
- **Run as Administrator**: Some actions, like modifying the ARP cache or adding firewall rules, require administrator privileges.
- **Regular Scanning**: The script scans the network every 5 seconds by default. Modify this interval if necessary in the code.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**CHINNAPAREDDY VENKATA KARTHIK REDDY** 

LinkedIn: [https://www.linkedin.com/in/cvkr/](https://www.linkedin.com/in/cvkr/)  
GitHub: [https://github.com/CEHCVKR](https://github.com/CEHCVKR)

---
