
class StrategySimulatorBridge:
    """Connects StrategyEngine candidates to the sandbox simulator."""

    def __init__(self, simulator):
        self.simulator = simulator

    def evaluate(self, candidate, initial_state, runs=10):
        return self.simulator.run(
            strategy_id=candidate.id,
            initial_state=initial_state,
            actions=candidate.steps,
            runs=runs,
        )

    def rank(self, candidates, initial_state, runs=10):
        results = [
            self.evaluate(c, initial_state, runs)
            for c in candidates
        ]
        return sorted(
            results,
            key=lambda r: (
                r.success_probability,
                r.expected_reward,
                -r.expected_duration,
                -r.expected_risk,
            ),
            reverse=True,
        )
