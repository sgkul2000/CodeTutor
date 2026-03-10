from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


class PreferencesUpdate(BaseModel):
    default_language: Optional[str] = None
    assistance_level: Optional[int] = None
    theme: Optional[str] = None


@router.patch("/preferences")
async def update_preferences(
    body: PreferencesUpdate, user: User = Depends(get_current_user)
):
    if body.default_language is not None:
        user.preferences.default_language = body.default_language
    if body.assistance_level is not None:
        if not 1 <= body.assistance_level <= 4:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="assistance_level must be 1-4")
        user.preferences.assistance_level = body.assistance_level
    if body.theme is not None:
        user.preferences.theme = body.theme
    await user.save()
    return user.preferences.model_dump()


@router.get("/knowledge-profile")
async def get_knowledge_profile(user: User = Depends(get_current_user)):
    profile = user.knowledge_profile
    return {
        "overall_level": profile.overall_level,
        "weakest_topics": profile.weakest_topics,
        "strongest_topics": profile.strongest_topics,
        "topics": {
            topic: stats.model_dump()
            for topic, stats in profile.topics.items()
        },
        "last_updated": profile.last_updated.isoformat(),
    }


@router.get("/dashboard")
async def get_dashboard(user: User = Depends(get_current_user)):
    """
    Single endpoint that returns everything the Dashboard page needs:
    - User identity
    - Aggregated stats (with computed acceptance_rate)
    - Full knowledge profile (for the radar chart)
    - Last 5 submissions with problem titles (recent activity feed)
    """
    from app.models.submission import Submission
    from app.models.problem import Problem

    # ── Recent activity (last 5 submissions) ─────────────────────────────────
    recent_subs = (
        await Submission.find(Submission.user_id == str(user.id))
        .sort(-Submission.submitted_at)
        .limit(5)
        .to_list()
    )

    # Fetch problem titles in bulk (one query per unique problem_id)
    problem_ids = list({s.problem_id for s in recent_subs})
    problems_map: dict[str, str] = {}
    for pid in problem_ids:
        try:
            prob = await Problem.get(pid)
            if prob:
                problems_map[pid] = prob.title
        except Exception:
            pass  # skip if problem not found

    recent_activity = [
        {
            "submission_id": str(s.id),
            "problem_id": s.problem_id,
            "problem_title": problems_map.get(s.problem_id, "Unknown Problem"),
            "status": s.status,
            "language": s.language,
            "submitted_at": s.submitted_at.isoformat(),
        }
        for s in recent_subs
    ]

    # ── Stats with derived acceptance_rate ───────────────────────────────────
    stats = user.stats
    attempted = stats.problems_attempted
    solved = stats.problems_solved
    acceptance_rate = round((solved / attempted * 100), 1) if attempted > 0 else 0.0

    # ── Knowledge profile ─────────────────────────────────────────────────────
    profile = user.knowledge_profile

    return {
        "user": {
            "id": str(user.id),
            "display_name": user.display_name,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "is_admin": user.is_admin,
            "member_since": user.created_at.isoformat(),
        },
        "stats": {
            "problems_attempted": attempted,
            "problems_solved": solved,
            "hints_used": stats.hints_used,
            "streak_days": stats.streak_days,
            "acceptance_rate": acceptance_rate,
        },
        "knowledge_profile": {
            "overall_level": profile.overall_level,
            "weakest_topics": profile.weakest_topics,
            "strongest_topics": profile.strongest_topics,
            "topics": {
                topic: {
                    "proficiency_score": ts.proficiency_score,
                    "problems_attempted": ts.problems_attempted,
                    "problems_solved": ts.problems_solved,
                    "avg_hints_per_solve": ts.avg_hints_per_solve,
                }
                for topic, ts in profile.topics.items()
            },
            "last_updated": profile.last_updated.isoformat(),
        },
        "recent_activity": recent_activity,
    }
