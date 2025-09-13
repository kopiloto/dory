"""Integration tests for embeddings service following project conventions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.dory.embeddings.adapters.mem0 import Mem0Adapter
from src.dory.embeddings.builders import build_mongo_embeddings
from src.dory.embeddings.config import EmbeddingsConfig
from src.dory.embeddings.service import Embeddings


async def test_should_complete_full_memory_flow_when_using_embeddings_service() -> None:
    """Verify end-to-end flow of adding and retrieving memories."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.add_memory.return_value = "mem_123"
    mock_adapter.search_memories.return_value = [
        {"content": "Test memory", "score": 0.95}
    ]
    service = Embeddings(adapter=mock_adapter)

    # Act - Add memory
    memory_id = await service.remember(
        content="Important information",
        user_id="test_user",
    )

    # Act - Search memories
    results = await service.recall(
        query="Important",
        user_id="test_user",
    )

    # Assert
    assert memory_id == "mem_123", f"Expected 'mem_123', got '{memory_id}'"
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    assert results[0]["content"] == "Test memory"
    assert results[0]["score"] == 0.95

    # Verify adapter calls
    mock_adapter.add_memory.assert_called_once()
    mock_adapter.search_memories.assert_called_once()


async def test_should_handle_vector_operations_when_storing_embeddings() -> None:
    """Verify that raw embeddings can be stored and searched."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.add_embedding.return_value = "emb_456"
    mock_adapter.search_embeddings.return_value = [
        {"content": "Similar content", "score": 0.89}
    ]
    service = Embeddings(adapter=mock_adapter)

    # Act - Store embedding
    embedding_id = await service.store_embedding(
        content="Document content",
        user_id="test_user",
        message_id="msg_789",
    )

    # Act - Search embeddings
    results = await service.search_embeddings(
        query="Document",
        user_id="test_user",
    )

    # Assert
    assert embedding_id == "emb_456", f"Expected 'emb_456', got '{embedding_id}'"
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    assert results[0]["content"] == "Similar content"
    assert results[0]["score"] == 0.89

    # Verify adapter calls
    mock_adapter.add_embedding.assert_called_once()
    mock_adapter.search_embeddings.assert_called_once()


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_process_memories_when_using_mem0_adapter(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that Mem0Adapter correctly integrates with mem0 library."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.return_value = {
        "id": "mem_from_mem0"
    }  # Changed from "memory_id" to "id"
    mock_memory.search.return_value = [{"memory": "Found by mem0", "score": 0.91}]

    adapter = Mem0Adapter(config=embeddings_config)
    service = Embeddings(adapter=adapter)

    # Act - Add memory
    memory_id = await service.remember(
        content="Test with mem0",
        user_id="test_user",
    )

    # Act - Search memories
    results = await service.recall(
        query="mem0",
        user_id="test_user",
    )

    # Assert
    assert memory_id == "mem_from_mem0", f"Expected 'mem_from_mem0', got '{memory_id}'"
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    assert results[0]["content"] == "Found by mem0"
    assert results[0]["score"] == 0.91

    # Verify mem0 calls
    mock_memory.add.assert_called_once_with(
        messages="Test with mem0",
        user_id="test_user",
        metadata={},  # Empty dict instead of None
    )
    mock_memory.search.assert_called_once_with(
        query="mem0",
        user_id="test_user",
        limit=10,
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_separate_memories_and_embeddings_when_both_stored(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that memories and raw embeddings are stored and searched separately."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    # Setup different responses for different types
    def add_side_effect(messages, user_id, metadata=None):
        if metadata and metadata.get("type") == "raw_embedding":
            return {"id": "emb_id"}  # Changed from "memory_id" to "id"
        return {"id": "mem_id"}  # Changed from "memory_id" to "id"

    mock_memory.add.side_effect = add_side_effect
    mock_memory.search.return_value = [
        {"memory": "Memory result", "score": 0.95, "metadata": {"type": "memory"}},
        {
            "memory": "Embedding result",
            "score": 0.92,
            "metadata": {"type": "raw_embedding"},
        },
    ]

    adapter = Mem0Adapter(config=embeddings_config)
    service = Embeddings(adapter=adapter)

    # Act - Add both memory and embedding
    memory_id = await service.remember(
        content="This is a memory",
        user_id="test_user",
    )
    embedding_id = await service.store_embedding(
        content="This is an embedding",
        user_id="test_user",
    )

    # Act - Search memories (should filter to only memories)
    memory_results = await service.recall(
        query="test",
        user_id="test_user",
    )

    # Act - Search embeddings (should filter to only embeddings)
    embedding_results = await service.search_embeddings(
        query="test",
        user_id="test_user",
    )

    # Assert - Different IDs returned
    assert memory_id == "mem_id", f"Memory should get 'mem_id', got '{memory_id}'"
    assert embedding_id == "emb_id", (
        f"Embedding should get 'emb_id', got '{embedding_id}'"
    )

    # Assert - Filtered results
    assert len(memory_results) == 1, "Should return only memory results"
    assert memory_results[0]["content"] == "Memory result"

    assert len(embedding_results) == 1, "Should return only embedding results"
    assert embedding_results[0]["content"] == "Embedding result"


async def test_should_handle_conversation_context_when_provided() -> None:
    """Verify that conversation context is properly passed through the service."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.add_memory.return_value = "conv_mem_123"
    mock_adapter.search_memories.return_value = [
        {"content": "Conversation memory", "score": 0.93}
    ]
    service = Embeddings(adapter=mock_adapter)

    conversation_id = "conv_456"
    user_id = "test_user"

    # Act - Add memory with conversation context
    memory_id = await service.remember(
        content="Message in conversation",
        user_id=user_id,
        conversation_id=conversation_id,
    )

    # Act - Search with conversation filter
    results = await service.recall(
        query="conversation",
        user_id=user_id,
        conversation_id=conversation_id,
    )

    # Assert
    assert memory_id == "conv_mem_123"
    assert len(results) == 1
    assert results[0]["content"] == "Conversation memory"

    # Verify conversation_id was passed
    mock_adapter.add_memory.assert_called_once_with(
        content="Message in conversation",
        user_id=user_id,
        conversation_id=conversation_id,
        metadata=None,
    )
    mock_adapter.search_memories.assert_called_once_with(
        query="conversation",
        user_id=user_id,
        conversation_id=conversation_id,
        limit=10,
    )


