# Forget Me Not (FMN)

## Phase 1: Message History (Short-term memory) 

A database-agnostic Python library for managing conversational message history in AI-powered applications. This library provides a clean abstraction over conversation and message persistence, supporting multiple database backends while maintaining a consistent API.

## Overview

The Message History Library is designed to handle the complex requirements of conversational AI applications, including:

- **Conversation Management**: Automatic conversation lifecycle handling with configurable retention policies
- **Message Persistence**: Flexible message storage supporting various content types and metadata
- **Context Building**: Intelligent message filtering and formatting for LLM context windows
- **Database Agnostic**: Support for MongoDB, PostgreSQL, DynamoDB, and more through adapters

## Key Features

### Automatic Conversation Management
- Smart conversation reuse within configurable time windows
- Automatic conversation creation when needed
- Conversation expiration and cleanup

### Flexible Message Types
- Support for different message types (user messages, AI responses, tool queries, etc.)
- Dynamic content storage (text, JSON, binary data)
- Metadata attachment for analytics and debugging

### Context Window Management
- Configurable message filtering for LLM context
- Message count and token-based limiting
- Format conversion for popular LLM frameworks (LangChain, LlamaIndex, etc.)

### Pluggable Storage Backends
- MongoDB, PostgreSQL, DynamoDB adapters included
- Simple interface for custom adapter implementation
- Connection pooling and retry logic

### Performance Optimized
- Indexed queries for fast retrieval
- Batch operations support
- Caching layer for frequently accessed conversations

## Architecture

```mermaid
graph TD
    A[Application Layer] --> B[Message History Library API]
    B --> C[Core Abstractions]
    C --> D[Conversation Manager]
    C --> E[Message Store]
    C --> F[Context Builder]
    
    D --> G[Storage Adapter Interface]
    E --> G
    
    G --> H[MongoDB Adapter]
    G --> I[PostgreSQL Adapter]
    G --> J[DynamoDB Adapter]
    G --> K[Custom Adapter]
    
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#bbf,stroke:#333,stroke-width:2px
```


## Quick Start

```python
from message_history import MessageHistory, ConversationConfig
from message_history.adapters import MongoDBAdapter
from message_history.types import MessageType, ChatRole

# Initialize with MongoDB
adapter = MongoDBAdapter(connection_string="mongodb://localhost:27017/myapp")
history = MessageHistory(
    adapter=adapter,
    config=ConversationConfig(
        reuse_window_days=14,  # Reuse conversations
        max_messages_per_conversation=1000,
        auto_cleanup=True
    )
)

# Get or create a conversation for a user
conversation = await history.get_or_create_conversation(user_id="user_123")

# Add a user message
await history.add_message(
    conversation_id=conversation.id,
    user_id="user_123",
    role=ChatRole.USER,
    content="What's the weather like?",
    message_type=MessageType.USER_MESSAGE
)

# Add an AI response
await history.add_message(
    conversation_id=conversation.id,
    user_id="user_123",
    role=ChatRole.AI,
    content={"text": "I'll check the weather for you.", "action": "weather_check"},
    message_type=MessageType.AI_RESPONSE
)

# Get conversation history for LLM context
context = await history.get_context(
    conversation_id=conversation.id,
    include_types=[MessageType.USER_MESSAGE, MessageType.TOOL_QUERY],
    limit=50,
    format="langchain"  # Returns LangChain message objects
)
```

## Core Concepts

### Conversations

A conversation represents a continuous interaction session between a user and the AI system. Key properties:

- **Automatic Lifecycle**: Conversations are automatically created and reused based on configured rules
- **Metadata Support**: Attach custom metadata for analytics and filtering
- **Time-based Reuse**: Recent conversations (within configured window) are automatically reused
- **Soft Expiration**: Old conversations are marked inactive but retained for history

### Messages

Messages are the atomic units of conversation. Each message has:

- **Role**: Who sent the message (user, AI, system)
- **Type**: Classification for filtering and processing
- **Content**: Flexible content storage (string, dict, or custom types)
- **Metadata**: Optional metadata for tracking and analytics
- **Timestamps**: Automatic created_at tracking

### Message Types

The library provides built-in message types with extensibility:

```python
class MessageType(str, Enum):
    USER_MESSAGE = "user_message"          # Direct user input
    AI_RESPONSE = "ai_response"            # Final AI response
    TOOL_QUERY = "tool_query"              # AI's query before tool execution
    TOOL_RESULT = "tool_result"            # Result from tool execution
    SYSTEM_MESSAGE = "system_message"      # System-level messages
    ERROR_MESSAGE = "error_message"        # Error tracking
    CUSTOM = "custom"                      # For extensibility
```

