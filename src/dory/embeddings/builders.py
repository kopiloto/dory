"""Builder functions for constructing configured Embeddings instances."""

from __future__ import annotations

from typing import Any, Callable

from .adapters.mem0 import Mem0Adapter
from .config import EmbeddingsConfig
from .service import Embeddings

__all__ = [
    "build_mongo_embeddings",
    "build_local_embeddings",
    "build_with_adapter",
]


def build_with_adapter(
    adapter_builder: Callable[[EmbeddingsConfig], Any],
    config: EmbeddingsConfig,
) -> Embeddings:
    """Build Embeddings service with a specific adapter builder."""
    adapter = adapter_builder(config)
    return Embeddings(adapter=adapter)


def build_mongo_embeddings(
    mongodb_uri: str | None = None,
    openai_api_key: str | None = None,
    collection_name: str = "dory_memories",
    **kwargs,
) -> Embeddings:
    """Build an Embeddings service configured for MongoDB."""
    advanced_config = kwargs.get("advanced_config", {})

    if "vector_store" not in advanced_config:
        advanced_config["vector_store"] = {}

    advanced_config["vector_store"]["provider"] = "mongodb_atlas"
    advanced_config["vector_store"]["config"] = {
        "collection_name": collection_name,
        "index_name": f"{collection_name}_index",
        "embedding_field": "embedding",
        "text_field": "text",
    }

    if mongodb_uri:
        advanced_config["vector_store"]["config"]["connection_string"] = mongodb_uri

    if openai_api_key:
        if "llm" not in advanced_config:
            advanced_config["llm"] = {}
        advanced_config["llm"]["config"] = {"api_key": openai_api_key}

    config = EmbeddingsConfig(
        llm_provider="openai",
        vector_store_provider="mongodb",
        collection_name=collection_name,
        advanced_config=advanced_config,
        **{k: v for k, v in kwargs.items() if k != "advanced_config"},
    )

    adapter = Mem0Adapter(config=config)
    return Embeddings(adapter=adapter)


def build_local_embeddings(
    model_name: str = "all-MiniLM-L6-v2",
    persist_directory: str = "./embeddings",
    **kwargs,
) -> Embeddings:
    """Build an Embeddings service for local/offline use."""

    advanced_config = kwargs.get("advanced_config", {})

    if "vector_store" not in advanced_config:
        advanced_config["vector_store"] = {}

    advanced_config["vector_store"]["config"] = {
        "persist_directory": persist_directory,
    }

    if "llm" not in advanced_config:
        advanced_config["llm"] = {}

    advanced_config["llm"]["config"] = {
        "model": model_name,
        "base_url": "http://localhost:11434",
    }

    config = EmbeddingsConfig(
        llm_provider="ollama",
        llm_model=model_name,
        vector_store_provider="chroma",
        collection_name="local_memories",
        advanced_config=advanced_config,
        **{k: v for k, v in kwargs.items() if k != "advanced_config"},
    )

    adapter = Mem0Adapter(config=config)
    return Embeddings(adapter=adapter)
