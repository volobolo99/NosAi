"""Runtime helpers for strict client-adapter integration and live telemetry."""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.client import ClientState
from app.client.nostale_windows import NosTaleClientError, WindowInfo


@dataclass(frozen=True)
class ClientProbeResult:
    connected: bool
    state_valid: bool
    action_valid: bool
    detail: str


def probe_client(adapter: Any) -> ClientProbeResult:
    """Run a non-destructive live probe through the strict adapter contract."""
    if not bool(adapter.check_connection()):
        return ClientProbeResult(False, False, False, "connection check returned false")
    state = adapter.read_state()
    if not isinstance(state, ClientState):
        raise TypeError("client adapter read_state() must return ClientState")
    action_valid = bool(adapter.validate_action(None))
    return ClientProbeResult(True, True, action_valid, "connected; state readable; dry-run validated")


@dataclass(frozen=True)
class PilotAction:
    name: str
    duration_s: float = 0.0


class PilotPolicy(Protocol):
    def choose(self, state: ClientState) -> PilotAction: ...


class ConservativePilotPolicy:
    """Deterministic probe policy, not a learned gameplay policy."""

    def __init__(self) -> None:
        self._step = 0

    def choose(self, state: ClientState) -> PilotAction:
        del state
        self._step += 1
        if self._step == 1:
            return PilotAction("noop")
        return PilotAction("move_left" if self._step % 2 == 0 else "move_right", 0.15)


class TelemetryRecorder:
    """Append-only JSONL dataset for replay and future model training."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


class WindowsPilotInput:
    """Explicitly armed, two-action keyboard transport for the smoke test."""

    KEYS = {"move_left": 0x41, "move_right": 0x44}

    def __init__(self, armed: bool = False) -> None:
        self.armed = armed

    def execute(self, action: PilotAction) -> dict[str, Any]:
        if action.name == "noop":
            return {"executed": False, "reason": "noop"}
        if not self.armed:
            return {"executed": False, "reason": "actions_not_armed"}
        if os.name != "nt":
            raise RuntimeError("live input requires Windows")
        vk = self.KEYS.get(action.name)
        if vk is None:
            raise ValueError(f"unsupported pilot action: {action.name}")
        user32 = ctypes.windll.user32
        user32.keybd_event(vk, 0, 0, 0)
        try:
            time.sleep(max(0.0, min(action.duration_s, 0.5)))
        finally:
            user32.keybd_event(vk, 0, 2, 0)
        return {"executed": True, "action": action.name, "duration_s": action.duration_s}


def capture_client_frame(window: WindowInfo, output_dir: str | Path) -> tuple[str | None, str | None]:
    """Capture the detected client window when optional Pillow support exists."""
    try:
        from PIL import ImageGrab
    except ImportError:
        return None, None
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        image = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
    except (OSError, ValueError):
        return None, None
    path = directory / f"frame_{time.time_ns()}.png"
    image.save(path, format="PNG")
    return str(path), hashlib.sha256(path.read_bytes()).hexdigest()


def run_live_pilot(
    adapter: Any,
    telemetry: TelemetryRecorder,
    *,
    steps: int = 5,
    interval_s: float = 0.5,
    armed: bool = False,
    frame_dir: str | Path = "artifacts/live_pilot/frames",
    policy: PilotPolicy | None = None,
) -> list[dict[str, Any]]:
    """Run observe -> decide -> validate -> act -> record for bounded steps."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if not adapter.check_connection():
        raise NosTaleClientError("NosTale client is not connected")
    policy = policy or ConservativePilotPolicy()
    controller = WindowsPilotInput(armed=armed)
    records: list[dict[str, Any]] = []
    for index in range(steps):
        state = adapter.read_state()
        windows = adapter.find_windows()
        if not windows:
            raise NosTaleClientError("NosTale client window disappeared during pilot")
        window = max(windows, key=lambda item: item.area)
        frame_path, frame_sha256 = capture_client_frame(window, frame_dir)
        action = policy.choose(state)
        valid = bool(adapter.validate_action(None if action.name == "noop" else action.name))
        outcome = controller.execute(action) if valid else {"executed": False, "reason": "invalid_action"}
        record = {
            "schema": "nosai.live_pilot.v1",
            "step": index,
            "timestamp_ns": time.time_ns(),
            "state": state.payload,
            "frame_path": frame_path,
            "frame_sha256": frame_sha256,
            "decision": {"name": action.name, "duration_s": action.duration_s},
            "action_valid": valid,
            "outcome": outcome,
        }
        telemetry.append(record)
        records.append(record)
        if index + 1 < steps:
            time.sleep(max(0.0, interval_s))
    return records
