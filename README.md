<div align="center">

# Miori Core

**A cross-platform personal AI friend, workstation, and remote desktop companion.**

_Warm. Sharp. Present. A friend, not a servant._

</div>

---

Miori Core is the foundation of Miori — a personal AI you actually live alongside:
a desktop companion you talk to, a workspace you think in, and a remote presence
you can reach from your phone. This repository is the **v0.1 foundation**: a clean,
modular monorepo with a buildable spine. The heavy intelligence (real model
providers, deep memory, computer-use, voice) is scaffolded behind clean interfaces
and lands in later phases — see [`TASKS.md`](./TASKS.md).

> **Status:** v0.1 foundation. Runs as a shell with mock data + a mock model
> provider so everything is demoable offline. Nothing here is a finished god-agent
> — it's the spine that makes the rest possible.

## What's in the box

```
miori-core/
├─ apps/
│  ├─ desktop/            # Tauri v2 + React + TS + Tailwind — the companion UI
│  └─ remote-dashboard/   # Mobile-first React web app — reach Miori from your phone
├─ services/
│  └─ core-api/           # FastAPI backend — chat, memory, providers, persona, remote…
├─ packages/
│  ├─ ui/                 # Shared design tokens
│  ├─ types/              # Shared TypeScript contracts (mirror of the API schemas)
│  ├─ prompts/            # Persona prompt packs (friend / operator / researcher / coder)
│  └─ config/            # Shared tsconfig + Tailwind preset (the Miori design tokens)
├─ integrations/          # Donor repos cloned here for analysis & selective harvesting
├─ docs/                  # Architecture, repo analyses, feature matrix, UI spec
├─ scripts/               # bootstrap.{sh,ps1}, run-dev.{sh,ps1}, analyze_repos.py
├─ MISSION.md             # The product north star
└─ TASKS.md               # Roadmap: v0.1 → v0.2 → v0.3
```

## Tech stack

| Layer | Choice |
| --- | --- |
| Desktop shell | Tauri v2 · React · TypeScript · Vite · TailwindCSS · Framer Motion |
| Remote dashboard | React · TypeScript · Vite · Tailwind (mobile-first) |
| Backend | Python 3.11+ · FastAPI · Uvicorn · Pydantic v2 |
| Data | SQLAlchemy 2.x · SQLite (default) |
| Realtime | WebSocket streaming (`/ws/chat`, `/ws/status`, `/ws/remote`) |
| Design | Minimal, dark, glassy, one warm accent — a presence, not a cockpit |

Built to stay usable on **low-end machines**: SQLite by default, a "lite mode"
that keeps heavy/optional dependencies (vector DB, embeddings) lazy and off.

## Quick start

Prerequisites: **Python 3.11+**, **Node 18+**, **pnpm**, and (for the native
desktop build) the [Tauri prerequisites](https://tauri.app/start/prerequisites/).
You can run the web UIs without the Tauri toolchain.

```bash
# 1) Install everything (creates the backend venv + installs frontend deps)
bash scripts/bootstrap.sh          # Windows: scripts\bootstrap.ps1

# 2) Run a piece (or all of them)
bash scripts/run-dev.sh api        # FastAPI on http://127.0.0.1:8000
bash scripts/run-dev.sh desktop    # Desktop (Vite) on http://localhost:5173
bash scripts/run-dev.sh remote     # Remote dashboard on http://localhost:5174
bash scripts/run-dev.sh all        # everything together
```

Then open the desktop UI at <http://localhost:5173>. The backend is optional —
the frontends fall back to mock data when it isn't running.

Per-component instructions:
- Backend — [`services/core-api/README.md`](./services/core-api/README.md)
- Desktop — [`apps/desktop/README.md`](./apps/desktop/README.md)
- Remote — [`apps/remote-dashboard/README.md`](./apps/remote-dashboard/README.md)

## Architecture at a glance

The desktop app and remote dashboard talk to `core-api` over REST (`/api/*`) and
WebSocket (`/ws/*`). The backend is organised around swappable service
abstractions so the spine stays stable while implementations grow:

`MemoryService` · `ProviderRegistry` · `ToolRegistry` · `PersonaService` ·
`RemoteSessionService` · `TaskService` · `FileIngestionService`

Full details: [`docs/architecture/system-overview.md`](./docs/architecture/system-overview.md).

## Documentation

| Doc | What it covers |
| --- | --- |
| [`MISSION.md`](./MISSION.md) | Product north star and constraints |
| [`docs/architecture/`](./docs/architecture/) | System overview, data model, API surface |
| [`docs/feature-matrix.md`](./docs/feature-matrix.md) | Capability → donor repo → destination module → priority |
| [`docs/repo-analysis/`](./docs/repo-analysis/) | Engineering analyses of donor repos |
| [`docs/ui-spec/`](./docs/ui-spec/) · [`apps/desktop/UI_SPEC.md`](./apps/desktop/UI_SPEC.md) | Visual language & design system |
| [`TASKS.md`](./TASKS.md) | Roadmap and backlog |

## Design principles

- **Friend, not servant.** Miori has warmth, taste, and a point of view.
- **Calm, not a cockpit.** Minimal, dark, glassy; subtle motion; generous space.
- **Low-end first.** Lazy-load heavy features; SQLite + lite mode by default.
- **Interfaces over fake complexity.** Where something isn't built yet, there's a
  clean interface and a `TODO`, not pretend logic.

## License

MIT © 2026 Cobalt — see [`LICENSE`](./LICENSE).
