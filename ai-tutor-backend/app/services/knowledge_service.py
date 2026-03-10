"""
Knowledge model service.

Tracks per-topic proficiency for each user based on their submission history.
Called asynchronously after every graded submission.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.problem import Problem
    from app.models.submission import Submission


def compute_proficiency(topic_stats) -> float:
    """
    Compute a proficiency score (0.0 – 1.0) for a single topic.

    Formula (per TDD §6.5.2):
        score = solve_rate × 0.4 + hint_efficiency × 0.3 + first_attempt_rate × 0.3

    Recency decay: score × max(0.5, 1 – (days_inactive – 14) × 0.02)
    applied if the topic hasn't been practised in > 14 days.
    """
    if topic_stats.problems_attempted == 0:
        return 0.0

    solve_rate = topic_stats.problems_solved / topic_stats.problems_attempted
    hint_efficiency = max(0.0, 1.0 - (topic_stats.avg_hints_per_solve / 4.0))
    first_attempt = topic_stats.first_attempt_solve_rate

    score = solve_rate * 0.4 + hint_efficiency * 0.3 + first_attempt * 0.3

    # Recency decay
    if topic_stats.last_practiced:
        now = datetime.now(timezone.utc)
        last = topic_stats.last_practiced
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        days_since = (now - last).days
        if days_since > 14:
            decay = max(0.5, 1.0 - (days_since - 14) * 0.02)
            score *= decay

    return round(min(score, 1.0), 2)


def get_overall_level(profile) -> str:
    """Derive overall level from average proficiency across all topics."""
    if not profile.topics:
        return "beginner"
    avg = sum(s.proficiency_score for s in profile.topics.values()) / len(profile.topics)
    if avg >= 0.65:
        return "advanced"
    if avg >= 0.35:
        return "intermediate"
    return "beginner"


async def update_knowledge_profile(
    user: "User",
    problem: "Problem",
    submission: "Submission",
    hints_used_this_session: int = 0,
) -> None:
    """
    Update the user's knowledge profile after a graded submission.
    Called after every submission regardless of outcome.
    """
    from app.models.user import TopicStats

    solved = submission.status == "accepted"
    now = datetime.now(timezone.utc)

    for topic in problem.category:
        if topic not in user.knowledge_profile.topics:
            user.knowledge_profile.topics[topic] = TopicStats()

        stats = user.knowledge_profile.topics[topic]
        stats.problems_attempted += 1

        if solved:
            stats.problems_solved += 1

            # Update first-attempt solve rate
            # first_attempt_solve_rate = solves with 0 hints / total solves
            total_solves = stats.problems_solved
            first_attempt_solves_before = round(
                stats.first_attempt_solve_rate * max(total_solves - 1, 1)
            )
            if hints_used_this_session == 0:
                first_attempt_solves_before += 1
            stats.first_attempt_solve_rate = round(
                first_attempt_solves_before / total_solves, 2
            )

            # Rolling average of hints per solve
            if total_solves == 1:
                stats.avg_hints_per_solve = float(hints_used_this_session)
            else:
                stats.avg_hints_per_solve = round(
                    (stats.avg_hints_per_solve * (total_solves - 1) + hints_used_this_session)
                    / total_solves,
                    2,
                )

        stats.last_practiced = now
        stats.proficiency_score = compute_proficiency(stats)

    # Recompute aggregate fields
    user.knowledge_profile.overall_level = get_overall_level(user.knowledge_profile)

    scored = {t: s.proficiency_score for t, s in user.knowledge_profile.topics.items()}
    sorted_topics = sorted(scored, key=scored.get)  # type: ignore[arg-type]
    user.knowledge_profile.weakest_topics = sorted_topics[:3]
    user.knowledge_profile.strongest_topics = sorted_topics[-3:][::-1]
    user.knowledge_profile.last_updated = now

    await user.save()
