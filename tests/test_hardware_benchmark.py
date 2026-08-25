from tools.hardware_benchmark import main


def test_hardware_benchmark_writes_json(tmp_path, monkeypatch):
    output = tmp_path / "benchmark.json"
    monkeypatch.setattr("sys.argv", ["hardware_benchmark", "--output", str(output)])
    assert main() == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert '"schema": 2' in text
    assert '"hardware"' in text
    assert '"benchmark"' in text
    assert '"workload_wall_time_s"' in text
