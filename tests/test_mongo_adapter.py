import asyncio

import mongomock
import pytest

from dory.adapters.mongo import MongoDBAdapter
from dory.messages import Messages
from dory.types import ChatRole, MessageType


@pytest.fixture(scope="function")
def mongo_adapter() -> MongoDBAdapter:
    from mongoengine import disconnect

    from dory.adapters.mongo import ConversationDocument, MessageDocument

    disconnect()

    adapter = MongoDBAdapter(
        connection_string="mongodb://localhost",
        database="test_db",
        mongo_client_class=mongomock.MongoClient,
    )

    yield adapter

    try:
        import asyncio

        loop = asyncio.get_event_loop()
        loop.run_until_complete(ConversationDocument.drop_collection())
        loop.run_until_complete(MessageDocument.drop_collection())
    except Exception:
        pass
    finally:
        disconnect()


@pytest.mark.asyncio
async def test_conversation_lifecycle(mongo_adapter: MongoDBAdapter) -> None:
    service = Messages(adapter=mongo_adapter)

    conv = await service.get_or_create_conversation(user_id="mongo-user")
    assert conv.user_id == "mongo-user"

    first_updated_at = conv.updated_at
    await asyncio.sleep(0)

    await service.add_message(
        conversation_id=conv.id,
        user_id="mongo-user",
        chat_role=ChatRole.USER,
        content="hello",
        message_type=MessageType.USER_MESSAGE,
    )

    fresh_conv = await mongo_adapter.get_conversation(conv.id)
    assert fresh_conv is not None
    assert fresh_conv.updated_at >= first_updated_at

    # Reuse conversation within 14-day window
    reused = await service.get_or_create_conversation(user_id="mongo-user")
    assert reused.id == conv.id


@pytest.mark.asyncio
async def test_chat_history_order(mongo_adapter: MongoDBAdapter) -> None:
    service = Messages(adapter=mongo_adapter)
    conv = await service.get_or_create_conversation(user_id="hist-user")

    await service.add_message(
        conversation_id=conv.id,
        user_id="hist-user",
        chat_role=ChatRole.USER,
        content="msg1",
        message_type=MessageType.USER_MESSAGE,
    )

    # Small delay to ensure different timestamps
    await asyncio.sleep(0.001)

    await service.add_message(
        conversation_id=conv.id,
        user_id="hist-user",
        chat_role=ChatRole.AI,
        content="msg2",
        message_type=MessageType.REQUEST_RESPONSE,
    )

    history = await service.get_chat_history(conv.id, limit=10)
    assert history == [{"user": "msg1"}, {"ai": "msg2"}]
