/**
 * Typed API client for the Miori host.
 *
 * ┌──────────────────────────────────────────────────────────────────────────┐
 * │ STATUS: MOCKED. Every method below returns fabricated data so the phone    │
 * │ dashboard is fully usable before the backend `remote` module exists.       │
 * │                                                                            │
 * │ When the core-api lands, flip `USE_MOCK` to false (or drive it from an env │
 * │ flag) and the real fetch/WebSocket paths take over. The real endpoints are │
 * │ documented inline as TODOs against each method.                            │
 * │                                                                            │
 * │ Backend module:  services/core-api/app/services/remote                     │
 * │ REST base:       {host}/api/remote                                          │
 * │ Chat REST:       {host}/api/chat                                            │
 * │ WS stream:       {host}/ws/remote                                           │
 * └──────────────────────────────────────────────────────────────────────────┘
 */
import type {
  Connection,
  ConnectResult,
  DeviceStatus,
  PowerState,
  UploadProgress,
  UploadResult,
} from "./types";
import {
  MOCK_HOST_NAME,
  MOCK_VERSION,
  delay,
  getMockPower,
  makeMockDeviceStatus,
  mockReplyFor,
  setMockPower,
} from "./mock";

/** Master switch. Until the backend is wired, this stays true. */
const USE_MOCK = true;

/** Build a fully-qualified URL against the connected host. */
function url(conn: Connection, path: string): string {
  const base = conn.host.replace(/\/+$/, "");
  return `${base}${path}`;
}

/** Standard auth headers for the host's bearer/pairing token. */
function authHeaders(conn: Connection): HeadersInit {
  return {
    Authorization: `Bearer ${conn.token}`,
    "X-Miori-Remote": "1",
  };
}

/* ------------------------------------------------------------------ connect */

/**
 * Connect / pair with a host.
 *
 * TODO(remote-backend): replace mock with
 *   GET {host}/api/remote/ping  (Authorization: Bearer <token>)
 *   → { ok, hostName, version }
 */
export async function connect(conn: Connection): Promise<ConnectResult> {
  if (USE_MOCK) {
    await delay(700, 500);
    if (!conn.host.trim()) {
      return { ok: false, error: "Enter the host address." };
    }
    if (!conn.token.trim()) {
      return { ok: false, error: "A pairing token is required." };
    }
    // Pretend any non-empty token works, except an obvious "bad" one for demoing.
    if (conn.token.trim().toLowerCase() === "wrong") {
      return { ok: false, error: "Host rejected the token." };
    }
    return { ok: true, hostName: MOCK_HOST_NAME, version: MOCK_VERSION };
  }

  // --- real path (disabled until backend lands) ---
  try {
    const res = await fetch(url(conn, "/api/remote/ping"), {
      headers: authHeaders(conn),
    });
    if (!res.ok) {
      return { ok: false, error: `Host responded ${res.status}` };
    }
    const data = (await res.json()) as { hostName?: string; version?: string };
    return { ok: true, hostName: data.hostName, version: data.version };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : "Could not reach host.",
    };
  }
}

/* --------------------------------------------------------------- sendMessage */

/**
 * Send a chat message and stream Miori's reply.
 *
 * The mock emits the reply token-by-token via `onChunk` to exercise the
 * streaming UI. `onChunk` receives incremental text deltas; the returned
 * promise resolves with the full text once the stream completes.
 *
 * TODO(remote-backend): replace mock with a WebSocket to {host}/ws/remote
 *   (or POST {host}/api/chat with a streamed response). Forward each token to
 *   `onChunk`. Honor `signal` for cancellation.
 */
