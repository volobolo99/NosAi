from __future__ import annotations

import json
from pathlib import Path

from tools.profile_runtime import main


def test_runtime_profile_writes_json(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "nested" / "runtime.json"
    monkeypatch.setattr("sys.argv", ["profile_runtime", "--output", str(output), "--episodes", "1", "--max-steps", "1", "--simulations", "1", "--horizon", "1"])
    assert main() == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == 1
    assert payload["profile"]
    assert payload["benchmark"]
