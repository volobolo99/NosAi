from app.static_data.knowledge_registry import load_packet_catalog, load_source_manifest, packet_headers


def test_source_manifest_has_provenance_policy():
    manifest = load_source_manifest()
    assert manifest["ingestion_policy"]["require_provenance"] is True
    assert len(manifest["sources"]) >= 4


def test_packet_catalog_has_core_runtime_headers():
    catalog = load_packet_catalog()
    headers = set(packet_headers())
    assert len(catalog["packets"]) >= 25
    assert {"in", "mv", "out", "cond", "drop", "get", "pinit", "st", "su"}.issubset(headers)
