from sensors import co2_status
from config import READ_INTERVAL

def _advice(label):
    return {
        "Excellent": "Great air quality — keep it up!",
        "Good":      "Air quality is good",
        "Fair":      "Consider opening a window",
        "Poor":      "Open a window to improve",
        "Bad":       "Ventilate the room now!",
    }.get(label, "")

def build(latest):
    co2      = latest["co2"]
    temp     = latest["temp"]
    humidity = latest["humidity"]
    updated  = latest["updated"]

    co2_display  = f"{co2} ppm"    if co2      is not None else "Warming up..."
    temp_display = f"{temp}&#176;C" if temp     is not None else "--"
    hum_display  = f"{humidity}%"  if humidity is not None else "--"

    label, colour = co2_status(co2)
    bar_pct = min(int((co2 / 2000) * 100), 100) if co2 else 0
    advice  = _advice(label)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="{READ_INTERVAL}">
<title>Room Sensor</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg:      #0e1117;
  --surface: #161b25;
  --border:  #242b38;
  --text:    #e8eaf0;
  --muted:   #5a6278;
  --accent:  {colour};
}}
html, body {{
  width: 100%; height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Mono', monospace;
  overflow: hidden;
}}
.dash {{
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto 1fr 1fr auto;
  gap: 14px;
  padding: 24px;
}}
.dash-header {{
  grid-column: 1 / -1;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}}
.dash-header h1 {{
  font-family: 'Syne', sans-serif;
  font-size: clamp(1.2rem, 3vw, 2rem);
  font-weight: 800;
}}
.dash-header p {{
  font-size: clamp(0.6rem, 1vw, 0.75rem);
  color: var(--muted);
}}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  overflow: hidden;
}}
.card.co2 {{
  grid-column: 1 / -1;
  border-color: var(--accent);
  flex-direction: row;
  align-items: center;
  gap: 24px;
}}
.card-label {{
  font-size: clamp(0.55rem, 0.9vw, 0.7rem);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin-bottom: 8px;
}}
.card-value {{
  font-family: 'Syne', sans-serif;
  font-size: clamp(1.8rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1;
  white-space: nowrap;
}}
.co2-left {{ flex: 0 0 auto; }}
.co2-right {{ flex: 1; min-width: 0; }}
.co2-val {{ color: var(--accent); }}
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(0.6rem, 1vw, 0.75rem);
  color: var(--accent);
  margin-top: 8px;
}}
.badge::before {{
  content: '';
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent);
}}
.bar-track {{
  width: 100%; height: 8px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 6px;
}}
.bar-fill {{
  height: 100%;
  width: {bar_pct}%;
  background: var(--accent);
  border-radius: 99px;
}}
.scale {{
  display: flex;
  justify-content: space-between;
  font-size: clamp(0.5rem, 0.8vw, 0.65rem);
  color: var(--muted);
}}
.advice {{
  font-size: clamp(0.55rem, 0.9vw, 0.7rem);
  color: var(--muted);
  margin-top: 10px;
}}
.quality-val {{
  font-family: 'Syne', sans-serif;
  font-size: clamp(1.4rem, 3.5vw, 2.5rem);
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}}
.dash-footer {{
  grid-column: 1 / -1;
  text-align: center;
  font-size: clamp(0.55rem, 0.9vw, 0.7rem);
  color: var(--muted);
}}
.dash-footer span {{ color: var(--text); }}
</style>
</head>
<body>
<div class="dash">

  <div class="dash-header">
    <h1>Room Sensor</h1>
    <p>Auto-refreshes every {READ_INTERVAL}s</p>
  </div>

  <div class="card co2">
    <div class="co2-left">
      <div class="card-label">Carbon Dioxide</div>
      <div class="card-value co2-val">{co2_display}</div>
      <div class="badge">{label}</div>
    </div>
    <div class="co2-right">
      <div class="bar-track"><div class="bar-fill"></div></div>
      <div class="scale">
        <span>0</span><span>600</span><span>1000</span><span>1500</span><span>2000+ ppm</span>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-label">Temperature</div>
    <div class="card-value">{temp_display}</div>
  </div>

  <div class="card">
    <div class="card-label">Humidity</div>
    <div class="card-value">{hum_display}</div>
  </div>

  <div class="card">
    <div class="card-label">Air Quality</div>
    <div class="quality-val">{label}</div>
    <div class="advice">{advice}</div>
  </div>

  <div class="dash-footer">Last updated: <span>{updated}</span></div>

</div>
</body>
</html>"""
