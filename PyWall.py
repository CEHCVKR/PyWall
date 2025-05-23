import os
import time
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor

BLOCKED_FILE = "blocked_devices.txt"
SAFE_DEVICES_FILE = "safe_devices.txt"
MODE = "SMART"  # Change to "STRICT" for Method-II

known_macs = {
    "50-5a-65-f7-b0-29",  # CEHCVKR
    "4e-73-bf-1a-1e-97",  # Venkat
    "bc-9d-4e-e1-6d-9b",  # Example router
}

def normalize_mac(mac):
    return mac.lower().replace(":", "-")

def load_list(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return {line.strip() for line in f.readlines()}
    return set()

def save_list(filename, data):
    with open(filename, "w") as f:
        for item in data:
            f.write(item + "\n")

def is_admin():
    try:
        return os.getuid() == 0  # Linux-style
    except AttributeError:
        # Windows check
        try:
            output = subprocess.check_output("net session", shell=True, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

import subprocess

def block_ip(ip):
    print(f"🚫 Blocking IP: {ip}")

    commands = [
        f'netsh advfirewall firewall add rule name="Block {ip} Inbound" dir=in action=block remoteip={ip}',
        f'netsh advfirewall firewall add rule name="Block {ip} Outbound" dir=out action=block remoteip={ip}',
        f'netsh advfirewall firewall add rule name="Block {ip} ICMP Inbound" protocol=ICMPv4 dir=in action=block remoteip={ip}',
        f'netsh advfirewall firewall add rule name="Block {ip} ICMP Outbound" protocol=ICMPv4 dir=out action=block remoteip={ip}',
    ]

    success = True
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            success = False

    if success:
        print(f"✅ Successfully blocked all traffic for {ip}")
    else:
        print(f"❌ Failed to block some traffic for {ip}. You may need to run as administrator.")

def get_default_gateway():
    result = subprocess.run("ipconfig /all", capture_output=True, text=True)
    matches = re.findall(r"Default Gateway[ .]*: (\d+\.\d+\.\d+\.\d+)", result.stdout)

    if matches:
        gateway_ip = matches[0]
        print(f"🌐 Detected Default Gateway: {gateway_ip}")
        return gateway_ip

    print("⚠️ No default gateway found via ipconfig. Trying 'route print'...")
    route_result = subprocess.run("route print 0.0.0.0", capture_output=True, text=True)
    route_matches = re.findall(r"\s0.0.0.0\s+\d+\.\d+\.\d+\.\d+\s+(\d+\.\d+\.\d+\.\d+)", route_result.stdout)

    if route_matches:
        gateway_ip = route_matches[0]
        print(f"🌐 Detected Router IP via route print: {gateway_ip}")
        return gateway_ip

    print("❌ No default gateway found. Please check your network connection.")
    return None

def ping_ip(ip):
    subprocess.run(f"ping -n 1 -w 200 {ip} >nul 2>&1", shell=True)

def scan_network():
    router_ip = get_default_gateway()
    if not router_ip:
        print("⚠️ No default gateway detected. Skipping scan.")
        return
    
    subnet_prefix = ".".join(router_ip.split(".")[:3])
    print(f"\n🔍 Scanning subnet: {subnet_prefix}.x  | Mode: {MODE.upper()}")

    print("🧹 Clearing ARP cache...")
    arp_clear = subprocess.run("arp -d *", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if arp_clear.returncode != 0:
        print("❌ Failed to clear ARP cache. Requires admin privileges.")

    safe_devices = load_list(SAFE_DEVICES_FILE)
    blocked_devices = load_list(BLOCKED_FILE)
    unknown_devices = set()

    if MODE.upper() == "SMART":
        with ThreadPoolExecutor(max_workers=500) as executor:
            for i in range(1, 255):
                executor.submit(ping_ip, f"{subnet_prefix}.{i}")
        time.sleep(2)

        arp_output = subprocess.check_output("arp -a", shell=True).decode()
        arp_entries = re.findall(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:-]+)", arp_output)

        for ip, mac in arp_entries:
            normalized_mac = normalize_mac(mac)
            device_info = f"{ip} - {normalized_mac}"

            if mac == "---" or mac.startswith("01-00-5e") or mac == "ff-ff-ff-ff-ff-ff":
                continue

            if normalized_mac not in known_macs and device_info not in safe_devices:
                if device_info not in blocked_devices:
                    block_ip(ip)
                    blocked_devices.add(device_info)
                    unknown_devices.add(device_info)

    elif MODE.upper() == "STRICT":
        # Step 1: Ping all devices first
        with ThreadPoolExecutor(max_workers=500) as executor:
            for i in range(1, 255):
                executor.submit(ping_ip, f"{subnet_prefix}.{i}")
        time.sleep(2)

        # Step 2: Build ARP table
        arp_output = subprocess.check_output("arp -a", shell=True).decode()
        arp_entries = dict(re.findall(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:-]+)", arp_output))
        
        for i in range(1, 255):
            ip = f"{subnet_prefix}.{i}"
            if ip == router_ip:
                continue

            found_safe = False
            for item in safe_devices:
                if item.startswith(ip + " "):
                    found_safe = True
                    break

            if found_safe:
                continue

            # Get MAC if available
            mac = arp_entries.get(ip, "unknown")
            normalized_mac = normalize_mac(mac)
            device_info = f"{ip} - {normalized_mac}"

            if device_info not in blocked_devices:
                block_ip(ip)
                blocked_devices.add(device_info)

    else:
        print("❌ Invalid MODE. Use 'SMART' or 'STRICT'.")
        return

    save_list(BLOCKED_FILE, blocked_devices)

    elapsed_time = time.time() - time.perf_counter() + start_time
    print(f"\n⚡ Scan Complete in {elapsed_time:.2f} seconds ⚡")
    
    if unknown_devices and MODE.upper() == "SMART":
        for device in unknown_devices:
            print(f"⚠️ Unknown Device Detected and Blocked: {device}")
    elif MODE.upper() == "SMART":
        print("✅ No new unknown devices detected.")

if __name__ == "__main__":
    if not is_admin():
        print("❌ This script must be run as Administrator to modify ARP cache and firewall.")
        print("➡️ Right-click your terminal or script and select 'Run as Administrator'.")
        exit(1)

    try:
        while True:
            start_time = time.perf_counter()
            scan_network()
            print("\n🔄 Scanning again in 5 seconds...\n")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🚪 Exiting Network Scanner. Goodbye!")
