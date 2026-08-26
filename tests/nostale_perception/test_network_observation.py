from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.nostale_perception.network_observation import (
    NetworkObservation,
    load_observations,
    observation_from_mapping,
    write_observations,
)


def test_observation_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "packets.jsonl"
    source = NetworkObservation(123, "recv", "stat", "221 221 60")
    write_observations(path, [source])
    loaded = load_observations(path)
    assert loaded == [source]


def test_invalid_direction_is_rejected() -> None:
    with pytest.raises(ValueError, match="direction"):
        observation_from_mapping({"timestamp_ms": 1, "direction": "inject", "header": "stat"})
