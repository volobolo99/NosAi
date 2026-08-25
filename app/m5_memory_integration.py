from app.m5_unified_memory import UnifiedMemory

def attach_unified_memory(memory_v2):
    """Attach the unified read model while preserving AIMemoryV2 compatibility."""
    if not hasattr(memory_v2, "unified"):
        memory_v2.unified = UnifiedMemory(memory_v2)
    return memory_v2.unified
