from dataclasses import dataclass

__all__ = ["ConversationConfig"]


@dataclass(slots=True)
class ConversationConfig:
    """Runtime configuration for conversation behaviour."""

    reuse_window_days: int = 14  # Conversation reuse window
    history_limit: int = 30  # Default chat history limit
