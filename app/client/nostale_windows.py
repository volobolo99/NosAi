"""Windows observation adapter for a real NosTale client.

This adapter deliberately stops at observation. It detects the real client
process/window and exposes a normalized snapshot, but never injects input,
patches memory, or sends game actions. That keeps the live boundary safe while
we build and validate perception before enabling control.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import subprocess
import time
from dataclasses import dataclass
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


class WindowsNosTaleAdapter:
    """Read-only adapter for a running NosTale Windows client.

    Process names are configurable because Gameforge/Steam distributions can
    differ. The adapter never guesses a process from unrelated windows.
    """

    def __init__(self, process_names: Iterable[str] | None = None) -> None:
        configured = process_names or os.getenv(
            "NOSAI_NOSTALE_PROCESS_NAMES", "NostaleClientX.exe;NostaleClient.exe"
        ).split(";")
        self._process_names = {name.strip().lower() for name in configured if name.strip()}
        if not self._process_names:
            raise ValueError("at least one NosTale process name is required")

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
        for line in output.splitlines():
            fields = [field.strip('"') for field in line.split('","')]
            if len(fields) >= 2 and fields[0].lower() in self._process_names:
                try:
                    pids.add(int(fields[1]))
                except ValueError:
                    continue
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
            windows.append(
                WindowInfo(
                    pid=int(pid.value),
                    title=buffer.value,
                    left=rect.left,
                    top=rect.top,
                    right=rect.right,
                    bottom=rect.bottom,
                )
            )
            return True

        user32.EnumWindows(enum_proc(callback), 0)
        return windows

    def check_connection(self) -> bool:
        return bool(self._windows_for_pids(self._matching_pids()))

    def read_state(self) -> ClientState:
        pids = self._matching_pids()
        windows = self._windows_for_pids(pids)
        if not windows:
            raise NosTaleClientError("no visible NosTale client window found")
        window = windows[0]
        return ClientState(
            tick=time.monotonic_ns(),
            payload={
                "source": "windows_observation",
                "pid": window.pid,
                "process_names": sorted(self._process_names),
                "window_title": window.title,
                "window_rect": {
                    "left": window.left,
                    "top": window.top,
                    "right": window.right,
                    "bottom": window.bottom,
                },
                "observation_only": True,
            },
        )

    def validate_action(self, action: Any) -> bool:
        return action is None

    def close(self) -> None:
        return None
