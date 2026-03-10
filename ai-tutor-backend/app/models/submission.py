from datetime import datetime, timezone
from typing import Optional

from beanie import Document, Link
from bson import ObjectId
from pydantic import BaseModel, Field


class FailedTestCase(BaseModel):
    input: str
    expected: str
    actual: str


class ExecutionResults(BaseModel):
    total_test_cases: int = 0
    passed_test_cases: int = 0
    failed_test_case: Optional[FailedTestCase] = None
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    stderr: str = ""


class AIAnalysis(BaseModel):
    triggered: bool = False
    error_type: Optional[str] = None  # logical_error | edge_case | wrong_approach | runtime | syntax
    conversation_id: Optional[str] = None


class Submission(Document):
    user_id: str
    problem_id: str
    language: str  # python | java | javascript
    code: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"
    # pending | accepted | wrong_answer | time_limit | runtime_error | compile_error
    execution_results: Optional[ExecutionResults] = None
    ai_analysis: AIAnalysis = Field(default_factory=AIAnalysis)

    class Settings:
        name = "submissions"
        indexes = ["user_id", "problem_id", "status"]
