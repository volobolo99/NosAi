from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .multi_entity import MultiEntityRecognizer
from .nostale_windows import WindowsNosTaleAdapter
from .windows_hud import WindowsHudOcr
from .windows_perception import WindowsNosTalePerception
from .world_state import from_client_state


class LiveObservation:
    """One real-client observation cycle; never executes a game action."""

    def __init__(self, adapter: WindowsNosTaleAdapter | None = None) -> None:
        self.adapter = adapter or WindowsNosTaleAdapter()

    def capture(self) -> tuple[dict[str, Any], bytes]:
        perception = WindowsNosTalePerception(self.adapter)
        frame = perception.capture()
        hud: Any = None
        ocr_error: str | None = None
        try:
            hud = WindowsHudOcr().extract(frame)
        except Exception as exc:
            ocr_error = f"{type(exc).__name__}: {exc}"

        entities: Any = None
        entity_error: str | None = None
        manifest = os.getenv("NOSAI_ENTITY_MANIFEST", "").strip()
        if manifest and Path(manifest).is_file():
            try:
                recognizer = MultiEntityRecognizer.from_manifest(manifest)
                _, entities = perception.capture_and_recognize(recognizer)
            except Exception as exc:
                entity_error = f"{type(exc).__name__}: {exc}"

        state = self.adapter.read_state()
        world = from_client_state(state, hud=hud, perception=entities).to_dict()
        world["frame"] = {
            "width": frame.width,
            "height": frame.height,
            "source": frame.source,
            "observation_only": frame.observation_only,
        }
        world["quality"] = {
            "hud_ocr": "PASS" if hud is not None else "NOT_RUN",
            "entity_recognition": "PASS" if entities is not None else "NOT_RUN",
            "ocr_error": ocr_error,
            "entity_error": entity_error,
        }
        return world, frame.png
