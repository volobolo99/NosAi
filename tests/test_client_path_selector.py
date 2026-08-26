from __future__ import annotations

import pytest

from app.assets.path_selector import ClientPathSelectionError, validate_client_path


def test_validate_client_path_accepts_existing_directory(tmp_path) -> None:
    assert validate_client_path(tmp_path) == tmp_path.resolve()


def test_validate_client_path_rejects_missing_directory(tmp_path) -> None:
    with pytest.raises(ClientPathSelectionError):
        validate_client_path(tmp_path / "Nostale")
