import json
from pathlib import Path

from app.client.entity_detection import VisualEntityDetector, load_verified_templates


def test_weak_reference_candidates_are_never_loaded(tmp_path: Path):
    p = tmp_path / "manifest.json"
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"not-an-image")
    p.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "kind": "mob",
                        "path": str(candidate),
                        "status": "candidate_only",
                        "confidence": 0.99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert load_verified_templates(p) == {}


def test_verified_template_manifest_loads_only_thresholded_entries(tmp_path: Path):
    p = tmp_path / "manifest.json"
    verified = tmp_path / "mob.png"
    verified.write_bytes(b"placeholder")
    p.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "kind": "mob",
                        "path": str(verified),
                        "status": "verified",
                        "confidence": 0.90,
                    },
                    {
                        "kind": "npc",
                        "path": str(verified),
                        "status": "verified",
                        "confidence": 0.50,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    loaded = load_verified_templates(p, minimum_confidence=0.78)
    assert list(loaded) == ["mob"]
    assert VisualEntityDetector.from_manifest(p).threshold == 0.78
