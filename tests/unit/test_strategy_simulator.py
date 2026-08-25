
from app.strategy_simulator.engine import StrategySimulator
from app.strategy_simulator.models import SimState, SimAction
from app.strategy_simulator.scenarios.basic import BasicGameTransitionModel


def test_simulator_runs_actions():
    simulator = StrategySimulator(BasicGameTransitionModel())

    actions = (
        SimAction(
            "hit", "ATTACK",
            {"damage": 60, "time": 2, "risk": .1}
        ),
        SimAction(
            "hit2", "ATTACK",
            {"damage": 60, "time": 2, "risk": .1}
        ),
    )

    result = simulator.run(
        "fast_kill",
        SimState({"hp": 100, "target_hp": 100}),
        actions,
        runs=3,
    )

    assert result.success_probability == 1.0
    assert result.expected_duration == 4
    assert result.outcomes[0].state.get("target_hp") == 0


def test_failed_action_reduces_strategy_success():
    simulator = StrategySimulator(BasicGameTransitionModel())

    action = SimAction(
        "danger", "ATTACK",
        {"damage": 20, "self_damage": 120, "time": 1, "risk": .9}
    )

    result = simulator.run(
        "dangerous",
        SimState({"hp": 100, "target_hp": 100}),
        (action,),
        runs=2,
    )

    assert result.success_probability == 0.0
