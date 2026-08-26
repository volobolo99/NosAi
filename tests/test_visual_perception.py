from __future__ import annotations

import json

from app.client.screen_observation import ScreenFrame
from app.client.vision_observation import VisualObservation, _normalize, analyze_frame


def test_visual_observation_normalizes_numbers_and_entities() -> None:
    result = _normalize({
        "vita_percent": "93",
        "mana_percent": 71,
        "posizione_x": "128",
        "posizione_y": 74,
        "mappa": "NosVille",
        "bersaglio": "Mob A",
        "oggetti": [{"nome": "Diamante", "quantita": 2}],
        "nemici": [{"nome": "Mob A"}],
    })
    assert result.vita_percent == 93
    assert result.mana_percent == 71
    assert result.posizione_x == 128
    assert result.mappa == "NosVille"
    assert result.oggetti[0]["nome"] == "Diamante"


def test_missing_api_key_is_safe(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    frame = ScreenFrame(b"jpeg", 100, 50)
    result = analyze_frame(frame)
    assert isinstance(result, VisualObservation)
    assert result.vita_percent is None
    assert "OPENAI_API_KEY" in (result.note or "")


def test_openai_visual_response_is_structured(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"output_text": json.dumps({"vita_percent": 88, "mana_percent": 66})}).encode()

    def fake_urlopen(*args, **kwargs):
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = analyze_frame(ScreenFrame(b"jpeg", 100, 50))
    assert result.vita_percent == 88
    assert result.mana_percent == 66
