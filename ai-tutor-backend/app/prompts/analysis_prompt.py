def build_analysis_messages(problem, submission, execution_result, conversation_history, user):
    """Build the message list for initial code analysis."""
    assistance = user.preferences.assistance_level
    knowledge = user.knowledge_profile

    # Compute topic proficiency for this problem's categories
    topic_scores = {
        t: knowledge.topics[t].proficiency_score
        for t in problem.category
        if t in knowledge.topics
    }
    weak_topics = [t for t, s in topic_scores.items() if s < 0.4]

    messages = [
        # Inject problem context
        {
            "role": "user",
            "content": (
                f"PROBLEM: {problem.title}\n"
                f"Difficulty: {problem.difficulty}\n"
                f"Categories: {', '.join(problem.category)}\n\n"
                f"{problem.description}\n\n"
                f"CONSTRAINTS: {problem.constraints}"
            ),
        },
        {
            "role": "assistant",
            "content": "I understand the problem. Ready to help.",
        },
        # Inject student context
        {
            "role": "user",
            "content": (
                f"STUDENT CONTEXT:\n"
                f"Assistance level: {assistance}/4\n"
                f"Overall level: {knowledge.overall_level}\n"
                f"Topic proficiency for this problem: {topic_scores}\n"
                f"Weak areas: {weak_topics if weak_topics else 'none identified'}"
            ),
        },
        {
            "role": "assistant",
            "content": "Understood. I will calibrate my guidance accordingly.",
        },
        # Inject submission + results
        {
            "role": "user",
            "content": (
                f"STUDENT SUBMISSION ({submission.language}):\n"
                f"```{submission.language}\n{submission.code}\n```\n\n"
                f"EXECUTION RESULT: {submission.status}\n"
                f"Passed {execution_result.passed_test_cases}/{execution_result.total_test_cases} tests\n"
                + (
                    f"Failed on:\n"
                    f"  Input: {execution_result.failed_test_case.input}\n"
                    f"  Expected: {execution_result.failed_test_case.expected}\n"
                    f"  Got: {execution_result.failed_test_case.actual}\n"
                    if execution_result.failed_test_case
                    else ""
                )
                + (f"Stderr: {execution_result.stderr}\n" if execution_result.stderr else "")
                + f"\nThis is hint level 1. Provide a directional hint only."
            ),
        },
        *conversation_history,
    ]
    return messages
