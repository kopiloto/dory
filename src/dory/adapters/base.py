from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any, Protocol

from ..models import Conversation, Message
from ..types import ChatRole, MessageType


class StorageAdapter(Protocol):
    """Persistence abstraction for conversations and messages."""

    @abstractmethod
    async def find_recent_conversation(
        self, *, user_id: str, since: datetime
    ) -> Conversation | None: ...

    @abstractmethod
    async def create_conversation(self, *, user_id: str) -> Conversation: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Conversation | None: ...

    @abstractmethod
    async def update_conversation_timestamp(self, conversation_id: str) -> None: ...

    @abstractmethod
    async def add_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType,
    ) -> Message: ...

    @abstractmethod
    async def get_chat_history(
        self, *, conversation_id: str, limit: int
    ) -> list[dict[ChatRole, str]]: ...
