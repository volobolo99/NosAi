from hashlib import sha256

import pytest

from nosai.ai.model_registry import ModelManifest, ModelRegistry


def manifest(payload=b"model"):
    return ModelManifest(
        model_id="baseline", version="1.0.0", artifact_sha256=sha256(payload).hexdigest(),
        artifact_size=len(payload), dataset_digest="dataset-1", evaluation_digest="eval-1",
    )


def test_register_get_and_verify(tmp_path):
    registry = ModelRegistry(tmp_path)
    registry.register(manifest())
    loaded = registry.get("baseline", "1.0.0")
    assert loaded == manifest()
    assert registry.verify("baseline", "1.0.0", b"model")
    assert not registry.verify("baseline", "1.0.0", b"tampered")


def test_duplicate_registration_rejected(tmp_path):
    registry = ModelRegistry(tmp_path)
    registry.register(manifest())
    with pytest.raises(ValueError, match="already registered"):
        registry.register(manifest())


def test_lifecycle_is_monotonic(tmp_path):
    registry = ModelRegistry(tmp_path)
    registry.register(manifest())
    registry.transition("baseline", "1.0.0", "validated")
    registry.transition("baseline", "1.0.0", "promoted")
    assert registry.get("baseline", "1.0.0").lifecycle == "promoted"
    with pytest.raises(ValueError, match="invalid lifecycle"):
        registry.transition("baseline", "1.0.0", "candidate")


def test_required_lineage_and_checksum_are_validated(tmp_path):
    registry = ModelRegistry(tmp_path)
    with pytest.raises(ValueError):
        registry.register(ModelManifest("x", "1", "bad", 1, "dataset", "eval"))
    with pytest.raises(ValueError):
        registry.register(ModelManifest("x", "1", sha256(b"x").hexdigest(), 1, "", "eval"))
