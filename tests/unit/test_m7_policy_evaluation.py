from app.m7.multi_agent import MatchResult, PolicyEvaluator


def test_evaluation_counts_only_target_games():
    rows = [MatchResult('a', 'b'), MatchResult('c', 'd'), MatchResult('b', 'a'), MatchResult('a', 'c')]
    result = PolicyEvaluator().evaluate(rows, 'a')
    assert result.games == 3
    assert result.wins == 2
    assert result.losses == 1
    assert result.draws == 0
    assert result.score == 2 / 3


def test_evaluation_exposes_uncertainty_and_confidence():
    result = PolicyEvaluator().evaluate([MatchResult('a', 'b')] * 9, 'a')
    assert result.standard_error > 0
    assert 0 < result.confidence < 1


def test_empty_evaluation_is_safe():
    result = PolicyEvaluator().evaluate([], 'a')
    assert result.games == 0 and result.score == 0.0 and result.confidence == 0.0


def test_compare_reports_score_delta_and_pooled_error():
    evaluator = PolicyEvaluator()
    left = evaluator.evaluate([MatchResult('a', 'b')] * 4, 'a')
    right = evaluator.evaluate([MatchResult('b', 'a')] * 4, 'a')
    comparison = evaluator.compare(left, right)
    assert comparison['score_delta'] == 1.0
    assert comparison['pooled_standard_error'] > 0
