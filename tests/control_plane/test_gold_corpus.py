from app.control_plane.bug_corpus import build_bug_example
from app.control_plane.gold_corpus import VerificationEvidence, VerificationStatus, admit_gold, partition_negatives


def _candidate(commit: str):
    return build_bug_example(
        example_id=f"git-{commit}",
        repository_id="nosai",
        project_id="control",
        error_signature="fix: runner regression",
        root_cause="verified root cause",
        patch_summary="verified patch",
        lesson="verified lesson",
    )


def test_only_successfully_verified_candidates_enter_gold() -> None:
    candidates = [_candidate("good"), _candidate("bad"), _candidate("unknown")]
    evidence = [
        VerificationEvidence("good", VerificationStatus.VERIFIED, "pytest", 0),
        VerificationEvidence("bad", VerificationStatus.FAILED, "pytest", 1),
        VerificationEvidence("unknown", VerificationStatus.UNKNOWN, "pytest", 0),
    ]
    gold = admit_gold(candidates, evidence)
    negatives = partition_negatives(candidates, evidence)
    assert [item.example_id for item in gold] == ["git-good"]
    assert [item.example_id for item in negatives] == ["git-bad"]


def test_verified_status_with_nonzero_exit_does_not_pass() -> None:
    candidate = _candidate("broken")
    evidence = [VerificationEvidence("broken", VerificationStatus.VERIFIED, "pytest", 1)]
    assert admit_gold([candidate], evidence) == ()
