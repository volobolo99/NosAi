"""Provider-neutral local intelligence adapters for NosAi."""

from .llama_cpp import LlamaCppConfig, LlamaCppDecisionProvider

__all__ = ["LlamaCppConfig", "LlamaCppDecisionProvider"]
