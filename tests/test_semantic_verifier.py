from app.knowledge.semantic_verifier import verify_candidate


def test_present_field_is_not_promoted_without_semantic_evidence():
    result = verify_candidate(
        {"packet": "in", "source_field": "PositionX", "canonical_field": "x"},
        {"fields": [{"name": "PositionX", "type": "short"}]},
    )
    assert result.schema_present is True
    assert result.verified is False


def test_absent_field_is_rejected():
    result = verify_candidate(
        {"packet": "in", "source_field": "NoSuchField", "canonical_field": "x"},
        {"fields": [{"name": "PositionX", "type": "short"}]},
    )
    assert result.schema_present is False
    assert result.verified is False
