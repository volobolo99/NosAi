from __future__ import annotations

from pathlib import Path

from app.nostale_perception.network_observation import NetworkObservation
from app.nostale_perception.network_replay import NetworkReplayRecorder
from app.nostale_perception.packet_catalog import PacketCatalog, PacketSpec


def test_packet_catalog_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    catalog = PacketCatalog([PacketSpec("mv", "recv", "movement", "1", 0.9)])
    catalog.dump(path)
    loaded = PacketCatalog.load(path)
    assert loaded.get("recv", "mv").kind == "movement"


def test_network_replay_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "network.jsonl"
    observation = NetworkObservation("o1", 100, "recv", "mv", b"abc", "fixture", "1")
    recorder = NetworkReplayRecorder()
    recorder.append(observation)
    recorder.save(path)
    assert recorder.load(path).replay() == (observation,)
