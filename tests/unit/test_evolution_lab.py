import pytest

from app.evolution_lab.candidates import Candidate, compose_ensemble
from app.evolution_lab.research import ResearchFinding, rank_findings


def test_research_ranking_is_deterministic() -> None:
    findings = [
        ResearchFinding("b", "source-b", "B", "", relevance=.8, reliability=.8, freshness=.8),
        ResearchFinding("a", "source-a", "A", "", relevance=.9, reliability=.9, freshness=.9),
    ]
    assert [f.finding_id for f in rank_findings(findings)] == ["a", "b"]


def test_ensemble_preserves_all_candidate_provenance() -> None:
    candidates = [
        Candidate("c2", ("f2",), "patch-b", "b", score=.7),
        Candidate("c1", ("f1",), "patch-a", "a", score=.9),
    ]
    ensemble = compose_ensemble(candidates)
    assert ensemble.candidate_ids == ("c1", "c2")
    assert ensemble.provenance == ("f1", "f2")
    assert "patch-a" in ensemble.composite_patch and "patch-b" in ensemble.composite_patch


def test_empty_ensemble_is_rejected() -> None:
    with pytest.raises(ValueError):
        compose_ensemble([])
