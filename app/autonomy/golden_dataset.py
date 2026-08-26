"""Versioned, provenance-aware golden benchmark dataset."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from .replay_scenarios import GoldenScenario

DATASET_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class GoldenFixture:
    scenario_id: str
    dataset_version: str
    schema_version: str
    source_replay: str
    start_sequence: int
    end_sequence: int
    kind: str
    goal: str
    valid: bool
    expected_block: bool
    fingerprint: str


def fingerprint_scenario(scenario: GoldenScenario) -> str:
    payload = {
        "scenario_id": scenario.scenario_id,
        "source_replay": scenario.source_replay,
        "start_sequence": scenario.start_sequence,
        "end_sequence": scenario.end_sequence,
        "kind": scenario.kind.value,
        "goal": scenario.goal.value,
        "valid": scenario.valid,
        "expected_block": scenario.expected_block,
        "state": repr(scenario.state),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def to_fixture(scenario: GoldenScenario, dataset_version: str) -> GoldenFixture:
    return GoldenFixture(
        scenario_id=scenario.scenario_id,
        dataset_version=dataset_version,
        schema_version=DATASET_SCHEMA_VERSION,
        source_replay=scenario.source_replay,
        start_sequence=scenario.start_sequence,
        end_sequence=scenario.end_sequence,
        kind=scenario.kind.value,
        goal=scenario.goal.value,
        valid=scenario.valid,
        expected_block=scenario.expected_block,
        fingerprint=fingerprint_scenario(scenario),
    )


def build_dataset(scenarios: Iterable[GoldenScenario], dataset_version: str) -> tuple[GoldenFixture, ...]:
    fixtures = tuple(to_fixture(scenario, dataset_version) for scenario in scenarios)
    ids = [fixture.scenario_id for fixture in fixtures]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scenario_id in golden dataset")
    fingerprints = [fixture.fingerprint for fixture in fixtures]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("duplicate fixture fingerprint in golden dataset")
    return fixtures


def coverage(fixtures: Iterable[GoldenFixture]) -> dict[str, int]:
    items = tuple(fixtures)
    return {
        "total": len(items),
        "valid": sum(item.valid for item in items),
        "invalid": sum(not item.valid for item in items),
        "expected_block": sum(item.expected_block for item in items),
    }
