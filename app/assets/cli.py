"""CLI for local NosTale asset discovery and manifest generation."""
from __future__ import annotations

import argparse

from .asset_manifest import build_manifest, write_manifest
from .nostale_scanner import NosTaleAssetScanner, report_json
from .path_selector import select_client_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scansiona in sicurezza gli asset locali di NosTale")
    parser.add_argument(
        "data_dir",
        nargs="?",
        help="cartella del client NosTale; se omessa si apre il selettore grafico",
    )
    parser.add_argument("--taletool", help="percorso dell'eseguibile Taletool; default: PATH")
    parser.add_argument("--manifest", help="salva il manifest JSON locale")
    args = parser.parse_args(argv)
    data_dir = select_client_path() if not args.data_dir else args.data_dir
    report = NosTaleAssetScanner(data_dir, args.taletool).scan()
    print(report_json(report))
    if args.manifest:
        write_manifest(build_manifest(report), args.manifest)
    return 0 if report.diagnostic.status == "pronto" else 2


if __name__ == "__main__":
    raise SystemExit(main())
