import os
import subprocess

BLOCKED_FILE = "blocked_devices.txt"
SAFE_DEVICES_FILE = "safe_devices.txt"

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

def add_to_safe_list(device):
    """ Add a device to the safe list to prevent future blocking. """
    safe_devices = load_list(SAFE_DEVICES_FILE)
    if device not in safe_devices:
        safe_devices.add(device)
        save_list(SAFE_DEVICES_FILE, safe_devices)
        print(f"✅ Device added to safe list: {device}")

def unblock_ip(ip):
    """ Unblock an IP address from Windows Firewall. """
    print(f"🔓 Unblocking IP: {ip}")
    subprocess.run(f'netsh advfirewall firewall delete rule name="Block {ip}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Successfully unblocked {ip}")

def unblock_selected():
    """ Unblock selected devices from the blocked list. """
    blocked_devices = load_list(BLOCKED_FILE)

    if not blocked_devices:
        print("🚀 No blocked devices found!")
        return

    print("\n🔒 Blocked Devices:")
    blocked_list = list(blocked_devices)
    for i, device in enumerate(blocked_list, start=1):
        print(f"{i}. {device}")

    selected = input("\nEnter the numbers of the devices to unblock (comma-separated): ")
    selected_indexes = [int(x.strip()) for x in selected.split(",") if x.strip().isdigit()]

    updated_blocked_list = set(blocked_devices)

    for index in selected_indexes:
        if 1 <= index <= len(blocked_list):
            device_info = blocked_list[index - 1]
            ip = device_info.split(" - ")[0].strip()
            unblock_ip(ip)
            add_to_safe_list(device_info)
            updated_blocked_list.remove(device_info)

    save_list(BLOCKED_FILE, updated_blocked_list)
    print("\n✅ Unblocking complete! The devices won’t be blocked again.")

if __name__ == "__main__":
    unblock_selected()
