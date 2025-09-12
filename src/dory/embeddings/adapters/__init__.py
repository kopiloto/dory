"""Adapters for embeddings storage backends."""

from .base import MemoryAdapter
from .types import (
    EmbeddingMetadata,
    EmbeddingResult,
    MemoryMetadata,
    MemoryResult,
)

__all__ = [
    "MemoryAdapter",
    "MemoryResult",
    "EmbeddingResult",
    "MemoryMetadata",
    "EmbeddingMetadata",
]
