"""Validate reference/template manifests without promoting weak references.

This is deliberately metadata-only: it validates policy, classes and confidence
requirements. It does not claim public screenshots are ground truth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {"player", "npc", "mob"}
REQUIRED_SOURCE = "local_capture"
MIN_CONFIDENCE = 0.78


def validate(manifest: dict) -> list[str]:
    errors: list[str] = []
    for template in manifest.get("templates", []):
        kind = template.get("kind")
        if kind not in ALLOWED:
            errors.append(f"invalid entity class: {kind}")
        if template.get("source") != REQUIRED_SOURCE:
            errors.append(f"{kind}: source must be {REQUIRED_SOURCE}")
        confidence = float(template.get("confidence", 0.0))
        if confidence < MIN_CONFIDENCE:
            errors.append(f"{kind}: confidence below {MIN_CONFIDENCE}")
        if template.get("observation_only") is not True:
            errors.append(f"{kind}: observation_only must be true")
        if template.get("status") not in {"verified", "production"}:
            errors.append(f"{kind}: template is not verified/production")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("INVALID")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"VALID: {len(data.get('templates', []))} verified templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
