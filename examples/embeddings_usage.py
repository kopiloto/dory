"""Example usage of the Embeddings service with builder functions."""

import asyncio

from dory.embeddings import (
    EmbeddingsConfig,
    build_local_embeddings,
    build_mongo_embeddings,
    build_with_adapter,
)
from dory.embeddings.adapters import Mem0Adapter


async def example_simple_usage():
    """Simplest way to use embeddings with MongoDB."""
    # Build embeddings service with sensible defaults
    embeddings = build_mongo_embeddings(
        mongodb_uri="mongodb://localhost:27017/mydb",
        openai_api_key="sk-...",
    )

    # Store a memory
    memory_id = await embeddings.remember(
        "The user prefers dark mode interfaces",
        user_id="user123",
    )

    # Recall relevant memories
    memories = await embeddings.recall(
        "What are my UI preferences?",
        user_id="user123",
    )

    print(f"Found {len(memories)} relevant memories")


async def example_local_usage():
    """Use embeddings locally without external APIs."""
    # Build for local/offline use
    embeddings = build_local_embeddings(
        model_name="llama2",
        persist_directory="./local_memories",
    )

    # Store raw embedding for vector search
    embedding_id = await embeddings.store_embedding(
        "Python is a great programming language",
        user_id="dev001",
        metadata={"topic": "programming"},
    )

    # Search by similarity
    results = await embeddings.search_embeddings(
        "What programming languages are good?",
        user_id="dev001",
        limit=5,
    )

    for result in results:
        print(f"Score: {result['score']:.2f} - {result['content'][:50]}...")


async def example_advanced_usage():
    """Full control with manual configuration."""
    # Create custom configuration
    config = EmbeddingsConfig(
        llm_provider="azure",
        llm_model="gpt-4",
        vector_store_provider="pinecone",
        collection_name="production_memories",
        search_limit=20,
        advanced_config={
            "llm": {
                "config": {
                    "api_key": "azure-key",
                    "api_base": "https://myazure.openai.azure.com",
                }
            },
            "vector_store": {
                "config": {
                    "api_key": "pinecone-key",
                    "environment": "production",
                }
            },
        },
    )

    # Build with specific adapter
    embeddings = build_with_adapter(
        Mem0Adapter,  # Pass the adapter class
        config,
    )

    # Use with conversation context
    await embeddings.remember(
        "Budget limit is $10,000",
        user_id="manager001",
        conversation_id="planning-2024",
        metadata={"type": "constraint", "priority": "high"},
    )


async def example_custom_adapter():
    """Use with a custom adapter implementation."""

    class CustomAdapter:
        """Custom memory adapter implementation."""

        def __init__(self, config):
            self.config = config
            # Custom initialization

        async def add_memory(self, **kwargs):
            # Custom memory storage logic
            return "custom-memory-id"

        async def search_memories(self, **kwargs):
            # Custom search logic
            return []

        async def delete_memories(self, **kwargs):
            # Custom delete logic
            return 0

        async def add_embedding(self, **kwargs):
            # Custom embedding storage
            return "custom-embedding-id"

        async def search_embeddings(self, **kwargs):
            # Custom embedding search
            return []

    # Build with custom adapter
    config = EmbeddingsConfig()
    embeddings = build_with_adapter(CustomAdapter, config)

    # Use normally
    memory_id = await embeddings.remember(
        "Custom adapter test",
        user_id="test",
    )
    print(f"Stored with custom adapter: {memory_id}")


async def example_integration_with_messages():
    """Example of using Embeddings with Messages service."""
    from dory.messages import Messages
    from dory.messages.adapters import InMemoryAdapter

    # Create both services
    messages = Messages(adapter=InMemoryAdapter())
    embeddings = build_mongo_embeddings()

    # Add a message
    conversation_id = await messages.start_conversation(
        user_id="user123",
        title="Tech Support",
    )

    message = await messages.add_message(
        conversation_id=conversation_id,
        role="user",
        content="I need help with my printer",
    )

    # Store message content as embedding
    await embeddings.store_embedding(
        content=message.content,
        user_id="user123",
        conversation_id=conversation_id,
        message_id=message.id,
        metadata={"role": message.role.value},
    )

    # Also create a memory from it
    await embeddings.remember(
        f"User requested help with printer issues",
        user_id="user123",
        conversation_id=conversation_id,
    )

    print("Message stored in both services")


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_simple_usage())
