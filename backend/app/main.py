"""FastAPI application exposing the discovery chatbot API."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import discovery, schemas
from .config import get_settings, load_bot_config
from .database import get_db, init_db
from .llm import LLMError
from .models import Conversation, Message, Requirement


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Discovery Assistant API", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _get_conversation(
    conversation_id: uuid.UUID, db: AsyncSession
) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/bot", response_model=schemas.BotInfo)
async def bot_info() -> schemas.BotInfo:
    bot = load_bot_config()
    return schemas.BotInfo(
        name=bot.name,
        description=bot.description,
        welcome_message=bot.welcome_message,
    )


@app.post("/api/conversations", response_model=schemas.ConversationOut)
async def create_conversation(
    payload: schemas.ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    bot = load_bot_config()

    # Seed with the bot's opening message so the UI has something to show.
    # Attach it while the object is still pending (before flush) so SQLAlchemy
    # does not try to lazy-load the (empty) collection in a sync context.
    opening = await discovery.opening_message(bot)
    conv = Conversation(
        user_name=payload.user_name,
        user_email=payload.user_email,
        messages=[Message(role="assistant", content=opening)],
    )
    db.add(conv)

    await db.commit()
    await db.refresh(conv, attribute_names=["messages"])
    return conv


@app.get("/api/conversations", response_model=list[schemas.ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
) -> list[Conversation]:
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


@app.get(
    "/api/conversations/{conversation_id}",
    response_model=schemas.ConversationOut,
)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    return await _get_conversation(conversation_id, db)


@app.post(
    "/api/conversations/{conversation_id}/messages",
    response_model=schemas.ChatResponse,
)
async def post_message(
    conversation_id: uuid.UUID,
    payload: schemas.MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.ChatResponse:
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conv = await _get_conversation(conversation_id, db)
    bot = load_bot_config()

    # Persist the user's message first.
    user_msg = Message(role="user", content=payload.content.strip())
    conv.messages.append(user_msg)
    await db.flush()

    # Generate the assistant's reply from the full history.
    try:
        reply_text = await discovery.generate_reply(bot, list(conv.messages))
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    assistant_msg = Message(role="assistant", content=reply_text)
    conv.messages.append(assistant_msg)

    # Best-effort: set a title once, after the first exchange.
    if not conv.title:
        conv.title = await discovery.generate_title(list(conv.messages))

    await db.commit()
    await db.refresh(assistant_msg)
    return schemas.ChatResponse(message=schemas.MessageOut.model_validate(assistant_msg))


@app.post(
    "/api/conversations/{conversation_id}/summary",
    response_model=schemas.RequirementOut,
)
async def create_summary(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Requirement:
    conv = await _get_conversation(conversation_id, db)
    bot = load_bot_config()

    has_user_msg = any(m.role == "user" for m in conv.messages)
    if not has_user_msg:
        raise HTTPException(
            status_code=400,
            detail="Not enough conversation yet to generate requirements.",
        )

    try:
        summary_md = await discovery.generate_summary(bot, list(conv.messages))
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    req = Requirement(conversation_id=conv.id, content_markdown=summary_md)
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


@app.get(
    "/api/conversations/{conversation_id}/summary",
    response_model=schemas.RequirementOut,
)
async def get_latest_summary(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Requirement:
    await _get_conversation(conversation_id, db)  # 404 if missing
    result = await db.execute(
        select(Requirement)
        .where(Requirement.conversation_id == conversation_id)
        .order_by(Requirement.created_at.desc())
        .limit(1)
    )
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="No summary generated yet")
    return req
