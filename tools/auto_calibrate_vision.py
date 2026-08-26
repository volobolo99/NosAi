"""CLI for observation-only NosTale screenshot calibration.

Usage:
  python tools/auto_calibrate_vision.py captures/*.png --output .nosai/vision/calibration.json
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Allow running directly from a repository checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.client.calibration import auto_calibrate


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a reviewable NosTale vision calibration profile")
    parser.add_argument("screenshots", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".nosai/vision/calibration.json"))
    args = parser.parse_args()
    profile = auto_calibrate(args.screenshots, args.output)
    print(f"profile={profile.name}")
    print(f"resolution={profile.width}x{profile.height}")
    print(f"confidence={profile.confidence:.3f}")
    print(f"status={profile.status}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
