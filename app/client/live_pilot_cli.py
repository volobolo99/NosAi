"""CLI for the first real-client NosAi smoke test."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from app.client.live_pilot import JsonlTelemetryRecorder, LivePilot, WindowsInputController
from app.client.nostale_windows import WindowsNosTaleAdapter


def main() -> int:
    parser = argparse.ArgumentParser(description="NosAi real NosTale observation/pilot")
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--telemetry", type=Path, default=Path("artifacts/live_pilot/telemetry.jsonl"))
    parser.add_argument("--frames", type=Path, default=Path("artifacts/live_pilot/frames"))
    parser.add_argument(
        "--arm-actions",
        action="store_true",
        help="explicitly enable the tiny move_left/move_right pilot action allow-list",
    )
    args = parser.parse_args()

    adapter = WindowsNosTaleAdapter()
    recorder = JsonlTelemetryRecorder(args.telemetry)
    pilot = LivePilot(
        adapter,
        recorder,
        input_controller=WindowsInputController(armed=args.arm_actions),
        frame_dir=args.frames,
    )
    records = pilot.run(steps=args.steps, interval_s=args.interval)
    print(json.dumps({"records": len(records), "actions_armed": args.arm_actions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
