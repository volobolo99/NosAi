from __future__ import annotations

from dataclasses import dataclass

from app.simulation_repair.code_generation import CodeCandidate
from app.simulation_repair.models import ErrorEvent
from app.simulation_repair.research import ResearchHit, build_research_queries
from app.simulation_repair.research_pipeline import ResearchPipeline


@dataclass
class FakeResearcher:
    def search(self, queries, *, total_limit=16):
        assert queries
        return [ResearchHit(title="known fix", url="https://example.test/fix", source_type="test")]


class FakeCodeGenerator:
    def generate(self, *, error_type, message, proposals):
        return [
            CodeCandidate(
                candidate_id="good",
                source_candidate_id=proposals[0].candidate_id,
                file_path="app/example.py",
                patch_text="--- a/app/example.py\n+++ b/app/example.py\n@@\n+pass\n",
                rationale="test candidate",
                evidence_urls=proposals[0].evidence_urls,
            ),
            CodeCandidate(
                candidate_id="bad",
                source_candidate_id=proposals[0].candidate_id,
                file_path="../outside.py",
                patch_text="bad",
                rationale="unsafe path",
                evidence_urls=proposals[0].evidence_urls,
            ),
        ]


def test_query_generation_is_bounded_and_deterministic():
    first = build_research_queries("TimeoutError", "request timed out", "runtime")
    second = build_research_queries("TimeoutError", "request timed out", "runtime")
    assert first == second
    assert 1 <= len(first) <= 6


def test_pipeline_keeps_provenance_and_rejects_invalid_code_candidate():
    error = ErrorEvent.create(
        source="SIMULATED",
        severity="ERROR",
        component="runtime",
        test_name="example",
        error_type="TimeoutError",
        message="request timed out",
    )
    result = ResearchPipeline(FakeResearcher(), FakeCodeGenerator()).run(error)
    assert result.hits[0].url == "https://example.test/fix"
    assert result.proposals[0].evidence_urls == ("https://example.test/fix",)
    assert [candidate.candidate_id for candidate in result.code_candidates] == ["good"]
    assert result.rejected_code_candidates[0][0] == "bad"
