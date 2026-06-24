import type {
  ContextSnapshot,
  FileItem,
  MemoryEntry,
  ModelInfo,
  TaskItem,
} from "./types";
import {
  mockContext,
  mockFiles,
  mockMemoryEntries,
  mockModels,
  mockTasks,
} from "./mockData";

/**
 * Typed fetch client for the Miori FastAPI backend.
 *
 * The backend is OPTIONAL for v0.1: every call falls back to mock data when the
 * server is unreachable, so the shell is fully usable offline. Set
 * `VITE_MIORI_API` to override the base URL.
 */
const BASE =
  (import.meta.env.VITE_MIORI_API as string | undefined) ??
  "http://localhost:8000/api";

/** Short timeout so offline mode falls back fast instead of hanging the UI. */
const TIMEOUT_MS = 2500;

async function request<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } catch {
    // Offline / not-yet-built backend: serve mocks so the friend still shows up.
    return fallback;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  /**
   * Aggregate context for the right panel.
   *
   * TODO(core-api): there is no backend `/context` aggregate endpoint yet, so
   * this always falls back to `mockContext`. Wire a real endpoint (or compose
   * it client-side from providers/memory/persona) when the backend lands.
   */
  getContext: () => request<ContextSnapshot>("/context", mockContext),

  // Models live under the providers router: GET /api/providers/models.
  getModels: () => request<ModelInfo[]>("/providers/models", mockModels),

  getFiles: () => request<FileItem[]>("/files", mockFiles),

  getTasks: () => request<TaskItem[]>("/tasks", mockTasks),

  getMemory: () => request<MemoryEntry[]>("/memory", mockMemoryEntries),

  /** Liveness check used by the connection store. */
  async health(): Promise<boolean> {
    // Health lives at the server root (/health), not under the /api prefix that
    // BASE carries, so probe the origin directly.
    const healthUrl = BASE.replace(/\/api\/?$/, "") + "/health";
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    try {
      const res = await fetch(healthUrl, { signal: controller.signal });
      return res.ok;
    } catch {
      return false;
    } finally {
      clearTimeout(timer);
    }
  },
};

export const apiBaseUrl = BASE;
