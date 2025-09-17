"""Embeddings service for memory and vector search management."""

from .builders import build_embeddings
from .config import EmbeddingsConfig
from .service import Embeddings

__all__ = [
    "Embeddings",
    "EmbeddingsConfig",
    "build_embeddings",
]
