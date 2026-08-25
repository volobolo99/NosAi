"""Command-line entry point for NosAi startup validation."""

from __future__ import annotations

import argparse
import sys

from .client.loader import ClientAdapterLoadError, load_client_adapter
from .diagnostics import run_preflight


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run NosAi pre-flight diagnostics")
    parser.add_argument(
        "--require-client",
        action="store_true",
        help="require and probe the explicitly configured live client adapter",
    )
    parser.add_argument(
        "--client-adapter",
        metavar="MODULE:ATTRIBUTE",
        help="explicit live client adapter; overrides NOSAI_CLIENT_ADAPTER",
    )
    parser.add_argument(
        "--no-torch",
        action="store_true",
        help="skip the PyTorch dependency check",
    )
    parser.add_argument("--json", action="store_true", help="print the complete report as JSON")
    args = parser.parse_args(argv)

    adapter = None
    if args.require_client:
        try:
            adapter = load_client_adapter(args.client_adapter)
        except ClientAdapterLoadError as exc:
            print("[FAIL] NOSAI-CLIENT-0002 CLIENT_CONFIGURATION: BLOCKED")
            print(f"  error={type(exc).__name__}: {exc}")
            return 1

    report = run_preflight(
        client_adapter=adapter,
        require_client=args.require_client,
        require_torch=not args.no_torch,
    )
    if args.json:
        print(report.to_json())
    else:
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
