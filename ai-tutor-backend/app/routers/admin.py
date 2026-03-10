"""
Admin-only endpoints for problem management.
Requires is_admin=True on the authenticated user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.models.problem import Problem, Example, TestCase, StarterCode, HintsMetadata
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# ── Request schemas ───────────────────────────────────────────────────────────

class ExampleIn(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class TestCaseIn(BaseModel):
    input: str
    expected_output: str


class StarterCodeIn(BaseModel):
    python: str = ""
    java: str = ""
    javascript: str = ""


class HintsMetadataIn(BaseModel):
    common_mistakes: list[str] = []
    key_insight: str = ""
    related_problems: list[str] = []


class ProblemIn(BaseModel):
    title: str
    slug: str
    difficulty: str          # easy | medium | hard
    category: list[str]
    description: str         # Markdown
    constraints: str
    examples: list[ExampleIn] = []
    test_cases: list[TestCaseIn] = []
    starter_code: StarterCodeIn = StarterCodeIn()
    hints_metadata: HintsMetadataIn = HintsMetadataIn()


class BulkImportIn(BaseModel):
    problems: list[ProblemIn]
    skip_existing: bool = True   # if False, overwrites problems with same slug


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/problems")
async def list_all_problems(_admin: User = Depends(require_admin)):
    """List all problems including internal metadata."""
    problems = await Problem.find_all().to_list()
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "category": p.category,
            "test_cases_count": len(p.test_cases),
        }
        for p in problems
    ]


@router.post("/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(body: ProblemIn, _admin: User = Depends(require_admin)):
    """Create a single problem."""
    existing = await Problem.find_one(Problem.slug == body.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Problem with slug '{body.slug}' already exists. Use PUT to update.",
        )
    problem = _build_problem(body)
    await problem.insert()
    return {"id": str(problem.id), "slug": problem.slug, "title": problem.title}


@router.put("/problems/{slug}")
async def update_problem(slug: str, body: ProblemIn, _admin: User = Depends(require_admin)):
    """Replace an existing problem entirely."""
    existing = await Problem.find_one(Problem.slug == slug)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    # Update all fields in-place
    existing.title = body.title
    existing.slug = body.slug
    existing.difficulty = body.difficulty
    existing.category = body.category
    existing.description = body.description
    existing.constraints = body.constraints
    existing.examples = [Example(**e.model_dump()) for e in body.examples]
    existing.test_cases = [TestCase(**tc.model_dump()) for tc in body.test_cases]
    existing.starter_code = StarterCode(**body.starter_code.model_dump())
    existing.hints_metadata = HintsMetadata(**body.hints_metadata.model_dump())
    await existing.save()
    return {"id": str(existing.id), "slug": existing.slug, "updated": True}


@router.post("/problems/bulk-import")
async def bulk_import(body: BulkImportIn, _admin: User = Depends(require_admin)):
    """
    Import multiple problems at once.
    Returns a summary of inserted / skipped / updated counts.
    Useful for importing your scraped problem set.
    """
    inserted, skipped, updated = 0, 0, 0
    errors = []

    for p_in in body.problems:
        try:
            existing = await Problem.find_one(Problem.slug == p_in.slug)
            if existing:
                if body.skip_existing:
                    skipped += 1
                    continue
                # Overwrite
                existing.title = p_in.title
                existing.difficulty = p_in.difficulty
                existing.category = p_in.category
                existing.description = p_in.description
                existing.constraints = p_in.constraints
                existing.examples = [Example(**e.model_dump()) for e in p_in.examples]
                existing.test_cases = [TestCase(**tc.model_dump()) for tc in p_in.test_cases]
                existing.starter_code = StarterCode(**p_in.starter_code.model_dump())
                existing.hints_metadata = HintsMetadata(**p_in.hints_metadata.model_dump())
                await existing.save()
                updated += 1
            else:
                problem = _build_problem(p_in)
                await problem.insert()
                inserted += 1
        except Exception as e:
            errors.append({"slug": p_in.slug, "error": str(e)})

    return {
        "inserted": inserted,
        "skipped": skipped,
        "updated": updated,
        "errors": errors,
    }


@router.delete("/problems/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(slug: str, _admin: User = Depends(require_admin)):
    """Delete a problem by slug."""
    problem = await Problem.find_one(Problem.slug == slug)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    await problem.delete()


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_problem(body: ProblemIn) -> Problem:
    return Problem(
        title=body.title,
        slug=body.slug,
        difficulty=body.difficulty,
        category=body.category,
        description=body.description,
        constraints=body.constraints,
        examples=[Example(**e.model_dump()) for e in body.examples],
        test_cases=[TestCase(**tc.model_dump()) for tc in body.test_cases],
        starter_code=StarterCode(**body.starter_code.model_dump()),
        hints_metadata=HintsMetadata(**body.hints_metadata.model_dump()),
    )
