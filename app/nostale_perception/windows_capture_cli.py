"""Real Windows capture CLI for creating replay fixtures.

This module is intentionally read-only: it captures pixels and never sends
input or accesses the target process memory.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .capture_dataset import capture_frames
from .window_discovery import discover_windows
from .windows_backend import Win32WindowCaptureBackend
from .windows_capture import WindowsFrameSource, WindowsWindowTarget


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nostale-capture")
    parser.add_argument("--hwnd", type=int, help="explicit Windows HWND")
    parser.add_argument("--title", default="NosTale", help="window title hint for discovery")
    parser.add_argument("--output", required=True)
    parser.add_argument("--count", type=int, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "win32":
        print("nostale-capture requires Windows", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    if args.count <= 0:
        print("--count must be positive", file=sys.stderr)
        return 2

    if args.hwnd is not None:
        target = WindowsWindowTarget(args.hwnd)
    else:
        candidates = discover_windows(args.title)
        if not candidates:
            print(f"no visible window matching {args.title!r}", file=sys.stderr)
            return 3
        if len(candidates) > 1:
            print("multiple matching windows; choose one with --hwnd:", file=sys.stderr)
            for candidate in candidates:
                print(f"  hwnd={candidate.hwnd} pid={candidate.pid} title={candidate.title}", file=sys.stderr)
            return 4
        candidate = candidates[0]
        target = WindowsWindowTarget(candidate.hwnd, candidate.pid, candidate.title)

    source = WindowsFrameSource(target, Win32WindowCaptureBackend())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    written = capture_frames(source, output, args.count)
    print(f"captured={written} hwnd={target.hwnd} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
