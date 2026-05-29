from machine import UART, I2C, Pin
import time
from config import CO2_TX_PIN, CO2_RX_PIN, I2C_SCL_PIN, I2C_SDA_PIN, SHT30_ADDR

# ── Hardware init ─────────────────────────────────────────
# UART uses lazy init to avoid cold boot timing issues
_uart = None
_i2c  = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=100000)

_CMD_READ_CO2  = b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'
_CMD_CALIBRATE = b'\xff\x01\x87\x00\x00\x00\x00\x00\x78'
_CMD_ABC_ON    = b'\xff\x01\x79\xa0\x00\x00\x00\x00\xe6'
_CMD_ABC_OFF   = b'\xff\x01\x79\x00\x00\x00\x00\x00\x86'

def _get_uart():
    """Return UART, creating it on first call with settling delay."""
    global _uart
    if _uart is None:
        print("Initialising CO2 UART...")
        time.sleep_ms(500)   # Let power rails settle on cold boot
        _uart = UART(2, baudrate=9600, tx=CO2_TX_PIN, rx=CO2_RX_PIN)
        time.sleep_ms(200)
        # Flush any garbage in buffer on first init
        if _uart.any():
            _uart.read(_uart.any())
        print("CO2 UART ready")
    return _uart

# ── CO2 ───────────────────────────────────────────────────
def read_co2():
    """Returns CO2 in ppm or None on failure."""
    uart = _get_uart()
    uart.write(_CMD_READ_CO2)
    time.sleep_ms(150)       # Slightly longer wait for cold boot stability
    if uart.any() >= 9:
        r = uart.read(9)
        if r and r[0] == 0xFF and r[1] == 0x86:
            return (r[2] << 8) | r[3]
    return None

# ── Calibration ───────────────────────────────────────────
def calibrate_zero():
    """
    Calibrate CO2 sensor zero point to 400ppm.
    IMPORTANT: Only run after sensor has been in fresh outdoor
    air for at least 20 minutes with stable readings.
    """
    uart = _get_uart()
    print("⚠️  Sending zero point calibration command (400ppm baseline)...")
    uart.write(_CMD_CALIBRATE)
    time.sleep_ms(100)
    print("✅ Calibration command sent — sensor baseline set to 400ppm")
    print("   Allow 5 minutes for readings to stabilise")

def set_abc(enabled=True):
    """
    Enable or disable Auto Baseline Correction (ABC).
    ABC assumes sensor sees fresh air (400ppm) for at least
    1 hour every 24 hours. Disable if sensor is in a permanently
    occupied room with no fresh air periods.
    """
    uart = _get_uart()
    if enabled:
        uart.write(_CMD_ABC_ON)
        print("✅ ABC (Auto Baseline Correction) enabled")
    else:
        uart.write(_CMD_ABC_OFF)
        print("✅ ABC (Auto Baseline Correction) disabled")
    time.sleep_ms(100)

# ── Temperature & Humidity ────────────────────────────────
def read_sht30():
    """Returns (temp_c, humidity_pct) or (None, None) on failure."""
    try:
        _i2c.writeto(SHT30_ADDR, b'\x2C\x06')
        time.sleep_ms(500)
        d = _i2c.readfrom(SHT30_ADDR, 6)
        temp     = round(-45 + (175 * ((d[0] << 8) | d[1]) / 65535), 1)
        humidity = round(100 * ((d[3] << 8) | d[4]) / 65535, 1)
        return temp, humidity
    except Exception as e:
        print(f"SHT30 error: {e}")
        return None, None

# ── CO2 quality label ─────────────────────────────────────
def co2_status(ppm):
    """Returns (label, hex_colour) for a given CO2 ppm value."""
    if ppm is None:  return "Unknown",   "#888888"
    if ppm < 600:    return "Excellent", "#00c896"
    if ppm < 800:    return "Good",      "#7ec84c"
    if ppm < 1000:   return "Fair",      "#f5c400"
    if ppm < 1500:   return "Poor",      "#ff8c00"
    return                  "Bad",       "#e03030"
