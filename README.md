# Discovery Assistant

A discovery chatbot that interviews stakeholders to draw out their requirements.
You (the admin) prepare the bot with domain context in a YAML config, then hand
it to an end user. The bot asks questions one at a time, brainstorms, digs into
their **current manual process**, and — on demand — produces a structured
**requirements document** the team can build from.

- **Backend:** FastAPI + PostgreSQL (async SQLAlchemy), Claude via **OpenRouter**
- **Frontend:** React (Vite)
- **Bot setup:** edit [`backend/discovery_config.yaml`](backend/discovery_config.yaml)

```
┌──────────────┐    POST /api/conversations/{id}/messages   ┌──────────────┐
│  React app   │ ─────────────────────────────────────────► │   FastAPI    │
│  (Vite)      │ ◄───────────  assistant reply  ───────────  │   backend    │
└──────────────┘                                             └──────┬───────┘
                                                  OpenRouter ◄───────┤
                                                  Postgres   ◄───────┘
```

## 1. Prerequisites

- Python 3.11+
- Node.js 18+
- A PostgreSQL database (use Docker — see below — or your own)
- An **OpenRouter API key**: https://openrouter.ai/keys

## 2. Configure the bot (the "context" step)

Open [`backend/discovery_config.yaml`](backend/discovery_config.yaml) and fill in
the `context`, `goals`, `focus_areas`, and `seed_questions` for your engagement.
This is what turns a generic interviewer into one that understands *your*
client's domain. The header `name`, `description`, and `welcome_message` show up
in the UI.

## 3. Run it

### Option A — Postgres in Docker, app locally (recommended for dev)

```bash
# 1. Start just Postgres
docker compose up -d db

# 2. Backend
cd backend
cp .env.example .env          # then put your OPENROUTER_API_KEY in .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                   # opens http://localhost:5173
```

Visit **http://localhost:5173**.

### Option B — Everything in Docker

```bash
export OPENROUTER_API_KEY=sk-or-...   # required
docker compose up --build             # starts Postgres + backend on :8000
# then run the frontend (Option A step 3), or serve a production build
```

## 4. Environment variables

Backend (`backend/.env`, see `.env.example`):

| Variable             | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `OPENROUTER_API_KEY` | **Required.** Your OpenRouter key.                   |
| `OPENROUTER_MODEL`   | Model slug, e.g. `anthropic/claude-sonnet-4.5`.      |
| `DATABASE_URL`       | async Postgres URL (`postgresql+asyncpg://…`).       |
| `DISCOVERY_CONFIG`   | Path to the bot YAML (default `discovery_config.yaml`).|
| `CORS_ORIGINS`       | Comma-separated allowed frontend origins.            |

## 5. API overview

| Method & path                              | Description                          |
| ------------------------------------------ | ------------------------------------ |
| `GET  /api/bot`                            | Bot name/description/welcome message |
| `POST /api/conversations`                  | Start a session (returns opening msg)|
| `POST /api/conversations/{id}/messages`    | Send a user message, get the reply   |
| `GET  /api/conversations/{id}`             | Full conversation history            |
| `POST /api/conversations/{id}/summary`     | Generate a requirements document     |
| `GET  /api/conversations/{id}/summary`     | Latest generated requirements        |
| `GET  /api/conversations`                  | List all sessions (admin view)       |

Interactive API docs are served at **http://localhost:8000/docs**.

## 6. How the discovery flow works

1. The admin's YAML is compiled into a **system prompt** (`BotConfig.system_prompt`)
   that tells the model its mission, the topics to cover, and how to interview.
2. Each turn, the full conversation history is replayed to Claude (via OpenRouter)
   so it asks the next, context-aware question.
3. **Generate requirements** replays the conversation with an analyst instruction,
   producing a structured Markdown spec that's stored in Postgres and can be
   copied or downloaded.
