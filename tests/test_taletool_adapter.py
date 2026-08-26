import json

from app.assets.taletool_adapter import TaletoolAdapter


def test_taletool_adapter_normalizes_structured_metadata(tmp_path):
    root = tmp_path / "NostaleData"
    root.mkdir()
    tool = tmp_path / "fake_taletool.py"
    payload = {
        "assets": [{"id": "player-1", "family": "player_sprites", "path": "NSppData01.NOS", "sha256": "abc"}],
        "animations": [{"id": "walk", "looping": True, "frames": [{"sprite_frame_index": 3}, {"sprite_frame_index": 4, "event_timing_flag": 1}]}],
        "remaps": [{"sprite_frame_index": 4, "slots": [7, 6, 5]}],
    }
    tool.write_text("import json; print(json.dumps(" + repr(payload) + "))", encoding="utf-8")
    result = TaletoolAdapter(tool).parse(root)
    assert result.parser == "taletool"
    assert result.registry.animations["walk"].looping is True
    assert result.registry.animation_frame("walk", 1).sprite_frame_index == 4
    assert result.registry.resolve_frame_resources(4) == (7, 6, 5)
