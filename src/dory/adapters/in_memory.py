from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from ..models import Conversation, Message
from ..types import ChatRole, MessageType
from .base import StorageAdapter

__all__ = ["InMemoryAdapter"]


class InMemoryAdapter(StorageAdapter):
    """In-memory implementation for tests and demos."""

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, Message] = {}

    async def find_recent_conversation(
        self, *, user_id: str, since: datetime
    ) -> Conversation | None:
        for conv in self._conversations.values():
            if conv.user_id == user_id and conv.updated_at >= since:
                return conv
        return None

    async def create_conversation(self, *, user_id: str) -> Conversation:
        conv_id = f"CONV_{uuid.uuid4().hex}"
        conv = Conversation(id=conv_id, user_id=user_id)
        self._conversations[conv_id] = conv
        return conv

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    async def update_conversation_timestamp(self, conversation_id: str) -> None:
        conv = self._conversations.get(conversation_id)
        if conv:
            conv.updated_at = datetime.now(UTC)
            self._conversations[conversation_id] = conv

    async def add_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType,
    ) -> Message:
        msg_id = f"MSG_{uuid.uuid4().hex}"
        msg = Message(
            id=msg_id,
            conversation_id=conversation_id,
            user_id=user_id,
            chat_role=chat_role,
            content=content,
            message_type=message_type,
        )
        self._messages[msg_id] = msg
        await self.update_conversation_timestamp(conversation_id)
        return msg

    async def get_chat_history(
        self, *, conversation_id: str, limit: int
    ) -> list[dict[ChatRole, str]]:
        # Filter messages by conversation_id and message types for history
        filtered = [
            m for m in self._messages.values() if m.conversation_id == conversation_id
        ]
        # Order by created_at asc
        filtered.sort(key=lambda m: m.created_at)
        # Only keep last `limit`
        sliced = filtered[-limit:]
        return [{m.chat_role: m.content} for m in sliced]
