from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class TopicStats(BaseModel):
    problems_attempted: int = 0
    problems_solved: int = 0
    avg_hints_per_solve: float = 0.0
    first_attempt_solve_rate: float = 0.0
    proficiency_score: float = 0.0
    last_practiced: Optional[datetime] = None


class KnowledgeProfile(BaseModel):
    topics: dict[str, TopicStats] = Field(default_factory=dict)
    overall_level: str = "beginner"  # beginner | intermediate | advanced
    weakest_topics: list[str] = Field(default_factory=list)
    strongest_topics: list[str] = Field(default_factory=list)
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class UserPreferences(BaseModel):
    default_language: str = "python"
    assistance_level: int = 2  # 1-4 slider value
    theme: str = "dark"


class UserStats(BaseModel):
    problems_attempted: int = 0
    problems_solved: int = 0
    hints_used: int = 0
    streak_days: int = 0


class User(Document):
    email: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    oauth_provider: str  # "google" | "github" | "dev"
    oauth_id: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    knowledge_profile: KnowledgeProfile = Field(default_factory=KnowledgeProfile)
    stats: UserStats = Field(default_factory=UserStats)

    class Settings:
        name = "users"
        indexes = ["email", "oauth_provider", "oauth_id"]
