import pytest

from dory.adapters.in_memory import InMemoryAdapter
from dory.messages import Messages
from dory.types import ChatRole, MessageType


@pytest.mark.asyncio
async def test_get_or_create_and_history() -> None:
    service = Messages(adapter=InMemoryAdapter())

    conversation = await service.get_or_create_conversation(user_id="u12345678910")

    await service.add_message(
        conversation_id=conversation.id,
        user_id="u12345678910",
        chat_role=ChatRole.USER,
        content="hello",
        message_type=MessageType.USER_MESSAGE,
    )
    await service.add_message(
        conversation_id=conversation.id,
        user_id="u12345678910",
        chat_role=ChatRole.AI,
        content="hi!",
        message_type=MessageType.REQUEST_RESPONSE,
    )

    history = await service.get_chat_history(conversation.id)
    assert history[-1] == {ChatRole.AI: "hi!"}
    assert len(history) == 2
