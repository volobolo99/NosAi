"""CLI for inspecting a local NosTale installation."""
from __future__ import annotations

import argparse

from .nostale_scanner import NosTaleAssetScanner, report_json
from .path_selector import select_client_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Scansiona in sicurezza gli asset locali di NosTale")
    parser.add_argument(
        "data_dir",
        nargs="?",
        help="cartella del client NosTale; se omessa si apre il selettore grafico",
    )
    parser.add_argument("--taletool", help="percorso dell'eseguibile taletool; default: PATH")
    args = parser.parse_args()
    data_dir = select_client_path() if not args.data_dir else args.data_dir
    report = NosTaleAssetScanner(data_dir, args.taletool).scan()
    print(report_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
