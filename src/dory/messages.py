from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from .adapters.base import StorageAdapter
from .config import ConversationConfig
from .models import Conversation, Message
from .types import ChatRole, MessageType

__all__ = ["Messages"]


class Messages:
    """High-level API used by applications."""

    def __init__(
        self, adapter: StorageAdapter, config: ConversationConfig | None = None
    ) -> None:
        self._adapter = adapter
        self._config = config or ConversationConfig()

    async def get_or_create_conversation(self, *, user_id: str) -> Conversation:
        # Determine the earliest timestamp that still falls inside the
        # inactivity window. Any conversation whose `updated_at` is older than
        # this value is considered stale and will not be reused.
        reuse_since = datetime.now(UTC) - timedelta(days=self._config.reuse_window_days)
        conversation = await self._adapter.find_recent_conversation(
            user_id=user_id, since=reuse_since
        )
        if conversation:
            return conversation
        return await self._adapter.create_conversation(user_id=user_id)

    async def get_conversation(self, conversation_id: str) -> Conversation:
        """Fetch a conversation or raise if it does not exist."""

        conversation = await self._adapter.get_conversation(conversation_id)
        if conversation is None:
            from .exceptions import ConversationNotFoundError

            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def add_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType,
    ) -> Message:
        return await self._adapter.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            chat_role=chat_role,
            content=content,
            message_type=message_type,
        )

    async def get_chat_history(
        self, conversation_id: str, *, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return await self._adapter.get_chat_history(
            conversation_id=conversation_id,
            limit=limit or self._config.history_limit,
        )
