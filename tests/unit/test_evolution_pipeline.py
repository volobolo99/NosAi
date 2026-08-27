from app.evolution_lab.pipeline import build_proposal
from app.evolution_lab.research import ResearchFinding, ResearchResult


class Provider:
    name = "test-provider"

    def search(self, query: str, *, limit: int = 10) -> ResearchResult:
        return ResearchResult(query, (
            ResearchFinding("f1", self.name, "A", "patch-a", relevance=.9, reliability=.9, freshness=.9),
            ResearchFinding("f2", self.name, "B", "patch-b", relevance=.7, reliability=.8, freshness=.8),
        ))


def test_build_proposal_wires_research_candidates_and_ensemble() -> None:
    proposal = build_proposal("sandbox failure", [Provider()], limit=2)
    assert len(proposal.research.findings) == 2
    assert len(proposal.candidates) == 2
    assert len(proposal.ensemble.candidate_ids) == 2
    assert proposal.ensemble.provenance == ("f1", "f2")
