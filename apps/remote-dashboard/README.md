# Miori Core — Remote Dashboard

A mobile-first web app to reach the Miori host machine from your phone: chat
with Miori, watch the host's vitals, wake or sleep her, and send files over —
all from your pocket, over the local network.

It shares Miori Core's visual language with the desktop shell (near-black glass,
a single warm violet accent, calm motion). The remote is a friend in your
pocket, not a control panel.

> **Status:** UI shell with mocked data. Every backend call is stubbed in
> `src/lib/api.ts` and returns fabricated values so the app is fully explorable
> before the `core-api` `remote` module exists. Mocked surfaces are clearly
> labelled in the UI.

## Stack

React 18 · TypeScript · Vite 5 · Tailwind CSS 3 · react-router-dom 6 ·
lucide-react · clsx. No `shadcn` runtime dependency — the small component set
lives in `src/components`.

## Run it

From this folder (`apps/remote-dashboard`):

```bash
npm install      # first time only
npm run dev      # Vite dev server on 0.0.0.0:5174 (LAN-accessible)
```

Then, on your **phone on the same Wi-Fi**, open:

```
http://<your-computer-LAN-ip>:5174
```

(`vite.config.ts` sets `server.host = true`, so the dev server binds to all
interfaces. Find your LAN IP with `ipconfig` / `ifconfig` / `ip addr`.)

Other scripts:

```bash
npm run build      # type-check (tsc) then production build to dist/
npm run preview    # serve the production build, also LAN-bound on :5174
npm run typecheck  # tsc --noEmit
```

`base` is `"./"` so the built `dist/` can be served from any path — including
mounted behind the FastAPI core-api later (e.g. at `/remote`).

## Screens

| Tab          | File                              | What it does                                       |
| ------------ | --------------------------------- | -------------------------------------------------- |
| (Login)      | `src/screens/LoginScreen.tsx`     | Host address + token, "Connect" (mocked auth)      |
| Chat         | `src/screens/ChatScreen.tsx`      | Remote chat with mock token-by-token streaming     |
| Device       | `src/screens/DeviceScreen.tsx`    | CPU / memory / uptime / online — labelled **mock** |
| Power        | `src/screens/PowerScreen.tsx`     | Wake / Sleep toggle for the host assistant (mock)  |
| Files        | `src/screens/FilesScreen.tsx`     | File picker + progress UI (mock upload)            |
| Settings     | `src/screens/SettingsScreen.tsx`  | Host, token, theme, disconnect                     |

A persistent connection chip (`src/components/ConnectionChip.tsx`) lives in
every header, and a glassy bottom tab bar (`src/components/BottomNav.tsx`) is
safe-area aware for notch / home-indicator phones.

## How it connects to the backend (later)

All host I/O goes through the typed client in **`src/lib/api.ts`**. Today it
returns mocks; each method documents the real endpoint it will call. Flip the
`USE_MOCK` constant at the top of that file to `false` once the backend is live.

Target backend: **`services/core-api`**, module
`services/core-api/app/services/remote` (`REMOTE_ENABLED` flag already exists in
`app/core/config.py`).

| Client method        | Real endpoint (planned)                              |
| -------------------- | ---------------------------------------------------- |
| `connect`            | `GET  {host}/api/remote/ping`                        |
| `getDeviceStatus`    | `GET  {host}/api/remote/status`                      |
| `setPowerState`      | `POST {host}/api/remote/power`                       |
| `uploadFile`         | `POST {host}/api/remote/upload` (multipart)          |
| `sendMessage`        | `WS   {host}/ws/remote` (token stream), or `POST {host}/api/chat` |

Auth is sent as `Authorization: Bearer <token>` plus an `X-Miori-Remote: 1`
header. The host address and token are kept in `src/state/connection.tsx` and
persisted to `localStorage`.

## Security note (read this)

This dashboard is designed for **LAN-only** use — your phone and the Miori host
on the same trusted network.

- The pairing **token is stored in `localStorage`** in plain text. That's
  acceptable for a short-lived, single-purpose LAN pairing token, but do **not**
  reuse a long-lived or high-value secret here.
- There is **no transport encryption** assumed by default (`http://`). Do not
  expose the host directly to the public internet. If remote-over-WAN is ever
  needed, front it with a VPN / reverse proxy with TLS and proper auth — do not
  port-forward the raw core-api.
- The mocked auth in this build accepts any non-empty token (except the literal
  `wrong`, used to demo the error state). Real validation happens host-side once
  `/api/remote/ping` exists.

## Project layout

```
apps/remote-dashboard/
├─ index.html                 viewport-fit=cover, theme-color, PWA meta
├─ vite.config.ts             base "./", server.host true (LAN)
├─ tailwind.config.ts         shared Miori design tokens
├─ tsconfig*.json
├─ postcss.config.js
├─ public/favicon.svg
└─ src/
   ├─ main.tsx                Router + ConnectionProvider
   ├─ App.tsx                 Routes + auth guard + bottom-nav shell
   ├─ index.css               Tailwind + glass + safe-area utilities + tokens
   ├─ lib/
   │  ├─ api.ts               typed host client (mocked; documents real paths)
   │  ├─ types.ts             shared types
   │  ├─ mock.ts              fabricated data + helpers
   │  └─ cn.ts                class-name joiner
   ├─ state/
   │  ├─ connection.tsx       host/token/theme/status context (persisted)
   │  └─ chat.tsx             chat messages + mock streaming
   ├─ components/
   │  ├─ BottomNav.tsx
   │  ├─ ConnectionChip.tsx
   │  ├─ ScreenHeader.tsx
   │  ├─ GlassCard.tsx
   │  ├─ Button.tsx
   │  ├─ StatusDot.tsx
   │  └─ PresenceOrb.tsx
   └─ screens/
      ├─ LoginScreen.tsx
      ├─ ChatScreen.tsx
      ├─ DeviceScreen.tsx
      ├─ PowerScreen.tsx
      ├─ FilesScreen.tsx
      └─ SettingsScreen.tsx
```
