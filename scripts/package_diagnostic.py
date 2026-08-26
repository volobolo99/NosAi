"""Create a sanitized diagnostic ZIP ready for manual GitHub upload."""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from app.diagnostics.sanitize import sanitize_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", default="artifacts")
    parser.add_argument("--output", default="artifacts/nosai-diagnostic-package.zip")
    args = parser.parse_args()
    root = Path(args.artifacts).resolve()
    report = root / "nosai-client-test-report.json"
    manifest = root / "client-manifest.json"
    sanitized = root / "nosai-client-test-report.sanitized.json"
    if not report.is_file() or not manifest.is_file():
        raise SystemExit("Esegui prima il test del client: report o manifest mancanti.")
    sanitize_report(report, sanitized)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(sanitized, sanitized.name)
        archive.write(manifest, manifest.name)
        archive.writestr("PACKAGE_VERSION.txt", "NosAi diagnostic package v1\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
