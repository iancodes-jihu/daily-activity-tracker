import json
import psutil
import win32gui
import win32process
import ctypes
from ctypes import wintypes
import platform
import time
from datetime import datetime, timedelta


LOG_FILE = "data/activity_log.json"

def get_active_window():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        return process.name()
    except:
        return "Unknown"


# --- AFK detection using Win32 GetLastInputInfo ---
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

def get_idle_seconds():
    if platform.system() != "Windows":
        return 0

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)

    if not user32.GetLastInputInfo(ctypes.byref(li)):
        return 0

    now = kernel32.GetTickCount()
    idle_ms = (now - li.dwTime) & 0xFFFFFFFF
    return idle_ms // 1000


def is_afk(threshold=300):
    return get_idle_seconds() >= threshold
 

def load_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def load_rules():
    with open("app_rules.json", "r") as f:
        return json.load(f)

def classify_app(app_name, rules):
    for category, apps in rules.items():
        if app_name in apps:
            return category
    return "unknown"

def load_target():
    with open("daily_target.json", "r") as f:
        return json.load(f)

def load_offline_schedule():
    with open("offline_schedule.json", "r") as f:
        return json.load(f)
