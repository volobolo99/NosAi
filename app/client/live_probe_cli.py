"""CLI for safe observation and the first bounded NosTale live pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapter_runtime import TelemetryRecorder, run_live_pilot
from .nostale_windows import NosTaleClientError, WindowsNosTaleAdapter


def run_probe(adapter: WindowsNosTaleAdapter) -> dict[str, Any]:
    result: dict[str, Any] = {
        "connected": False,
        "state_read": False,
        "process_names": list(adapter.process_names),
        "observation_only": True,
        "action_transport": "disabled",
    }
    try:
        result["connected"] = adapter.check_connection()
        if result["connected"]:
            result["state"] = adapter.read_state().payload
            result["state_read"] = True
    except NosTaleClientError as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe or pilot a running NosTale client")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--pilot", action="store_true", help="run the bounded observe/decide/act/learn loop")
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--arm-actions", action="store_true", help="explicitly enable two movement actions")
    parser.add_argument("--telemetry", type=Path, default=Path("artifacts/live_pilot/telemetry.jsonl"))
    parser.add_argument("--frames", type=Path, default=Path("artifacts/live_pilot/frames"))
    args = parser.parse_args(argv)

    adapter = WindowsNosTaleAdapter()
    if args.pilot:
        records = run_live_pilot(
            adapter,
            TelemetryRecorder(args.telemetry),
            steps=args.steps,
            interval_s=args.interval,
            armed=args.arm_actions,
            frame_dir=args.frames,
        )
        result = {"pilot": True, "records": len(records), "actions_armed": args.arm_actions}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
        return 0

    result = run_probe(adapter)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"connected: {result['connected']}")
        print(f"state_read: {result['state_read']}")
        print(f"process_names: {', '.join(result['process_names'])}")
        print("observation_only: true")
        print("action_transport: disabled")
        if result.get("state_read"):
            state = result["state"]
            rect = state["window_rect"]
            print(f"pid: {state['pid']}")
            print(f"window: {state['window_title']!r}")
            print(f"rect: {rect['width']}x{rect['height']} @ ({rect['left']}, {rect['top']})")
        elif "error" in result:
            print(f"error: {result['error']['type']}: {result['error']['message']}")
    return 0 if result["connected"] and result["state_read"] else 1