async def test_should_delete_memories_when_forget_called() -> None:
    """Verify that memories can be deleted through the service."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.delete_memories.return_value = 3
    service = Embeddings(adapter=mock_adapter)

    user_id = "test_user"
    memory_ids = ["mem_1", "mem_2", "mem_3"]

    # Act
    deleted_count = await service.forget(
        user_id=user_id,
        memory_ids=memory_ids,
    )

    # Assert
    assert deleted_count == 3, f"Expected 3 deleted, got {deleted_count}"
    mock_adapter.delete_memories.assert_called_once_with(
        user_id=user_id,
        conversation_id=None,
        memory_ids=memory_ids,
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_create_working_service_when_using_builder(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that builder functions create fully functional services."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.return_value = {
        "id": "built_mem_123"
    }  # Changed from "memory_id" to "id"

    # Act - Create service with builder
    service = build_mongo_embeddings(
        mongodb_uri="mongodb://localhost:27017/test",
        openai_api_key="test-key",
        collection_name="test_collection",
    )

    # Act - Use the service
    memory_id = await service.remember(
        content="Built service test",
        user_id="test_user",
    )

    # Assert
    assert memory_id == "built_mem_123", f"Expected 'built_mem_123', got '{memory_id}'"
    mock_memory.add.assert_called_once()


async def test_should_handle_metadata_correctly_when_provided() -> None:
    """Verify that metadata is properly passed through all operations."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.add_memory.return_value = "meta_mem_123"
    mock_adapter.add_embedding.return_value = "meta_emb_456"
    service = Embeddings(adapter=mock_adapter)

    memory_metadata = {"source": "chat", "importance": "high"}
    embedding_metadata = {"type": "document", "format": "pdf"}

    # Act - Add memory with metadata
    memory_id = await service.remember(
        content="Memory with metadata",
        user_id="test_user",
        metadata=memory_metadata,
    )

    # Act - Add embedding with metadata
    embedding_id = await service.store_embedding(
        content="Embedding with metadata",
        user_id="test_user",
        metadata=embedding_metadata,
    )

    # Assert
    assert memory_id == "meta_mem_123"
    assert embedding_id == "meta_emb_456"

    # Verify metadata was passed correctly
    mock_adapter.add_memory.assert_called_once_with(
        content="Memory with metadata",
        user_id="test_user",
        conversation_id=None,
        metadata=memory_metadata,
    )

    mock_adapter.add_embedding.assert_called_once_with(
        content="Embedding with metadata",
        user_id="test_user",
        conversation_id=None,
        message_id=None,
        metadata=embedding_metadata,
    )


@pytest.mark.parametrize(
    "limit,expected_limit",
    [
        (5, 5),
        (20, 20),
        (None, 10),  # Default
    ],
)
async def test_should_respect_limit_parameter_when_searching(
    limit: int | None,
    expected_limit: int,
) -> None:
    """Verify that search operations respect the limit parameter."""
    # Arrange
    mock_adapter = AsyncMock()
    mock_adapter.search_memories.return_value = []
    mock_adapter.search_embeddings.return_value = []
    service = Embeddings(adapter=mock_adapter)

    # Act - Search with different limits
    if limit is not None:
        await service.recall(query="test", user_id="user", limit=limit)
        await service.search_embeddings(query="test", user_id="user", limit=limit)
    else:
        await service.recall(query="test", user_id="user")
        await service.search_embeddings(query="test", user_id="user")

    # Assert - Verify limit was passed correctly
    mock_adapter.search_memories.assert_called_once_with(
        query="test",
        user_id="user",
        conversation_id=None,
        limit=expected_limit,
    )

    mock_adapter.search_embeddings.assert_called_once_with(
        query="test",
        user_id="user",
        conversation_id=None,
        limit=expected_limit if limit is not None else 10,
    )
