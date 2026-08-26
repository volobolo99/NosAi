"""Integrity checks for JSONL network fixtures and replay inputs.

Malformed evidence is reported rather than silently dropped or crashing runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Iterable, Mapping

from app.nostale_perception.network_observation import NetworkObservation, observation_from_mapping


@dataclass(frozen=True)
class FixtureIssue:
    line: int
    code: str
    message: str


@dataclass
class ReplayIntegrityReport:
    path: str
    total_lines: int = 0
    valid_observations: int = 0
    duplicate_observations: int = 0
    issues: list[FixtureIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues

    @property
    def valid_ratio(self) -> float:
        return self.valid_observations / self.total_lines if self.total_lines else 0.0


def validate_records(records: Iterable[Mapping[str, object]], *, path: str = "<memory>") -> tuple[ReplayIntegrityReport, list[NetworkObservation]]:
    report = ReplayIntegrityReport(path=path)
    observations: list[NetworkObservation] = []
    seen: set[str] = set()
    previous_timestamp: int | None = None

    for line_number, record in enumerate(records, start=1):
        report.total_lines += 1
        try:
            observation = observation_from_mapping(record)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            report.issues.append(FixtureIssue(line_number, "INVALID_RECORD", repr(exc)))
            continue
        if observation.schema_version != 1:
            report.issues.append(FixtureIssue(line_number, "UNSUPPORTED_SCHEMA", str(observation.schema_version)))
            continue
        if observation.timestamp_ms < 0:
            report.issues.append(FixtureIssue(line_number, "NEGATIVE_TIMESTAMP", str(observation.timestamp_ms)))
            continue
        if observation.observation_id in seen:
            report.duplicate_observations += 1
            report.issues.append(FixtureIssue(line_number, "DUPLICATE", observation.observation_id))
            continue
        if previous_timestamp is not None and observation.timestamp_ms < previous_timestamp:
            report.issues.append(FixtureIssue(line_number, "TIMESTAMP_REGRESSION", f"{observation.timestamp_ms} < {previous_timestamp}"))
        previous_timestamp = observation.timestamp_ms
        seen.add(observation.observation_id)
        observations.append(observation)
        report.valid_observations += 1
    return report, observations


def validate_jsonl(path: str | Path) -> tuple[ReplayIntegrityReport, list[NetworkObservation]]:
    path = Path(path)
    if not path.exists():
        return ReplayIntegrityReport(str(path), issues=[FixtureIssue(0, "MISSING_FILE", str(path))]), []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return ReplayIntegrityReport(str(path), issues=[FixtureIssue(0, "READ_ERROR", repr(exc))]), []

    records: list[Mapping[str, object]] = []
    syntax_issues: list[FixtureIssue] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            syntax_issues.append(FixtureIssue(line_number, "EMPTY_LINE", "blank JSONL line"))
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            syntax_issues.append(FixtureIssue(line_number, "INVALID_JSON", str(exc)))
            continue
        if not isinstance(value, dict):
            syntax_issues.append(FixtureIssue(line_number, "NOT_OBJECT", "JSON record must be an object"))
            continue
        records.append(value)

    parsed, observations = validate_records(records, path=str(path))
    parsed.total_lines = len(lines)
    parsed.issues = syntax_issues + parsed.issues
    return parsed, observations
