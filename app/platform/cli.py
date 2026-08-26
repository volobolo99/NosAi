"""CLI for inspecting the detected NosAi Windows runtime profile."""

from __future__ import annotations

import argparse
import json

from .capabilities import detect_hardware_profile
from .runtime import select_runtime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect NosAi platform capabilities")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    profile = detect_hardware_profile()
    runtime = select_runtime(profile)
    payload = {"hardware": profile.to_dict(), "runtime": runtime.__dict__}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("NOSAI WINDOWS RUNTIME PROFILE")
    print(f"OS: {profile.os_name} {profile.os_version}")
    print(f"Python: {profile.python_version}")
    print(f"CPU cores: {profile.cpu_count}")
    print(f"RAM GB: {profile.ram_gb}")
    print(f"GPU: {profile.gpu_vendor or 'unknown'} / {profile.gpu_name or 'unknown'}")
    print(f"GPU VRAM MB: {profile.gpu_vram_mb}")
    print(f"NPU present: {profile.npu_present}")
    print(f"DirectX: {profile.directx_available}")
    print(f"Capture backend: {runtime.capture_backend}")
    print(f"Inference backend: {runtime.inference_backend}")
    print(f"Acceleration: {runtime.acceleration}")
    print(f"Reason: {runtime.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
