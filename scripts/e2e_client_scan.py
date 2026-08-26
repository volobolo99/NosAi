"""Full local NosTale diagnostic collector used by Nos AI Launcher Test."""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

from app.assets.asset_manifest import build_manifest, write_manifest
from app.assets.nostale_scanner import NosTaleAssetScanner


def collect_report(scanner: NosTaleAssetScanner, full: bool) -> dict:
    started = time.time()
    report = scanner.scan()
    payload = report.to_dict()
    payload["collector"] = {
        "schema_version": "2.0",
        "started_at_unix": started,
        "duration_seconds": round(time.time() - started, 3),
        "full": full,
        "python": sys.version,
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "windows": platform.version(),
    }
    payload["next_analysis"] = {
        "binary_families": sorted({item.family for item in report.files}),
        "file_count": len(report.files),
        "required_families_present": not bool(report.diagnostic.families_missing),
        "taletool_available": bool(scanner.taletool),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Raccolta dati E2E del client NosTale per NosAi")
    parser.add_argument("client_dir")
    parser.add_argument("--manifest", default="artifacts/client-manifest.json")
    parser.add_argument("--report", default="artifacts/nosai-client-test-report.json")
    parser.add_argument("--taletool")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    scanner = NosTaleAssetScanner(args.client_dir, args.taletool)
    payload = collect_report(scanner, args.full)
    report = scanner.scan()
    write_manifest(build_manifest(report), args.manifest)

    report_path = Path(args.report).expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"REPORT: {report_path}")
    print(f"MANIFEST: {Path(args.manifest).expanduser().resolve()}")
    if report.diagnostic.status != "pronto":
        print("E2E CLIENT GATE: INCOMPLETO — il report è stato comunque salvato", file=sys.stderr)
        return 2
    print("E2E CLIENT GATE: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
