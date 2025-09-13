"""Tests for the Mem0Adapter following project conventions."""

from unittest.mock import MagicMock, patch

import pytest

from src.dory.embeddings.adapters.mem0 import Mem0Adapter
from src.dory.embeddings.config import EmbeddingsConfig


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_initialize_memory_client_when_adapter_created(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that Mem0Adapter initializes Memory client correctly."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    # Act
    adapter = Mem0Adapter(config=embeddings_config)

    # Assert
    assert adapter._memory is not None, "Memory client should be initialized"
    assert adapter._config == embeddings_config, "Config should be stored"
    mock_memory_class.assert_called_once()


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_store_memory_and_return_id_when_add_memory_called(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that add_memory stores content and returns memory ID."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.return_value = {
        "id": "test_mem_123",  # Changed from "memory_id" to "id"
        "memory": "Test memory content",
    }
    adapter = Mem0Adapter(config=embeddings_config)
    content = "User likes Python programming"
    user_id = "user_123"
    metadata = {"context": "preferences"}

    # Act
    result = await adapter.add_memory(
        content=content,
        user_id=user_id,
        metadata=metadata,
    )

    # Assert
    assert result == "test_mem_123", f"Expected 'test_mem_123', got '{result}'"
    mock_memory.add.assert_called_once_with(
        messages=content,
        user_id=user_id,
        metadata=metadata,
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_search_and_return_memories_when_search_memories_called(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that search_memories returns formatted search results."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.search.return_value = [
        {"memory": "Found memory 1", "score": 0.95},
        {"memory": "Found memory 2", "score": 0.85},
    ]
    adapter = Mem0Adapter(config=embeddings_config)
    query = "test query"
    user_id = "user_123"

    # Act
    results = await adapter.search_memories(
        query=query,
        user_id=user_id,
        limit=10,
    )

    # Assert
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    assert results[0]["content"] == "Found memory 1", "First result content mismatch"
    assert results[0]["score"] == 0.95, "First result score mismatch"
    mock_memory.search.assert_called_once_with(
        query=query,
        user_id=user_id,
        limit=10,
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_delete_memory_and_return_count_when_delete_memories_called(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that delete_memories removes specified memories and returns count."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.delete.return_value = {"success": True}
    adapter = Mem0Adapter(config=embeddings_config)
    user_id = "user_123"
    memory_ids = ["mem_789"]

    # Act
    result = await adapter.delete_memories(user_id=user_id, memory_ids=memory_ids)

    # Assert
    assert result == 1, f"Expected 1 deleted, got {result}"
    mock_memory.delete.assert_called_once_with(memory_id="mem_789")


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_delete_multiple_memories_when_multiple_ids_provided(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that multiple memories can be deleted in one call."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.delete.return_value = {"success": True}
    adapter = Mem0Adapter(config=embeddings_config)
    user_id = "user_123"
    memory_ids = ["mem_1", "mem_2", "mem_3"]

    # Act
    result = await adapter.delete_memories(user_id=user_id, memory_ids=memory_ids)

    # Assert
    assert result == 3, f"Expected 3 deleted, got {result}"
    assert mock_memory.delete.call_count == 3, "Should call delete 3 times"


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_handle_delete_errors_gracefully_when_memory_not_found(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that delete continues even if some memories don't exist."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    def delete_side_effect(memory_id=None):
        if memory_id == "mem_2":
            raise KeyError("Memory not found")
        return {"success": True}

    mock_memory.delete.side_effect = delete_side_effect
    adapter = Mem0Adapter(config=embeddings_config)

    # Act
    result = await adapter.delete_memories(
        user_id="user_123", memory_ids=["mem_1", "mem_2", "mem_3"]
    )

    # Assert
    assert result == 2, f"Expected 2 successful deletions, got {result}"
    assert mock_memory.delete.call_count == 3, "Should attempt all deletions"


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_store_raw_embedding_when_add_embedding_called(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that add_embedding stores content as raw embedding."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.return_value = {"id": "emb_456"}  # Changed from "memory_id" to "id"
    adapter = Mem0Adapter(config=embeddings_config)
    content = "Text to embed"
    user_id = "user_123"
    metadata = {"source": "test"}

    # Act
    result = await adapter.add_embedding(
        content=content, user_id=user_id, metadata=metadata
    )

    # Assert
    assert result == "emb_456", f"Expected 'emb_456', got '{result}'"
    call_args = mock_memory.add.call_args[1]
    assert call_args["messages"] == content
    assert call_args["user_id"] == user_id
    assert call_args["metadata"]["type"] == "raw_embedding"
    assert call_args["metadata"]["source"] == "test"


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_filter_raw_embeddings_when_search_embeddings_called(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that search_embeddings only returns raw embeddings, not memories."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.search.return_value = [
        {
            "memory": "Similar text 1",
            "score": 0.92,
            "metadata": {"type": "raw_embedding"},
        },
        {
            "memory": "Similar text 2",
            "score": 0.88,
            "metadata": {"type": "raw_embedding"},
        },
        {"memory": "Not an embedding", "score": 0.95, "metadata": {"type": "memory"}},
    ]
    adapter = Mem0Adapter(config=embeddings_config)

    # Act
    results = await adapter.search_embeddings(
        query="test query", user_id="user_123", limit=3
    )

    # Assert - Should only return raw embeddings
    assert len(results) == 2, f"Expected 2 raw embeddings, got {len(results)}"
    assert results[0]["content"] == "Similar text 1"
    assert results[1]["content"] == "Similar text 2"
    # Verify mem0 was called with double limit (to account for filtering)
    mock_memory.search.assert_called_once_with(
        query="test query",
        user_id="user_123",
        limit=6,  # limit * 2
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_filter_by_conversation_when_search_with_conversation_id(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that results are filtered by conversation_id when provided."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.search.return_value = [
        {
            "memory": "Conv specific memory",
            "score": 0.90,
            "metadata": {"conversation_id": "conv_456"},
        },
        {
            "memory": "Other conversation memory",
            "score": 0.85,
            "metadata": {"conversation_id": "other_conv"},
        },
    ]
    adapter = Mem0Adapter(config=embeddings_config)

    # Act
    results = await adapter.search_memories(
        query="test", user_id="user_123", conversation_id="conv_456", limit=5
    )

    # Assert - Should only return memories from specified conversation
    assert len(results) == 1, f"Expected 1 result from conversation, got {len(results)}"
    assert results[0]["content"] == "Conv specific memory"
    mock_memory.search.assert_called_once_with(
        query="test", user_id="user_123", limit=5
    )


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_use_minimal_config_when_only_required_params_provided(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that adapter works with minimal configuration."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    minimal_config = EmbeddingsConfig(
        llm_provider="openai", vector_store_provider="mongodb"
    )

    # Act
    adapter = Mem0Adapter(config=minimal_config)

    # Assert
    assert adapter._memory is not None, "Should initialize with minimal config"
    mock_memory_class.assert_called_once()


@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_propagate_exception_when_mem0_fails(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
) -> None:
    """Verify that mem0 exceptions are propagated correctly."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.side_effect = Exception("API Error")
    adapter = Mem0Adapter(config=embeddings_config)

    # Act & Assert
    with pytest.raises(Exception, match="API Error"):
        await adapter.add_memory(content="This will fail", user_id="user_123")


@pytest.mark.parametrize(
    "conversation_id,message_id,expected_metadata_keys",
    [
        ("conv_123", None, ["conversation_id", "type"]),
        (None, "msg_456", ["message_id", "type"]),
        ("conv_123", "msg_456", ["conversation_id", "message_id", "type"]),
        (None, None, ["type"]),
    ],
)
@patch("src.dory.embeddings.adapters.mem0.Memory")
async def test_should_include_correct_metadata_when_different_ids_provided(
    mock_memory_class: MagicMock,
    embeddings_config: EmbeddingsConfig,
    conversation_id: str | None,
    message_id: str | None,
    expected_metadata_keys: list[str],
) -> None:
    """Verify that metadata includes appropriate IDs when provided."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mock_memory.add.return_value = {"id": "test_id"}  # Changed from "memory_id" to "id"
    adapter = Mem0Adapter(config=embeddings_config)

    # Act
    await adapter.add_embedding(
        content="Test content",
        user_id="user_123",
        conversation_id=conversation_id,
        message_id=message_id,
    )

    # Assert
    call_metadata = mock_memory.add.call_args[1]["metadata"]
    for key in expected_metadata_keys:
        assert key in call_metadata, f"Metadata should contain '{key}'"
    assert call_metadata["type"] == "raw_embedding", "Should mark as raw embedding"
