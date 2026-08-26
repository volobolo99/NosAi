from pathlib import Path
import json


def test_reference_manifest_is_reference_only():
    p = Path("data/vision/reference_sources.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["policy"]["reference_only"] is True
    assert data["policy"]["requires_local_capture_for_ground_truth"] is True
    assert len(data["sources"]) >= 3


def test_ground_truth_protocol_requires_local_capture():
    text = Path("data/vision/ground_truth/README.md").read_text(encoding="utf-8")
    assert "target Windows client" in text
    assert "observation_only" in text
    assert "player" in text and "npc" in text and "mob" in text
