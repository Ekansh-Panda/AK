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

## Phase 1 — Memory: Semantic Recall
**What changed:** 
- `SEMANTIC_MEMORY_ENABLED` config flag added.
- `MemoryProvider` base class `add` and `search` are now `async`.
- `SqliteMemoryProvider` implements `async` hooks for base operations.
- `EmbeddingMemoryProvider` rewritten to use `registry.get().embed()` dynamically, with fallback to substring search.
- `MemoryService.add/search/summarize_session` made async.
- Memory routers updated to await memory functions.
- `ChatService` async functions `_recall_context` and `_store_facts` hooked correctly into `respond()` and `stream_response()`.

**What's flag-gated:** Vector embeddings require `SEMANTIC_MEMORY_ENABLED=True`.
**What's still TODO:** Phases 2–10.

## Phase 2 — Files: Ingestion & RAG
**What changed:**
- Added `POST /api/files/{id}/ingest` endpoint to `routers/files.py`.
- Implemented `FileIngestionService.ingest` to split text into chunks and store in semantic memory under `file:{id}` namespace.
- Updated `ChatService._recall_context` to search `file:%` namespace and inject file chunks into the LLM context.
- Graceful 400 error if `SEMANTIC_MEMORY_ENABLED` is false.

**What's flag-gated:** File ingestion requires `SEMANTIC_MEMORY_ENABLED=True`.
**What's still TODO:** Phases 3–10.
**Resume point:** Start Phase 3 (Remote Presence: WebSocket & Pairing).
