# Dory

## Messages Library for Conversational AI

A library for managing conversation history in AI-powered applications
for reusability across projects.

## Overview

Dory messages provides simple, reliable conversation and message management with:

- **Automatic Conversation Management**: Reuses conversations within a 2-week window
- **Message Persistence**: Stores user messages and AI responses
- **LangChain/LangGraph Integration**: Returns chat history in the required format
- **MongoDB Support**: MongoDB only (for now)

## Installation

### Using uv (Recommended)

```bash
# Add to an existing project
uv add dory

# Or add to pyproject.toml dependencies
# Then run:
uv sync
```

### Using pip

```bash
pip install dory
```

### Add to pyproject.toml

```toml
[project]
dependencies = [
    "dory>=0.0.1",
    # ... other dependencies
]
```

## Quick Start

```python
import asyncio
from dory import Memory, Messages, ConversationConfig
from dory.adapters import MongoDBAdapter
from dory.types import MessageType, ChatRole


async def main():
    # Initialize with MongoDB
    adapter = MongoDBAdapter(
        connection_string="mongodb://localhost:27017/myapp",
        database="myapp",
    )

    # Create Messages service
    messages = Messages(adapter=adapter)

    # Create Memory facade with dependency injection
    memory = Memory(messages)

    # Get or create a conversation (reuses if within 2 weeks)
    conversation = await memory.get_or_create_conversation(user_id="user_123")

    # Add a user message
    await memory.add_message(
        conversation_id=conversation.id,
        user_id="user_123",
        chat_role=ChatRole.USER,
        content="What's the weather like?",
        message_type=MessageType.USER_MESSAGE
    )

    # Add an AI response
    await memory.add_message(
        conversation_id=conversation.id,
        user_id="user_123",
        chat_role=ChatRole.AI,
        content="It's sunny today!",
        message_type=MessageType.REQUEST_RESPONSE
    )

    # Get chat history for LangChain/LangGraph
    chat_history = await memory.get_chat_history(conversation.id, limit=30)
    # Returns list[dict[str, Any]]; content can be string or structured
    # E.g. [{"user": "What's the weather like?"}, {"ai": "It's sunny today!"}]


if __name__ == "__main__":
    asyncio.run(main())
```

## Core

### Memory

```python
# Initialize Memory with dependency injection
adapter = MongoDBAdapter(connection_string="...")
messages = Messages(adapter=adapter)
memory = Memory(messages)

# Memory methods (all require keyword arguments)
async def get_or_create_conversation(self, *, user_id: str) -> Conversation:
    """Get recent conversation or create new one (2-week reuse window)."""

async def add_message(
    self,
    *,
    conversation_id: str | None = None,
    message_id: str | None = None,
    user_id: str,
    chat_role: ChatRole,
    content: Any,
    message_type: MessageType,
) -> Message:
    """Add a message. If conversation_id is None, a new conversation is created.
    If message_id is None, an ID is auto-generated.
    """

async def get_chat_history(
    self,
    *,
    conversation_id: str,
    limit: int | None = None
) -> list[dict[str, Any]]:
    """Get chat history in LangChain/LangGraph format."""
```

### Message Types

```python
class MessageType(str, Enum):
    USER_MESSAGE = "user_message"              # User input
    REQUEST_RESPONSE = "request_response"        # Final AI response
```

### Optional IDs

Both `conversation_id` and `message_id` can be provided. If omitted:

- conversation_id: a new conversation is created for the given `user_id`
- message_id: an ID is generated using the configured prefix

### Chat Roles

```python
class ChatRole(str, Enum):
    USER = "user"
    HUMAN = "human"  # Legacy support
    AI = "ai"
```

### Models

```python
class Conversation:
    id: str                # Format: "CONV_<uuid>"
    user_id: str
    created_at: datetime
    updated_at: datetime

class Message:
    id: str                # Format: "MSG_<uuid>"
    conversation_id: str
    user_id: str
    chat_role: ChatRole
    content: Any           # String or dict
    message_type: MessageType
    created_at: datetime
```

## MongoDB Configuration

### Adapter Setup

```python
adapter = MongoDBAdapter(
    connection_string="mongodb://localhost:27017",
    database="myapp",
)
```

### Indexes Created

**Conversations:**

- `user_id`
- `updated_at`

**Messages:**

- `conversation_id`
- `created_at`
- `{conversation_id: 1, created_at: 1}` (compound)

## License

MIT
