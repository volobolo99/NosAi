from pathlib import Path

from app.client import ClientState
from app.client.live_pilot import JsonlTelemetryRecorder, LivePilot, PilotAction, WindowsInputController
from app.client.loader import ClientAdapterLoadError, load_client_adapter
from app.client.nostale_windows import WindowInfo
from app.client.probe import run_client_probe


class GoodAdapter:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=7, payload={"player": {"hp": 100}})

    def validate_action(self, action):
        assert action is None
        return True

    def close(self):
        return None


class BadStateAdapter(GoodAdapter):
    def read_state(self):
        return {"tick": 7}


def test_client_probe_is_non_destructive():
    assert run_client_probe(GoodAdapter()) == [
        ("CONNECTION", "CONNECTED"),
        ("STATE_READ", "tick=7"),
        ("ACTION_VALIDATE", "DRY_RUN_OK"),
    ]


def test_client_probe_rejects_invalid_state():
    try:
        run_client_probe(BadStateAdapter())
    except TypeError as exc:
        assert "ClientState" in str(exc)
    else:
        raise AssertionError("invalid client state must block the probe")


def test_loader_requires_explicit_configuration():
    try:
        load_client_adapter(None)
    except ClientAdapterLoadError as exc:
        assert "NOSAI-CLIENT-0002" in str(exc)
    else:
        raise AssertionError("missing adapter configuration must fail")


class FakeLiveAdapter:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=1, payload={"hp": 100})

    def validate_action(self, action):
        return action is None or action in {"move_left", "move_right"}

    def find_windows(self):
        return (WindowInfo(123, "NosTale", 0, 0, 10, 10),)

    def close(self):
        return None


class NoopPolicy:
    def choose(self, observation):
        return PilotAction("noop")


def test_live_pilot_records_replayable_telemetry(tmp_path: Path, monkeypatch):
    recorder = JsonlTelemetryRecorder(tmp_path / "telemetry.jsonl")
    pilot = LivePilot(FakeLiveAdapter(), recorder, policy=NoopPolicy(), frame_dir=tmp_path / "frames")
    monkeypatch.setattr("app.client.live_pilot._capture_window", lambda *args: (None, None))

    records = pilot.run(steps=1, interval_s=0)

    assert records[0]["schema"] == "nosai.live_pilot.v1"
    assert records[0]["state"] == {"hp": 100}
    assert records[0]["decision"]["name"] == "noop"
    assert records[0]["outcome"]["executed"] is False
    assert (tmp_path / "telemetry.jsonl").read_text(encoding="utf-8").count("\n") == 1


def test_live_actions_are_disabled_without_explicit_arm():
    result = WindowsInputController(armed=False).execute(PilotAction("move_left", duration_s=0.01))
    assert result == {"executed": False, "reason": "actions_not_armed"}
