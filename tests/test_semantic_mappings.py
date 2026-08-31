from app.knowledge.semantic_mappings import SemanticMapping, apply_mapping


def test_mapping_is_explicit_and_lossless():
    mapping = SemanticMapping("in", "PositionX", "x", evidence="verified schema", verified=True)
    assert apply_mapping({"PositionX": 12}, mapping) == {"x": 12}


def test_missing_source_field_produces_no_guess():
    mapping = SemanticMapping("in", "PositionX", "x")
    assert apply_mapping({}, mapping) == {}
