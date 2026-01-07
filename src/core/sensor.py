"""Low-level sensor functions (window tracking, AFK detection)."""
import psutil
import win32gui
import win32process
import ctypes
from ctypes import wintypes
import platform
from datetime import datetime, timedelta


class LASTINPUTINFO(ctypes.Structure):
    """Windows LASTINPUTINFO structure."""
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def get_active_window() -> str:
    """Get the name of the currently active window's process."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()
    except Exception:
        return "Unknown"


def get_idle_seconds() -> int:
    """Get idle time in seconds using Windows GetLastInputInfo."""
    if platform.system() != "Windows":
        return 0

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(LASTINPUTINFO)

        if not user32.GetLastInputInfo(ctypes.byref(li)):
            return 0

        now = kernel32.GetTickCount()
        idle_ms = (now - li.dwTime) & 0xFFFFFFFF
        return idle_ms // 1000
    except Exception:
        return 0


def is_afk(threshold: int = 300) -> bool:
    """Check if user is AFK (idle > threshold seconds)."""
    return get_idle_seconds() >= threshold
