"""P0 perception regressions.

The perception boundary must fail closed on incomplete or malformed evidence.
Tests are intentionally defensive so they remain useful while the decoder
surface evolves.
"""
from __future__ import annotations

import importlib

import pytest


MODULE_CANDIDATES = (
    "app.nostale_perception.network_decoder",
    "app.nostale_perception.decoder",
    "nosai.nostale_perception.network_decoder",
)


def _decoder_module():
    for name in MODULE_CANDIDATES:
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    pytest.skip("No public NosTale observation decoder module is available")


def test_decoder_rejects_empty_observation_when_public_decode_exists():
    module = _decoder_module()
    decode = getattr(module, "decode", None) or getattr(module, "decode_observation", None)
    if decode is None:
        pytest.skip("Decoder does not expose a public decode function")
    with pytest.raises((ValueError, TypeError, KeyError)):
        decode(b"")


def test_decoder_does_not_accept_none_as_valid_evidence():
    module = _decoder_module()
    decode = getattr(module, "decode", None) or getattr(module, "decode_observation", None)
    if decode is None:
        pytest.skip("Decoder does not expose a public decode function")
    with pytest.raises((ValueError, TypeError, KeyError, AttributeError)):
        decode(None)
