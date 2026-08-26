from __future__ import annotations

import sys

from app.nostale_perception.windows_capture_cli import main


def test_capture_cli_rejects_non_windows(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    assert main(["--output", "frames.jsonl", "--count", "1"]) == 2
