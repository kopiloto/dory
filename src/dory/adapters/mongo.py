from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable

from mongoengine import (
    DateTimeField,
    DynamicField,
    EnumField,
    StringField,
    connect,
)
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel, uuid_field
from mongoengine_plus.models.event_handlers import updated_at

from ..models import Conversation, Message
from ..types import ChatRole, MessageType
from .base import StorageAdapter

__all__ = ["MongoDBAdapter"]


@updated_at.apply
class ConversationDocument(BaseModel, AsyncDocument):
    meta = {
        "collection": "conversations",
        "indexes": [
            "user_id",
            "updated_at",
            {"fields": ["user_id", "updated_at"]},
        ],
        "auto_create_index": True,
    }

    id: str = StringField(primary_key=True, default=uuid_field("CONV_"))
    user_id: str = StringField(required=True)
    created_at: datetime = DateTimeField(default=lambda: datetime.now(UTC))
    updated_at: datetime = DateTimeField(default=lambda: datetime.now(UTC))


class MessageDocument(BaseModel, AsyncDocument):
    meta = {
        "collection": "messages",
        "indexes": [
            "conversation_id",
            "created_at",
            {"fields": ["conversation_id", "created_at"]},
        ],
        "auto_create_index": True,
    }

    id: str = StringField(primary_key=True, default=uuid_field("MSG_"))
    conversation_id: str = StringField(required=True)
    user_id: str = StringField(required=True)
    chat_role: ChatRole = EnumField(ChatRole, required=True)
    content: Any = DynamicField(required=True)
    message_type: MessageType = EnumField(MessageType, required=True)
    created_at: datetime = DateTimeField(default=lambda: datetime.now(UTC))


class MongoDBAdapter(StorageAdapter):
    """MongoDB implementation using mongoengine-plus async API."""

    def __init__(
        self,
        *,
        connection_string: str | None = None,
        database: str | None = None,
        alias: str = "default",
        **connect_kwargs: Any,
    ) -> None:
        if connection_string:
            connect(
                host=connection_string,
                db=database,
                alias=alias,
                **connect_kwargs,
            )
        self._alias = alias

    @staticmethod
    def _to_conversation(doc: ConversationDocument) -> Conversation:
        return Conversation.model_validate(doc, from_attributes=True)

    async def find_recent_conversation(
        self, *, user_id: str, since: datetime
    ) -> Conversation | None:
        doc = (
            await ConversationDocument.objects(user_id=user_id, updated_at__gte=since)
            .order_by("-updated_at")
            .limit(1)
            .async_first()
        )
        return self._to_conversation(doc) if doc else None

    async def create_conversation(self, *, user_id: str) -> Conversation:
        doc = ConversationDocument(user_id=user_id)
        await doc.async_save()
        await doc.async_reload()
        return self._to_conversation(doc)

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        doc = await ConversationDocument.objects(id=conversation_id).async_first()
        return self._to_conversation(doc) if doc else None

    async def update_conversation_timestamp(self, conversation_id: str) -> None:
        await ConversationDocument.objects(id=conversation_id).async_update(
            set__updated_at=datetime.now(UTC)
        )

    @staticmethod
    def _to_history_dict(msg: MessageDocument) -> dict[str, str]:
        return {msg.chat_role.value: msg.content}

    async def add_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType,
    ) -> Message:
        msg_doc = MessageDocument(
            conversation_id=conversation_id,
            user_id=user_id,
            chat_role=chat_role,
            content=content,
            message_type=message_type,
        )
        await msg_doc.async_save()
        await self.update_conversation_timestamp(conversation_id)
        return Message.model_validate(msg_doc, from_attributes=True)

    async def get_chat_history(
        self, *, conversation_id: str, limit: int
    ) -> list[dict[str, str]]:
        query: Iterable[MessageDocument] = (
            await MessageDocument.objects(conversation_id=conversation_id)
            .order_by("created_at")
            .limit(limit)
            .async_to_list()
        )
        return [self._to_history_dict(message) for message in query]
