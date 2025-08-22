# Doris

## Messages Library for Conversational AI

A library for managing conversation history in AI-powered applications for reusability across projects.

## Overview

Doris messages provides simple, reliable conversation and message management with:

- **Automatic Conversation Management**: Reuses conversations within a 2-week window
- **Message Persistence**: Stores user messages and AI responses  
- **LangChain/LangGraph Integration**: Returns chat history in the required format
- **MongoDB Support**: MongoDB only (for now)

## Installation

### Using uv (Recommended)

```bash
# Add to an existing project
uv add doris

# Or add to pyproject.toml dependencies
# Then run:
uv sync
```

### Using pip

```bash
pip install doris
```

### Add to pyproject.toml

```toml
[project]
dependencies = [
    "doris>=1.0.0",
    # ... other dependencies
]
```

## Quick Start

```python
from doris import Messages, ConversationConfig
from doris.adapters import MongoDBAdapter
from doris.types import MessageType, ChatRole

# Initialize with MongoDB
adapter = MongoDBAdapter(
    connection_string="mongodb://localhost:27017/myapp",
    database="myapp",
    conversations_collection="conversations",
    messages_collection="messages"
)

messages = Messages(adapter=adapter)

# Get or create a conversation (reuses if within 2 weeks)
conversation = await messages.get_or_create_conversation(user_id="user_123")

# Add a user message
await messages.add_message(
    conversation_id=conversation.id,
    user_id="user_123",
    chat_role=ChatRole.USER,
    content="What's the weather like?",
    message_type=MessageType.USER_MESSAGE
)

# Add an AI response
await messages.add_message(
    conversation_id=conversation.id,
    user_id="user_123", 
    chat_role=ChatRole.AI,
    content="It's sunny today!",
    message_type=MessageType.REQUEST_RESPONSE
)

# Get chat history for LangChain/LangGraph
chat_history = await messages.get_chat_history(conversation.id, limit=30)
# Returns: [{"user": "What's the weather like?"}, {"ai": "It's sunny today!"}]
```

## Core API

### Messages Class

```python
class Messages:
    async def get_or_create_conversation(
        self,
        user_id: str
    ) -> Conversation:
        """Get recent conversation or create new one (2-week reuse window)."""
        
    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        chat_role: ChatRole,
        content: Any,
        message_type: MessageType
    ) -> Message:
        """Add a message to a conversation."""
        
    async def get_chat_history(
        self,
        conversation_id: str,
        limit: int = 30
    ) -> list[dict[str, str]]:
        """Get chat history in LangChain/LangGraph format."""
```

### Message Types

```python
class MessageType(str, Enum):
    USER_MESSAGE = "user_message"              # User input
    TERMINAL_TOOL_QUERY = "terminal_tool_query"  # Tool execution query
    REQUEST_RESPONSE = "request_response"        # Final AI response
```

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
    conversations_collection="conversations",
    messages_collection="messages",
    create_indexes=True  # Auto-create indexes
)
```

### Indexes Created

**Conversations:**
- `user_id`
- `updated_at`

**Messages:**
- `conversation_id`
- `created_at`
- `{conversation_id: 1, created_at: -1}` (compound)

## Migration from kopi-ai-orchestrator-api

### 1. Install Doris

### Add to pyproject.toml

```toml
[project]
dependencies = [
    "doris>=1.0.0",
    # ... other dependencies
]
```

### 2. Update Imports

```python
# Before:
from kopi_ai_orchestrator_api.models import Message, Conversation
from kopi_ai_orchestrator_api.types import ChatRoleType, MessageType

# After:
from doris import Messages
from doris.adapters import MongoDBAdapter
from doris.types import MessageType, ChatRole
```

### 3. Initialize

```python
from doris import Messages
from doris.adapters import MongoDBAdapter

adapter = MongoDBAdapter(
    connection_string=MONGODB_URI,
    database="your_database",
    conversations_collection="conversations",
    messages_collection="messages"
)

messages = Messages(adapter)
```

### 4. Update Usage

```python
# Before:
conversation = await Conversation.find_recent_or_create(user_id=user_id)
await Message.create(
    conversation_id=conversation.id,
    user_id=user_id,
    chat_role=ChatRoleType.user,
    content=message,
    message_type=MessageType.user_message
)
chat_history = await Message.get_chat_history(conversation.id)

# After:
conversation = await messages.get_or_create_conversation(user_id=user_id)
await messages.add_message(
    conversation_id=conversation.id,
    user_id=user_id,
    chat_role=ChatRole.USER,
    content=message,
    message_type=MessageType.USER_MESSAGE
)
chat_history = await messages.get_chat_history(conversation.id)
```

### 5. Field Mapping

The library maintains compatibility with existing MongoDB field names:

- `chat_role` field name is preserved (not changed to `role`)
- ID formats remain the same (`CONV_xxx`, `MSG_xxx`)
- Collection names are configurable
- 2-week conversation reuse window is maintained

## Configuration

```python
@dataclass
class ConversationConfig:
    # Conversation reuse window in days
    reuse_window_days: int = 14
    
    # ID prefixes (matching existing schema)
    conversation_id_prefix: str = "CONV_"
    message_id_prefix: str = "MSG_"
```

## License

MIT