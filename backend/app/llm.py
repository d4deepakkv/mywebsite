"""Thin async client for Claude via OpenRouter's OpenAI-compatible API."""
from __future__ import annotations

import json
from typing import AsyncIterator, List

import httpx

from .config import get_settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(RuntimeError):
    pass


def _headers() -> dict:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise LLMError(
            "OPENROUTER_API_KEY is not set. Add it to backend/.env "
            "(see .env.example)."
        )
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        # Optional but recommended attribution headers for OpenRouter.
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }


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
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OPENROUTER_URL, headers=_headers(), json=payload)
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


async def chat_completion_stream(
    messages: List[dict],
    *,
    temperature: float = 0.7,
    max_tokens: int = 1200,
) -> AsyncIterator[str]:
    """Stream a chat completion from OpenRouter, yielding text deltas.

    Uses OpenRouter's SSE streaming (``stream: true``). Each yielded value is a
    chunk of assistant text to append to the message as it arrives.
    """
    settings = get_settings()
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", OPENROUTER_URL, headers=_headers(), json=payload
            ) as resp:
                if resp.status_code != 200:
                    body = (await resp.aread()).decode("utf-8", "replace")
                    raise LLMError(
                        f"OpenRouter returned {resp.status_code}: {body[:500]}"
                    )
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue  # skip keep-alive comments / blanks
                    data = line[len("data: ") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        delta = obj["choices"][0]["delta"].get("content")
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    if delta:
                        yield delta
    except httpx.HTTPError as exc:  # network-level failure mid-stream
        raise LLMError(f"Could not reach OpenRouter: {exc}") from exc
