"""NTP time sync with automatic GMT/BST for UK/Wales."""
import ntptime
import time

# ── UK DST rules ──────────────────────────────────────────
# BST (UTC+1): last Sunday in March → last Sunday in October

def _last_sunday(year, month):
    """Return day-of-month for last Sunday in given month."""
    import utime
    # Find last day of month
    if month == 12:
        last_day = 31
    else:
        last_day = (utime.mktime((year, month + 1, 1, 0, 0, 0, 0, 0)) -
                    utime.mktime((year, month,     1, 0, 0, 0, 0, 0))) // 86400
    # Walk back to Sunday (weekday 6)
    t = utime.mktime((year, month, last_day, 1, 0, 0, 0, 0))
    wday = utime.localtime(t)[6]          # 0=Mon … 6=Sun
    return last_day - ((wday - 6) % 7)

def _is_bst(t):
    """Return True if UTC time t falls within UK BST period."""
    year, month, day, hour = t[0], t[1], t[2], t[3]
    bst_start = _last_sunday(year, 3)     # Last Sun in March  01:00 UTC
    bst_end   = _last_sunday(year, 10)    # Last Sun in October 01:00 UTC
    if month > 3  and month < 10:  return True
    if month < 3  or  month > 10:  return False
    if month == 3:  return day > bst_start or (day == bst_start and hour >= 1)
    if month == 10: return day < bst_end   or (day == bst_end   and hour < 1)
    return False

def _offset():
    """Return UTC offset in seconds for current UK time."""
    return 3600 if _is_bst(time.gmtime()) else 0

# ── Public API ────────────────────────────────────────────
_synced = False

def sync():
    """Sync time from NTP. Call once after WiFi connects."""
    global _synced
    try:
        ntptime.settime()
        _synced = True
        t = now()
        print(f"✅ NTP synced — {t['date']} {t['time']}")
    except Exception as e:
        print(f"⚠️  NTP sync failed: {e} — using internal clock")

def now():
    """Return dict with 'time' (HH:MM:SS) and 'date' (Day DD Mon) strings."""
    epoch = time.time() + _offset()
    t = time.gmtime(epoch)
    days   = ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")
    months = ("Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec")
    return {
        "time": f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}",
        "date": f"{days[t[6]]} {t[2]:02d} {months[t[1]-1]}",
    }

def should_resync(last_sync):
    """Return True if 24 hours have passed since last sync."""
    return (time.time() - last_sync) >= 86400
