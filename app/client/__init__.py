"""Client integration contracts and concrete adapters for NosAi."""

from .adapter import ClientAdapter, ClientState
from .nostale_windows import NosTaleClientError, WindowsNosTaleAdapter

__all__ = [
    "ClientAdapter",
    "ClientState",
    "NosTaleClientError",
    "WindowsNosTaleAdapter",
]
