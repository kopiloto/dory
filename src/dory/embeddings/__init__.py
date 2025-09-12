"""Embeddings service for memory and vector search management."""

from .config import EmbeddingsConfig
from .service import Embeddings

__all__ = ["Embeddings", "EmbeddingsConfig"]
