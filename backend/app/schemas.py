"""Pydantic request/response schemas for the API."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BotInfo(BaseModel):
    name: str
    description: str
    welcome_message: str


class ConversationCreate(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_name: Optional[str]
    user_email: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []


class ConversationSummary(BaseModel):
    """Lightweight conversation row for list views (no messages)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_name: Optional[str]
    user_email: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str


class ChatResponse(BaseModel):
    """Returned after the user posts a message: the assistant's reply."""

    message: MessageOut


class RequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content_markdown: str
    created_at: datetime
