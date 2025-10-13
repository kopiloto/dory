from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

__all__ = ["UserAction"]


class UserAction(BaseModel):
    id: str = Field(..., description="Action identifier (e.g. ACT_<uuid>)")
    user_id: str = Field(..., description="User who performed the action")
    action_type: str = Field(
        ..., description="Type of action (defined by client application)"
    )
    action_name: str = Field(..., description="Human-readable name of the action")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional action-specific data"
    )
    conversation_id: str | None = Field(
        default=None, description="Associated conversation ID if applicable"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
