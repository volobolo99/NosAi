from app.benchmark.objective_ablation import run_objective_ablation


def test_goal_aware_objective_improves_goal_choice():
    report = run_objective_ablation()
    assert report.goal_aware_improves_goal_success
    assert report.goal_aware_improves_utility
    assert report.goal_aware_goal_success == 1.0
    assert report.reward_only_goal_success == 0.0
