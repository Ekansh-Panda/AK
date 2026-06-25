# Jarvis Build Log

## Phase 0 — Audit
**What changed:** 
- Conducted full audit of `services/core-api/app/` code versus `api-surface.md`.
- Derived the true implementation status.

**Corrected API Surface Status Table:**

| Endpoint / Feature | Docs Status | Actual Code Status | Notes |
|---|---|---|---|
| `REST /api/chat/*` | mock | **REAL** | Full CRUD to SQLite via ChatService. |
| `REST /api/memory` | mock | **REAL** | Full CRUD implemented (SqliteMemoryProvider). |
| `REST /api/memory/search` | mock | **PARTIAL** | Substring search real; embeddings/vector search deferred. |
| `REST /api/files` | mock | **REAL** | Text/PDF extraction happens on upload and saves to DB. |
| `REST /api/files/{id}/ingest` | planned | **STUB** | Chunk/index pipeline deferred. |
| `REST /api/providers/*` | mock | **REAL** | Registry loads real SDKs (OpenAI, Gemini). Active selection persisted. |
| `REST /api/persona/*` | mock | **REAL** | Loads prompts from disk, fallback to built-ins. |
| `REST /api/remote/devices` | mock | **REAL** | CRUD implemented in RemoteSessionService. |
| `REST /api/remote/pair` | planned | **STUB** | Needs actual pairing secret logic. |
| `REST /api/remote/devices/{id}/wake` | planned | **STUB** | Needs WS relay. |
| `REST /api/tasks/*` | mock | **REAL** | Full CRUD to SQLite. |
| `REST /api/settings/*` | mock | **REAL** | SettingsService DB overrides active. |
| `WS /ws/chat` | mock | **REAL** | Fully streams tokens from active real provider. Memory recall hooks exist. |
| `WS /ws/status` | mock | **MOCK** | Heartbeat loop + canned events only. |
| `WS /ws/remote` | mock | **STUB** | In-memory session tracking, no real relay or computer-use yet. |

**What's flag-gated:** None
**What's still TODO:** Phases 1–10.
**Resume point:** Start Phase 1 (Memory: semantic recall).
