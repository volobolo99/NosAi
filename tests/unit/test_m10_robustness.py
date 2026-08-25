from app.m10.robustness import RobustnessEngine

def test_adversarial_and_rare_scores():
    r=RobustnessEngine(); assert r.adversarial_score(1,[1,1])==1; assert r.rare_event_score(1,10)==.9

def test_observation_quality():
    assert RobustnessEngine().observation_quality([1,2],[1,2])==1

def test_failure_and_fallback():
    r=RobustnessEngine(); assert r.predict_failure(1,1); assert r.safe_action('p','f',failure_probability=.9)=='f'
