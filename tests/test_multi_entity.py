from __future__ import annotations

import numpy as np

from app.client.entity_detection import Detection, Roi
from app.client.multi_entity import MultiEntityObservation, MultiEntityRecognizer


class FakeDetector:
    def __init__(self, detections):
        self._detections = tuple(detections)

    def detect_templates(self, image):
        return self._detections


def test_multi_entity_groups_and_offsets_world_roi():
    detector = FakeDetector(
        [
            Detection("player", 10, 20, 12, 12, 0.91),
            Detection("npc", 40, 30, 12, 12, 0.88),
            Detection("mob", 70, 40, 12, 12, 0.84),
        ]
    )
    rois = (
        Roi("world", 0.1, 0.1, 0.8, 0.8),
        Roi("minimap", 0.8, 0.0, 0.2, 0.2),
        Roi("hud", 0.0, 0.8, 1.0, 0.2),
    )
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    result = MultiEntityRecognizer(detector, rois=rois).recognize(image)

    assert isinstance(result, MultiEntityObservation)
    assert [d.kind for d in result.player] == ["player"]
    assert result.player[0].x == 30
    assert result.npc[0].x == 60
    assert result.mob[0].x == 90
    assert result.minimap is not None
    assert result.observation_only is True


def test_dedupe_keeps_highest_confidence_same_kind():
    detections = [
        Detection("mob", 10, 10, 20, 20, 0.80),
        Detection("mob", 11, 11, 20, 20, 0.95),
        Detection("npc", 11, 11, 20, 20, 0.81),
    ]
    result = MultiEntityRecognizer._dedupe(detections)
    mobs = [d for d in result if d.kind == "mob"]
    assert len(mobs) == 1
    assert mobs[0].confidence == 0.95
    assert any(d.kind == "npc" for d in result)


def test_empty_minimap_is_valid_observation_without_false_entities():
    detector = FakeDetector([])
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    result = MultiEntityRecognizer(detector).recognize(image)
    assert result.player == ()
    assert result.npc == ()
    assert result.mob == ()
    assert result.minimap is not None
    assert result.minimap.detections == ()
    assert result.minimap.confidence == 0.0
    assert result.observation_only is True
