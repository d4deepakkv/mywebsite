"""Thin async client for Claude via OpenRouter's OpenAI-compatible API."""
from __future__ import annotations

from typing import List

import httpx

from .config import get_settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(RuntimeError):
    pass


async def chat_completion(
    messages: List[dict],
    *,
    temperature: float = 0.7,
    max_tokens: int = 1200,
) -> str:
    """Send a chat completion request to OpenRouter and return the text reply.

    ``messages`` is a list of ``{"role": ..., "content": ...}`` dicts following
    the OpenAI chat format (roles: system / user / assistant).
    """
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise LLMError(
            "OPENROUTER_API_KEY is not set. Add it to backend/.env "
            "(see .env.example)."
        )

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        # Optional but recommended attribution headers for OpenRouter.
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)
    except httpx.HTTPError as exc:  # network-level failure
        raise LLMError(f"Could not reach OpenRouter: {exc}") from exc

    if resp.status_code != 200:
        raise LLMError(
            f"OpenRouter returned {resp.status_code}: {resp.text[:500]}"
        )

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError) as exc:
        raise LLMError(f"Unexpected OpenRouter response shape: {data}") from exc
