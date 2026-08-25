"""Command-line entry point for privacy-safe local diagnostics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .collector import collect_diagnostics, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect NosAi Windows/NosTale diagnostics")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--output", type=Path, help="also save a JSON report to this path")
    args = parser.parse_args(argv)

    report = collect_diagnostics()
    if args.output:
        write_report(args.output, report)
        print(f"report: {args.output}")
    if args.json or not args.output:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

    nostale = report["nostale"]
    return 0 if nostale["connected"] and nostale["state_read"] else 1
