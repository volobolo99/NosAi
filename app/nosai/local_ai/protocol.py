"""Versioned protocol for primary/local AI cooperation."""
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any, Mapping
from uuid import uuid4

class MessageType(str, Enum):
    TASK = "task"
    PROPOSAL = "proposal"
    REVIEW = "review"
    CONSENSUS = "consensus"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"

@dataclass(frozen=True)
class AIMessage:
    message_id: str
    correlation_id: str
    sender: str
    recipient: str
    type: MessageType
    payload: Mapping[str, Any]
    context_id: str
    protocol_version: str = "1.0"
    created_at: float = field(default_factory=time)

    @classmethod
    def create(cls, *, sender: str, recipient: str, type: MessageType,
               payload: Mapping[str, Any], context_id: str,
               correlation_id: str | None = None) -> "AIMessage":
        return cls(str(uuid4()), correlation_id or str(uuid4()), sender,
                   recipient, type, dict(payload), context_id)

    def validate(self) -> None:
        if not self.message_id or not self.correlation_id:
            raise ValueError("message identifiers are required")
        if not self.sender or not self.recipient or not self.context_id:
            raise ValueError("sender, recipient and context_id are required")
        if self.protocol_version != "1.0":
            raise ValueError(f"unsupported protocol version: {self.protocol_version}")

__all__ = ["AIMessage", "MessageType"]
