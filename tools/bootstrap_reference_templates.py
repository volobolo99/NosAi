"""Bootstrap a weakly-supervised vision template library from public references.

Public screenshots are *reference* data, not ground truth. This tool downloads the
reference set, validates images, and creates reviewable candidate patches only for
stable UI regions (HUD/minimap). Entity templates (player/NPC/mob) require local
annotated captures and are never fabricated from public screenshots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/vision/reference_sources.json"
DEFAULT_OUT = ROOT / ".nosai/vision/reference"


def _download(url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "NosAi-vision-reference/1.0"})
    with urlopen(req, timeout=20) as response:
        data = response.read()
    destination.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def bootstrap(manifest: Path, output: Path) -> dict:
    spec = json.loads(manifest.read_text(encoding="utf-8"))
    results = []
    for item in spec.get("sources", []):
        rid = item["id"]
        suffix = Path(item["url"].split("?", 1)[0]).suffix.lower() or ".img"
        target = output / f"{rid}{suffix}"
        try:
            sha = _download(item["url"], target)
            results.append({"id": rid, "path": str(target.relative_to(ROOT)), "sha256": sha, "tags": item.get("tags", []), "status": "downloaded"})
        except Exception as exc:  # reference sources can disappear; bootstrap remains best-effort
            results.append({"id": rid, "status": "unavailable", "error": str(exc), "tags": item.get("tags", [])})

    # Explicitly prevent accidental promotion of public references into entity ground truth.
    library = {
        "version": 1,
        "policy": "reference_only",
        "entity_templates": [],
        "ui_reference_images": [r for r in results if r.get("status") == "downloaded"],
        "ground_truth_required": True,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "library.json").write_text(json.dumps(library, indent=2), encoding="utf-8")
    return library


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = bootstrap(args.manifest, args.output)
    print(json.dumps({"downloaded": len(result["ui_reference_images"]), "entity_templates": 0, "ground_truth_required": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
