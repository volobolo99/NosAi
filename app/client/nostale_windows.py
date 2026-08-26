"""Windows adapter for a real NosTale client.

Observation remains non-invasive. The optional pilot action surface is a tiny
allow-list used only by the first smoke-test loop; no memory patching,
injection, packet forgery, or arbitrary process manipulation is performed.
"""
from __future__ import annotations

import csv
import ctypes
import ctypes.wintypes
import os
import subprocess
import time
from dataclasses import dataclass
from io import StringIO
from typing import Any, Iterable

from app.client.adapter import ClientState


class NosTaleClientError(RuntimeError):
    """Raised when the Windows client cannot be observed safely."""


@dataclass(frozen=True)
class WindowInfo:
    pid: int
    title: str
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def area(self) -> int:
        return self.width * self.height


class WindowsNosTaleAdapter:
    """Windows adapter for a running NosTale client.

    Process names are configurable because Gameforge/Steam distributions can
    differ. A connection is considered valid only when a matching process has
    a visible window. The pilot action surface is intentionally tiny and
    explicit so arbitrary input cannot leak through this adapter.
    """

    DEFAULT_PROCESS_NAMES = ("NostaleClientX.exe", "NostaleClient.exe")
    PILOT_ACTIONS = frozenset({"move_left", "move_right"})

    def __init__(self, process_names: Iterable[str] | None = None) -> None:
        if process_names is None:
            configured = os.getenv("NOSAI_NOSTALE_PROCESS_NAMES")
            names = configured.split(";") if configured else self.DEFAULT_PROCESS_NAMES
        else:
            names = process_names
        self._process_names = {name.strip().lower() for name in names if name.strip()}
        if not self._process_names:
            raise ValueError("at least one NosTale process name is required")

    @property
    def process_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._process_names))

    def _matching_pids(self) -> set[int]:
        if os.name != "nt":
            return set()
        try:
            output = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise NosTaleClientError(f"cannot enumerate Windows processes: {exc}") from exc

        pids: set[int] = set()
        try:
            for fields in csv.reader(StringIO(output)):
                if len(fields) < 2 or fields[0].strip().lower() not in self._process_names:
                    continue
                try:
                    pids.add(int(fields[1].strip()))
                except ValueError:
                    continue
        except csv.Error as exc:
            raise NosTaleClientError(f"cannot parse tasklist output: {exc}") from exc
        return pids

    @staticmethod
    def _windows_for_pids(pids: set[int]) -> list[WindowInfo]:
        if os.name != "nt" or not pids:
            return []

        user32 = ctypes.windll.user32
        windows: list[WindowInfo] = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if int(pid.value) not in pids:
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            buffer = ctypes.create_unicode_buffer(max(length + 1, 1))
            user32.GetWindowTextW(hwnd, buffer, len(buffer))
            rect = ctypes.wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True
            windows.append(WindowInfo(int(pid.value), buffer.value, int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)))
            return True

        user32.EnumWindows(enum_proc(callback), 0)
        return windows

    def find_windows(self) -> tuple[WindowInfo, ...]:
        return tuple(self._windows_for_pids(self._matching_pids()))

    def _find_windows(self) -> list[WindowInfo]:
        return list(self.find_windows())

    def check_connection(self) -> bool:
        return bool(self.find_windows())

    def read_state(self) -> ClientState:
        windows = self.find_windows()
        if not windows:
            raise NosTaleClientError("no visible NosTale client window found")
        window = max(windows, key=lambda item: (item.area, item.width, item.height))
        return ClientState(
            tick=time.monotonic_ns(),
            payload={
                "source": "windows_observation",
                "pid": window.pid,
                "process_names": list(self.process_names),
                "window_title": window.title,
                "window_rect": {
                    "left": window.left, "top": window.top, "right": window.right, "bottom": window.bottom,
                    "width": window.width, "height": window.height,
                },
                "observation_only": False,
                "pilot_action_allowlist": sorted(self.PILOT_ACTIONS),
            },
        )

    def validate_action(self, action: Any) -> bool:
        return action is None or action in self.PILOT_ACTIONS

    def close(self) -> None:
        return None
