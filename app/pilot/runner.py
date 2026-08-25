"""Orchestrator for the first safe NosAi Test Pilot."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any
import uuid

from app.client.adapter import ClientAdapter, validate_adapter
from app.self_repair.telemetry import TelemetryStore

from .models import PilotError, PilotResult, PilotSessionConfig, StateQuality

DecisionFn = Callable[[dict[str, Any]], Any]


class TestPilot:
    """Run simulation/shadow observations and collect actionable diagnostics.

    This component deliberately has no method that executes an action. It only
    asks the adapter to *validate* a proposed action, preserving the safety
    boundary required before a real client integration exists.

    ``__test__ = False`` is intentional: the production runner is named
    ``TestPilot`` for domain/API compatibility, but it is not itself a pytest
    test class. This prevents pytest from attempting to collect it and removes
    a misleading collection warning during the environment gate.
    """

    __test__ = False

    def __init__(
        self,
        adapter: ClientAdapter,
        config: PilotSessionConfig | None = None,
        decision_fn: DecisionFn | None = None,
    ) -> None:
        """Validate dependencies and initialize the pilot session components."""
        validate_adapter(adapter)
        self.adapter = adapter
        self.config = config or PilotSessionConfig()
        self.decision_fn = decision_fn or self._baseline_decision
        self.telemetry = TelemetryStore(self.config.telemetry_path)

    @staticmethod
    def _baseline_decision(state: dict[str, Any]) -> dict[str, Any]:
        """Small deterministic baseline used only to exercise the pipeline."""

        target = state.get("target")
        entities = state.get("entities") or []
        if target and any(item.get("id") == target for item in entities if isinstance(item, dict)):
            return {"type": "attack", "target": target}
        return {"type": "wait"}

    @staticmethod
    def _missing_capabilities(
        payload: dict[str, Any], required: tuple[str, ...]
    ) -> tuple[str, ...]:
        """Return required dotted-path capabilities absent from the state payload."""
        missing: list[str] = []
        for capability in required:
            current: Any = payload
            for part in capability.split("."):
                if not isinstance(current, dict) or part not in current:
                    missing.append(capability)
                    break
                current = current[part]
        return tuple(missing)

    @staticmethod
    def _state_quality(missing: tuple[str, ...], required: tuple[str, ...]) -> StateQuality:
        """Classify state before the decision engine is allowed to run."""

        if not missing:
            return StateQuality.VALID

        # Missing structural perception is unsafe for an operational decision.
        # Any missing required field therefore blocks the decision in v0.1.
        critical = {"player.position", "entities", "target"}
        if critical.intersection(missing):
            return StateQuality.UNUSABLE

        # Non-structural fields are retained as degraded telemetry for future
        # policy refinement, but are still blocked in this first safety gate.
        return StateQuality.DEGRADED

    def run(self) -> PilotResult:
        """Execute the configured safe pilot loop and return collected diagnostics."""
        session_id = uuid.uuid4().hex
        errors: list[PilotError] = []
        latencies: list[float] = []
        decisions = 0
        valid_decisions = 0
        blocked_decisions = 0
        missing_seen: set[str] = set()
        state_quality_counts = {quality.value: 0 for quality in StateQuality}

        if not self.adapter.check_connection():
            errors.append(
                PilotError(
                    "C001", "client", "critical", "client adapter is not connected", False
                )
            )
            return PilotResult(
                session_id, self.config.mode, 0, 0, 0, 0, state_quality_counts,
                tuple(errors), (), None
            )

        for _ in range(self.config.ticks):
            cycle_id = self.telemetry.start_cycle(
                "test_pilot", {"session_id": session_id, "mode": self.config.mode.value}
            )
            started = perf_counter()
            tick_errors: list[str] = []
            try:
                state = self.adapter.read_state()
                payload = state.payload
                missing = self._missing_capabilities(payload, self.config.required_capabilities)
                missing_seen.update(missing)
                quality = self._state_quality(missing, self.config.required_capabilities)
                state_quality_counts[quality.value] += 1

                if missing:
                    severity = "error" if quality is StateQuality.UNUSABLE else "warning"
                    error = PilotError(
                        "P001",
                        "perception",
                        severity,
                        "required state capabilities are missing",
                        True,
                        {
                            "missing_capabilities": missing,
                            "state_quality": quality.value,
                            "tick": state.tick,
                        },
                    )
                    errors.append(error)
                    tick_errors.append(error.error_id)

                if quality is not StateQuality.VALID:
                    blocked_decisions += 1
                    self.telemetry.finish_cycle(
                        cycle_id,
                        "test_pilot",
                        "BLOCKED",
                        (perf_counter() - started) * 1000.0,
                        {"state_quality": quality.value, "decision_blocked": True},
                        tuple(tick_errors),
                        {
                            "session_id": session_id,
                            "mode": self.config.mode.value,
                            "missing_capabilities": missing,
                        },
                    )
                    continue

                decision_started = perf_counter()
                action = self.decision_fn(payload)
                latency_ms = (perf_counter() - decision_started) * 1000.0
                latencies.append(latency_ms)
                decisions += 1

                valid = self.adapter.validate_action(action)
                if valid:
                    valid_decisions += 1
                else:
                    error = PilotError(
                        "A001",
                        "action",
                        "error",
                        "adapter rejected proposed action",
                        True,
                        {"action": action, "tick": state.tick},
                    )
                    errors.append(error)
                    tick_errors.append(error.error_id)

                self.telemetry.finish_cycle(
                    cycle_id,
                    "test_pilot",
                    "OK" if not tick_errors else "DEGRADED",
                    (perf_counter() - started) * 1000.0,
                    {
                        "state_quality": quality.value,
                        "tick": state.tick,
                        "decision_latency_ms": latency_ms,
                        "action_valid": valid,
                        "decision_blocked": False,
                    },
                    tuple(tick_errors),
                    {"session_id": session_id, "action": action, "mode": self.config.mode.value},
                )
            except Exception as exc:  # noqa: BLE001 - pilot must capture runtime failures
                error = PilotError(
                    "C004",
                    "client",
                    "error",
                    f"pilot cycle failed: {exc}",
                    True,
                    {"cycle_id": cycle_id},
                )
                errors.append(error)
                self.telemetry.finish_cycle(
                    cycle_id,
                    "test_pilot",
                    "ERROR",
                    (perf_counter() - started) * 1000.0,
                    error_ids=(error.error_id,),
                    metadata={"session_id": session_id},
                )

        return PilotResult(
            session_id=session_id,
            mode=self.config.mode,
            ticks=self.config.ticks,
            decisions=decisions,
            valid_decisions=valid_decisions,
            blocked_decisions=blocked_decisions,
            state_quality_counts=state_quality_counts,
            errors=tuple(errors),
            missing_capabilities=tuple(sorted(missing_seen)),
            avg_decision_latency_ms=(sum(latencies) / len(latencies)) if latencies else None,
        )
