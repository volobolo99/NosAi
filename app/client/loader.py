"""Runtime loader for an externally supplied client adapter."""

from __future__ import annotations

import importlib
import os
from typing import Any

from .adapter import validate_adapter


class ClientAdapterLoadError(RuntimeError):
    """Raised when the configured live-client adapter cannot be loaded safely."""


def load_client_adapter(spec: str | None = None) -> Any:
    """Load ``module:attribute`` from an explicit spec or NOSAI_CLIENT_ADAPTER.

    The attribute may be an already-created adapter or a zero-argument factory.
    No implicit client discovery is performed: a live client must be explicitly
    configured so a wrong process cannot be attached accidentally.
    """

    target = spec or os.getenv("NOSAI_CLIENT_ADAPTER")
    if not target:
        raise ClientAdapterLoadError(
            "NOSAI-CLIENT-0002: no client adapter configured; set NOSAI_CLIENT_ADAPTER="
            "module:attribute"
        )
    if ":" not in target:
        raise ClientAdapterLoadError(
            "NOSAI-CLIENT-0003: invalid adapter spec; expected module:attribute"
        )
    module_name, attribute_name = target.split(":", 1)
    if not module_name or not attribute_name:
        raise ClientAdapterLoadError(
            "NOSAI-CLIENT-0003: invalid adapter spec; expected module:attribute"
        )
    try:
        module = importlib.import_module(module_name)
        value = getattr(module, attribute_name)
        adapter = value() if callable(value) and not hasattr(value, "check_connection") else value
        validate_adapter(adapter)
        return adapter
    except ClientAdapterLoadError:
        raise
    except Exception as exc:  # noqa: BLE001 - convert transport setup failures to diagnostics.
        raise ClientAdapterLoadError(
            f"NOSAI-CLIENT-0004: unable to load adapter {target!r}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
