
import random, math
from .models import RolloutResult, MonteCarloResult

class MonteCarloPlanner:
    """Stochastic planning layer over a supplied transition model."""

    def __init__(self, transition_model, seed=42):
        self.transition_model = transition_model
        self.rng = random.Random(seed)

    def evaluate(self, strategy_id, initial_state, actions, runs=100):
        rollouts=[]
        for _ in range(max(1,runs)):
            state=initial_state
            total_reward=0.0
            total_time=0.0
            total_risk=0.0
            success=True
            for action in actions:
                outcome=self.transition_model.apply_stochastic(
                    state, action, self.rng
                )
                state=outcome.state
                total_reward += outcome.reward
                total_time += outcome.duration_seconds
                total_risk += outcome.risk
                if not outcome.success:
                    success=False
                    break
            rollouts.append(RolloutResult(
                success, total_reward, total_time, total_risk,
                getattr(state, "values", {})
            ))

        n=len(rollouts)
        p=sum(r.success for r in rollouts)/n
        se=math.sqrt(max(p*(1-p)/n,0))
        ci=(max(0,p-1.96*se), min(1,p+1.96*se))
        return MonteCarloResult(
            strategy_id, n, p,
            sum(r.reward for r in rollouts)/n,
            sum(r.duration_seconds for r in rollouts)/n,
            sum(r.risk for r in rollouts)/n,
            ci, tuple(rollouts)
        )

    def rank(self, candidates, initial_state, runs=100):
        results=[self.evaluate(c.id, initial_state, c.steps, runs)
                 for c in candidates]
        return sorted(results, key=lambda r: (
            r.success_probability, r.mean_reward,
            -r.mean_duration, -r.mean_risk
        ), reverse=True)
