from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.problem import Problem
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("")
async def list_problems(
    difficulty: Optional[str] = Query(None, pattern="^(easy|medium|hard)$"),
    category: Optional[str] = Query(None),
    _user: User = Depends(get_current_user),
):
    filters = {}
    if difficulty:
        filters["difficulty"] = difficulty
    if category:
        filters["category"] = category

    problems = await Problem.find(filters).to_list()
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "category": p.category,
        }
        for p in problems
    ]


@router.get("/{slug}")
async def get_problem(slug: str, _user: User = Depends(get_current_user)):
    problem = await Problem.find_one(Problem.slug == slug)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    return {
        "id": str(problem.id),
        "title": problem.title,
        "slug": problem.slug,
        "difficulty": problem.difficulty,
        "category": problem.category,
        "description": problem.description,
        "constraints": problem.constraints,
        "examples": [e.model_dump() for e in problem.examples],
        "starter_code": problem.starter_code.model_dump(),
        "hints_metadata": {
            "common_mistakes": problem.hints_metadata.common_mistakes,
            "related_problems": problem.hints_metadata.related_problems,
        },
    }


@router.get("/{slug}/related")
async def get_related_problems(slug: str, _user: User = Depends(get_current_user)):
    problem = await Problem.find_one(Problem.slug == slug)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    related_slugs = problem.hints_metadata.related_problems[:3]
    related = await Problem.find({"slug": {"$in": related_slugs}}).to_list()
    return [
        {"id": str(p.id), "title": p.title, "slug": p.slug, "difficulty": p.difficulty}
        for p in related
    ]
