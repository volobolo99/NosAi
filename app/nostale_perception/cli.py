"""Command-line entry points for the NosTale perception dataset loop."""
from __future__ import annotations

import argparse
from pathlib import Path

from .annotator import annotate_replay
from .capture_dataset import capture_frames
from .dataset import build_manifest, write_manifest
from .evaluation_report import QualityGate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nostale-perception")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="capture bounded replay frames")
    capture.add_argument("--output", required=True)
    capture.add_argument("--count", required=True, type=int)

    annotate = sub.add_parser("annotate", help="annotate replay frames")
    annotate.add_argument("--frames", required=True)
    annotate.add_argument("--truth", required=True)

    manifest = sub.add_parser("manifest", help="create content-addressed dataset manifest")
    manifest.add_argument("--name", required=True)
    manifest.add_argument("--version", required=True)
    manifest.add_argument("--frames", required=True)
    manifest.add_argument("--truth", required=True)
    manifest.add_argument("--output", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "capture":
        raise SystemExit("capture requires an application-provided Windows FrameSource")
    if args.command == "annotate":
        return 0 if annotate_replay(args.frames, args.truth) >= 0 else 1
    if args.command == "manifest":
        manifest = build_manifest(args.name, args.version, args.frames, args.truth)
        write_manifest(args.output, manifest)
        print(f"manifest written: {args.output}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
