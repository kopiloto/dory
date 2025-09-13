"""Mem0 adapter implementation for memory and embeddings storage."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from mem0 import Memory

from ..config import EmbeddingsConfig
from .base import MemoryAdapter

__all__ = ["Mem0Adapter"]


class Mem0Adapter(MemoryAdapter):
    """Adapter that wraps mem0 for both memories and embeddings."""

    def __init__(self, config: EmbeddingsConfig) -> None:
        """Initialize the Mem0 adapter with configuration."""
        self._config = config
        self._memory = self._init_memory()
        self._embeddings_cache: dict[str, str] = {}

    def _init_memory(self) -> Memory:
        """Initialize mem0 Memory with configuration."""
        mem0_config: dict[str, Any] = {
            "llm": {
                "provider": self._config.llm_provider,
            },
            "vector_store": {
                "provider": self._config.vector_store_provider,
                "config": {
                    "collection_name": self._config.collection_name,
                },
            },
        }

        if self._config.llm_model:
            if "llm" in mem0_config and isinstance(mem0_config["llm"], dict):
                mem0_config["llm"]["config"] = {"model": self._config.llm_model}

        if self._config.advanced_config:
            for key, value in self._config.advanced_config.items():
                if key in mem0_config:
                    existing = mem0_config[key]
                    if isinstance(existing, dict) and isinstance(value, dict):
                        existing.update(value)
                    else:
                        mem0_config[key] = value
                else:
                    mem0_config[key] = value

        return Memory(config=mem0_config)

    async def add_memory(
        self,
        *,
        content: str,
        user_id: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a memory to the store and return its ID."""
        mem0_metadata = metadata or {}
        if conversation_id:
            mem0_metadata["conversation_id"] = conversation_id

        result = self._memory.add(
            messages=content,
            user_id=user_id,
            metadata=mem0_metadata,
        )

        if isinstance(result, dict) and "id" in result:
            return result["id"]
        elif isinstance(result, list) and result:
            return result[0].get("id", "")
        else:
            return self._generate_id(content, user_id)

    async def search_memories(
        self,
        *,
        query: str,
        user_id: str,
        conversation_id: str | None = None,
        limit: int = 10,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant memories matching the query."""
        results = self._memory.search(
            query=query,
            user_id=user_id,
            limit=limit,
        )

        results = [
            r for r in results if r.get("metadata", {}).get("type") != "raw_embedding"
        ]

        if conversation_id:
            results = [
                r
                for r in results
                if r.get("metadata", {}).get("conversation_id") == conversation_id
            ]

        if since:
            results = [
                r
                for r in results
                if self._parse_timestamp(r.get("created_at")) >= since
            ]

        return [
            {
                "id": r.get("id", ""),
                "content": r.get("memory", ""),
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ]

    async def delete_memories(
        self,
        *,
        user_id: str,
        conversation_id: str | None = None,
        memory_ids: list[str] | None = None,
    ) -> int:
        """Delete memories based on filters and return count."""
        deleted_count = 0

        if memory_ids:
            for memory_id in memory_ids:
                try:
                    self._memory.delete(memory_id=memory_id)
                    deleted_count += 1
                except (KeyError, ValueError):
                    # Memory doesn't exist, skip silently
                    pass
        else:
            all_memories = self._memory.get_all(user_id=user_id)

            for memory in all_memories:
                if conversation_id:
                    if (
                        memory.get("metadata", {}).get("conversation_id")
                        != conversation_id
                    ):
                        continue

                try:
                    self._memory.delete(memory_id=memory["id"])
                    deleted_count += 1
                except (KeyError, ValueError):
                    pass

        return deleted_count

    async def add_embedding(
        self,
        *,
        content: str,
        user_id: str,
        conversation_id: str | None = None,
        message_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store raw content as embedding for vector search."""

        embedding_metadata = metadata or {}
        embedding_metadata["type"] = "raw_embedding"
        embedding_metadata["user_id"] = user_id

        if conversation_id:
            embedding_metadata["conversation_id"] = conversation_id
        if message_id:
            embedding_metadata["message_id"] = message_id

        result = self._memory.add(
            messages=content,
            user_id=user_id,
            metadata=embedding_metadata,
        )

        if isinstance(result, dict) and "id" in result:
            embedding_id = result["id"]
        elif isinstance(result, list) and result:
            embedding_id = result[0].get("id", "")
        else:
            embedding_id = self._generate_id(content, user_id)

        self._embeddings_cache[embedding_id] = content

        return embedding_id

    async def search_embeddings(
        self,
        *,
        query: str,
        user_id: str,
        conversation_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for similar embeddings using vector similarity."""
        results = self._memory.search(
            query=query,
            user_id=user_id,
            limit=limit * 2,
        )

        embeddings = []
        for r in results:
            metadata = r.get("metadata", {})

            if metadata.get("type") != "raw_embedding":
                continue

            if conversation_id and metadata.get("conversation_id") != conversation_id:
                continue

            embeddings.append(
                {
                    "id": r.get("id", ""),
                    "content": r.get("memory", ""),
                    "score": r.get("score", 0.0),
                    "metadata": metadata,
                }
            )

            if len(embeddings) >= limit:
                break

        return embeddings

    def _generate_id(self, content: str, user_id: str) -> str:
        """Generate a deterministic ID for content."""
        hash_input = f"{user_id}:{content}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return datetime.min
        else:
            return datetime.min
