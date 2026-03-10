from fastapi import HTTPException, status

MAX_CODE_LENGTH = 50_000  # characters

# Patterns that may attempt prompt injection via code comments or strings
_SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "you are now",
    "disregard your",
    "new system prompt",
    "###system",
    "<|system|>",
]


def sanitize(code: str) -> None:
    """
    Raises HTTPException if the submitted code violates safety constraints.
    Does NOT modify the code — sanitization is purely a gate check.
    """
    if "\x00" in code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code contains null bytes",
        )

    if len(code) > MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters",
        )

    lower = code.lower()
    for pattern in _SUSPICIOUS_PATTERNS:
        if pattern in lower:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code contains disallowed content",
            )
