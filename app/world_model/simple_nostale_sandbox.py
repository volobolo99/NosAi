
from .model import WorldModel
from .state import WorldState, EntityState

class SimpleNosTaleSandbox(WorldModel):
    """Generic game-state sandbox, not a live client controller."""

    def apply(self, state, action, rng=None):
        s=state.copy()
        s.tick += 1
        events=[]

        if action.kind == "ATTACK":
            target_id=action.parameters.get("target_id")
            damage=float(action.parameters.get("damage",10))
            target=s.entities.get(target_id)
            if target:
                target=EntityState(target.entity_id,target.entity_type,
                                   dict(target.attributes))
                hp=max(0,float(target.attributes.get("hp",100))-damage)
                target.attributes["hp"]=hp
                s.entities[target_id]=target
                events.append("DAMAGE")
                if hp <= 0:
                    events.append("TARGET_DEFEATED")

        elif action.kind == "USE_ITEM":
            item=action.parameters.get("item_id")
            amount=s.inventory.get(item,0)
            if amount > 0:
                s.inventory[item]=amount-1
                events.append("ITEM_USED")

        elif action.kind == "MOVE":
            s.character["position"]=action.parameters.get(
                "position",s.character.get("position")
            )
            events.append("MOVED")

        return s, tuple(events)
