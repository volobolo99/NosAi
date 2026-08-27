"""Client integration contracts and concrete adapters for NosAi."""

from .adapter import ClientAdapter, ClientState
from .nostale_windows import NosTaleClientError, WindowsNosTaleAdapter
from .runtime_adapter import AdapterMode, RuntimeAdapter, RuntimeObservation

__all__ = [
    "AdapterMode",
    "ClientAdapter",
    "ClientState",
    "NosTaleClientError",
    "RuntimeAdapter",
    "RuntimeObservation",
    "WindowsNosTaleAdapter",
]
