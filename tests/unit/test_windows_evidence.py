from pathlib import Path

from app.simulation_repair.windows_evidence import collect_windows_evidence, write_evidence


def test_windows_evidence_is_structured_and_serializable(tmp_path: Path) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"nosai")
    evidence = collect_windows_evidence(
        payload_root=payload,
        command=("python", "-V"),
        exit_code=0,
    )
    destination = tmp_path / "evidence.json"
    write_evidence(evidence, destination)
    assert evidence.schema_version == "1.0"
    assert evidence.payload_sha256
    assert evidence.exit_code == 0
    assert destination.is_file()
    assert '"schema_version": "1.0"' in destination.read_text(encoding="utf-8")
