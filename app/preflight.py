"""Command-line entry point for NosAi startup validation."""

from __future__ import annotations

import argparse
import sys

from .diagnostics import run_preflight


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run NosAi pre-flight diagnostics")
    parser.add_argument(
        "--require-client",
        action="store_true",
        help="fail unless a client adapter is supplied by an integration wrapper",
    )
    parser.add_argument(
        "--no-torch",
        action="store_true",
        help="skip the PyTorch dependency check",
    )
    args = parser.parse_args(argv)

    report = run_preflight(require_client=args.require_client, require_torch=not args.no_torch)
    for check in report.checks:
        print(f"[{check.status}] {check.check_id} {check.phase}: {check.message}")
        if check.status == "FAIL":
            print(f"  expected={check.expected}")
            print(f"  actual={check.actual}")
            print(f"  error={check.error_type}: {check.exception}")
    print(f"STATUS: {report.status}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
