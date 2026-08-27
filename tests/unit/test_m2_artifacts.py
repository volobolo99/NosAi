from pathlib import Path

from app.simulation_repair.m2_artifacts import collect_artifacts, write_artifact_index


def test_artifact_index_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "b.log").write_text("b", encoding="utf-8")
    (tmp_path / "a.json").write_text("{\"ok\":true}", encoding="utf-8")
    items = collect_artifacts(tmp_path)
    assert [item["path"] for item in items] == ["a.json", "b.log"]
    output = tmp_path / "index.json"
    write_artifact_index(tmp_path, output)
    assert '"schema_version": "1.0"' in output.read_text(encoding="utf-8")
