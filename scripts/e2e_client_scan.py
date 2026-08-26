"""Run the real-client asset scan and fail loudly on incomplete prerequisites.

Usage on Windows:
    python scripts/e2e_client_scan.py "C:\\Games\\NosTale" --manifest artifacts/client-manifest.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.assets.asset_manifest import build_manifest, write_manifest
from app.assets.nostale_scanner import NosTaleAssetScanner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("client_dir")
    parser.add_argument("--manifest", default="artifacts/client-manifest.json")
    parser.add_argument("--taletool")
    args = parser.parse_args()

    scanner = NosTaleAssetScanner(args.client_dir, args.taletool)
    report = scanner.scan()
    manifest = build_manifest(report)
    output = write_manifest(manifest, args.manifest)

    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    print(f"Manifest: {output}")
    if report.diagnostic.status != "pronto":
        print("E2E CLIENT GATE: FALLITO — asset fondamentali mancanti", file=sys.stderr)
        return 2
    print("E2E CLIENT GATE: OK — client rilevato e famiglie fondamentali presenti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
