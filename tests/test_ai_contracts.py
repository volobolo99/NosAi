from dataclasses import FrozenInstanceError

import pytest

from app.ai.contracts import (
    CONTRACT_VERSION,
    ActionIntent,
    ActionKind,
    Decision,
    Goal,
    MemoryRecord,
    Outcome,
    RewardEvidence,
    WorldState,
)


def test_contracts_are_versioned_and_constructible():
    goal = Goal(kind="survive", priority=1.0)
    state = WorldState(timestamp=1.0, player_hp_ratio=0.25)
    intent = ActionIntent(ActionKind.NOOP)
    outcome = Outcome(status="unknown")
    reward = RewardEvidence(components={"survival": 1.0})
    memory = MemoryRecord("abc", goal, intent, outcome, reward)
    decision = Decision(intent, confidence=0.5, rationale="test", safety_ok=True)

    assert all(
        item.contract_version == CONTRACT_VERSION
        for item in (goal, state, intent, outcome, reward, memory, decision)
    )


def test_action_taxonomy_covers_existing_strategy_primitives():
    assert {ActionKind.ATTACK, ActionKind.MOVE, ActionKind.HEAL,
            ActionKind.RETREAT, ActionKind.WAIT}.issubset(set(ActionKind))


def test_action_intent_is_not_an_execution_side_effect():
    intent = ActionIntent(ActionKind.ATTACK, parameters={"target_id": "x"})
    assert intent.kind is ActionKind.ATTACK
    assert intent.parameters["target_id"] == "x"


def test_world_state_is_immutable_at_decision_boundary():
    state = WorldState(timestamp=1.0, player_hp_ratio=0.5)
    with pytest.raises(FrozenInstanceError):
        state.player_hp_ratio = 0.2
    assert state.player_hp_ratio == 0.5
