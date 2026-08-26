"""Gated first-contact pilot for a real NosTale Windows client.

The pilot is deliberately conservative: observation and dataset collection are
available by default; game input requires an explicit runtime arm flag. It
captures the real client window, records normalized state/action/outcome
telemetry, and exposes a small deterministic decision policy suitable for the
first closed-loop smoke test.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.client.nostale_windows import NosTaleClientError, WindowInfo, WindowsNosTaleAdapter


class PilotError(RuntimeError):
    """Raised for pilot configuration or transport failures."""


@dataclass(frozen=True)
class PilotAction:
    name: str
    key: str | None = None
    duration_s: float = 0.0


@dataclass(frozen=True)
class PilotObservation:
    timestamp_ns: int
    state: dict[str, Any]
    frame_path: str | None
    frame_sha256: str | None


class DecisionPolicy(Protocol):
    def choose(self, observation: PilotObservation) -> PilotAction: ...


class ConservativeProbePolicy:
    """Make only a tiny, deterministic probe decision after observation.

    The first decision is always no-op. When actions are armed, subsequent
    decisions alternate between short left/right probes. This is intentionally
    not presented as learned gameplay: it exists to validate the full
    observe -> decide -> act -> measure loop and generate training data.
    """

    def __init__(self) -> None:
        self._step = 0

    def choose(self, observation: PilotObservation) -> PilotAction:
        del observation
        self._step += 1
        if self._step == 1:
            return PilotAction("noop")
        return PilotAction("move_left" if self._step % 2 == 0 else "move_right", duration_s=0.15)


class JsonlTelemetryRecorder:
    """Append-only telemetry store suitable for later replay/training."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


class WindowsInputController:
    """Minimal Win32 keyboard transport used only after explicit arming."""

    VK = {"a": 0x41, "d": 0x44}

    def __init__(self, armed: bool = False) -> None:
        self.armed = armed

    def execute(self, action: PilotAction) -> dict[str, Any]:
        if action.name == "noop":
            return {"executed": False, "reason": "noop"}
        if not self.armed:
            return {"executed": False, "reason": "actions_not_armed"}
        if os.name != "nt":
            raise PilotError("live input is only supported on Windows")
        key = action.key or {"move_left": "a", "move_right": "d"}.get(action.name)
        if key not in self.VK:
            raise PilotError(f"unsupported pilot action: {action.name}")
        user32 = ctypes.windll.user32
        vk = self.VK[key]
        user32.keybd_event(vk, 0, 0, 0)
        try:
            time.sleep(max(0.0, min(action.duration_s, 0.5)))
        finally:
            user32.keybd_event(vk, 0, 0x0002, 0)
        return {"executed": True, "key": key, "duration_s": action.duration_s}


def _capture_window(window: WindowInfo, output_dir: Path) -> tuple[str | None, str | None]:
    """Capture the client window when Pillow is installed; otherwise continue."""
    try:
        from PIL import ImageGrab
    except ImportError:
        return None, None

    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        image = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
    except (OSError, ValueError):
        return None, None
    stamp = time.time_ns()
    path = output_dir / f"frame_{stamp}.png"
    image.save(path, format="PNG")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return str(path), digest


class LivePilot:
    """Run a bounded live observe/decide/act/learn smoke test."""

    def __init__(
        self,
        adapter: WindowsNosTaleAdapter,
        telemetry: JsonlTelemetryRecorder,
        policy: DecisionPolicy | None = None,
        input_controller: WindowsInputController | None = None,
        frame_dir: str | Path = "artifacts/live_pilot/frames",
    ) -> None:
        self.adapter = adapter
        self.telemetry = telemetry
        self.policy = policy or ConservativeProbePolicy()
        self.input_controller = input_controller or WindowsInputController(False)
        self.frame_dir = Path(frame_dir)

    def run(self, steps: int = 5, interval_s: float = 0.5) -> list[dict[str, Any]]:
        if steps < 1:
            raise ValueError("steps must be >= 1")
        if not self.adapter.check_connection():
            raise NosTaleClientError("NosTale client is not connected")

        results: list[dict[str, Any]] = []
        for index in range(steps):
            state = self.adapter.read_state()
            windows = self.adapter._find_windows()
            window = max(windows, key=lambda item: item.area)
            frame_path, frame_sha256 = _capture_window(window, self.frame_dir)
            observation = PilotObservation(time.time_ns(), state.payload, frame_path, frame_sha256)
            action = self.policy.choose(observation)
            action_valid = self.adapter.validate_action(None if action.name == "noop" else action.name)
            outcome = self.input_controller.execute(action) if action_valid else {"executed": False, "reason": "invalid_action"}
            record = {
                "schema": "nosai.live_pilot.v1",
                "step": index,
                "timestamp_ns": observation.timestamp_ns,
                "state": observation.state,
                "frame_path": observation.frame_path,
                "frame_sha256": observation.frame_sha256,
                "decision": {"name": action.name, "duration_s": action.duration_s},
                "action_valid": action_valid,
                "outcome": outcome,
            }
            self.telemetry.append(record)
            results.append(record)
            if index + 1 < steps:
                time.sleep(max(0.0, interval_s))
        return results
