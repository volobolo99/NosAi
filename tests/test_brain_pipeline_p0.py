"""P0 regression tests for the brain decision boundary.

These tests intentionally exercise public contracts only.  They do not invoke
or emulate client-side action execution.
"""
from __future__ import annotations

import inspect

import pytest


def _load_brain():
    candidates = ("app.ai.brain", "app.brain", "nosai.ai.brain")
    for name in candidates:
        try:
            module = __import__(name, fromlist=["*"])
            return module
        except ImportError:
            continue
    pytest.skip("Brain implementation is not exposed under a known public module")


def test_brain_module_has_no_direct_execution_entrypoint():
    module = _load_brain()
    forbidden = {"execute_action", "send_input", "press_key", "click"}
    exported = set(dir(module))
    assert not forbidden.intersection(exported)


def test_brain_public_callables_do_not_require_runtime_client_side_effects():
    module = _load_brain()
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if callable(obj) and inspect.isfunction(obj):
            source = inspect.getsource(obj)
            assert "send_input(" not in source
            assert "execute_action(" not in source
