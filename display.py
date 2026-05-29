"""ILI9341 portrait display module — rdagger library with xglcd fonts."""
from machine import Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# ── Colours ───────────────────────────────────────────────
C_EXCELLENT = color565(0,   200, 150)
C_GOOD      = color565(126, 200, 76)
C_FAIR      = color565(245, 196, 0)
C_POOR      = color565(255, 140, 0)
C_BAD       = color565(224, 48,  48)
C_MUTED     = color565(90,  98,  120)
C_SURFACE   = color565(60,  50,  40)   # Warm dark grey for cards
C_BORDER    = color565(60,  60,  60)   # Mid grey for dividers
C_WHITE     = color565(232, 234, 240)
C_BLACK     = color565(0,   0,   0)

# ── CO2 advice messages ───────────────────────────────────
ADVICE = {
    "Excellent": "Great air quality!",
    "Good":      "Air quality is good",
    "Fair":      "Consider opening window",
    "Poor":      "Open a window ...",
    "Bad":       "Open a Window NOW!",
    "Unknown":   "Sensor warming up...",
}

def _status_colour(label):
    return {
        "Excellent": C_EXCELLENT,
        "Good":      C_GOOD,
        "Fair":      C_FAIR,
        "Poor":      C_POOR,
        "Bad":       C_BAD,
    }.get(label, C_MUTED)

# ── Init display ──────────────────────────────────────────
_spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
_tft = Display(_spi, dc=Pin(2), cs=Pin(5), rst=Pin(4), width=240, height=320)

# ── Load fonts ────────────────────────────────────────────
# Unispace: labels, advice, date, status
# IBMPlexMono: time, CO2 value, temp, humidity values
_uni = XglcdFont('Unispace12x24.c',    12, 24)
_ibm = XglcdFont('IBMPlexMono12x24.c', 12, 24, 32, 216)

W      = 240
H      = 319   # Max safe y (320px screen, 0-indexed)
FONT_W = 12    # Both fonts 12px wide
FONT_H = 24    # Both fonts 24px tall

# ── Layout constants — adjust these to reposition elements ──
# All y values are top edge of element
Y_TIME      = 6    # HH:MM:SS
Y_DATE      = 34   # Day DD Mon
Y_DIV1      = 62   # Divider below date
Y_CO2_LBL   = 68   # "CARBON DIOXIDE" label
Y_CO2_VAL   = 94   # CO2 value + ppm
Y_STATUS    = 122  # "Excellent" / "Good" etc
Y_BAR       = 152  # Progress bar top
BAR_H       = 15   # Progress bar height
BAR_W       = 200  # Progress bar width
BAR_X       = 20   # Progress bar left edge
             # Scale labels auto-position at Y_BAR + BAR_H + 2
Y_DIV2      = 200  # Divider above cards
Y_CARDS     = 208  # Cards top edge
CARD_H      = 62   # Card height
Y_CARD_LBL  = 215  # TEMP / HUMID label y
Y_CARD_VAL  = 240  # TEMP / HUMID value y
Y_DIV3      = 278  # Divider above advice
Y_ADVICE    = 282  # Advice text y (282+24=306, within 319)

def _cx(text):
    """Return x to centre text horizontally."""
    return max(0, (W - len(text) * FONT_W) // 2)

def _divider(y):
    _tft.draw_hline(20, y, W - 40, C_BORDER)

def _bar(ppm, colour):
    """Draw CO2 progress bar with scale labels below."""
    # Background track
    _tft.fill_rectangle(BAR_X, Y_BAR, BAR_W, BAR_H, C_BLACK)
    # Filled portion
    filled = min(int((ppm / 2000) * BAR_W), BAR_W) if ppm else 0
    if filled:
        _tft.fill_rectangle(BAR_X, Y_BAR, filled, BAR_H, colour)
    # Scale labels 8px below bar
    y_lbl = Y_BAR + BAR_H + 8
    _tft.fill_rectangle(BAR_X, y_lbl, BAR_W, FONT_H, C_BLACK)
    for lbl, pos in [("0", 0), ("1000", 76), ("2000+", 148)]:
        _tft.draw_text(BAR_X + pos, y_lbl, lbl, _uni, C_MUTED)

def draw(co2, temp, humidity, time_str, date_str, label):
    """Full screen redraw with current sensor data."""
    colour = _status_colour(label)
    advice = ADVICE.get(label, "")

    _tft.clear()

    # ── Time & date ───────────────────────────────────────
    _tft.draw_text(_cx(time_str), Y_TIME, time_str, _ibm, C_WHITE)
    _tft.draw_text(_cx(date_str), Y_DATE, date_str, _uni, C_MUTED)
    _divider(Y_DIV1)

    # ── CO2 ───────────────────────────────────────────────
#    _tft.draw_text(_cx("CO2 LEVEL"), Y_CO2_LBL, "CO2 LEVEL", _uni, C_MUTED)
    # "CO" normal, "2" dropped down to simulate subscript
    _tft.draw_text(84, Y_CO2_LBL,      "CO", _uni, C_MUTED)
    _tft.draw_text(108, Y_CO2_LBL + 6, "2",  _uni, C_MUTED)

    if co2 is not None:
        val_str = str(co2)
        ppm_str = " ppm"
        x_start = max(0, (W - (len(val_str) + len(ppm_str)) * FONT_W) // 2)
        _tft.draw_text(x_start,                        Y_CO2_VAL, val_str, _ibm, colour)
        _tft.draw_text(x_start + len(val_str) * FONT_W, Y_CO2_VAL, ppm_str, _uni, colour)
    else:
        _tft.draw_text(_cx("---"), Y_CO2_VAL, "---", _ibm, C_MUTED)

    _tft.draw_text(_cx(label), Y_STATUS, label, _uni, colour)

    # ── Progress bar ──────────────────────────────────────
    _bar(co2, colour)
    _divider(Y_DIV2)

    # ── Temp card (left half) ─────────────────────────────
    _tft.fill_rectangle(8, Y_CARDS, 108, CARD_H, C_SURFACE)
    _tft.draw_text(25,  Y_CARD_LBL, "TEMP.", _uni, C_MUTED)
    if temp is not None:
        _tft.draw_text(25, Y_CARD_VAL, f"{temp}°C", _ibm, C_WHITE)
    else:
        _tft.draw_text(25, Y_CARD_VAL, "--", _ibm, C_MUTED)

    # ── Humidity card (right half) ────────────────────────
    _tft.fill_rectangle(124, Y_CARDS, 108, CARD_H, C_SURFACE)
    _tft.draw_text(141, Y_CARD_LBL, "HUMID.", _uni, C_MUTED)
    if humidity is not None:
        _tft.draw_text(141, Y_CARD_VAL, f"{humidity}%", _ibm, C_WHITE)
    else:
        _tft.draw_text(141, Y_CARD_VAL, "--", _ibm, C_MUTED)

    # ── Advice line ───────────────────────────────────────
    _divider(Y_DIV3)
    _tft.draw_text(_cx(advice), Y_ADVICE, advice, _uni, colour)

def splash():
    """Boot splash screen shown during CO2 warm-up."""
    _tft.clear()
    _tft.draw_text(_cx("ROOM SENSOR"),     94, "ROOM SENSOR",    _uni, C_WHITE)
    _tft.draw_text(_cx("Starting up..."), 122, "Starting up...", _uni, C_MUTED)
    _tft.draw_text(_cx("Warming up CO2"), 150, "Warming up CO2", _uni, C_MUTED)
    _tft.draw_text(_cx("sensor 30s..."),  178, "sensor 30s...",  _uni, C_MUTED)
