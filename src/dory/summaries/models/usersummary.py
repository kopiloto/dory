from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

__all__ = ["UserSummary"]


class UserSummary(BaseModel):
    id: str = Field(..., description="Summary identifier (e.g. SUMM_<uuid>)")
    user_id: str = Field(..., description="User who owns the summary")
    content: str = Field(..., description="Summary text content")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured data extracted from conversations and actions",
    )
    conversation_ids: list[str] = Field(
        default_factory=list,
        description="List of conversation IDs used to build this summary",
    )
    action_ids: list[str] = Field(
        default_factory=list,
        description="List of action IDs included in this summary",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
