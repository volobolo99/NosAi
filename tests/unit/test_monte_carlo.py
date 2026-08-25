
from app.planning_monte_carlo.planner import MonteCarloPlanner
from app.planning_monte_carlo.scenarios import StochasticBasicModel
from app.strategy_simulator.models import SimState, SimAction

class Candidate:
    def __init__(self,id,steps): self.id=id; self.steps=steps

def test_monte_carlo_is_deterministic_with_seed():
    planner=MonteCarloPlanner(StochasticBasicModel(),seed=7)
    c=Candidate("test",(SimAction("a","ATTACK",{
        "damage":100,"hit_chance":.8,"time":2,"risk":.2
    }),))
    a=planner.evaluate("test",SimState({"hp":100,"target_hp":100}),c.steps,200)
    planner2=MonteCarloPlanner(StochasticBasicModel(),seed=7)
    b=planner2.evaluate("test",SimState({"hp":100,"target_hp":100}),c.steps,200)
    assert a.success_probability==b.success_probability
    assert 0 <= a.confidence_interval_95[0] <= a.confidence_interval_95[1] <= 1