### Context Building

Context building is the process of selecting and formatting messages for LLM consumption:

- **Type Filtering**: Include only relevant message types
- **Content Extraction**: Extract text content from complex message structures
- **Format Conversion**: Convert to framework-specific formats (LangChain, LlamaIndex, raw dicts)
- **Token Limiting**: Respect LLM context window limits
- **Message Ordering**: Maintain chronological order

## API Reference

### MessageHistory Class

The main entry point for the library:

```python
class MessageHistory:
    def __init__(
        self,
        adapter: StorageAdapter,
        config: ConversationConfig = ConversationConfig()
    ):
        """Initialize the message history manager."""
        
    async def get_or_create_conversation(
        self,
        user_id: str,
        metadata: dict[str, Any] | None = None
    ) -> Conversation:
        """Get recent conversation or create new one."""
        
    async def get_conversation(
        self,
        conversation_id: str
    ) -> Conversation | None:
        """Retrieve a specific conversation by ID."""
        
    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: ChatRole,
        content: Any,
        message_type: MessageType,
        metadata: dict[str, Any] | None = None
    ) -> Message:
        """Add a message to a conversation."""
        
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
        message_types: list[MessageType] | None = None
    ) -> list[Message]:
        """Retrieve messages with filtering."""
        
    async def get_context(
        self,
        conversation_id: str,
        include_types: list[MessageType] | None = None,
        exclude_types: list[MessageType] | None = None,
        limit: int = 50,
        format: ContextFormat = "dict"
    ) -> list[Any]:
        """Build context for LLM consumption."""
        
    async def delete_conversation(
        self,
        conversation_id: str,
        hard_delete: bool = False
    ) -> None:
        """Delete or deactivate a conversation."""
```

### Configuration

```python
@dataclass
class ConversationConfig:
    # Conversation reuse window in days
    reuse_window_days: int = 14
    
    # Maximum messages per conversation before rotation
    max_messages_per_conversation: int = 10000
    
    # Automatically cleanup old conversations
    auto_cleanup: bool = True
    
    # Cleanup threshold in days
    cleanup_after_days: int = 90
    
    # Default context limit
    default_context_limit: int = 50
    
    # Enable message content compression
    enable_compression: bool = False
    
    # Custom ID prefixes
    conversation_id_prefix: str = "CONV_"
    message_id_prefix: str = "MSG_"
```

### Models

```python
class Conversation(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = {}
    is_active: bool = True
    
class Message(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    role: ChatRole
    content: Any  # Can be str, dict, or custom type
    message_type: MessageType
    created_at: datetime
    metadata: dict[str, Any] = {}
```

## Database Adapters

### MongoDB Adapter

```python
from message_history.adapters import MongoDBAdapter

adapter = MongoDBAdapter(
    connection_string="mongodb://localhost:27017",
    database="myapp",
    conversations_collection="conversations",
    messages_collection="messages",
    create_indexes=True  # Auto-create optimal indexes
)
```

### PostgreSQL Adapter

```python
from message_history.adapters import PostgreSQLAdapter

adapter = PostgreSQLAdapter(
    connection_string="postgresql://user:pass@localhost/myapp",
    schema="message_history",
    create_tables=True,  # Auto-create tables if not exist
    use_json_field=True  # Use JSONB for content storage
)
```

### DynamoDB Adapter

```python
from message_history.adapters import DynamoDBAdapter

adapter = DynamoDBAdapter(
    table_name="message-history",
    region="us-east-1",
    create_table=True,
    read_capacity_units=5,
    write_capacity_units=5
)
```

### Custom Adapter Implementation

```python
from message_history.adapters import StorageAdapter
from message_history.types import Conversation, Message

class CustomAdapter(StorageAdapter):
    async def create_conversation(self, user_id: str, metadata: dict) -> Conversation:
        # Implement conversation creation
        pass
        
    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        # Implement conversation retrieval
        pass
        
    async def update_conversation(self, conversation_id: str, updated_at: datetime) -> None:
        # Implement conversation update
        pass
        
    async def find_recent_conversation(
        self, 
        user_id: str, 
        since: datetime
    ) -> Conversation | None:
        # Implement recent conversation search
        pass
        
    async def create_message(self, message: Message) -> Message:
        # Implement message creation
        pass
        
    async def get_messages(
        self,
        conversation_id: str,
        limit: int,
        offset: int,
        message_types: list[MessageType] | None
    ) -> list[Message]:
        # Implement message retrieval with filtering
        pass
        
    async def delete_conversation(self, conversation_id: str) -> None:
        # Implement conversation deletion
        pass
```

