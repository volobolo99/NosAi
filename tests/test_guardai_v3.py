from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_telemetry_contract_contains_pts_field():
    proto = (ROOT / "config/telemetry.proto").read_text()
    assert "presentation_timestamp_us = 2" in proto
    assert "message PerceptionFrame" in proto


def test_stream_profile_is_zero_copy_target():
    cfg = (ROOT / "config/sunshine.conf").read_text()
    assert "capture_method = dxgi" in cfg
    assert "encoder = nvenc" in cfg
    assert "nvenc_bframes = 0" in cfg
    assert "fps = 60" in cfg


def test_signaling_has_explicit_pairing_gate():
    src = (ROOT / "pc_host/guardai_signaling_server.py").read_text()
    assert 'REALME_X50_PRO_GUARD' in src
    assert 'WS_1008_POLICY_VIOLATION' in src
    assert 'SIGNAL_LOST_FORCE_OFFLINE' in src


def test_offline_schema_is_local():
    schema = (ROOT / "config/schema.sql").read_text()
    assert "telemetry_frames" in schema
    assert "failure_analytics" in schema
    assert "mcts_decision_logs" in schema
