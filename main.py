import time

# ── Boot delay: lets hardware stabilise on cold power-up ──
time.sleep(5)

import socket
import wifi
import sensors
import webpage
import mqtt
import ntp
import display
from config import READ_INTERVAL, WARMUP_SECONDS, WEB_PORT

# ── Show splash screen immediately ───────────────────────
display.splash()

# ── Connect to WiFi ───────────────────────────────────────
wifi.connect()

# ── Sync time via NTP ─────────────────────────────────────
ntp.sync()
last_ntp_sync = time.time()

# ── Connect to MQTT broker ────────────────────────────────
mqtt.connect()

# ── Warm up CO2 sensor ────────────────────────────────────
print(f"Warming up MH-Z19B for {WARMUP_SECONDS}s...")
time.sleep(WARMUP_SECONDS)

# ── Shared sensor state ───────────────────────────────────
latest = {"co2": None, "temp": None, "humidity": None, "updated": "never"}

# ── Start web server ──────────────────────────────────────
addr = socket.getaddrinfo("0.0.0.0", WEB_PORT)[0][-1]
srv  = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(addr)
srv.listen(1)
print(f"Web server running on port {WEB_PORT}")

last_read    = 0
last_display = 0

while True:
    now = time.time()

    # ── Re-sync NTP once every 24 hours ───────────────────
    if ntp.should_resync(last_ntp_sync):
        ntp.sync()
        last_ntp_sync = time.time()

    # ── Send MQTT keepalive ping ───────────────────────────
    mqtt.ping()

    # ── Read sensors every READ_INTERVAL seconds ──────────
    if now - last_read >= READ_INTERVAL:
        co2       = sensors.read_co2()
        temp, hum = sensors.read_sht30()

        latest["co2"]      = co2
        latest["temp"]     = temp
        latest["humidity"] = hum
        t = ntp.now()
        latest["updated"]  = t["time"]

        print(f"CO2: {co2} ppm | Temp: {temp}°C | Humidity: {hum}% | {t['time']}")

        # ── Publish to Home Assistant via MQTT ────────────
        mqtt.publish(co2, temp, hum)

        last_read = now

    # ── Update display every READ_INTERVAL seconds ────────
    if now - last_display >= READ_INTERVAL:
        t = ntp.now()
        from sensors import co2_status
        label, _ = co2_status(latest["co2"])
        display.draw(
            co2      = latest["co2"],
            temp     = latest["temp"],
            humidity = latest["humidity"],
            time_str = t["time"],
            date_str = t["date"],
            label    = label,
        )
        last_display = now

    # ── Handle web requests ───────────────────────────────
    try:
        srv.settimeout(1)
        conn, _ = srv.accept()
        conn.recv(1024)
        html = webpage.build(latest)
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)
        conn.close()
    except OSError:
        pass
