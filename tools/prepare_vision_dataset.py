"""Prepare public reference screenshots and local ground-truth captures.

The tool downloads only the URLs listed in data/vision/reference_sources.json,
records dimensions and SHA-256 hashes, and writes a manifest. Reference images
remain non-ground-truth. Local captures can be passed with --captures and are
checked for consistent resolution before calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data/vision/reference_sources.json"
OUT = ROOT / "data/vision/reference"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "NosAi-Vision-Reference/1.0"})
    with urlopen(req, timeout=20) as response:
        return response.read()


def image_size(path: Path) -> tuple[int, int]:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("install the vision extra to inspect images") from exc
    frame = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if frame is None:
        raise ValueError(f"cannot decode {path}")
    h, w = frame.shape[:2]
    return w, h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", nargs="*", default=[])
    ap.add_argument("--download-reference", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(SOURCES.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    if args.download_reference:
        for item in manifest["sources"]:
            target = OUT / f"{item['id']}.img"
            data = download(item["url"])
            target.write_bytes(data)
            try:
                width, height = image_size(target)
            except Exception:
                width, height = None, None
            records.append({**item, "local_file": str(target.relative_to(ROOT)), "sha256": sha256(data), "width": width, "height": height})
    else:
        records = [{**x, "local_file": None} for x in manifest["sources"]]

    captures = [Path(x) for x in args.captures if Path(x).is_file()]
    capture_records = []
    if captures:
        sizes = [image_size(p) for p in captures]
        if len(set(sizes)) != 1:
            raise SystemExit("local captures have mixed resolutions; split them into calibration groups")
        capture_records = [{"file": str(p), "width": sizes[0][0], "height": sizes[0][1], "ground_truth_required": True} for p in captures]

    output = ROOT / "data/vision/reference_dataset_prepared.json"
    output.write_text(json.dumps({"version": 1, "reference": records, "local_captures": capture_records, "ground_truth_policy": "local-target-only", "observation_only": True}, indent=2), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
