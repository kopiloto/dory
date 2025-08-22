from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Final

from pydantic import BaseModel, Field

from .types import ChatRole, MessageType

__all__: Final = [
    "Conversation",
    "Message",
]


class Conversation(BaseModel):
    """Lightweight conversation DTO used by services and adapters."""

    id: str = Field(..., description="Conversation identifier (e.g. CONV_<uuid>)")
    user_id: str = Field(..., description="User who owns the conversation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Message(BaseModel):
    """Lightweight message DTO."""

    id: str = Field(..., description="Message identifier (e.g. MSG_<uuid>)")
    conversation_id: str = Field(...)
    user_id: str = Field(...)
    chat_role: ChatRole
    content: Any
    message_type: MessageType
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
