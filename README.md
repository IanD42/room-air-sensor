# Room Air Quality Sensor

ESP32 MicroPython project measuring CO2, temperature and humidity.

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
