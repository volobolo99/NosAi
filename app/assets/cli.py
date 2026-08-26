"""CLI for inspecting a local NosTale installation."""
from __future__ import annotations

import argparse

from .nostale_scanner import NosTaleAssetScanner, report_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Scansiona in sicurezza gli asset locali di NosTale")
    parser.add_argument("data_dir", help="cartella NostaleData del client NosTale")
    parser.add_argument("--taletool", help="percorso dell'eseguibile taletool; default: PATH")
    args = parser.parse_args()
    report = NosTaleAssetScanner(args.data_dir, args.taletool).scan()
    print(report_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
