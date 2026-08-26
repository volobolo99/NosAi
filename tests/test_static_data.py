import json

import pytest

from app.knowledge.static_data import StaticDataError, iter_records


def test_static_records_round_trip(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "source": "test",
        "records": [{"id": "1", "kind": "skill", "fields": {"name": "x"}}],
    }), encoding="utf-8")
    assert list(iter_records(path))[0]["kind"] == "skill"


def test_static_data_requires_provenance_source(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"schema_version": 1, "records": []}), encoding="utf-8")
    with pytest.raises(StaticDataError):
        list(iter_records(path))
