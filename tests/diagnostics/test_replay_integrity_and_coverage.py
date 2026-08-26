from __future__ import annotations

import json

from app.diagnostics.decoder_coverage import measure_decoder_coverage
from app.diagnostics.replay_integrity import validate_jsonl, validate_records
from app.nostale_perception.network_decoder import DecoderRegistry, DecodedObservation
from app.nostale_perception.network_observation import NetworkObservation


def test_integrity_rejects_duplicate_and_bad_schema() -> None:
    record = {"timestamp_ms": 1, "direction": "recv", "header": "a", "payload": "x", "schema_version": 1}
    report, observations = validate_records([record, record, {**record, "schema_version": 99}])
    assert len(observations) == 1
    assert report.duplicate_observations == 1
    assert {issue.code for issue in report.issues} == {"DUPLICATE", "UNSUPPORTED_SCHEMA"}
    assert not report.ok


def test_jsonl_total_lines_are_counted_once(tmp_path) -> None:
    path = tmp_path / "replay.jsonl"
    path.write_text(json.dumps({"timestamp_ms": 1, "direction": "recv", "header": "a", "payload": "x"}) + "\n" + "not-json\n", encoding="utf-8")
    report, observations = validate_jsonl(path)
    assert report.total_lines == 2
    assert len(observations) == 1
    assert any(issue.code == "INVALID_JSON" for issue in report.issues)


def test_decoder_coverage_separates_unknown_and_decoder_failure() -> None:
    registry = DecoderRegistry()
    registry.register("ok", lambda observation: DecodedObservation(observation.observation_id, "test", {}, 1.0, "1"))
    registry.register("bad", lambda observation: (_ for _ in ()).throw(RuntimeError("decoder bug")))
    observations = [
        NetworkObservation(1, "recv", "ok", "x"),
        NetworkObservation(2, "recv", "unknown", "x"),
        NetworkObservation(3, "recv", "bad", "x"),
    ]
    report = measure_decoder_coverage(observations, registry)
    assert report.total == 3
    assert report.known == 1
    assert report.unknown == 1
    assert report.decode_failures == 1
    assert report.decode_ratio == 1 / 3
