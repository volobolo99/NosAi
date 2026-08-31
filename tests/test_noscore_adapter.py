from app.knowledge.noscore_adapter import packet_schema_candidates


def test_packet_schema_is_preserved_without_semantic_inference():
    result = packet_schema_candidates(
        {"in": {"fields": [{"name": "VisualId", "type": "long"}]}},
        source_ref="NosCoreIO/NosCore.Packets@abc",
        source_commit="abc",
    )
    assert len(result) == 1
    assert result[0].record_id == "in"
    assert result[0].kind == "packet_schema"
    assert result[0].fields["fields"][0]["name"] == "VisualId"
    assert result[0].verified is False
