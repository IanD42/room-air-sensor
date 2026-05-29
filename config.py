# ── WiFi ──────────────────────────────────────────────────
WIFI_SSID     = "XXXXXX"
WIFI_PASSWORD = "XXXXXX"

# ── MQTT ──────────────────────────────────────────────────
MQTT_BROKER   = "XXXXXX"    # Your Home Assistant IP
MQTT_PORT     = 1883
MQTT_USER     = "XXXXXX"
MQTT_PASSWORD = "XXXXXX"
MQTT_CLIENT   = "Bedroom_CO2_sensor"    # Unique name for this device

# ── Sensor read interval (seconds) ───────────────────────
READ_INTERVAL = 10

# ── MH-Z19B warm-up time on first boot (seconds) ─────────
WARMUP_SECONDS = 30

# ── Web server port ───────────────────────────────────────
WEB_PORT = 80

# ── SHT30 I2C address ────────────────────────────────────
SHT30_ADDR = 0x44

# ── UART pins for MH-Z19B ────────────────────────────────
CO2_TX_PIN = 17
CO2_RX_PIN = 16

# ── I2C pins for SHT30 ───────────────────────────────────
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
