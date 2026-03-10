from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    hint_level: Optional[int] = None  # 1-4, set on assistant messages
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationMetadata(BaseModel):
    total_tokens_used: int = 0
    model_used: str = ""
    resolved: bool = False


class Conversation(Document):
    user_id: str
    problem_id: str
    submission_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hint_level_reached: int = 1  # Tracks escalation (1-4)
    messages: list[Message] = Field(default_factory=list)
    metadata: ConversationMetadata = Field(default_factory=ConversationMetadata)

    class Settings:
        name = "conversations"
        indexes = ["user_id", "problem_id", "submission_id"]
