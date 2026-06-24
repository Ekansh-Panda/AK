import { mockReply } from "./mockData";

/**
 * Chat websocket helper.
 *
 * When a real backend exists it connects to `ws://localhost:8000/ws/chat` and
 * streams token chunks. When it's unreachable (the v0.1 default) it falls back
 * to a local mock that "types" a canned reply chunk-by-chunk, so the streaming
 * UX is fully exercised with no server.
 */

const WS_URL =
  (import.meta.env.VITE_MIORI_WS as string | undefined) ??
  "ws://localhost:8000/ws/chat";

export interface ChatStreamHandlers {
  /** Called for each streamed token/chunk. */
  onChunk: (chunk: string) => void;
  /** Called once when the reply is complete. */
  onDone: () => void;
  onError?: (err: unknown) => void;
}

/** A handle you can call to abort an in-flight reply. */
export interface ChatStreamHandle {
  cancel: () => void;
}

/**
 * Send a prompt and stream the reply.
 * Tries a real websocket first; on failure, falls back to the local mock.
 */
export function streamChat(prompt: string, handlers: ChatStreamHandlers): ChatStreamHandle {
  let cancelled = false;

  // Attempt a real connection; gracefully degrade to mock on any issue.
  let socket: WebSocket | null = null;
  try {
    socket = new WebSocket(WS_URL);
  } catch {
    socket = null;
  }

  if (socket) {
    const ws = socket;
    let opened = false;

    const fallbackTimer = setTimeout(() => {
      if (!opened && !cancelled) {
        try {
          ws.close();
        } catch {
          /* noop */
        }
        runMock(prompt, handlers, () => cancelled);
      }
    }, 1500);

    ws.onopen = () => {
      opened = true;
      clearTimeout(fallbackTimer);
      // Backend (services/core-api/app/ws/chat.py) reads the user text from
      // `message`; `session_id`/`persona_mode` are optional pass-throughs.
      ws.send(JSON.stringify({ message: prompt }));
    };
    ws.onmessage = (ev) => {
      if (cancelled) return;
      try {
        // Frames sent by the backend, see ws/chat.py:
        //   {"type":"session","session_id":...}
        //   {"type":"token","token":...}
        //   {"type":"done","session_id":...}
        //   {"type":"error","detail":...}
        const data = JSON.parse(ev.data as string) as {
          type: "session" | "token" | "done" | "error";
          token?: string;
          session_id?: string;
          detail?: string;
        };
        if (data.type === "token" && data.token) handlers.onChunk(data.token);
        else if (data.type === "error") {
          handlers.onError?.(new Error(data.detail ?? "chat error"));
          ws.close();
        } else if (data.type === "done") {
          handlers.onDone();
          ws.close();
        }
        // "session" frames carry the session id; nothing to render for now.
      } catch (err) {
        handlers.onError?.(err);
      }
    };
    ws.onerror = () => {
      clearTimeout(fallbackTimer);
      if (!opened && !cancelled) {
        runMock(prompt, handlers, () => cancelled);
      }
    };

    return {
      cancel: () => {
        cancelled = true;
        clearTimeout(fallbackTimer);
        try {
          ws.close();
        } catch {
          /* noop */
        }
      },
    };
  }

  // No socket at all — pure mock path.
  runMock(prompt, handlers, () => cancelled);
  return {
    cancel: () => {
      cancelled = true;
    },
  };
}

/** Locally "type out" the mock reply chunk-by-chunk. */
function runMock(
  _prompt: string,
  handlers: ChatStreamHandlers,
  isCancelled: () => boolean,
): void {
  const words = mockReply.split(" ");
  let i = 0;
  const tick = () => {
    if (isCancelled()) return;
    if (i >= words.length) {
      handlers.onDone();
      return;
    }
    handlers.onChunk((i === 0 ? "" : " ") + words[i]);
    i += 1;
    setTimeout(tick, 45 + Math.random() * 55);
  };
  // Small "thinking" delay before the first token.
  setTimeout(tick, 320);
}

export const wsUrl = WS_URL;
