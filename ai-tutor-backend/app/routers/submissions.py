from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models.problem import Problem
from app.models.submission import Submission, ExecutionResults
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services import local_executor as execution_backend
# PRODUCTION: swap to `from app.services import piston_service as execution_backend`
#             and set PISTON_URL to your hosted Piston instance.

router = APIRouter()


class SubmitRequest(BaseModel):
    problem_id: str
    language: str  # python | java | javascript
    code: str


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_code(body: SubmitRequest, user: User = Depends(get_current_user)):
    if body.language not in ("python", "java", "javascript"):
        raise HTTPException(status_code=400, detail="Unsupported language")

    problem = await Problem.get(body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    from app.utils.code_sanitizer import sanitize
    sanitize(body.code)  # raises HTTPException on violation

    submission = Submission(
        user_id=str(user.id),
        problem_id=body.problem_id,
        language=body.language,
        code=body.code,
        status="pending",
    )
    await submission.insert()

    # Execute synchronously for now (async Celery in Phase 3)
    try:
        exec_result = await execution_backend.execute_code(
            body.code, body.language, problem.test_cases
        )
        submission.status = exec_result["status"]
        submission.execution_results = ExecutionResults(**exec_result["results"])
        await submission.save()

        # Update user stats
        user.stats.problems_attempted += 1
        if submission.status == "accepted":
            user.stats.problems_solved += 1
        await user.save()

        # Async knowledge profile update (fire-and-forget)
        import asyncio
        from app.services.knowledge_service import update_knowledge_profile
        asyncio.create_task(
            update_knowledge_profile(user, problem, submission, hints_used_this_session=0)
        )
    except Exception as e:
        submission.status = "runtime_error"
        await submission.save()

    return {
        "submission_id": str(submission.id),
        "status": submission.status,
        "execution_results": submission.execution_results.model_dump()
        if submission.execution_results
        else None,
        "ai_analysis_available": submission.status != "accepted",
    }


@router.get("/history/{problem_id}")
async def submission_history(problem_id: str, user: User = Depends(get_current_user)):
    submissions = await Submission.find(
        Submission.user_id == str(user.id),
        Submission.problem_id == problem_id,
    ).sort(-Submission.submitted_at).to_list()

    return [
        {
            "id": str(s.id),
            "status": s.status,
            "language": s.language,
            "submitted_at": s.submitted_at.isoformat(),
            "execution_results": s.execution_results.model_dump()
            if s.execution_results
            else None,
        }
        for s in submissions
    ]


@router.get("/{submission_id}")
async def get_submission(submission_id: str, user: User = Depends(get_current_user)):
    submission = await Submission.get(submission_id)
    if not submission or submission.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "submission_id": str(submission.id),
        "status": submission.status,
        "language": submission.language,
        "submitted_at": submission.submitted_at.isoformat(),
        "execution_results": submission.execution_results.model_dump()
        if submission.execution_results
        else None,
        "ai_analysis": submission.ai_analysis.model_dump(),
        "ai_analysis_available": submission.status != "accepted",
    }
