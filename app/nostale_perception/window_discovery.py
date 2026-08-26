"""Deterministic, read-only discovery of candidate NosTale windows."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import sys


@dataclass(frozen=True)
class WindowCandidate:
    hwnd: int
    pid: int
    title: str


def discover_windows(title_hint: str = "NosTale") -> list[WindowCandidate]:
    """Return visible top-level windows matching the title hint, newest-free order."""
    if sys.platform != "win32":
        return []

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    enum_windows = user32.EnumWindows
    enum_windows.argtypes = [wintypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
    enum_windows.restype = wintypes.BOOL
    is_window_visible = user32.IsWindowVisible
    get_window_text_length = user32.GetWindowTextLengthW
    get_window_text = user32.GetWindowTextW
    get_window_thread_process_id = user32.GetWindowThreadProcessId

    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    candidates: list[WindowCandidate] = []
    needle = title_hint.casefold().strip()

    @callback_type
    def callback(hwnd: wintypes.HWND, _lparam: int) -> bool:
        if not is_window_visible(hwnd):
            return True
        length = get_window_text_length(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        get_window_text(hwnd, buffer, length + 1)
        title = buffer.value
        if needle and needle not in title.casefold():
            return True
        pid = wintypes.DWORD()
        get_window_thread_process_id(hwnd, ctypes.byref(pid))
        candidates.append(WindowCandidate(int(hwnd), int(pid.value), title))
        return True

    enum_windows(callback, 0)
    return candidates
