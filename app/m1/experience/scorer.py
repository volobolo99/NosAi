from ..core.types import ExperienceQuality
class ExperienceQualityScorer:
    def __init__(self, weights=None):
        self.w=weights or {'novelty':1,'uncertainty':1,'prediction_error':1,'reward_information':1,'causal_relevance':1,'corruption_penalty':1}
    def score(self, transition, prediction=None, uncertainty=None):
        info=transition.info or {}; novelty=float(info.get('novelty',0)); unc=float(info.get('uncertainty',getattr(uncertainty,'epistemic',0) if uncertainty else 0)); pe=float(info.get('prediction_error',0)); ri=abs(float(transition.reward)); cr=float(info.get('causal_relevance',0)); cp=float(info.get('corruption_score',0))
        vals=[novelty,unc,pe,ri,cr]; total=sum(self.w[k]*v for k,v in zip(['novelty','uncertainty','prediction_error','reward_information','causal_relevance'],vals))-self.w['corruption_penalty']*cp
        return ExperienceQuality(total,novelty,unc,pe,ri,cr,cp)
