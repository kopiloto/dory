import asyncio
from typing import Any

import pytest

from dory.adapters.in_memory import InMemoryAdapter
from dory.exceptions import ConversationNotFoundError
from dory.messages import Messages
from dory.types import ChatRole, MessageType


@pytest.mark.asyncio
async def test_get_conversation_not_found() -> None:
    service = Messages(adapter=InMemoryAdapter())

    with pytest.raises(ConversationNotFoundError):
        await service.get_conversation("CONV_nonexistent")


@pytest.mark.asyncio
async def test_chat_history_limit_behavior() -> None:
    service = Messages(adapter=InMemoryAdapter())
    conversation = await service.get_or_create_conversation(user_id="limit-user")

    # Create 5 messages
    contents: list[str] = ["m1", "m2", "m3", "m4", "m5"]
    for idx, text in enumerate(contents):
        await service.add_message(
            conversation_id=conversation.id,
            user_id="limit-user",
            chat_role=ChatRole.USER if idx % 2 == 0 else ChatRole.AI,
            content=text,
            message_type=(
                MessageType.USER_MESSAGE
                if idx % 2 == 0
                else MessageType.REQUEST_RESPONSE
            ),
        )
        await asyncio.sleep(0)

    history = await service.get_chat_history(conversation.id, limit=3)
    assert len(history) == 3
    assert history == [
        {"user": "m3"},
        {"ai": "m4"},
        {"user": "m5"},
    ]


@pytest.mark.asyncio
async def test_non_string_content_in_history() -> None:
    service = Messages(adapter=InMemoryAdapter())
    conversation = await service.get_or_create_conversation(user_id="content-user")

    payload: dict[str, Any] = {"tool": "search", "args": {"query": "hello"}}
    await service.add_message(
        conversation_id=conversation.id,
        user_id="content-user",
        chat_role=ChatRole.USER,
        content=payload,
        message_type=MessageType.USER_MESSAGE,
    )

    history = await service.get_chat_history(conversation.id, limit=10)
    assert history[-1] == {"user": payload}
