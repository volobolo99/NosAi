
from .base import RLEnvironment
from app.world_model.simple_nostale_sandbox import SimpleNosTaleSandbox
from app.world_model.state import WorldState, EntityState
from app.world_model.actions import WorldAction

class WorldRLEnvironment(RLEnvironment):
    """RL adapter around the world-model sandbox."""

    def __init__(self, seed_state=None):
        self.initial=seed_state or WorldState(
            character={"hp":100,"mp":100,"position":"start"},
            entities={
                "mob:1": EntityState("mob:1","monster",{"hp":100})
            },
            inventory={"potion":3},
            map_id="sandbox",
        )
        self.model=SimpleNosTaleSandbox()

    def reset(self):
        return self.initial.copy()

    def actions(self,state):
        actions=[]
        if state.entities.get("mob:1",None):
            actions.append(WorldAction(
                "attack","ATTACK",{"target_id":"mob:1","damage":25}
            ))
        if state.inventory.get("potion",0)>0 and state.character.get("hp",100)<100:
            actions.append(WorldAction("potion","USE_ITEM",{"item_id":"potion"}))
        actions.append(WorldAction("move","MOVE",{"position":"safe"}))
        return actions

    def step(self,state,action):
        before=state
        current,events=self.model.apply(state,action)
        reward=self.reward(before,current,events)
        target=current.entities.get("mob:1")
        done=(target is not None and target.attributes.get("hp",100)<=0)
        return current,reward,done

    def reward(self,previous,current,events):
        reward=0.0
        if "DAMAGE" in events: reward+=1.0
        if "TARGET_DEFEATED" in events: reward+=10.0
        if "ITEM_USED" in events: reward-=0.5
        if "MOVED" in events: reward-=0.1
        return reward
