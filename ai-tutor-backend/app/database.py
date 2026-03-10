from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global _client
    from app.models.user import User
    from app.models.problem import Problem
    from app.models.submission import Submission
    from app.models.conversation import Conversation

    _client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=_client[settings.mongodb_database],
        document_models=[User, Problem, Submission, Conversation],
    )


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        _client = None
