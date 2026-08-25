
from app.strategy_simulator.models import SimOutcome

class StochasticBasicModel:
    """Sandbox-only stochastic transition model."""

    def apply_stochastic(self, state, action, rng):
        hp=float(state.get("hp",100))
        target=float(state.get("target_hp",100))
        base_damage=float(action.params.get("damage",0))
        hit_chance=float(action.params.get("hit_chance",1.0))
        self_damage=float(action.params.get("self_damage",0))
        time=float(action.params.get("time",1))
        risk=float(action.params.get("risk",.1))

        hit=rng.random() <= hit_chance
        damage=base_damage if hit else 0
        target=max(0,target-damage)
        hp=max(0,hp-self_damage)
        success=hp>0
        reward=damage+(action.params.get("kill_reward",10) if target==0 else 0)

        return SimOutcome(
            success=success,
            state=state.with_updates(hp=hp,target_hp=target),
            reward=reward,
            duration_seconds=time,
            risk=risk,
            events=(action.kind, "HIT" if hit else "MISS")
        )
