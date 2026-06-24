/**
 * Shared types for the Miori remote dashboard.
 *
 * These mirror the shapes the core-api `remote` module is expected to expose.
 * When the real backend lands, keep these aligned with the FastAPI schemas in
 * `services/core-api/app/schemas`.
 */

/** Where the dashboard points and how it authenticates. */
export interface Connection {
  /** Host address incl. scheme + port, e.g. "http://192.168.1.20:8000". */
  host: string;
  /** Bearer / pairing token issued by the host for this device. */
  token: string;
}

export type ConnectionStatus =
  | "disconnected"
  | "connecting"
  | "connected"
  | "error";

/** Result of attempting to connect/pair with a host. */
export interface ConnectResult {
  ok: boolean;
  /** Friendly host name reported back by the machine, if connected. */
  hostName?: string;
  /** Miori core version reported by the host. */
  version?: string;
  /** Present when ok === false. */
  error?: string;
}

export type ChatRole = "user" | "miori" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  /** Epoch ms. */
  at: number;
  /** True while a streamed reply is still arriving. */
  streaming?: boolean;
}

/** Snapshot of the host machine's vitals. All values are 0..100 where noted. */
export interface DeviceStatus {
  online: boolean;
  /** CPU load percentage, 0..100. */
  cpu: number;
  /** Memory used percentage, 0..100. */
  mem: number;
  /** Total RAM in GB (for labelling the mem bar). */
  memTotalGb: number;
  /** Seconds since the host process started. */
  uptimeSec: number;
  /** Current assistant power state. */
  power: PowerState;
  /** OS / platform label, e.g. "Linux", "macOS", "Windows". */
  platform: string;
  /** True when these numbers are fabricated (always true until backend lands). */
  isMock: boolean;
}

export type PowerState = "awake" | "sleeping";

/** Upload progress callback payload. */
export interface UploadProgress {
  /** 0..100. */
  percent: number;
  loadedBytes: number;
  totalBytes: number;
}

export interface UploadResult {
  ok: boolean;
  fileId?: string;
  name: string;
  sizeBytes: number;
  error?: string;
}

export type ThemeMode = "dark" | "dusk";
