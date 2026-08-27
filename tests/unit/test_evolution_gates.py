from __future__ import annotations

from app.simulation_repair.governance import GateResult, GateStatus, PromotionFirewall, REQUIRED_GATES
from app.simulation_repair.replay import ReplayCase, anti_forgetting_gate
from app.simulation_repair.registry import RegistryEntry, VersionRegistry


def test_promotion_firewall_blocks_missing_real_validation():
    result = PromotionFirewall().evaluate({"unit_tests": GateResult("unit_tests", GateStatus.PASS)})
    assert not result.allowed
    assert "real_windows" in result.blocking_gates
    assert "real_nostale" in result.blocking_gates


def test_promotion_requires_explicit_confirmation():
    gates = {name: GateResult(name, GateStatus.PASS) for name in REQUIRED_GATES if name != "explicit_confirmation"}
    assert not PromotionFirewall().evaluate(gates).allowed
    assert PromotionFirewall().evaluate(gates, explicit_confirmation=True).allowed


def test_anti_forgetting_detects_regression():
    ok, regressions = anti_forgetting_gate({"combat": 0.9, "escape": 0.8}, {"combat": 0.91, "escape": 0.79})
    assert not ok
    assert regressions == ["escape"]


def test_replay_fingerprint_is_stable():
    case = ReplayCase("CASE-1", {"hp": 50}, {"action": "heal"})
    assert case.fingerprint == ReplayCase("CASE-1", {"hp": 50}, {"action": "heal"}).fingerprint


def test_registry_roundtrip(tmp_path):
    registry = VersionRegistry(tmp_path / "registry.jsonl")
    entry = RegistryEntry("model-1", "policy", "1.0.0", None, "abc", "run-1", "replay-1", "test", {"score": 1.0}, "PASS", ("source",), None)
    registry.register(entry)
    assert registry.latest("policy") == entry
