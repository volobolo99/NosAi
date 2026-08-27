from app.simulation_repair.candidate_generator import generate_candidates
from app.simulation_repair.research import ResearchHit, build_research_queries


def test_build_research_queries_is_bounded_and_deterministic():
    queries = build_research_queries("TimeoutError", "socket timeout", "client")
    assert queries == [
        "TimeoutError socket timeout",
        "TimeoutError client",
        '"socket timeout" TimeoutError',
        "TimeoutError Python fix",
        "TimeoutError Windows Python",
        "client TimeoutError regression",
    ]
    assert len(queries) == 6


def test_candidate_generation_keeps_source_provenance():
    hits = [ResearchHit("Fix example", "https://github.com/example/project/blob/main/x.py", "github_code", repository="example/project")]
    candidates = generate_candidates("TimeoutError", "socket timeout", hits)
    assert len(candidates) == 1
    assert candidates[0].evidence_urls == (hits[0].url,)
    assert candidates[0].source_repositories == ("example/project",)
