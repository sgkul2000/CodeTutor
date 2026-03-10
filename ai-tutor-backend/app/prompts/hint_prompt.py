HINT_LEVEL_INSTRUCTIONS = {
    1: (
        "This is hint level 1 — DIRECTION only. "
        "Point to the general area of the code that has an issue. "
        "Do NOT name the algorithm or data structure. "
        "Ask a single guiding question at the end.",
        250,
    ),
    2: (
        "This is hint level 2 — APPROACH. "
        "Name the algorithmic technique or data structure that would help. "
        "Do NOT show any code or pseudocode. "
        "Use an analogy if helpful. End with a guiding question.",
        350,
    ),
    3: (
        "This is hint level 3 — STRUCTURE. "
        "Describe the step-by-step approach in plain English. "
        "Reference the student's code structure. "
        "Pseudocode is allowed but no working code. End with a guiding question.",
        500,
    ),
    4: (
        "This is hint level 4 — FULL WALKTHROUGH. "
        "Provide a detailed explanation with working code examples. "
        "Explain why the student's approach failed and how the correct approach works. "
        "Be thorough and educational.",
        800,
    ),
}


def build_hint_message(hint_level: int) -> tuple[str, int]:
    """Returns (instruction_text, max_tokens) for the given hint level."""
    return HINT_LEVEL_INSTRUCTIONS.get(hint_level, HINT_LEVEL_INSTRUCTIONS[1])
