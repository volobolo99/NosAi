"""Print the detected platform profile and selected runtime."""
from __future__ import annotations

import argparse
import json

from .capabilities import detect_hardware_profile
from .runtime import select_runtime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect NosAi Windows/AI runtime capabilities")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    profile = detect_hardware_profile()
    runtime = select_runtime(profile)
    payload = {"profile": profile.to_dict(), "runtime": runtime.__dict__}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("NOSAI SYSTEM PROFILE")
        for key, value in payload["profile"].items():
            print(f"{key}: {value}")
        print("\nNOSAI RUNTIME")
        for key, value in payload["runtime"].items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
