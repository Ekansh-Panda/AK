# Miori Core — API Surface

> The contract between the frontends (`apps/desktop`, `apps/remote-dashboard`) and the brain
> (`services/core-api`). Two transports: **REST `/api/*`** and **WebSocket `/ws/*`**.
>
> Status tags reflect v0.1 reality: most endpoints exist as **mock** (interface + canned/echo
> behavior); deeper intelligence is **planned**. The schedule to flip mock → real lives in
> [TASKS.md](../../TASKS.md).
>
> Related: [System Overview](system-overview.md) · [Data Model](data-model.md) · [Feature Matrix](../feature-matrix.md)

Conventions:
- Base URL defaults to `http://127.0.0.1:8000` (`core/config.py`).
- All bodies are JSON. IDs are string UUIDs.
- Routers live in `services/core-api/app/routers/`; WS handlers in `services/core-api/app/ws/`.
- **Status**: `mock` = wired, returns stub/echo data · `planned` = documented only.

---

## REST `/api`

### Health — `/api/health` · `routers/health.py`
| Method | Path | Notes | Status |
|---|---|---|---|
| GET | `/api/health` | Liveness + version + flags (`lite_mode`, `remote_enabled`). Used by status bar / dashboard handshake. | **mock → implemented** (real, trivial) |

### Chat — `/api/chat` · `routers/chat.py`
REST handles session CRUD + history; live streaming is on `/ws/chat`.
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/chat/sessions` | — | list of `ChatSession` | mock |
| POST | `/api/chat/sessions` | `{title?, persona_mode?}` | created `ChatSession` | mock |
| GET | `/api/chat/sessions/{id}/messages` | — | list of `Message` | mock |
| POST | `/api/chat/sessions/{id}/messages` | `{role, content}` | persisted `Message` (non-streaming fallback) | mock |
| DELETE | `/api/chat/sessions/{id}` | — | `{ok}` | mock |

### Memory — `/api/memory` · `routers/memory.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/memory` | `?namespace=` | list of `Memory` | mock |
| POST | `/api/memory` | `{namespace?, content, meta?}` | created `Memory` | mock |
| POST | `/api/memory/search` | `{query, k?}` | ranked memories (lite: text match) | mock |
| DELETE | `/api/memory/{id}` | — | `{ok}` | mock |

> Vector/semantic search is **planned** (Odysseus/Khoj); lite search is substring/keyword only.

### Files — `/api/files` · `routers/files.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/files` | — | list of `FileRecord` | mock |
| POST | `/api/files` | multipart upload | `FileRecord` (`status=uploaded`) | mock |
| POST | `/api/files/{id}/ingest` | — | `FileRecord` (`status=ingesting`→`ingested`) — **ingest is no-op tonight** | planned |
| GET | `/api/files/{id}` | — | `FileRecord` | mock |
| DELETE | `/api/files/{id}` | — | `{ok}` | mock |

### Providers — `/api/providers` · `routers/providers.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/providers` | — | available providers + configured state (lite: `echo`) | mock |
| GET | `/api/providers/models` | `?provider=` | model list | mock |
| POST | `/api/providers/select` | `{provider, model}` | persisted to `settings` | mock |

> Real OpenAI/Anthropic/Ollama/local providers are **planned**, lazy-imported per provider.

### Persona — `/api/persona` · `routers/persona.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/persona/modes` | — | `[friend, operator, researcher, coder]` + descriptions | mock |
| GET | `/api/persona` | — | active persona config | mock |
| POST | `/api/persona` | `{mode}` | updated persona | mock |

> Prompt profiles sourced from `packages/prompts/`; service degrades gracefully if the dir is missing.

### Remote — `/api/remote` · `routers/remote.py`
Gated by `REMOTE_ENABLED`.
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/remote/devices` | — | list of `Device` + presence | mock |
| POST | `/api/remote/pair` | `{name, platform}` | `Device` (`is_paired=true`) — **mock pairing, no real secret** | planned |
| POST | `/api/remote/devices/{id}/wake` | — | `{ok}` | planned |
| DELETE | `/api/remote/devices/{id}` | — | `{ok}` | mock |

### Tasks — `/api/tasks` · `routers/tasks.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/tasks` | `?status=` | list of `Task` | mock |
| POST | `/api/tasks` | `{title, description?, due_at?}` | created `Task` | mock |
| PATCH | `/api/tasks/{id}` | `{status?, title?, ...}` | updated `Task` | mock |
| DELETE | `/api/tasks/{id}` | — | `{ok}` | mock |

> Scheduling / recurring jobs (APScheduler) are **planned** for v0.3.

### Settings — `/api/settings` · `routers/settings.py`
| Method | Path | Request | Response | Status |
|---|---|---|---|---|
| GET | `/api/settings` | — | merged config flags + key/value `settings` | mock |
| PUT | `/api/settings/{key}` | `{value}` | updated `Setting` | mock |

---

## WebSocket `/ws`

All WS messages are JSON envelopes: `{ "type": "...", ... }`.

### `/ws/chat` · `ws/chat.py` — token streaming
- **Client → server:** `{type:"message", session_id, content}` · `{type:"cancel"}`
- **Server → client:** `{type:"token", delta}` (repeated) · `{type:"done", message_id}` · `{type:"error", detail}`
- Orchestrates persona → memory recall → provider stream → persist (see [chat data flow](system-overview.md#3-data-flow-for-a-chat-message)).
- **Status:** mock (echoes/canned tokens; real provider streaming planned).

### `/ws/status` · `ws/status.py` — live status bus
- **Server → client:** `{type:"heartbeat", ts}` · `{type:"provider", state}` · `{type:"task", id, status}` · `{type:"device", id, state}`
- Feeds the desktop status bar / presence-orb state and the dashboard.
- **Status:** mock (heartbeat + canned events; real event fan-out planned).

### `/ws/remote` · `ws/remote.py` — remote presence & control
- **Client → server:** `{type:"hello", device}` · `{type:"command", action, args}`
- **Server → client:** `{type:"presence", devices}` · `{type:"ack", id}` · `{type:"frame", ...}` (computer-use, P2)
- Gated by `REMOTE_ENABLED`.
- **Status:** mock presence; real transport + pairing + computer-use frames are **planned** (Mark-XLVI / computer-use repos).

---

## Implemented-as-mock vs planned (summary)

| Bucket | Endpoints |
|---|---|
| **Real tonight** | `/api/health`; session/message/memory/task/file/setting **persistence** (CRUD writes to SQLite) |
| **Mock (wired, canned/echo)** | `/ws/chat` streaming, `/ws/status` heartbeat, `/api/providers` (echo), `/api/persona`, `/api/remote/devices`, memory `search` |
| **Planned (interface/TODO only)** | real provider streaming, semantic/vector memory, file ingestion pipeline, real remote transport + pairing secrets, computer-use frames, task scheduler, voice |

The authoritative flip-list is [TASKS.md](../../TASKS.md); the capability→repo mapping is the [feature matrix](../feature-matrix.md).
