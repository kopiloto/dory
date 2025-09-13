"""Embeddings service for memory and vector search management."""

from .builders import (
    build_local_embeddings,
    build_mongo_embeddings,
    build_with_adapter,
)
from .config import EmbeddingsConfig
from .service import Embeddings

__all__ = [
    "Embeddings",
    "EmbeddingsConfig",
    "build_mongo_embeddings",
    "build_local_embeddings",
    "build_with_adapter",
]
