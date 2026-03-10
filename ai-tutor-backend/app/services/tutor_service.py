import json
from typing import AsyncGenerator

import anthropic

from app.config import settings
from app.models.conversation import Conversation, Message
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.prompts.analysis_prompt import build_analysis_messages
from app.prompts.hint_prompt import build_hint_message

# Use the async client so streaming doesn't block the asyncio event loop
client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


def _history_to_messages(conversation: Conversation) -> list[dict]:
    return [
        {"role": m.role, "content": m.content}
        for m in conversation.messages
    ]


async def stream_analysis(
    problem: Problem,
    submission: Submission,
    conversation: Conversation,
    user: User,
) -> AsyncGenerator:
    exec_result = submission.execution_results
    history = _history_to_messages(conversation)
    messages = build_analysis_messages(problem, submission, exec_result, history, user)
    _, max_tokens = build_hint_message(1)

    async def generator():
        full_response = ""
        try:
            async with client.messages.stream(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield {"event": "token", "data": json.dumps({"text": text})}

            # Persist assistant message
            conversation.messages.append(
                Message(role="assistant", content=full_response, hint_level=1)
            )
            conversation.metadata.model_used = settings.anthropic_model
            await conversation.save()

            yield {"event": "done", "data": json.dumps({"conversation_id": str(conversation.id)})}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return generator()


async def stream_followup(
    problem: Problem,
    submission: Submission,
    conversation: Conversation,
    user: User,
    user_message: str,
) -> AsyncGenerator:
    # Append user message first
    conversation.messages.append(Message(role="user", content=user_message))
    await conversation.save()

    exec_result = submission.execution_results
    history = _history_to_messages(conversation)
    messages = build_analysis_messages(problem, submission, exec_result, history, user)

    async def generator():
        full_response = ""
        try:
            async with client.messages.stream(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield {"event": "token", "data": json.dumps({"text": text})}

            conversation.messages.append(
                Message(role="assistant", content=full_response,
                        hint_level=conversation.hint_level_reached)
            )
            conversation.metadata.total_tokens_used += len(full_response) // 4
            await conversation.save()

            yield {"event": "done", "data": json.dumps({"conversation_id": str(conversation.id)})}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return generator()


async def stream_hint(
    problem: Problem,
    submission: Submission,
    conversation: Conversation,
    user: User,
    next_level: int,
) -> AsyncGenerator:
    instruction, max_tokens = build_hint_message(next_level)

    exec_result = submission.execution_results
    history = _history_to_messages(conversation)

    # Build messages with escalated hint instruction
    from app.prompts.analysis_prompt import build_analysis_messages
    messages = build_analysis_messages(problem, submission, exec_result, history, user)

    # Append a fresh user message with the hint instruction so messages always
    # end with a user turn (required by Claude's API).
    messages.append({"role": "user", "content": instruction})

    async def generator():
        full_response = ""
        try:
            async with client.messages.stream(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield {"event": "token", "data": json.dumps({"text": text})}

            conversation.hint_level_reached = next_level
            conversation.messages.append(
                Message(role="assistant", content=full_response, hint_level=next_level)
            )
            await conversation.save()

            yield {"event": "done", "data": json.dumps({
                "conversation_id": str(conversation.id),
                "hint_level": next_level,
            })}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return generator()
