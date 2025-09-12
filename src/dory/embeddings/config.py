"""Configuration for embeddings service."""

from typing import Any, Literal

from pydantic import BaseModel, Field

__all__ = ["EmbeddingsConfig"]


class EmbeddingsConfig(BaseModel):
    """Configuration for embeddings and memory management."""

    llm_provider: Literal["openai", "ollama", "gemini"] = Field(
        default="openai",
        description="LLM provider for generating embeddings",
    )

    llm_model: str | None = Field(
        default=None,
        description="Specific LLM model to use. If None, uses provider's default",
    )

    vector_store_provider: Literal["qdrant", "chroma", "mongodb", "postgres"] = Field(
        default="qdrant",
        description="Vector store provider for storing embeddings",
    )

    collection_name: str = Field(
        default="dory_memories",
        description="Collection/index name in the vector store",
    )

    embedding_dimension: int = Field(
        default=1536,
        ge=1,
        description="Dimension of embedding vectors (depends on model)",
    )

    search_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Default limit for search results",
    )

    enable_auto_memories: bool = Field(
        default=True,
        description="Automatically create memories from messages",
    )

    memory_threshold_score: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for memory retrieval",
    )

    advanced_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Advanced mem0 configuration options",
    )
