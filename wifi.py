import network
import time
import machine
from config import WIFI_SSID, WIFI_PASSWORD

def connect():
    """Connect to WiFi. Auto-reboots if connection fails after 30 attempts."""
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)

    # Already connected? (e.g. soft reset)
    if wlan.isconnected():
        print(f"WiFi already connected: {wlan.ifconfig()[0]}")
        return wlan.ifconfig()[0]

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to WiFi", end="")

    for _ in range(30):
        if wlan.isconnected():
            break
        print(".", end="")
        time.sleep(1)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"\n✅ WiFi connected — http://{ip}")
        return ip

    print("\n❌ WiFi failed — rebooting in 5s")
    time.sleep(5)
    machine.reset()
