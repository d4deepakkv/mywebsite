"""Application settings (env) and bot configuration (YAML).

Two distinct concerns live here:

* ``Settings`` – operational/runtime config read from environment variables
  (API keys, database URL, CORS). These are secrets / deployment details.
* ``BotConfig`` – the *discovery bot's* persona and playbook, authored by the
  admin in ``discovery_config.yaml``. This is the "context" the admin prepares
  before handing the bot to end users.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="anthropic/claude-sonnet-4.5", alias="OPENROUTER_MODEL"
    )
    openrouter_site_url: str = Field(
        default="http://localhost:5173", alias="OPENROUTER_SITE_URL"
    )
    openrouter_app_name: str = Field(
        default="Discovery Assistant", alias="OPENROUTER_APP_NAME"
    )

    database_url: str = Field(
        default="postgresql+asyncpg://discovery:discovery@localhost:5432/discovery",
        alias="DATABASE_URL",
    )

    discovery_config: str = Field(
        default="discovery_config.yaml", alias="DISCOVERY_CONFIG"
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# --- Bot (discovery) configuration -----------------------------------------


class LLMConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 1200


class BotConfig(BaseModel):
    """The admin-authored discovery playbook."""

    name: str = "Discovery Assistant"
    description: str = ""
    welcome_message: str = "Hi! Let's figure out what you need."
    llm: LLMConfig = Field(default_factory=LLMConfig)

    context: str = ""
    goals: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    seed_questions: List[str] = Field(default_factory=list)
    conversation_guidelines: str = ""

    def system_prompt(self) -> str:
        """Assemble the full system prompt fed to the model."""

        def bullets(items: List[str]) -> str:
            return "\n".join(f"- {i}" for i in items) if items else "- (none specified)"

        return f"""You are "{self.name}", an expert product discovery facilitator.

Your mission is to run a structured but friendly discovery conversation with a
stakeholder in order to deeply understand their needs so the team can ship the
right product. You interview, brainstorm, and probe — you do not build anything
yourself in this conversation.

# Background context the admin prepared for you
{self.context.strip() or "(no extra context provided)"}

# Goals of this discovery session
{bullets(self.goals)}

# Topics you must make sure you cover
{bullets(self.focus_areas)}

# Examples of opening / seed questions you can draw from
{bullets(self.seed_questions)}

# How to conduct the conversation
- Ask ONE focused question at a time. Never dump a long list of questions.
- Start broad, then drill into specifics with follow-ups ("why", "walk me
  through it", "what happens when…", "who is involved", "how often").
- Actively brainstorm: surface edge cases, suggest possibilities the user may
  not have considered, and reflect back what you heard to confirm understanding.
- Pay special attention to the user's CURRENT manual process: the step-by-step
  workflow, the people involved, the tools/spreadsheets used, the pain points,
  the data that flows through it, and how they measure success.
- Be warm, curious, and concise. Acknowledge answers before asking the next
  question.
- When you believe you have gathered enough across all focus areas, let the user
  know they can generate a requirements summary, but keep going if they want.
{self.conversation_guidelines.strip()}
""".strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _config_path(settings: Settings) -> Path:
    p = Path(settings.discovery_config)
    if not p.is_absolute():
        # resolve relative to the backend package root (parent of app/)
        p = Path(__file__).resolve().parent.parent / p
    return p


def load_bot_config() -> BotConfig:
    """Load the bot config from YAML, falling back to defaults if absent.

    Read fresh each call so admins can edit the YAML and pick up changes by
    restarting (or, since this is cheap, even without a restart).
    """
    settings = get_settings()
    path = _config_path(settings)
    if not path.exists():
        return BotConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # Allow either a flat mapping or a top-level "bot:" / "discovery:" grouping.
    merged: dict = {}
    merged.update(data.get("bot", {}))
    merged.update(data.get("discovery", {}))
    if "llm" in data:
        merged["llm"] = data["llm"]
    # also accept fully-flat configs
    for key in (
        "name",
        "description",
        "welcome_message",
        "context",
        "goals",
        "focus_areas",
        "seed_questions",
        "conversation_guidelines",
    ):
        if key in data:
            merged[key] = data[key]
    return BotConfig(**merged)
