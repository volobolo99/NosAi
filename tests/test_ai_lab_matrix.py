from app.ai_lab.matrix import build_edge_case_matrix, run_edge_case_matrix


def test_edge_case_matrix_is_large_and_deterministic() -> None:
    first = build_edge_case_matrix()
    second = build_edge_case_matrix()
    assert len(first) == 144
    assert first == second


def test_edge_case_matrix_never_marks_forbidden_action_as_safe() -> None:
    runs, summary = run_edge_case_matrix()
    assert summary.total == len(runs) == 144
    assert summary.safety_failed == 0
    assert all(run.result.safety_status == "PASS" for run in runs)
