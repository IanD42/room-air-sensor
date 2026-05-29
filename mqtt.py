import json
import time
from umqtt.simple import MQTTClient
from config import (MQTT_BROKER, MQTT_PORT, MQTT_USER,
                    MQTT_PASSWORD, MQTT_CLIENT)

# ── Topic helpers ─────────────────────────────────────────
def _state_topic(sensor):
    return f"homeassistant/sensor/{MQTT_CLIENT}/{sensor}/state"

def _config_topic(sensor):
    return f"homeassistant/sensor/{MQTT_CLIENT}/{sensor}/config"

# ── Sensor definitions ────────────────────────────────────
SENSORS = [
    {"id": "co2",         "name": "Study CO2",         "unit": "ppm", "class": "carbon_dioxide", "icon": "mdi:molecule-co2"},
    {"id": "temperature", "name": "Study Temperature",  "unit": "°C",  "class": "temperature",    "icon": "mdi:thermometer"},
    {"id": "humidity",    "name": "Study Humidity",     "unit": "%",   "class": "humidity",       "icon": "mdi:water-percent"},
]

_client           = None
_discovery_done   = False        # Only publish discovery once
_last_ping        = 0
PING_INTERVAL     = 30           # Send keepalive ping every 30s
KEEPALIVE         = 60           # Must be > PING_INTERVAL

# ── Internal: create a fresh client ──────────────────────
def _make_client():
    return MQTTClient(
        client_id = MQTT_CLIENT,
        server    = MQTT_BROKER,
        port      = MQTT_PORT,
        user      = MQTT_USER,
        password  = MQTT_PASSWORD,
        keepalive = KEEPALIVE,
    )

# ── Internal: publish discovery payloads ─────────────────
def _publish_discovery(c):
    device = {
        "identifiers":  [MQTT_CLIENT],
        "name":         "Study Sensor",
        "model":        "ESP32 + MH-Z19B + SHT30",
        "manufacturer": "DIY",
    }
    for s in SENSORS:
        payload = {
            "name":                s["name"],
            "unique_id":           f"{MQTT_CLIENT}_{s['id']}",
            "state_topic":         _state_topic(s["id"]),
            "unit_of_measurement": s["unit"],
            "device_class":        s["class"],
            "icon":                s["icon"],
            "device":              device,
        }
        c.publish(_config_topic(s["id"]), json.dumps(payload), retain=True)
    print("📡 MQTT discovery published")

# ── Connect (or reconnect) ────────────────────────────────
def connect():
    global _client, _discovery_done, _last_ping
    try:
        c = _make_client()
        c.connect()
        _client     = c
        _last_ping  = time.time()
        print("✅ MQTT connected")
        if not _discovery_done:
            _publish_discovery(c)
            _discovery_done = True
        return True
    except Exception as e:
        print(f"❌ MQTT connect failed: {e}")
        _client = None
        return False

# ── Keepalive ping (call regularly from main loop) ────────
def ping():
    global _client, _last_ping
    if _client is None:
        return
    now = time.time()
    if now - _last_ping >= PING_INTERVAL:
        try:
            _client.ping()
            _last_ping = now
        except Exception as e:
            print(f"⚠️  MQTT ping failed: {e} — will reconnect on next publish")
            _client = None

# ── Publish sensor readings ───────────────────────────────
def publish(co2, temp, humidity):
    global _client
    if _client is None:
        connect()
        if _client is None:
            print("⚠️  MQTT unavailable — skipping publish")
            return

    values = {"co2": co2, "temperature": temp, "humidity": humidity}
    try:
        for s in SENSORS:
            val = values.get(s["id"])
            if val is not None:
                _client.publish(_state_topic(s["id"]), str(val))
        print(f"📤 MQTT published — CO2:{co2} Temp:{temp} Hum:{humidity}")
    except Exception as e:
        print(f"⚠️  MQTT publish failed: {e} — reconnecting")
        _client = None
        connect()
