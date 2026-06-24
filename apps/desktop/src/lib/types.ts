/**
 * Shared local types for the Miori Core desktop shell.
 * These mirror the eventual FastAPI contracts but stay frontend-owned for v0.1.
 */

/** Miori's live presence — drives the orb + status badge. */
export type PresenceState = "idle" | "listening" | "thinking" | "speaking";

/** Backend / device reachability. */
export type ConnectionStatus = "connected" | "connecting" | "offline";

/** Persona "mood" — how warm vs. focused Miori feels. */
export type PersonaMode = "warm" | "focused" | "playful" | "quiet";

/** Chat roles. */
export type Role = "user" | "miori" | "system";

export interface Attachment {
  id: string;
  name: string;
  size: number;
  kind: "image" | "audio" | "doc" | "other";
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  createdAt: number;
  /** True while a miori message is still streaming in. */
  streaming?: boolean;
  attachments?: Attachment[];
}

export interface ModelInfo {
  id: string;
  label: string;
  provider: string;
  contextTokens: number;
  local: boolean;
}

export interface ToolInfo {
  id: string;
  name: string;
  active: boolean;
  description: string;
}

export interface MemoryHit {
  id: string;
  snippet: string;
  source: string;
  score: number;
  recalledAt: number;
}

export interface DeviceStatus {
  id: string;
  name: string;
  platform: "windows" | "linux" | "macos" | "web";
  online: boolean;
  lastSeen: number;
  cpu?: number;
  battery?: number;
}

export interface FileItem {
  id: string;
  name: string;
  size: number;
  kind: Attachment["kind"];
  uploadedAt: number;
}

export interface TaskItem {
  id: string;
  title: string;
  done: boolean;
  createdAt: number;
}

export interface MemoryEntry {
  id: string;
  title: string;
  body: string;
  tags: string[];
  pinned: boolean;
  updatedAt: number;
}

/** Right-panel aggregate context, all cleanly typed. */
export interface ContextSnapshot {
  model: ModelInfo;
  tools: ToolInfo[];
  recentMemory: MemoryHit[];
  devices: DeviceStatus[];
  persona: PersonaMode;
}
