import math
class DataValidator:
    def validate(self,t):
        errors=[]; warnings=[]
        for name,v in [('reward',t.reward)]:
            if not isinstance(v,(int,float)) or not math.isfinite(v): errors.append(f'{name}: non-finite numeric')
        if t.state is None or t.next_state is None: errors.append('state/next_state missing')
        if t.action is None: errors.append('action missing')
        return {'valid':not errors,'errors':errors,'warnings':warnings}
