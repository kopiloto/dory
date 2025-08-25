from dataclasses import dataclass

__all__ = ["ConversationConfig"]


@dataclass(slots=True)
class ConversationConfig:
    """Runtime configuration for conversation behaviour."""

    # Maximum period of inactivity (in days) after which a new
    # conversation will be created instead of re-using the previous one.
    # The counter is reset every time the conversation `updated_at` field
    # is modified (i.e. whenever a new message is stored).
    reuse_window_days: int = 14
    history_limit: int = 30  # Default chat history limit
    conversation_id_prefix: str = "CONV_"
    message_id_prefix: str = "MSG_"

    connection_timeout_seconds: int = 30  # Adapter connection timeout
