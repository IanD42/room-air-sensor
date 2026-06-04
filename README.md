# Room Air Quality Sensor
ESP32 MicroPython project measuring CO2, temperature and humidity.
All Code developed in conjunction with Claude Code AI
## Hardware
- ESP32 WROOM
- MH-Z19B CO2 sensor
- SHT30 temperature/humidity sensor  
- DollaTek 2.8" ILI9341 TFT display

## Features
- Live TFT display with time, CO2, temperature, humidity
- Web dashboard at http://[device-ip]
- MQTT publishing to Home Assistant
- Auto-discovery in Home Assistant
- UK GMT/BST time sync via NTP

## Setup
1. Copy all files to ESP32 via Thonny
2. Edit config.py with your WiFi and MQTT credentials
3. Power on — connects automatically and starts monitoring

## Files
| File | Purpose |
|---|---|
| main.py | Boot entry point |
| config.py | All settings (add your credentials) |
| wifi.py | WiFi connection |
| sensors.py | MH-Z19B and SHT30 drivers |
| mqtt.py | Home Assistant MQTT |
| ntp.py | UK time sync |
| display.py | TFT screen layout |
| webpage.py | Web dashboard |

## Wiring
MH-Z19B          ESP32
───────          ─────
VIN      ──────  VUSB (5V)
GND      ──────  GND
TXD      ──────  GPIO16
RXD      ──────  GPIO17

SHT30            ESP32
─────            ─────
VCC      ──────  3.3V
GND      ──────  GND
SCL      ──────  GPIO22
SDA      ──────  GPIO21

ILI9341          ESP32
───────          ─────
VCC      ──────  3.3V
GND      ──────  GND
CLK      ──────  GPIO18
MOSI     ──────  GPIO23
RES      ──────  GPIO4
DC       ──────  GPIO2
CS       ──────  GPIO5
BLK      ──────  VUSB (5V)
```
