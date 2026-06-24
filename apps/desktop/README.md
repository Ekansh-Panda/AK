# Miori Core — Desktop

The desktop companion shell for **Miori Core**, a personal AI friend +
workstation. Built with **Tauri v2 + React + TypeScript + Vite + TailwindCSS**.

Miori is designed to feel like a friend, not a servant — minimal, dark, glassy,
with a small "presence orb" that breathes with her state. See
[`UI_SPEC.md`](./UI_SPEC.md) for the full design system.

---

## Prerequisites

- **Node.js** 18+ and npm
- For the native desktop build only: **Rust** (stable) and the
  [Tauri v2 system prerequisites](https://v2.tauri.app/start/prerequisites/)
  for your OS (webview, build tools, etc.)

The Python FastAPI backend is **optional**. With no backend running, every data
call falls back to local mock data and chat streams a canned reply, so the whole
shell is usable offline.

---

## Install

```bash
cd apps/desktop
npm install
```

## Run — web (fastest, no Rust needed)

```bash
npm run dev
```

Opens the Vite dev server at `http://localhost:1420`. This renders the entire UI
in the browser using mocks.

## Run — native desktop (Tauri)

```bash
npm run tauri dev
```

This launches the Tauri window (1200×800, dark) and runs the Vite dev server
underneath. Requires the Rust/Tauri prerequisites above.

> First native build only: generate app icons once with
> `npm run tauri icon path/to/source-1024.png` (see `src-tauri/icons/README.md`).

## Build

```bash
npm run build        # typecheck + Vite production build (web bundle -> dist/)
npm run tauri build  # package the native desktop app
```

## Other scripts

```bash
npm run typecheck    # tsc --noEmit
npm run preview      # preview the built web bundle
```

---

## Connecting a backend (optional)

By default the app targets:

- HTTP API: `http://localhost:8000/api`
- Chat WebSocket: `ws://localhost:8000/ws/chat`

Override via env (Vite picks these up):

```bash
# apps/desktop/.env
VITE_MIORI_API=http://localhost:8000/api
VITE_MIORI_WS=ws://localhost:8000/ws/chat
```

When a call fails or times out (~2.5s), the app transparently uses mocks and the
status bar shows **"Offline · mocks."**

---

## Project structure

```
apps/desktop/
├── index.html
├── package.json
├── tailwind.config.ts        # dark theme tokens
├── tsconfig.json / tsconfig.node.json
├── vite.config.ts            # "@/" alias -> src/, dev port 1420
├── postcss.config.js
├── public/vite.svg
├── UI_SPEC.md                # design system
├── src-tauri/                # Tauri v2 host (Rust)
│   ├── Cargo.toml
│   ├── build.rs
│   ├── tauri.conf.json       # com.miori.core, 1200x800, dark
│   ├── capabilities/default.json
│   ├── icons/README.md
│   └── src/{main.rs, lib.rs}
└── src/
    ├── main.tsx              # entry + BrowserRouter
    ├── App.tsx               # providers + routes
    ├── index.css             # Tailwind + CSS variables + glass recipe
    ├── vite-env.d.ts
    ├── lib/                  # cn, types, api, ws, mockData
    ├── components/ui/        # Button, Card, GlassPanel, Input, Avatar, StatusBadge, ScrollArea
    ├── components/layout/    # AppShell, LeftRail, RightPanel, TopBar, Composer, PresenceOrb, PageContainer
    ├── features/             # one folder per page (chat, files, memory, projects, research, tasks, remote, settings)
    └── state/                # ChatStore, PersonaStore, ConnectionStore (context + useReducer)
```

---

## Pages

Chat · Files · Memory · Projects · Research · Tasks · Remote · Settings.
Projects and Research are intentional placeholders for v0.1.
