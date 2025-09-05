import asyncio
from collections.abc import Generator

import mongomock  # type: ignore[import-not-found]
import pytest  # type: ignore[import-not-found]
from mongoengine import disconnect  # type: ignore[import-not-found]

from dory.adapters.mongo import ConversationDocument, MessageDocument, MongoDBAdapter


@pytest.fixture(scope="function")  # type: ignore[misc]
def mongo_adapter() -> Generator[MongoDBAdapter, None, None]:
    """Provide a MongoDBAdapter backed by mongomock for integration tests."""

    disconnect()

    adapter = MongoDBAdapter(
        connection_string="mongodb://localhost",
        database="test_db",
        mongo_client_class=mongomock.MongoClient,  # type: ignore[arg-type]
    )

    yield adapter

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ConversationDocument.drop_collection())  # type: ignore[arg-type]
        loop.run_until_complete(MessageDocument.drop_collection())  # type: ignore[arg-type]
    except Exception:
        pass
    finally:
        disconnect()