export async function sendMessage(
  conn: Connection,
  text: string,
  onChunk: (delta: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  if (USE_MOCK) {
    void conn;
    const reply = mockReplyFor(text);
    const words = reply.split(" ");
    let acc = "";
    await delay(380, 220); // "thinking" pause
    for (const word of words) {
      if (signal?.aborted) break;
      const piece = (acc ? " " : "") + word;
      acc += piece;
      onChunk(piece);
      await delay(38, 60);
    }
    return acc;
  }

  // --- real path (disabled until backend lands) ---
  // Prefer WS {host}/ws/remote for low-latency token streaming; falls back to
  // a fetch stream against {host}/api/chat. Left intentionally unimplemented.
  throw new Error("Real chat transport not implemented yet.");
}

/* ----------------------------------------------------------- getDeviceStatus */

/**
 * Fetch the host's current vitals.
 *
 * TODO(remote-backend): replace mock with
 *   GET {host}/api/remote/status → DeviceStatus (set isMock=false server-side)
 */
export async function getDeviceStatus(conn: Connection): Promise<DeviceStatus> {
  if (USE_MOCK) {
    void conn;
    await delay(250, 200);
    return makeMockDeviceStatus();
  }

  const res = await fetch(url(conn, "/api/remote/status"), {
    headers: authHeaders(conn),
  });
  return (await res.json()) as DeviceStatus;
}

/* -------------------------------------------------------------- setPowerState */

/**
 * Wake or sleep the host assistant.
 *
 * TODO(remote-backend): replace mock with
 *   POST {host}/api/remote/power  body: { state: "awake" | "sleeping" }
 *   → { state }
 */
export async function setPowerState(
  conn: Connection,
  state: PowerState,
): Promise<PowerState> {
  if (USE_MOCK) {
    void conn;
    await delay(900, 400); // host takes a beat to change state
    return setMockPower(state);
  }

  const res = await fetch(url(conn, "/api/remote/power"), {
    method: "POST",
    headers: { ...authHeaders(conn), "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
  const data = (await res.json()) as { state: PowerState };
  return data.state;
}

/** Read the current mocked power state without hitting the (mock) network. */
export function currentPowerState(): PowerState {
  return getMockPower();
}

/* ----------------------------------------------------------------- uploadFile */

/**
 * Upload a file from the phone to the host.
 *
 * The mock animates progress to 100% so the progress UI is exercised; nothing
 * leaves the device.
 *
 * TODO(remote-backend): replace mock with a real upload to
 *   POST {host}/api/remote/upload  (multipart/form-data, field "file")
 *   Use XMLHttpRequest (or fetch + ReadableStream) to report real progress to
 *   `onProgress`. Honor `signal` for cancellation.
 */
export async function uploadFile(
  conn: Connection,
  file: File,
  onProgress: (p: UploadProgress) => void,
  signal?: AbortSignal,
): Promise<UploadResult> {
  if (USE_MOCK) {
    void conn;
    const total = file.size || 1;
    const steps = 24;
    for (let i = 1; i <= steps; i++) {
      if (signal?.aborted) {
        return { ok: false, name: file.name, sizeBytes: file.size, error: "Cancelled." };
      }
      const percent = Math.round((i / steps) * 100);
      onProgress({
        percent,
        loadedBytes: Math.round((percent / 100) * total),
        totalBytes: total,
      });
      await delay(70, 90);
    }
    return {
      ok: true,
      fileId: `mock_${Date.now().toString(36)}`,
      name: file.name,
      sizeBytes: file.size,
    };
  }

  // --- real path (disabled until backend lands) ---
  return new Promise<UploadResult>((resolve) => {
    const form = new FormData();
    form.append("file", file);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url(conn, "/api/remote/upload"));
    xhr.setRequestHeader("Authorization", `Bearer ${conn.token}`);
    xhr.upload.onprogress = (e) => {
      if (!e.lengthComputable) return;
      onProgress({
        percent: Math.round((e.loaded / e.total) * 100),
        loadedBytes: e.loaded,
        totalBytes: e.total,
      });
    };
    xhr.onload = () =>
      resolve({ ok: xhr.status < 300, name: file.name, sizeBytes: file.size });
    xhr.onerror = () =>
      resolve({ ok: false, name: file.name, sizeBytes: file.size, error: "Upload failed." });
    signal?.addEventListener("abort", () => xhr.abort());
    xhr.send(form);
  });
}