## Advanced Usage

### Custom Message Types

```python
from message_history.types import MessageType

# Extend the enum
class CustomMessageType(MessageType):
    FEEDBACK = "feedback"
    ANNOTATION = "annotation"
    
# Use in your application
await history.add_message(
    conversation_id=conv.id,
    user_id="user_123",
    role=ChatRole.USER,
    content={"rating": 5, "comment": "Great response!"},
    message_type=CustomMessageType.FEEDBACK
)
```

### Context Formatters

```python
from message_history.formatters import ContextFormatter

class CustomFormatter(ContextFormatter):
    def format(self, messages: list[Message]) -> list[Any]:
        # Custom formatting logic
        return [
            {
                "speaker": msg.role.value,
                "text": msg.content if isinstance(msg.content, str) else str(msg.content),
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]

# Register and use
history.register_formatter("custom", CustomFormatter())
context = await history.get_context(
    conversation_id=conv.id,
    format="custom"
)
```

### Batch Operations

```python
# Batch message insertion
messages = [
    {
        "role": ChatRole.USER,
        "content": "Hello",
        "message_type": MessageType.USER_MESSAGE
    },
    {
        "role": ChatRole.AI,
        "content": "Hi there!",
        "message_type": MessageType.AI_RESPONSE
    }
]

await history.add_messages_batch(
    conversation_id=conv.id,
    user_id="user_123",
    messages=messages
)
```

### Message Compression

```python
# Enable compression for large content
config = ConversationConfig(enable_compression=True)
history = MessageHistory(adapter=adapter, config=config)

# Large content will be automatically compressed
await history.add_message(
    conversation_id=conv.id,
    user_id="user_123",
    role=ChatRole.AI,
    content=large_json_response,  # Automatically compressed if > 1KB
    message_type=MessageType.AI_RESPONSE
)
```

### Conversation Metadata and Search

```python
# Create conversation with metadata
conversation = await history.get_or_create_conversation(
    user_id="user_123",
    metadata={
        "channel": "web",
        "session_id": "sess_abc123",
        "user_segment": "premium"
    }
)

# Search conversations by metadata
conversations = await history.search_conversations(
    filters={"channel": "web", "user_segment": "premium"},
    user_id="user_123",
    limit=10
)
```

### Event Hooks

```python
from message_history.events import EventHooks

# Define custom hooks
class MyHooks(EventHooks):
    async def on_conversation_created(self, conversation: Conversation):
        # Log to analytics
        await analytics.track("conversation_started", {
            "user_id": conversation.user_id,
            "conversation_id": conversation.id
        })
        
    async def on_message_added(self, message: Message):
        # Check for sensitive content
        if await is_sensitive(message.content):
            await flag_for_review(message.id)

# Register hooks
history = MessageHistory(adapter=adapter, hooks=MyHooks())
```

## Migration Guide

### From Existing MongoDB Implementation

```python
# 1. Install the library
# pip install message-history[mongodb]

# 2. Update imports
# Before:
# from kopi_ai_orchestrator_api.models import Message, Conversation

# After:
from message_history import MessageHistory
from message_history.adapters import MongoDBAdapter
from message_history.types import MessageType, ChatRole

# 3. Initialize the library
adapter = MongoDBAdapter(
    connection_string=MONGODB_URI,
    database="your_db",
    conversations_collection="conversations",
    messages_collection="messages"
)

history = MessageHistory(adapter=adapter)

# 4. Update usage patterns
# Before:
# conversation = await Conversation.find_recent_or_create(user_id=user_id)
# await Message.create(
#     conversation_id=conversation.id,
#     user_id=user_id,
#     chat_role=ChatRoleType.user,
#     content=message,
#     message_type=MessageType.user_message
# )

# After:
conversation = await history.get_or_create_conversation(user_id=user_id)
await history.add_message(
    conversation_id=conversation.id,
    user_id=user_id,
    role=ChatRole.USER,
    content=message,
    message_type=MessageType.USER_MESSAGE
)
```

### Data Migration

```python
from message_history.migration import MigrationTool

# Migrate from one adapter to another
migrator = MigrationTool(
    source_adapter=old_mongodb_adapter,
    target_adapter=new_postgres_adapter
)

# Run migration with progress tracking
async for progress in migrator.migrate(batch_size=1000):
    print(f"Migrated {progress.processed}/{progress.total} records")
```

