from app.progression import CharacterSnapshot, ProgressionPlan, ProgressionSimulator, ProgressionAdvisor


def snapshot():
    return CharacterSnapshot(snapshot_id="s1", timestamp=1.0, level=50, confidence=0.9, resources={"gold": 1000}, equipment={"weapon": "basic"}, skills={"main": 1}, derived={"progression_score": 0.4})


def test_snapshot_is_validated():
    assert snapshot().validate() == ()


def test_simulator_is_reproducible():
    plans = (ProgressionPlan("a", "farm", ("farm",), 1.0, 3600, 10, 0.1),)
    sim = ProgressionSimulator(seed=7, simulations=64)
    assert sim.evaluate(snapshot(), plans) == sim.evaluate(snapshot(), plans)


def test_policy_blocked_plan_cannot_win():
    plans = (
        ProgressionPlan("blocked", "external", (), 10.0, 1, 0, 0, policy_status="BLOCKED"),
        ProgressionPlan("safe", "farm", ("farm",), 1.0, 100, 0, 0.1),
    )
    ranked = ProgressionSimulator(simulations=32).evaluate(snapshot(), plans)
    assert ranked[0].plan_id == "safe"
    assert any(r.status == "BLOCKED_BY_POLICY" for r in ranked)


def test_advisor_returns_top_three_or_fewer_and_explanation():
    plans = tuple(ProgressionPlan(str(i), "plan", (), i / 10, 100 + i, i, 0.1) for i in range(5))
    report = ProgressionAdvisor(ProgressionSimulator(simulations=32)).evaluate(snapshot(), "next upgrade", plans)
    assert report.recommendation
    assert report.explanation.startswith("GuardAi")
    assert len(report.ranked) == 5
