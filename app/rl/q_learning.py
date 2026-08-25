
import random

class QLearningAgent:
    def __init__(self, alpha=.1, gamma=.95, epsilon=.2, seed=42):
        self.alpha=alpha
        self.gamma=gamma
        self.epsilon=epsilon
        self.q={}
        self.rng=random.Random(seed)

    def _key(self, obj):
        if hasattr(obj, "key"):
            return obj.key
        if hasattr(obj, "values"):  # WorldState-like object
            v=obj.values
            return repr(v)
        if hasattr(obj, "character") and hasattr(obj, "entities"):
            char=tuple(sorted(obj.character.items()))
            entities=tuple(sorted(
                (k, tuple(sorted(e.attributes.items())))
                for k,e in obj.entities.items()
            ))
            inv=tuple(sorted(obj.inventory.items()))
            return repr((obj.map_id,char,entities,inv))
        return repr(obj)

    def value(self,state,action):
        return self.q.get((self._key(state),self._key(action)),0.0)

    def choose(self,state,actions):
        if not actions: return None
        if self.rng.random()<self.epsilon:
            return self.rng.choice(actions)
        return max(actions,key=lambda a:self.value(state,a))

    def update_raw(self,state,action,reward,next_state,done,next_actions):
        sk,ak=self._key(state),self._key(action)
        nsk=self._key(next_state)
        old=self.q.get((sk,ak),0.0)
        future=0.0 if done else max(
            (self.q.get((nsk,self._key(a)),0.0) for a in next_actions),
            default=0.0
        )
        self.q[(sk,ak)]=old+self.alpha*(
            reward+self.gamma*future-old
        )

    def update(self, transition):
        # Backward-compatible API used by the original v4.6 trainer.
        next_actions=[]
        self.update_raw(
            transition.state,
            transition.action,
            transition.reward,
            transition.next_state,
            transition.done,
            next_actions,
        )

    def export(self):
        return dict(self.q)
