from dataclasses import dataclass

__all__ = ["ConversationConfig"]


@dataclass(slots=True)
class ConversationConfig:
    """Runtime configuration for conversation behaviour."""

    reuse_window_days: int = 14  # Conversation reuse window
    history_limit: int = 30  # Default chat history limit
    conversation_id_prefix: str = "CONV_"
    message_id_prefix: str = "MSG_"

    connection_timeout_seconds: int = 30  # Adapter connection timeout
