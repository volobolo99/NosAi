from __future__ import annotations


def test_live_character_view_returns_rgba_png_and_activity_state() -> None:
    import cv2
    import numpy as np

    from app.client.live_character_view import build_character_view

    image = np.zeros((180, 240, 3), dtype=np.uint8)
    image[:] = (30, 70, 110)
    cv2.rectangle(image, (95, 55), (145, 150), (220, 220, 220), -1)
    ok, encoded = cv2.imencode(".png", image)
    assert ok

    view = build_character_view(encoded.tobytes())
    assert view.png.startswith(b"\x89PNG")
    assert view.width > 0
    assert view.height > 0
    assert view.activity_state == "IDLE"

    rgba = cv2.imdecode(np.frombuffer(view.png, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    assert rgba is not None
    assert rgba.shape[2] == 4
    assert int(rgba[:, :, 3].max()) > 0


def test_live_character_view_reports_activity_from_frame_change() -> None:
    import cv2
    import numpy as np

    from app.client.live_character_view import build_character_view

    first = np.zeros((180, 240, 3), dtype=np.uint8)
    first[:] = (30, 70, 110)
    second = first.copy()
    cv2.rectangle(second, (40, 30), (200, 165), (255, 255, 255), -1)

    ok_a, a = cv2.imencode(".png", first)
    ok_b, b = cv2.imencode(".png", second)
    assert ok_a and ok_b

    view = build_character_view(b.tobytes(), a.tobytes())
    assert view.activity_score > 0
    assert view.activity_state == "ACTIVE"