## Performance Considerations

### Indexing Strategy

The library automatically creates optimal indexes for common query patterns:

**MongoDB Indexes:**
- `conversations`: `{user_id: 1, updated_at: -1}`
- `messages`: `{conversation_id: 1, created_at: -1}`, `{conversation_id: 1, message_type: 1}`

**PostgreSQL Indexes:**
- `conversations`: `(user_id, updated_at DESC)`
- `messages`: `(conversation_id, created_at DESC)`, `(conversation_id, message_type)`

### Caching

```python
from message_history.cache import RedisCache

# Enable caching for frequently accessed conversations
cache = RedisCache(redis_url="redis://localhost:6379")
history = MessageHistory(
    adapter=adapter,
    cache=cache,
    cache_ttl=3600  # 1 hour TTL
)
```

### Connection Pooling

All adapters support connection pooling:

```python
# MongoDB with connection pooling
adapter = MongoDBAdapter(
    connection_string="mongodb://localhost:27017",
    max_pool_size=100,
    min_pool_size=10
)

# PostgreSQL with connection pooling
adapter = PostgreSQLAdapter(
    connection_string="postgresql://localhost/myapp",
    pool_size=20,
    max_overflow=40
)
```

## Error Handling

The library provides specific exceptions for different error scenarios:

```python
from message_history.exceptions import (
    ConversationNotFoundError,
    MessageValidationError,
    StorageConnectionError,
    ContextBuildError
)

try:
    conversation = await history.get_conversation("invalid_id")
except ConversationNotFoundError:
    # Handle missing conversation
    pass

try:
    await history.add_message(
        conversation_id=conv.id,
        user_id="user_123",
        role="invalid_role",  # This will fail validation
        content="Hello",
        message_type=MessageType.USER_MESSAGE
    )
except MessageValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e}")
```

## Testing

The library includes testing utilities:

```python
from message_history.testing import InMemoryAdapter, HistoryTestCase

class TestMyApplication(HistoryTestCase):
    async def setUp(self):
        # Use in-memory adapter for tests
        self.adapter = InMemoryAdapter()
        self.history = MessageHistory(adapter=self.adapter)
        
    async def test_conversation_flow(self):
        # Helper methods for common test scenarios
        conversation = await self.create_test_conversation("user_123")
        messages = await self.create_test_message_sequence(
            conversation.id,
            [
                ("user", "Hello"),
                ("ai", "Hi there!"),
                ("user", "How are you?"),
                ("ai", "I'm doing well, thanks!")
            ]
        )
        
        context = await self.history.get_context(conversation.id)
        assert len(context) == 4
```

## Monitoring and Observability

### Metrics

```python
from message_history.metrics import PrometheusMetrics

# Enable Prometheus metrics
metrics = PrometheusMetrics(port=9090)
history = MessageHistory(adapter=adapter, metrics=metrics)

# Available metrics:
# - message_history_conversations_created_total
# - message_history_messages_added_total
# - message_history_context_builds_total
# - message_history_operation_duration_seconds
```

### Logging

```python
import logging

# Configure logging
logging.getLogger("message_history").setLevel(logging.INFO)

# Structured logging with context
history = MessageHistory(
    adapter=adapter,
    log_context={"service": "my_app", "environment": "production"}
)
```

### Tracing

```python
from message_history.tracing import OpenTelemetryTracer

# Enable distributed tracing
tracer = OpenTelemetryTracer(
    service_name="message-history",
    endpoint="http://localhost:4317"
)
history = MessageHistory(adapter=adapter, tracer=tracer)
```

## Security Considerations

### Data Encryption

```python
from message_history.security import EncryptionConfig

# Enable at-rest encryption for sensitive content
encryption = EncryptionConfig(
    enabled=True,
    key_id="aws-kms-key-id",  # Or local key
    encrypt_fields=["content", "metadata"]
)

history = MessageHistory(
    adapter=adapter,
    encryption=encryption
)
```

### Access Control

```python
from message_history.security import AccessControl

# Implement row-level security
access_control = AccessControl(
    enable_user_isolation=True,  # Users can only access their own conversations
    enable_audit_log=True,       # Log all access attempts
    admin_roles=["admin", "moderator"]  # Roles that can access any conversation
)

history = MessageHistory(
    adapter=adapter,
    access_control=access_control
)
```
