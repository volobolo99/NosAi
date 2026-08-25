
from app.strategy_simulator.engine import StrategySimulator
from app.strategy_simulator.models import SimState, SimAction
from app.strategy_simulator.scenarios.basic import BasicGameTransitionModel
from app.strategy_simulator.strategy_bridge import StrategySimulatorBridge


class Candidate:
    def __init__(self, id, steps):
        self.id = id
        self.steps = steps


def test_bridge_ranks_candidates():
    simulator = StrategySimulator(BasicGameTransitionModel())
    bridge = StrategySimulatorBridge(simulator)

    safe = Candidate("safe", (
        SimAction("a", "ATTACK", {"damage": 100, "time": 5, "risk": .1}),
    ))
    fast = Candidate("fast", (
        SimAction("a", "ATTACK", {"damage": 100, "time": 2, "risk": .2}),
    ))

    ranked = bridge.rank(
        [safe, fast],
        SimState({"hp": 100, "target_hp": 100}),
        runs=5,
    )

    assert ranked[0].strategy_id == "fast"
