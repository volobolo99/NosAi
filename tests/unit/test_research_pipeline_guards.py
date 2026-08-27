from __future__ import annotations

import pytest

from app.simulation_repair.research_pipeline import ResearchPipeline


class EmptyResearcher:
    def search(self, queries, *, total_limit):
        return []


def test_pipeline_rejects_non_positive_limits() -> None:
    pipeline = ResearchPipeline(researcher=EmptyResearcher())
    error = type(
        "Error",
        (),
        {"error_type": "RuntimeError", "message": "boom", "component": "test"},
    )()

    with pytest.raises(ValueError):
        pipeline.run(error, max_sources=0)

    with pytest.raises(ValueError):
        pipeline.run(error, max_proposals=0)
