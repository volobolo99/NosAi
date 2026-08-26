"""Optional structured visual perception for the real NosTale client.

The analyzer receives a screenshot of the visible game window and returns a
small, typed observation. It is deliberately read-only: no tool/action call is
made and no client input is generated.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any

from .screen_observation import ScreenFrame


@dataclass(frozen=True)
class VisualObservation:
    vita_percent: float | None = None
    mana_percent: float | None = None
    posizione_x: float | None = None
    posizione_y: float | None = None
    mappa: str | None = None
    bersaglio: str | None = None
    oggetti: tuple[dict[str, Any], ...] = ()
    giocatori: tuple[dict[str, Any], ...] = ()
    nemici: tuple[dict[str, Any], ...] = ()
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SYSTEM = """Sei il modulo di percezione visiva di NosAi per un client NosTale.
Analizza esclusivamente ciò che è chiaramente visibile nello screenshot.
Non inventare valori. Usa null se un dato non è leggibile. Rispondi SOLO con
JSON valido con queste chiavi: vita_percent, mana_percent, posizione_x,
posizione_y, mappa, bersaglio, oggetti, giocatori, nemici, note.
Gli oggetti devono avere almeno nome e, se leggibile, quantità. Non descrivere
azioni da compiere e non usare comandi sul client."""


def _coerce_number(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
        return number if number == number else None
    except (TypeError, ValueError):
        return None


def _normalize(data: dict[str, Any]) -> VisualObservation:
    def entities(key: str) -> tuple[dict[str, Any], ...]:
        raw = data.get(key) or []
        if not isinstance(raw, list):
            return ()
        return tuple(item for item in raw if isinstance(item, dict))

    return VisualObservation(
        vita_percent=_coerce_number(data.get("vita_percent")),
        mana_percent=_coerce_number(data.get("mana_percent")),
        posizione_x=_coerce_number(data.get("posizione_x")),
        posizione_y=_coerce_number(data.get("posizione_y")),
        mappa=str(data["mappa"]) if data.get("mappa") is not None else None,
        bersaglio=str(data["bersaglio"]) if data.get("bersaglio") is not None else None,
        oggetti=entities("oggetti"),
        giocatori=entities("giocatori"),
        nemici=entities("nemici"),
        note=str(data["note"]) if data.get("note") is not None else None,
    )


def analyze_frame(frame: ScreenFrame) -> VisualObservation:
    """Analyze one frame through OpenAI Responses API when configured.

    The API key stays server-side. Set OPENAI_API_KEY and optionally
    NOSAI_VISION_MODEL. A missing key produces a safe empty observation.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return VisualObservation(note="percezione AI non configurata: OPENAI_API_KEY assente")

    model = os.getenv("NOSAI_VISION_MODEL", "gpt-5.6-luna").strip()
    encoded = base64.b64encode(frame.image_bytes).decode("ascii")
    payload = {
        "model": model,
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": _SYSTEM},
            {"type": "input_image", "image_url": f"data:{frame.content_type};base64,{encoded}"},
        ]}],
        "max_output_tokens": 500,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return VisualObservation(note=f"percezione AI non disponibile: {exc}")

    text = result.get("output_text", "")
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return VisualObservation(note="percezione AI: risposta non JSON")
    return _normalize(parsed if isinstance(parsed, dict) else {})
