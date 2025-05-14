import os
import time
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor

BLOCKED_FILE = "blocked_devices.txt"
SAFE_DEVICES_FILE = "safe_devices.txt"

# MODE: Set to "SMART" or "STRICT"
MODE = "SMART"  # Change to "STRICT" for Method-II

# Define known MAC addresses
known_macs = {
    "50-5a-65-f7-b0-29",  # CEHCVKR
    "4e-73-bf-1a-1e-97",  # Venkat
    "bc-9d-4e-e1-6d-9b",  # Example router
}

def normalize_mac(mac):
    """ Convert MAC addresses to lowercase and replace ':' with '-' for consistency """
    return mac.lower().replace(":", "-")

def load_list(filename):
    """ Load data from a file. """
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return {line.strip() for line in f.readlines()}
    return set()

def save_list(filename, data):
    """ Save data to a file. """
    with open(filename, "w") as f:
        for item in data:
            f.write(item + "\n")

def block_ip(ip):
    """ Block an IP address using Windows Firewall. """
    print(f"🚫 Blocking IP: {ip}")
    subprocess.run(f'netsh advfirewall firewall add rule name="Block {ip}" dir=in action=block remoteip={ip}', shell=True)
    subprocess.run(f'netsh advfirewall firewall add rule name="Block {ip}" dir=out action=block remoteip={ip}', shell=True)
    print(f"✅ Successfully blocked {ip}")

def get_default_gateway():
    """Find the default gateway using multiple methods."""
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
    """Ping a single IP address with a timeout of 200ms."""
    subprocess.run(f"ping -n 1 -w 200 {ip} >nul 2>&1", shell=True)

def scan_network():
    """ Scans and blocks based on selected mode. """
    router_ip = get_default_gateway()
    if not router_ip:
        print("⚠️ No default gateway detected. Skipping scan.")
        return
    
    subnet_prefix = ".".join(router_ip.split(".")[:3])
    print(f"\n🔍 Scanning subnet: {subnet_prefix}.x  | Mode: {MODE.upper()}")

    start_time = time.time()

    print("🧹 Clearing ARP cache...")
    subprocess.run("arp -d *", shell=True)

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

    elapsed_time = time.time() - start_time
    print(f"\n⚡ Scan Complete in {elapsed_time:.2f} seconds ⚡")
    
    if unknown_devices and MODE.upper() == "SMART":
        for device in unknown_devices:
            print(f"⚠️ Unknown Device Detected and Blocked: {device}")
    elif MODE.upper() == "SMART":
        print("✅ No new unknown devices detected.")

if __name__ == "__main__":
    try:
        while True:
            scan_network()
            print("\n🔄 Scanning again in 5 seconds...\n")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🚪 Exiting Network Scanner. Goodbye!")
