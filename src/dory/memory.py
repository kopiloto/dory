from __future__ import annotations

from typing import Any

from .messages import Messages
from .models import Conversation, Message
from .types import ChatRole, MessageType

__all__ = ["Memory"]


class Memory:
    """Unified facade for memory features."""

    def __init__(self, messages: Messages) -> None:
        """Initialize Memory with a Messages instance."""
        self._messages = messages

    async def get_or_create_conversation(self, *, user_id: str) -> Conversation:
        return await self._messages.get_or_create_conversation(user_id=user_id)

    async def get_conversation(self, *, conversation_id: str) -> Conversation:
        return await self._messages.get_conversation(conversation_id=conversation_id)

    async def add_message(
        self,
        *,
        conversation_id: str | None = None,
        message_id: str | None = None,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType,
    ) -> Message:
        return await self._messages.add_message(
            conversation_id=conversation_id,
            message_id=message_id,
            user_id=user_id,
            chat_role=chat_role,
            content=content,
            message_type=message_type,
        )

    async def get_chat_history(
        self, *, conversation_id: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return await self._messages.get_chat_history(
            conversation_id=conversation_id, limit=limit
        )
