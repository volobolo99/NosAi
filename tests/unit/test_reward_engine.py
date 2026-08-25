from app.reward.engine import RewardEngine, RewardContext

def test_reward_engine_penalizes_risk_and_time():
    e=RewardEngine()
    good=e.calculate(RewardContext(goal_progress=1,success=True,intrinsic_reward=5,duration_seconds=1,risk=.1))
    bad=e.calculate(RewardContext(goal_progress=.2,success=False,duration_seconds=20,risk=.9,failed=True))
    assert good > bad
