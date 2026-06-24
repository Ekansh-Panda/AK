# Miori Core — Roadmap & Backlog

> The schedule of record for Miori Core. The **map** (capability → donor repo → module) lives in
> [docs/feature-matrix.md](docs/feature-matrix.md); this file is the **plan** (what gets built when,
> and what is mocked vs implemented).
>
> Related: [System Overview](docs/architecture/system-overview.md) · [Data Model](docs/architecture/data-model.md) · [API Surface](docs/architecture/api-surface.md) · [Visual Direction](docs/ui-spec/visual-inspirations.md) · [Overnight Build Plan](docs/overnight-plan/build-plan.md)

Guiding principle ([MISSION.md](MISSION.md)): **a working v0.1 foundation, not a finished AI.**
Miori must feel like a *friend, not a cockpit*, and stay usable on low-end machines.

---

## v0.1 — Tonight (Foundation / scaffold)

The scaffold delivers:

- [ ] Monorepo structure (`apps/`, `services/`, `packages/`)
- [ ] Desktop app shell — Tauri + React + TS + Tailwind + shadcn/ui (`apps/desktop/`)
- [ ] All 8 pages render: Chat, Files, Memory, Projects, Research, Tasks, Remote, Settings (`apps/desktop/src/features/*`)
- [ ] Layout shell + sidebar + status bar (`apps/desktop/src/components/layout/`)
- [ ] Presence orb stub (cheap CSS, no WebGL) (`apps/desktop/src/components/`)
- [ ] Remote dashboard shell (`apps/remote-dashboard/`)
- [ ] FastAPI app boots with REST `/api/*` + WS `/ws/*` registered (`services/core-api/`)
- [ ] SQLAlchemy models for all 8 tables + SQLite engine/session (`services/core-api/app/models/*`, `db/*`)
- [ ] Service-layer skeletons: memory, providers, tools, persona, remote, tasks, files (`services/core-api/app/services/*`)
- [ ] Persona system skeleton with `friend`/`operator`/`researcher`/`coder` modes + prompt profiles (`packages/prompts/`)
- [ ] Provider abstraction with lite `echo` default (`services/core-api/app/services/providers/`)
- [ ] Memory abstraction (SQLite text store, no embeddings) (`services/core-api/app/services/memory/`)
- [ ] Tool registry contract (`services/core-api/app/services/tools/`)
- [ ] Chat streaming over `/ws/chat` (echo), messages persisted (`services/core-api/app/ws/chat.py`)
- [ ] Status heartbeat over `/ws/status`
- [ ] `LITE_MODE` + `REMOTE_ENABLED` flags + `.env.example` (`services/core-api/app/core/config.py`)
- [ ] Shared design tokens + UI primitives (`packages/ui/`) + shared types (`packages/types/`)
- [ ] Repo analysis docs (`docs/repo-analysis/` — separate job)
- [ ] Integration feature matrix + architecture/UI/plan docs (`docs/`)
- [ ] README with run instructions for backend + both frontends

---

## v0.2 — Integration phase (wire real backends)

Flip the mocks into real behavior, one abstraction at a time.

- [ ] **Real model providers** behind the provider interface — OpenAI, Anthropic, Ollama, local (`services/core-api/app/services/providers/`)
  - [ ] Lazy-import each provider SDK (only when selected)
  - [ ] API-key config via `settings` table + `.env`
  - [ ] Real token streaming through `/ws/chat`
- [ ] **Memory retrieval** — upgrade from keyword to semantic recall (`services/core-api/app/services/memory/`)
  - [ ] Optional embedding provider (lazy, off in lite mode)
  - [ ] Optional vector index (no mandatory vector DB)
  - [ ] `recall()` wired into the chat orchestration loop
- [ ] **Remote transport** — real device pairing + relay (`services/core-api/app/services/remote/`, `ws/remote.py`)
  - [ ] Pairing secrets / auth tokens on `devices` (extend `models/device.py`)
  - [ ] Live presence over `/ws/remote`; dashboard reaches paired devices
- [ ] **File ingestion** — parse → chunk → index pipeline (`services/core-api/app/services/files/`)
  - [ ] Real `/api/files/{id}/ingest` (status `uploaded`→`ingesting`→`ingested`)
  - [ ] Searchable file content feeding memory/research
- [ ] **Persona depth** — mode-specific tuned prompts + memory-aware tone (`packages/prompts/`)
- [ ] **Status bus** — real event fan-out (provider health, task, device) over `/ws/status`
- [ ] **Presence orb** reactive to real chat/voice state

---

## v0.3 — Advanced automation

- [ ] **Computer-use** — sandboxed actions (screenshot/click/type/shell), safety gating, opt-in only (`services/core-api/app/services/tools/`, `ws/remote.py`)
- [ ] **Voice pipeline** — STT/TTS, push-to-talk, amplitude-reactive orb (`services/providers/` voice, `apps/desktop/src/features/chat/`)
- [ ] **Multi-agent orchestration** — agent loop + sub-agent delegation over the tool registry
- [ ] **Task scheduler** — APScheduler recurring/cron jobs; add `cron`/`next_run` to `models/task.py`
- [ ] **Projects & Research** pages graduate from placeholders to real workspaces
- [ ] **Packaging** — Tauri installers for Windows/Linux/macOS; backend bundling; first-run setup
- [ ] **3D presence orb** as an opt-in, setting-gated enhancement (still off by default for low-end)

---

## Low-end optimization rules (apply to every version)

- [ ] Heavy deps are **lazy-imported** inside the function that needs them — never at module load
- [ ] **SQLite is the default**; no external DB server required to run Miori
- [ ] **`LITE_MODE=True` by default** — app is fully usable with **zero API keys**
- [ ] **No mandatory vector DB** — semantic memory is an optional upgrade
- [ ] Feature flags (`LITE_MODE`, `REMOTE_ENABLED`, per-provider) gate all cost
- [ ] Frontends stay thin; no always-on 3D/animation in the baseline; respect `prefers-reduced-motion`
- [ ] Everything **degrades gracefully** — missing keys/prompts/remote never crash boot

---

## Mocked vs implemented (after tonight)

### Real / implemented after v0.1
- [x] Monorepo + desktop shell + remote dashboard shell
- [x] FastAPI app, REST + WS routes registered
- [x] SQLite + all 8 tables, CRUD **persistence** (sessions, messages, memories, files, tasks, settings, devices)
- [x] `GET /api/health`
- [x] Service-layer interfaces + lite default implementations
- [x] `LITE_MODE` / `REMOTE_ENABLED` config

### Mocked after v0.1 (wired, canned/echo — to be made real in v0.2)
- [ ] Chat streaming = **echo provider** (no real LLM yet) → v0.2
- [ ] Providers list = **`echo` only** → v0.2
- [ ] Memory search = **keyword/substring** (no embeddings) → v0.2
- [ ] Persona = **static friend-first prompt** (no mode tuning) → v0.2
- [ ] Remote = **mock device presence**, no real pairing/transport → v0.2
- [ ] Status bus = **heartbeat + canned events** → v0.2

### Deferred (interface/TODO only after v0.1)
- [ ] Real providers · semantic memory · file ingestion · real remote transport → v0.2
- [ ] Computer-use · voice · multi-agent · scheduler · packaging → v0.3
