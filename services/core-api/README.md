# Miori Core API

The backend service for **Miori Core** — a cross-platform personal AI
workstation and desktop companion. This is a v0.1 skeleton: it boots fully
offline (chat runs through a mock provider), uses SQLite by default, and keeps
all heavy features optional and lazy-loaded.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2 / pydantic-settings
- SQLAlchemy 2.x (SQLite default)
- WebSockets for streaming chat + status + remote

## Quick start

```bash
cd services/core-api

# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (optional) configure
cp .env.example .env

# 4. Run the API
uvicorn app.main:app --reload
```

The API starts on `http://127.0.0.1:8000`. Interactive docs at `/docs`.
On first boot it creates `miori.db` and the `data/uploads/` directory.

## Architecture

```
app/
  main.py            FastAPI app factory, CORS, router wiring, lifespan (DB init)
  core/              config (Pydantic Settings) + logging
  db/                DeclarativeBase, engine, SessionLocal, get_db, init_db
  models/            SQLAlchemy models (UUID ids, timestamps)
  schemas/           Pydantic v2 schemas (from_attributes)
  services/          business logic, all behind clean interfaces
    chat_service.py  orchestrates persona + provider + persistence
    memory/          MemoryProvider ABC + SQLite lite impl + MemoryService
    tools/           Tool ABC + ToolRegistry + example tools (echo/time)
    providers/       ModelProvider ABC + ProviderRegistry + offline MockProvider
    persona/         PersonaService (modes, prompt profiles) + PersonaConfig
    remote/          RemoteSessionService (device registry, sessions)
    tasks/           TaskService (CRUD + scheduler hook stub)
    files/           FileIngestionService (upload + metadata)
  routers/           one router per domain, mounted under /api
  ws/                ConnectionManager + chat/status/remote WebSocket endpoints
```

## REST endpoints (prefix `/api`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | service health (no prefix) |
| POST | `/api/chat` | single-turn chat (mock assistant reply) |
| POST | `/api/chat/sessions` | create a chat session |
| GET | `/api/chat/sessions/{id}/messages` | session history |
| POST | `/api/memory` | add a memory |
| POST | `/api/memory/search` | search memories |
| GET/DELETE | `/api/memory/{id}` | get / delete a memory |
| POST/GET | `/api/files` | upload / list files |
| GET/DELETE | `/api/files/{id}` | get / delete a file |
| GET | `/api/providers` | list providers |
| GET | `/api/providers/models` | list models |
| GET | `/api/persona` | active persona config + prompt |
| GET | `/api/persona/modes` | list persona modes |
| POST | `/api/persona/mode` | switch mode (friend/operator/researcher/coder) |
| POST/GET | `/api/tasks` | create / list tasks |
| GET/PATCH/DELETE | `/api/tasks/{id}` | task CRUD |
| POST/GET | `/api/remote/devices` | register / list devices |
| POST | `/api/remote/devices/{id}/wake` `/sleep` | device state |
| POST/GET | `/api/remote/...sessions` | remote sessions |
| GET/PUT/DELETE | `/api/settings` | key/value settings |

## WebSocket endpoints

| Path | Purpose |
| --- | --- |
| `/ws/chat` | token-by-token streaming chat (mock provider) |
| `/ws/status` | periodic heartbeat for the desktop/remote UIs |
| `/ws/remote` | remote dashboard echo stub |

`/ws/chat` protocol — send `{"message": "...", "session_id"?: "...", "persona_mode"?: "..."}`,
receive `{"type":"session"|"token"|"done", ...}` frames.

## Integration roadmap (donor repos)

- **Mark-XLVI** — real remote control transport + device pairing/auth (`services/remote`, `ws/remote`)
- **Odysseus** — real model providers and vector memory (`services/providers`, `services/memory`)
- **Khoj** — memory ingestion pipeline + task scheduling/APScheduler (`services/files`, `services/tasks`)
- **computer-use** — sandboxed screen/keyboard/file tools (`services/tools`)

These are marked with `TODO(...)` comments at the relevant integration points.

## Caveats

- The mock provider just echoes the user's last message; it is for wiring/UX, not real intelligence.
- Memory search is substring matching while `LITE_MODE=true`.
- Remote sessions are in-memory (lost on restart); devices persist in the DB.
- No auth yet — intended for local/dev use.
