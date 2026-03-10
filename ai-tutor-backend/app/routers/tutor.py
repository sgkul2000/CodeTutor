from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from app.models.conversation import Conversation
from app.models.submission import Submission
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services import tutor_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class AnalyzeRequest(BaseModel):
    submission_id: str


class AskRequest(BaseModel):
    conversation_id: str
    message: str


class HintRequest(BaseModel):
    conversation_id: str


@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_submission(
    request: Request, body: AnalyzeRequest, user: User = Depends(get_current_user)
):
    submission = await Submission.get(body.submission_id)
    if not submission or submission.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status == "accepted":
        raise HTTPException(status_code=400, detail="Submission already accepted")

    from app.models.problem import Problem
    problem = await Problem.get(submission.problem_id)

    # Create or reuse conversation
    conversation = await Conversation.find_one(
        Conversation.submission_id == str(submission.id)
    )
    if not conversation:
        conversation = Conversation(
            user_id=str(user.id),
            problem_id=str(problem.id),
            submission_id=str(submission.id),
        )
        await conversation.insert()

        # Link conversation to submission
        submission.ai_analysis.triggered = True
        submission.ai_analysis.conversation_id = str(conversation.id)
        await submission.save()

    return EventSourceResponse(
        await tutor_service.stream_analysis(problem, submission, conversation, user)
    )


@router.post("/ask")
@limiter.limit("10/minute")
async def ask_question(request: Request, body: AskRequest, user: User = Depends(get_current_user)):
    conversation = await Conversation.get(body.conversation_id)
    if not conversation or conversation.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")

    from app.models.problem import Problem
    from app.models.submission import Submission as Sub
    problem = await Problem.get(conversation.problem_id)
    submission = await Sub.get(conversation.submission_id)

    return EventSourceResponse(
        await tutor_service.stream_followup(
            problem, submission, conversation, user, body.message
        )
    )


@router.post("/hint")
@limiter.limit("10/minute")
async def request_hint(request: Request, body: HintRequest, user: User = Depends(get_current_user)):
    conversation = await Conversation.get(body.conversation_id)
    if not conversation or conversation.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")

    from app.models.problem import Problem
    from app.models.submission import Submission as Sub
    problem = await Problem.get(conversation.problem_id)
    submission = await Sub.get(conversation.submission_id)

    # Escalate hint level (max 4)
    next_level = min(conversation.hint_level_reached + 1, 4)

    return EventSourceResponse(
        await tutor_service.stream_hint(
            problem, submission, conversation, user, next_level
        )
    )


@router.get("/conversation/{submission_id}")
async def get_conversation(submission_id: str, user: User = Depends(get_current_user)):
    conversation = await Conversation.find_one(
        Conversation.submission_id == submission_id,
        Conversation.user_id == str(user.id),
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": str(conversation.id),
        "hint_level_reached": conversation.hint_level_reached,
        "messages": [m.model_dump() for m in conversation.messages],
        "metadata": conversation.metadata.model_dump(),
    }
