from __future__ import annotations

from typing import Any

from app.ai.brain import NosAiBrain
from app.ai_lab.matrix import build_edge_case_matrix, run_edge_case_matrix
from app.client.adapter import ClientState, validate_adapter
from app.client.adapter_runtime import probe_client
from app.client.nostale_windows import WindowsNosTaleAdapter


class FakeRuntimeAdapter:
    """Deterministic adapter used by CI; it can never touch a real client."""

    def __init__(self) -> None:
        self.closed = False
        self.reads = 0

    def check_connection(self) -> bool:
        return True

    def read_state(self) -> ClientState:
        self.reads += 1
        return ClientState(tick=self.reads, payload={"source": "test-center", "observation_only": True})

    def validate_action(self, action: Any) -> bool:
        return action is None

    def close(self) -> None:
        self.closed = True


def test_edge_case_matrix_is_exactly_144() -> None:
    scenarios = build_edge_case_matrix()
    assert len(scenarios) == 144
    assert len({scenario["scenario_id"] for scenario in scenarios}) == 144


def test_edge_case_matrix_is_safe_and_passes() -> None:
    runs, summary = run_edge_case_matrix(NosAiBrain())
    assert len(runs) == 144
    assert summary.total == 144
    assert summary.safety_failed == 0
    assert summary.failed == 0
    assert summary.passed == 144


def test_adapter_contract_and_dry_run_are_integrated() -> None:
    adapter = FakeRuntimeAdapter()
    validate_adapter(adapter)
    result = probe_client(adapter)
    assert result.connected is True
    assert result.state_valid is True
    assert result.action_valid is True
    assert adapter.reads == 1
    adapter.close()
    assert adapter.closed is True


def test_windows_adapter_is_observation_only_on_ci_host() -> None:
    adapter = WindowsNosTaleAdapter(process_names=("NostaleClientX.exe",))
    assert adapter.validate_action(None) is True
    assert adapter.validate_action({"action_type": "attack"}) is False
    assert "nostaleclientx.exe" in adapter.process_names
