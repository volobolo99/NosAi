
from app.memory_v2.storage.sqlite_store import SQLiteMemoryStore
from app.memory_v2.models import Observation
from app.planning_monte_carlo.planner import MonteCarloPlanner
from app.planning_monte_carlo.scenarios import StochasticBasicModel
from app.strategy_simulator.models import SimState, SimAction

def test_persistent_memory_and_monte_carlo(tmp_path):
    store=SQLiteMemoryStore(tmp_path/"ai.db")
    store.save_observation(Observation("x","MAP_CHANGED",{"map_id":1},"tcp"))
    planner=MonteCarloPlanner(StochasticBasicModel(),seed=1)
    action=SimAction("a","ATTACK",{"damage":120,"hit_chance":1,"time":2})
    result=planner.evaluate("farm",SimState({"hp":100,"target_hp":100}),(action,),20)
    assert store.count("observations")==1
    assert result.success_probability==1.0
    store.close()
