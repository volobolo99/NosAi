
from app.world_model.state import WorldState,EntityState
from app.world_model.actions import WorldAction
from app.world_model.simple_nostale_sandbox import SimpleNosTaleSandbox

def test_world_model_attack_transition():
    s=WorldState(
        character={"hp":100},
        entities={"m":EntityState("m","monster",{"hp":50})}
    )
    model=SimpleNosTaleSandbox()
    ns,events=model.apply(s,WorldAction(
        "a","ATTACK",{"target_id":"m","damage":60}
    ))
    assert ns.entities["m"].attributes["hp"]==0
    assert "TARGET_DEFEATED" in events
