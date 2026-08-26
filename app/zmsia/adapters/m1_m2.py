"""Compatibility adapters for the existing M1/M2 domain layers.

Adapters deliberately keep legacy module types out of the ZMSIA Core. M1 is
mapped explicitly because its public value objects are stable. M2 is exposed
through a tiny duck-typed boundary so the planner implementation can evolve
without coupling Core to its concrete class layout.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from app.m1.core.types import Action as M1Action
from app.m1.core.types import State as M1State

from app.zmsia.core.contracts import Action, Plan, State


class M2PlannerLike(Protocol):
    """Minimum surface an existing M2 planner must expose to be adapted."""

    def plan(self, goal: Any, state: Any) -> Any:
        ...


def m1_state_to_zmsia(state: M1State, *, observation_ids: tuple[str, ...] = ()) -> State:
    """Convert an M1 state to the provider-neutral ZMSIA state."""
    values: dict[str, Any] = {
        "features": state.features,
        "scenario_id": state.scenario_id,
        "metadata": dict(state.metadata),
    }
    confidence = _confidence_from_metadata(state.metadata)
    return State(
        state_id=f"m1:{state.scenario_id}:{state.timestamp}",
        timestamp_ms=int(state.timestamp),
        values=values,
        confidence=confidence,
        source_observation_ids=observation_ids,
    )


def m1_action_to_zmsia(action: M1Action, *, decision_id: str = "") -> Action:
    """Convert an M1 action into an unchecked ZMSIA action intent."""
    return Action(
        action_id=str(action.id),
        parameters=dict(action.parameters),
        decision_id=decision_id,
    )


def m2_plan_to_zmsia(plan: Any, *, goal_id: str) -> Plan:
    """Normalize common planner outputs into the ZMSIA Plan contract.

    Supported planner output forms are intentionally small: an existing Plan,
    a mapping, or an object exposing ``steps``/``actions``. Unknown fields are
    ignored rather than leaking concrete M2 objects into the Core.
    """
    if isinstance(plan, Plan):
        return plan

    if isinstance(plan, Mapping):
        plan_id = str(plan.get("plan_id", plan.get("id", f"m2:{goal_id}")))
        raw_steps = plan.get("steps", plan.get("actions", ()))
        rationale = str(plan.get("rationale", ""))
        confidence = float(plan.get("confidence", 0.0))
        provider = str(plan.get("provider", "m2"))
    else:
        plan_id = str(getattr(plan, "plan_id", getattr(plan, "id", f"m2:{goal_id}")))
        raw_steps = getattr(plan, "steps", getattr(plan, "actions", ()))
        rationale = str(getattr(plan, "rationale", ""))
        confidence = float(getattr(plan, "confidence", 0.0))
        provider = str(getattr(plan, "provider", "m2"))

    steps = tuple(_step_id(step) for step in _as_sequence(raw_steps))
    return Plan(
        plan_id=plan_id,
        goal_id=goal_id,
        steps=steps,
        rationale=rationale,
        confidence=max(0.0, min(1.0, confidence)),
        provider=provider,
    )


def _as_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        return (value,)
    try:
        return tuple(value)
    except TypeError:
        return (value,)


def _step_id(step: Any) -> str:
    if isinstance(step, Mapping):
        return str(step.get("id", step.get("action_id", step)))
    return str(getattr(step, "id", getattr(step, "action_id", step)))


def _confidence_from_metadata(metadata: Mapping[str, Any]) -> float:
    value = metadata.get("confidence", 1.0)
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 1.0
