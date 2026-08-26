from app.knowledge.source_snapshot import build_snapshot, snapshot_digest


def test_digest_is_order_independent():
    assert snapshot_digest({"b": 2, "a": 1}) == snapshot_digest({"a": 1, "b": 2})


def test_snapshot_records_provenance_and_digest():
    snapshot = build_snapshot(source_id="noscore", source_ref="repo@abc", payload={"x": 1}, commit="abc")
    assert snapshot["source_id"] == "noscore"
    assert snapshot["commit"] == "abc"
    assert len(snapshot["sha256"]) == 64
