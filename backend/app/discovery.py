"""Core discovery logic: building prompts and generating replies / summaries."""
from __future__ import annotations

from typing import AsyncIterator, Iterable, List, Tuple

from .config import BotConfig
from .llm import chat_completion, chat_completion_stream


def _normalize(history: Iterable) -> List[Tuple[str, str]]:
    """Accept a list of ORM ``Message`` objects or ``{role, content}`` dicts."""
    out: List[Tuple[str, str]] = []
    for m in history:
        if isinstance(m, dict):
            role, content = m.get("role"), m.get("content")
        else:
            role, content = m.role, m.content
        out.append((role, content))
    return out


def _history_to_messages(bot: BotConfig, history: Iterable) -> List[dict]:
    """Convert stored messages + bot config into an OpenAI-style message list."""
    msgs: List[dict] = [{"role": "system", "content": bot.system_prompt()}]
    for role, content in _normalize(history):
        if role in ("user", "assistant"):
            msgs.append({"role": role, "content": content})
    return msgs


async def opening_message(bot: BotConfig) -> str:
    """Generate the bot's first message to kick off discovery.

    We prefer the admin-authored welcome message verbatim so the experience is
    predictable, then the model takes over from the user's first reply.
    """
    return bot.welcome_message


async def generate_reply(bot: BotConfig, history: Iterable) -> str:
    """Generate the assistant's next discovery question/response."""
    messages = _history_to_messages(bot, history)
    return await chat_completion(
        messages,
        temperature=bot.llm.temperature,
        max_tokens=bot.llm.max_tokens,
    )


async def generate_reply_stream(
    bot: BotConfig, history: Iterable
) -> AsyncIterator[str]:
    """Stream the assistant's next discovery response as text deltas."""
    messages = _history_to_messages(bot, history)
    async for delta in chat_completion_stream(
        messages,
        temperature=bot.llm.temperature,
        max_tokens=bot.llm.max_tokens,
    ):
        yield delta


SUMMARY_INSTRUCTION = """\
You are now switching from interviewer to analyst. Based ONLY on the discovery
conversation above, produce a clear, well-structured **requirements document**
in Markdown that the engineering and product team can act on.

Use these sections (omit a section only if there is genuinely nothing to say):

## 1. Overview
A short paragraph summarising who the user is and what they want to achieve.

## 2. Current Manual Process
Step-by-step description of how they do this today, the people involved, and the
tools/spreadsheets used.

## 3. Pain Points & Goals
What hurts today and what success looks like for them.

## 4. Functional Requirements
A numbered list of concrete capabilities the product must have. Be specific.

## 5. Non-Functional Requirements & Constraints
Performance, integrations, security, compliance, data volumes, deadlines, etc.

## 6. Users & Roles
The different types of users and what each needs to do.

## 7. Open Questions
Anything still ambiguous that the team should follow up on.

Be faithful to what the user actually said — do not invent requirements. Where
the user was vague, note it under Open Questions rather than guessing.
"""


async def generate_summary(bot: BotConfig, history: Iterable) -> str:
    """Produce a structured requirements summary from the conversation."""
    messages = _history_to_messages(bot, history)
    messages.append({"role": "user", "content": SUMMARY_INSTRUCTION})
    return await chat_completion(
        messages,
        temperature=0.3,  # lower temp for a faithful, structured summary
        max_tokens=2000,
    )


async def generate_title(history: Iterable) -> str | None:
    """Generate a short title from the first user message (best effort)."""
    first_user = next(
        (content for role, content in _normalize(history) if role == "user"), None
    )
    if not first_user:
        return None
    prompt = [
        {
            "role": "user",
            "content": (
                "Summarise the following request as a short title of at most 6 "
                "words. Reply with ONLY the title, no quotes.\n\n"
                f"{first_user[:500]}"
            ),
        }
    ]
    try:
        title = await chat_completion(prompt, temperature=0.2, max_tokens=30)
        return title.strip().strip('"')[:255] or None
    except Exception:
        return None
