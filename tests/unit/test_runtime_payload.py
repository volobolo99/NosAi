from pathlib import Path

from app.simulation_repair.runtime_payload import PayloadFile, sha256_file, verify_payload


def test_payload_verification_accepts_matching_file(tmp_path: Path):
    target = tmp_path / "runtime.txt"
    target.write_text("NosAi", encoding="utf-8")
    item = PayloadFile("runtime.txt", sha256_file(target), target.stat().st_size)
    result = verify_payload(tmp_path, (item,))
    assert result.passed is True
    assert result.checked == 1
    assert result.failures == ()


def test_payload_verification_rejects_modified_file(tmp_path: Path):
    target = tmp_path / "runtime.txt"
    target.write_text("NosAi", encoding="utf-8")
    item = PayloadFile("runtime.txt", sha256_file(target), target.stat().st_size)
    target.write_text("tampered", encoding="utf-8")
    result = verify_payload(tmp_path, (item,))
    assert result.passed is False
    assert any("sha256 mismatch" in failure for failure in result.failures)


def test_payload_verification_rejects_path_escape(tmp_path: Path):
    item = PayloadFile("../outside.txt", "0" * 64, 0)
    result = verify_payload(tmp_path, (item,))
    assert result.passed is False
    assert any("escapes payload root" in failure for failure in result.failures)
