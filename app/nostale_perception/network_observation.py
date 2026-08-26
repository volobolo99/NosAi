"""Read-only network observation contracts for NosTale telemetry.

The adapter accepts already-observed packet records and never sends, mutates,
or injects network traffic. Decoding is deliberately separated from policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class NetworkObservation:
    timestamp_ms: int
    direction: str
    header: str
    payload: str
    source: str = "network"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.direction not in {"recv", "send"}:
            raise ValueError("direction must be 'recv' or 'send'")
        if not self.header.strip():
            raise ValueError("header must not be empty")


def observation_from_mapping(record: Mapping[str, object]) -> NetworkObservation:
    return NetworkObservation(
        timestamp_ms=int(record["timestamp_ms"]),
        direction=str(record["direction"]).lower(),
        header=str(record["header"]),
        payload=str(record.get("payload", "")),
        source=str(record.get("source", "network")),
        schema_version=int(record.get("schema_version", 1)),
    )


def load_observations(path: str | Path) -> list[NetworkObservation]:
    observations: list[NetworkObservation] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            observations.append(observation_from_mapping(json.loads(line)))
    return observations


def write_observations(path: str | Path, observations: Iterable[NetworkObservation]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for observation in observations:
            handle.write(json.dumps(observation.__dict__, sort_keys=True) + "\n")
