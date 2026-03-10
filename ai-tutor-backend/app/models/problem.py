from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class Example(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class TestCase(BaseModel):
    input: str
    expected_output: str


class StarterCode(BaseModel):
    python: str = ""
    java: str = ""
    javascript: str = ""


class HintsMetadata(BaseModel):
    common_mistakes: list[str] = Field(default_factory=list)
    key_insight: str = ""
    related_problems: list[str] = Field(default_factory=list)


class Problem(Document):
    title: str
    slug: str
    difficulty: str  # easy | medium | hard
    category: list[str]  # e.g. ["array", "hash-map"]
    description: str  # Markdown
    constraints: str
    examples: list[Example] = Field(default_factory=list)
    test_cases: list[TestCase] = Field(default_factory=list)
    starter_code: StarterCode = Field(default_factory=StarterCode)
    hints_metadata: HintsMetadata = Field(default_factory=HintsMetadata)

    class Settings:
        name = "problems"
        indexes = ["slug", "difficulty", "category"]
