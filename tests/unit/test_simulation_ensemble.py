from app.simulation_repair.ensemble import synthesize
from app.simulation_repair.models import CandidateResult


def candidate(cid: str, status: str = "PASS", notes=None) -> CandidateResult:
    return CandidateResult(
        candidate_id=cid,
        status=status,
        description=f"candidate {cid}",
        evidence=[f"evidence-{cid}"],
        checks={"replay": "PASS", "regression": "PASS"} if status == "PASS" else {"replay": "FAIL"},
        notes=notes or [],
    )


def test_synthesis_keeps_multiple_compatible_candidates():
    result = synthesize([candidate("A"), candidate("B")])
    assert result.status == "READY_FOR_REVIEW"
    assert result.selected_candidate_ids == ["A", "B"]
    assert result.composite_plan == ["candidate:A", "candidate:B"]


def test_synthesis_does_not_merge_explicit_conflicts():
    result = synthesize([
        candidate("A", notes=["CONFLICT:transport"]),
        candidate("B", notes=["CONFLICT:transport"]),
    ])
    assert result.status == "CONFLICT_REVIEW"
    assert result.selected_candidate_ids == ["A"]
    assert result.conflicts


def test_synthesis_requires_at_least_one_pass():
    result = synthesize([candidate("A", "FAIL"), candidate("B", "NOT_RUN")])
    assert result.status == "NO_PASS"
    assert result.selected_candidate_ids == []
