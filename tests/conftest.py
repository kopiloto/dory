from collections.abc import AsyncGenerator, Generator
from typing import Any

import mongoengine
import pytest
import pytest_asyncio
from mongoengine_plus.aio.utils import (
    create_awaitable,
)
from testcontainers.mongodb import (
    MongoDbContainer,
)

from dory.adapters.mongo import ConversationDocument, MessageDocument, MongoDBAdapter


@pytest.fixture(scope="session", autouse=True)
def mongo_connection_url() -> Generator[str, None, None]:
    """Start a MongoDB Testcontainer and yield the connection URL for the session."""
    from testcontainers.mongodb import (
        MongoDbContainer,
    )

    with MongoDbContainer() as mongo:
        yield (
            mongo.get_connection_url()
            + "/db?authSource=admin&retryWrites=true&w=majority"
        )


@pytest.fixture(scope="session", autouse=True)
def db_connection(mongo_connection_url: str) -> Any:
    """Autouse mongoengine connection for the whole test session."""

    return mongoengine.connect(host=mongo_connection_url)


@pytest_asyncio.fixture(scope="function")
async def mongo_adapter() -> AsyncGenerator[MongoDBAdapter, None]:
    """Provide a MongoDBAdapter backed by a real MongoDB container for tests."""

    adapter = MongoDBAdapter()

    yield adapter

    await create_awaitable(ConversationDocument.drop_collection)
    await create_awaitable(MessageDocument.drop_collection)
