
from app.strategy_simulator.engine import TransitionModel
from app.strategy_simulator.models import SimState, SimAction, SimOutcome


class BasicGameTransitionModel(TransitionModel):
    """Small deterministic sandbox model for strategy tests."""

    def apply(self, state: SimState, action: SimAction) -> SimOutcome:
        hp = float(state.get("hp", 100))
        target_hp = float(state.get("target_hp", 100))
        time = float(action.params.get("time", 1))
        risk = float(action.params.get("risk", 0.1))
        damage = float(action.params.get("damage", 0))

        target_hp = max(0, target_hp - damage)
        hp = max(0, hp - float(action.params.get("self_damage", 0)))

        success = hp > 0
        reward = damage

        if target_hp == 0:
            reward += float(action.params.get("kill_reward", 10))

        return SimOutcome(
            success=success,
            state=state.with_updates(hp=hp, target_hp=target_hp),
            reward=reward,
            duration_seconds=time,
            risk=risk,
            events=(action.kind,),
        )
