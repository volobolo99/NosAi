from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.nostale_perception.nostale_packet_catalog import PacketCatalog, PacketDefinition


def test_catalog_round_trip(tmp_path: Path) -> None:
    catalog = PacketCatalog("0.1.0")
    catalog.add(PacketDefinition("walk", "recv", "movement", "1", 0.6, "public-reference"))
    path = tmp_path / "catalog.json"
    catalog.to_json(path)
    restored = PacketCatalog.from_json(path)
    assert restored.version == "0.1.0"
    assert restored.get("recv", "walk").kind == "movement"


def test_catalog_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        PacketDefinition("x", "recv", "x", "1", 1.1, "unknown")
