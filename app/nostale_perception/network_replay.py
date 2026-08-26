"""Deterministic recorder/replayer for already-observed network records."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .network_observation import NetworkObservation


@dataclass(frozen=True)
class ReplayPacket:
    sequence: int
    observation: NetworkObservation


class NetworkReplayRecorder:
    def __init__(self) -> None:
        self._items: list[ReplayPacket] = []

    def append(self, observation: NetworkObservation) -> None:
        self._items.append(ReplayPacket(len(self._items), observation))

    def save(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as handle:
            for item in self._items:
                handle.write(json.dumps({"sequence": item.sequence, "observation": item.observation.__dict__}, sort_keys=True) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> "NetworkReplayRecorder":
        recorder = cls()
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            recorder._items.append(ReplayPacket(item["sequence"], NetworkObservation(**item["observation"])))
        return recorder

    def replay(self) -> tuple[NetworkObservation, ...]:
        return tuple(item.observation for item in sorted(self._items, key=lambda item: item.sequence))
