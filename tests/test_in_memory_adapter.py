import pytest

from dory.adapters.in_memory import InMemoryAdapter
from dory.types import ChatRole, MessageType


@pytest.mark.asyncio
async def test_conversation_reuse() -> None:
    adapter = InMemoryAdapter()
    conv1 = await adapter.create_conversation(user_id="user_1")

    recent = await adapter.find_recent_conversation(
        user_id="user_1", since=conv1.updated_at
    )
    assert recent == conv1


@pytest.mark.asyncio
async def test_add_and_fetch_messages() -> None:
    adapter = InMemoryAdapter()
    conv = await adapter.create_conversation(user_id="u")

    await adapter.add_message(
        conversation_id=conv.id,
        user_id="u",
        chat_role=ChatRole.USER,
        content="hi",
        message_type=MessageType.USER_MESSAGE,
    )
    await adapter.add_message(
        conversation_id=conv.id,
        user_id="u",
        chat_role=ChatRole.AI,
        content="hello",
        message_type=MessageType.REQUEST_RESPONSE,
    )

    history = await adapter.get_chat_history(conversation_id=conv.id, limit=5)
    assert history == [{ChatRole.USER: "hi"}, {ChatRole.AI: "hello"}]
