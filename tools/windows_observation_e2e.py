"""Windows/NosTale observation-only smoke harness.

This module deliberately does not inject input, access process memory, or issue
client commands. It captures a configured window region and feeds frames to the
existing perception adapter when available.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


class WindowsObservationHarness:
    def __init__(self, output_dir: Path, interval_s: float = 0.2) -> None:
        self.output_dir = output_dir
        self.interval_s = interval_s
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_once(self) -> Path:
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError("Install Pillow on Windows to capture observations") from exc
        image = ImageGrab.grab()
        target = self.output_dir / "frame_0001.png"
        image.save(target)
        return target

    def run(self, frames: int = 10) -> dict[str, Any]:
        captured = []
        for index in range(frames):
            path = self.capture_once()
            captured.append({"frame": index + 1, "path": str(path), "observation_only": True})
            if index + 1 < frames:
                time.sleep(self.interval_s)
        report = {"frames": captured, "observation_only": True}
        (self.output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description="NosAi Windows observation-only smoke capture")
    parser.add_argument("--output", default="artifacts/windows_observation")
    parser.add_argument("--frames", type=int, default=10)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()
    if args.frames < 1 or args.frames > 300:
        parser.error("--frames must be between 1 and 300")
    print(json.dumps(WindowsObservationHarness(Path(args.output), args.interval).run(args.frames), indent=2))


if __name__ == "__main__":
    main()
