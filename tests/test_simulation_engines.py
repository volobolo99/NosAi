from app.simulation.combat import AttackInput, BCardEffect, BCardFSM, BCardPriority, CombatSimulator
from app.simulation.ekf import EKFStateEstimator, Observation
from app.simulation.economy import ExtendedMakeOrBuyOptimizer, Ingredient
from app.simulation.pathfinding import GridMap, HazardCell, PathPlanner
from app.simulation.rca import PostMortemRCA, TelemetryBuffer, TelemetrySample


def test_combat_miss_short_circuits_damage_chain():
    data = AttackInput(50, 10, 10, 100, 100, 10, 20, 0.0, 20, 1, 50, 0, 0, 0)
    result = CombatSimulator(seed=1).simulate_attack(data, forced_roll=0.9)
    assert not result.hit
    assert result.total_damage == 0


def test_combat_hit_calculates_positive_damage():
    data = AttackInput(100, 10, 10, 100, 100, 10, 20, 0.5, 20, 2, 50, 10, 20, 5)
    result = CombatSimulator(seed=1).simulate_attack(data, forced_roll=0.1)
    assert result.hit
    assert result.physical_damage > 0
    assert result.total_damage > 0


def test_bcard_hard_cc_cancels_cast_and_cleanse_removes_low_level():
    fsm = BCardFSM()
    fsm.cast_active = True
    fsm.apply(BCardEffect("stun", BCardPriority.HARD_CC, level=2, duration_ticks=2))
    assert fsm.hard_cc and not fsm.cast_active
    fsm.apply(BCardEffect("cleanse", BCardPriority.CLEANSE, level=2))
    assert not fsm.effects


def test_ekf_update_moves_estimate_toward_observation():
    ekf = EKFStateEstimator([0.0, 0.0], initial_variance=[1.0, 1.0])
    ekf.predict([1.0, 0.0], dt=0.05)
    result = ekf.update(Observation((1.0, 0.0), (0.01, 0.01)))
    assert result.values[0] > 0.9


def test_make_or_buy_uses_geometric_expected_attempts_and_90_percent_bound():
    result = ExtendedMakeOrBuyOptimizer().evaluate_with_rmt(
        "Test Sword", 0.5, 1000, 500, [Ingredient("mat", 2, 100)], 10000, 15000, 10.0
    )
    assert result.gold_expected_make == 13400
    assert result.gold_worst_case_90 == 16800
    assert result.verdict == "MAKE_SAFE"


def test_path_planner_avoids_expensive_hazard_when_route_exists():
    grid = GridMap(5, 3)
    grid.set_hazard(2, 1, HazardCell(aoe=10))
    path = PathPlanner(grid).plan((0, 1), (4, 1))
    assert (2, 1) not in path


def test_rca_finds_first_divergence_and_bayesian_update():
    samples = [
        TelemetrySample(1.0, (0.0,), (0.0,)),
        TelemetrySample(2.0, (0.0,), (0.1,)),
        TelemetrySample(3.0, (0.0,), (0.4,)),
    ]
    buffer = TelemetryBuffer(capacity=2)
    for sample in samples:
        buffer.append(sample)
    divergence = PostMortemRCA.first_divergence(buffer.snapshot(), epsilon=0.05)
    assert divergence is not None and divergence.timestamp == 2.0
    posterior = PostMortemRCA.bayesian_update({"a": 0.5, "b": 0.5}, {"a": 0.8, "b": 0.2})
    assert round(posterior["a"], 3) == 0.8
