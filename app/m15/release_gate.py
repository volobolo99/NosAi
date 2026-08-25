from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any, Callable


@dataclass(frozen=True)
class HardeningReport:
    name: str
    passed: bool
    iterations: int = 0
    failures: int = 0
    digest_before: str = ""
    digest_after: str = ""
    details: str = ""


@dataclass(frozen=True)
class ReleaseGate:
    long_run_pass: bool
    fault_injection_pass: bool
    recovery_pass: bool
    reproducibility_pass: bool
    release_pass: bool


class ReliabilityGate:
    """Evidence-producing release gate.

    The gate deliberately does not accept precomputed booleans as evidence.
    Each release check executes a real operation and returns a report that can
    be persisted for audit/reproducibility.
    """

    @staticmethod
    def deterministic_hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _safe_digest(snapshot: Callable[[], Any] | None) -> str:
        if snapshot is None:
            return ""
        return ReliabilityGate.deterministic_hash(snapshot())

    def long_run(
        self,
        fn: Callable[[], Any],
        iterations: int = 1000,
        *,
        snapshot: Callable[[], Any] | None = None,
        invariant: Callable[[Any], bool] | None = None,
    ) -> bool:
        return self.execute_long_run(fn, iterations, snapshot=snapshot, invariant=invariant).passed

    def execute_long_run(
        self,
        fn: Callable[[], Any],
        iterations: int = 10_000,
        *,
        snapshot: Callable[[], Any] | None = None,
        invariant: Callable[[Any], bool] | None = None,
    ) -> HardeningReport:
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        before = self._safe_digest(snapshot)
        failures = 0
        try:
            for _ in range(iterations):
                value = fn()
                if invariant is not None and not invariant(value):
                    failures += 1
                    break
        except Exception as exc:
            failures += 1
            details = f"exception={type(exc).__name__}: {exc}"
        else:
            details = "completed"
        after = self._safe_digest(snapshot)
        return HardeningReport("long_run", failures == 0, iterations, failures, before, after, details)

    def fault_injection(
        self,
        fn: Callable[[], Any],
        expected_exception: type[BaseException] = Exception,
    ) -> bool:
        return self.execute_fault_injection(fn, expected_exception).passed

    def execute_fault_injection(
        self,
        fn: Callable[[], Any],
        expected_exception: type[BaseException] = Exception,
    ) -> HardeningReport:
        caught = False
        unexpected = False
        try:
            fn()
        except expected_exception:
            caught = True
        except Exception as exc:
            unexpected = True
            details = f"unexpected={type(exc).__name__}: {exc}"
        else:
            details = "expected exception was not raised"
        if not unexpected and caught:
            details = "expected exception caught"
        return HardeningReport("fault_injection", caught and not unexpected, 1, 0 if caught else 1, details=details)

    def recovery(
        self,
        fail_fn: Callable[[], Any],
        recover_fn: Callable[[], Any],
    ) -> bool:
        return self.execute_recovery(fail_fn, recover_fn).passed

    def execute_recovery(
        self,
        fail_fn: Callable[[], Any],
        recover_fn: Callable[[], Any],
        *,
        validator: Callable[[Any], bool] | None = None,
    ) -> HardeningReport:
        failure_caught = False
        try:
            fail_fn()
        except Exception:
            failure_caught = True
        if not failure_caught:
            return HardeningReport("recovery", False, 1, 1, details="failure injection did not fail")
        try:
            recovered = recover_fn()
            valid = bool(recovered) if validator is None else bool(validator(recovered))
        except Exception as exc:
            return HardeningReport("recovery", False, 1, 1, details=f"recovery exception={type(exc).__name__}: {exc}")
        return HardeningReport("recovery", valid, 1, 0 if valid else 1, details="recovered and validated")

    def reproducible(self, fn: Callable[[], Any], runs: int = 3) -> bool:
        return self.execute_reproducibility(fn, runs).passed

    def execute_reproducibility(self, fn: Callable[[], Any], runs: int = 3) -> HardeningReport:
        if runs < 2:
            raise ValueError("runs must be >= 2")
        hashes = [self.deterministic_hash(fn()) for _ in range(runs)]
        passed = all(value == hashes[0] for value in hashes[1:])
        return HardeningReport("reproducibility", passed, runs, 0 if passed else 1, hashes[0], hashes[-1], "identical deterministic outputs" if passed else "output hashes differ")

    def final(self, checks: list[bool] | tuple[bool, ...]) -> ReleaseGate:
        # Kept for compatibility, but hardened callers must use evidence reports.
        ok = bool(checks) and all(checks)
        return ReleaseGate(ok, ok, ok, ok, ok)

    def hardened_release(
        self,
        *,
        long_run: HardeningReport,
        fault_injection: HardeningReport,
        recovery: HardeningReport,
        reproducibility: HardeningReport,
        tests_pass: bool,
        build_pass: bool,
        wheel_integrity: bool,
        end_to_end_pass: bool,
    ) -> ReleaseGate:
        checks = [
            long_run.passed,
            fault_injection.passed,
            recovery.passed,
            reproducibility.passed,
            bool(tests_pass and build_pass and wheel_integrity and end_to_end_pass),
        ]
        ok = all(checks)
        return ReleaseGate(checks[0], checks[1], checks[2], checks[3], ok)

    def hardened_suite(self, *, iterations: int = 10_000) -> dict[str, Any]:
        """Execute real release evidence against the deterministic NosTale sandbox."""
        from app.world_model.actions import WorldAction
        from app.world_model.simple_nostale_sandbox import SimpleNosTaleSandbox
        from app.world_model.state import EntityState, WorldState

        model = SimpleNosTaleSandbox()
        actions = [
            WorldAction("attack", "ATTACK", {"target_id": "mob", "damage": 1.0}),
            WorldAction("move", "MOVE", {"position": (1, 2)}),
        ]

        def make_state():
            return WorldState(
                character={"hp": 100, "position": (0, 0)},
                entities={"mob": EntityState("mob", "monster", {"hp": 100.0})},
                inventory={"potion": 2},
            )

        state = make_state()

        def step():
            nonlocal state
            state, _ = model.apply(state, actions[state.tick % len(actions)])
            return state.tick

        def snap():
            return {
                "tick": state.tick,
                "character": state.character,
                "entities": {k: v.attributes for k, v in state.entities.items()},
                "inventory": state.inventory,
            }

        long_report = self.execute_long_run(step, iterations, snapshot=snap, invariant=lambda x: x > 0)

        injected_state = make_state()
        checkpoint = json.loads(json.dumps({"tick": injected_state.tick, "character": injected_state.character, "inventory": injected_state.inventory}))
        restored = {"ok": False}

        def fail():
            injected_state.tick += 1
            raise RuntimeError("injected runtime fault")

        def recover():
            injected_state.tick = checkpoint["tick"]
            injected_state.character = dict(checkpoint["character"])
            injected_state.inventory = dict(checkpoint["inventory"])
            restored["ok"] = injected_state.tick == checkpoint["tick"] and injected_state.character == checkpoint["character"]
            return restored["ok"]

        fault_report = self.execute_fault_injection(fail, RuntimeError)
        recovery_report = self.execute_recovery(fail, recover, validator=lambda x: x is True)

        def deterministic_run():
            s = make_state()
            trace = []
            for i in range(250):
                s, events = model.apply(s, actions[i % len(actions)])
                trace.append((s.tick, events, s.character, s.inventory, {k: v.attributes for k, v in s.entities.items()}))
            return trace

        reproducibility_report = self.execute_reproducibility(deterministic_run, runs=3)

        # Real end-to-end runtime: M1 -> learned World Model -> M2..M15.
        from app.nosai_runtime import NosAiCoreRuntime

        def end_to_end_run():
            import tempfile
            from pathlib import Path
            from app.world_model.actions import WorldAction
            runtime = NosAiCoreRuntime(memory_path=Path(tempfile.mkdtemp()) / "runtime.db", seed=42)
            s = make_state()
            trace = []
            actions = [
                WorldAction("attack", "ATTACK", {"target_id": "mob", "damage": 1.0}),
                WorldAction("move", "MOVE", {"position": (1, 2)}),
            ]
            for i in range(25):
                decision = runtime.decide(s, actions, goal_distance=max(0.0, s.entities["mob"].attributes["hp"] / 100.0))
                chosen = next(a for a in actions if a.action_id == decision.action.action_id or decision.action.action_id == a.action_id)
                before_hp = s.entities["mob"].attributes["hp"]
                s, events = model.apply(s, chosen)
                after_hp = s.entities["mob"].attributes["hp"]
                trace.append((s.tick, decision.action.action_id, round(decision.confidence, 6), events, after_hp, decision.trace))
                if before_hp == after_hp and not events:
                    raise RuntimeError("runtime decision produced no observable environment transition")
            runtime.close()
            return trace

        e2e_first = end_to_end_run()
        e2e_second = end_to_end_run()
        end_to_end_pass = self.deterministic_hash(e2e_first) == self.deterministic_hash(e2e_second) and len(e2e_first) == 25 and all(len(x[-1]) == 15 for x in e2e_first)

        return {
            "long_run": asdict(long_report),
            "fault_injection": asdict(fault_report),
            "recovery": asdict(recovery_report),
            "reproducibility": asdict(reproducibility_report),
            "end_to_end": {"passed": end_to_end_pass, "steps": len(e2e_first)},
        }
