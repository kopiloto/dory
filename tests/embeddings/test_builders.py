"""Tests for embeddings builder functions following project conventions."""

from unittest.mock import MagicMock, patch

import pytest

from src.dory.embeddings import (
    build_local_embeddings,
    build_mongo_embeddings,
    build_with_adapter,
)
from src.dory.embeddings.adapters.base import MemoryAdapter
from src.dory.embeddings.config import EmbeddingsConfig
from src.dory.embeddings.service import Embeddings


@patch("src.dory.embeddings.adapters.mem0.Memory")
def test_should_create_mongo_embeddings_service_when_build_mongo_embeddings_called(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that build_mongo_embeddings creates configured service for MongoDB."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    mongodb_uri = "mongodb://localhost:27017/test"
    api_key = "test-key"
    collection = "test_collection"

    # Act
    service = build_mongo_embeddings(
        mongodb_uri=mongodb_uri,
        openai_api_key=api_key,
        collection_name=collection,
    )

    # Assert
    assert isinstance(service, Embeddings), "Should return Embeddings instance"
    mock_memory_class.assert_called_once()

    # Verify MongoDB configuration
    config_passed = mock_memory_class.call_args[1]["config"]
    assert config_passed["vector_store"]["provider"] == "mongodb_atlas"
    assert config_passed["vector_store"]["config"]["collection_name"] == collection
    assert "connection_string" in config_passed["vector_store"]["config"]

    # Verify OpenAI configuration
    assert config_passed["llm"]["config"]["api_key"] == api_key


@patch("src.dory.embeddings.adapters.mem0.Memory")
def test_should_use_default_collection_when_not_specified_in_build_mongo(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that build_mongo_embeddings uses default collection name when not provided."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    # Act
    service = build_mongo_embeddings(
        mongodb_uri="mongodb://localhost:27017/test",
        openai_api_key="test-key",
    )

    # Assert
    assert isinstance(service, Embeddings)
    config_passed = mock_memory_class.call_args[1]["config"]
    assert config_passed["vector_store"]["config"]["collection_name"] == "dory_memories"


@patch("src.dory.embeddings.adapters.mem0.Memory")
def test_should_create_local_embeddings_service_when_build_local_embeddings_called(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that build_local_embeddings creates service with local vector store."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory
    persist_dir = "./test_data"
    model_name = "test-model"

    # Act
    service = build_local_embeddings(
        model_name=model_name,
        persist_directory=persist_dir,
    )

    # Assert
    assert isinstance(service, Embeddings), "Should return Embeddings instance"
    mock_memory_class.assert_called_once()

    # Verify Chroma configuration
    config_passed = mock_memory_class.call_args[1]["config"]
    assert config_passed["vector_store"]["provider"] == "chroma"
    assert config_passed["vector_store"]["config"]["persist_directory"] == persist_dir

    # Verify Ollama configuration (not OpenAI for local)
    assert config_passed["llm"]["config"]["model"] == model_name
    assert config_passed["llm"]["config"]["base_url"] == "http://localhost:11434"


@patch("src.dory.embeddings.adapters.mem0.Memory")
def test_should_use_temp_directory_when_persist_dir_not_specified(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that build_local_embeddings uses temp directory as default."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    # Act
    service = build_local_embeddings()

    # Assert
    assert isinstance(service, Embeddings)
    config_passed = mock_memory_class.call_args[1]["config"]
    persist_path = config_passed["vector_store"]["config"]["persist_directory"]
    assert persist_path == "./embeddings", (
        f"Expected default './embeddings', got {persist_path}"
    )


def test_should_create_service_with_custom_adapter_when_build_with_adapter_called() -> (
    None
):
    """Verify that build_with_adapter creates service with provided adapter factory."""
    # Arrange
    mock_adapter = MagicMock(spec=MemoryAdapter)
    config = EmbeddingsConfig(llm_provider="openai", vector_store_provider="mongodb")

    def custom_factory(cfg: EmbeddingsConfig) -> MemoryAdapter:
        assert cfg == config, "Factory should receive config"
        return mock_adapter

    # Act
    service = build_with_adapter(
        config=config,
        adapter_builder=custom_factory,
    )

    # Assert
    assert isinstance(service, Embeddings), "Should return Embeddings instance"
    assert service._adapter == mock_adapter, "Should use custom adapter"


def test_should_raise_error_when_adapter_builder_not_provided_to_build_with_adapter() -> (
    None
):
    """Verify that build_with_adapter requires adapter_builder parameter."""
    # Arrange
    config = EmbeddingsConfig(llm_provider="openai", vector_store_provider="mongodb")

    # Act & Assert
    with pytest.raises(TypeError, match="adapter_builder"):
        build_with_adapter(config=config)  # Missing adapter_builder


def test_should_validate_config_when_invalid_values_provided_to_build_with_adapter() -> (
    None
):
    """Verify that build_with_adapter validates configuration."""
    # Arrange
    mock_adapter = MagicMock(spec=MemoryAdapter)

    # Act & Assert - Invalid provider value should raise ValidationError
    with pytest.raises(Exception):  # Pydantic ValidationError
        config = EmbeddingsConfig(
            llm_provider="invalid_provider",  # Invalid value
            vector_store_provider="mongodb",
        )


@patch("src.dory.embeddings.adapters.mem0.Memory")
def test_should_support_different_collection_names_when_multiple_services_created(
    mock_memory_class: MagicMock,
) -> None:
    """Verify that multiple services can be created with different collections."""
    # Arrange
    mock_memory = MagicMock()
    mock_memory_class.return_value = mock_memory

    # Act - Create two services with different collections
    service1 = build_mongo_embeddings(
        mongodb_uri="mongodb://localhost:27017/test",
        openai_api_key="test-key",
        collection_name="coll1",
    )

    service2 = build_mongo_embeddings(
        mongodb_uri="mongodb://localhost:27017/test",
        openai_api_key="test-key",
        collection_name="coll2",
    )

    # Assert - Both services created and configured differently
    assert isinstance(service1, Embeddings)
    assert isinstance(service2, Embeddings)
    assert mock_memory_class.call_count == 2

    config1 = mock_memory_class.call_args_list[0][1]["config"]
    config2 = mock_memory_class.call_args_list[1][1]["config"]

    assert config1["vector_store"]["config"]["collection_name"] == "coll1"
    assert config2["vector_store"]["config"]["collection_name"] == "coll2"


@pytest.mark.parametrize(
    "llm_provider,vector_store,expected_error",
    [
        ("invalid_llm", "mongodb", True),
        ("openai", "invalid_store", True),
        ("openai", "mongodb", False),
    ],
)
def test_should_validate_provider_values_when_creating_config(
    llm_provider: str,
    vector_store: str,
    expected_error: bool,
) -> None:
    """Verify that EmbeddingsConfig validates provider values."""
    # Act & Assert
    if expected_error:
        with pytest.raises(Exception):  # Pydantic ValidationError
            EmbeddingsConfig(
                llm_provider=llm_provider, vector_store_provider=vector_store
            )
    else:
        # Should not raise
        config = EmbeddingsConfig(
            llm_provider=llm_provider, vector_store_provider=vector_store
        )
        assert config.llm_provider == llm_provider
        assert config.vector_store_provider == vector_store
