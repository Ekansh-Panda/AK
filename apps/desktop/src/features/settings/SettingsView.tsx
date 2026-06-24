import { useEffect, useState, type ReactNode } from "react";
import { Check } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { usePersona, PERSONA_MODES } from "@/state/PersonaStore";
import { useConnection } from "@/state/ConnectionStore";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { ApiProviderInfo, ApiProviderStatus } from "@/lib/types";

const LITE_MODE_KEY = "lite_mode";

function SettingRow({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className="glass-soft rounded-lg p-5">
      <div className="mb-4">
        <h3 className="text-sm font-medium text-ink">{title}</h3>
        <p className="mt-0.5 text-xs text-ink-faint">{description}</p>
      </div>
      {children}
    </section>
  );
}

export function SettingsView() {
  const { mode, setMode, backendModes, backendMode, setBackendMode, refreshPersona } =
    usePersona();
  const { refresh: refreshConnection } = useConnection();

  const [providers, setProviders] = useState<ApiProviderInfo[]>([]);
  const [statuses, setStatuses] = useState<ApiProviderStatus[]>([]);
  const [theme, setTheme] = useState<"dark" | "midnight">("dark");
  const [lite, setLite] = useState(false);

  const loadProviders = async () => {
    const [p, s] = await Promise.all([api.listProviders(), api.providerStatus()]);
    setProviders(p.data);
    setStatuses(s.data);
  };

  useEffect(() => {
    void loadProviders();
    void api.getSetting(LITE_MODE_KEY).then((r) => {
      if (r.ok && r.data) setLite(r.data.value === "true" || r.data.value === "1");
    });
  }, []);

  const statusFor = (name: string) => statuses.find((s) => s.name === name);

  const chooseProvider = async (name: string) => {
    const r = await api.setActiveProvider(name);
    if (r.ok) {
      await loadProviders();
      refreshConnection();
    }
  };

  const choosePersona = async (next: string) => {
    await setBackendMode(next);
    refreshPersona();
  };

  const toggleLite = async () => {
    const next = !lite;
    setLite(next);
    await api.putSetting(LITE_MODE_KEY, String(next));
  };

  return (
    <PageContainer title="Settings" subtitle="Shape how Miori shows up for you.">
      <div className="space-y-5">
        {/* Provider (active model backend) */}
        <SettingRow
          title="Model provider"
          description="The active provider chat uses. Configured providers have a valid key/endpoint."
        >
          <div className="space-y-2">
            {providers.map((p) => {
              const st = statusFor(p.name);
              const active = p.active || st?.active;
              const configured = p.configured || st?.configured;
              return (
                <button
                  key={p.name}
                  onClick={() => void chooseProvider(p.name)}
                  className={cn(
                    "flex w-full items-center justify-between rounded px-4 py-2.5 text-left transition-colors",
                    active
                      ? "border border-accent/40 bg-accent/10"
                      : "border border-white/[0.06] hover:bg-white/[0.04]",
                  )}
                >
                  <span>
                    <span className="block text-sm capitalize text-ink">{p.name}</span>
                    <span className="block text-xs text-ink-faint">
                      {configured ? "configured" : "not configured"}
                      {p.models.length > 0 && ` · ${p.models.length} models`}
                      {active ? " · active" : ""}
                    </span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span
                      className={cn(
                        "h-1.5 w-1.5 rounded-full",
                        configured ? "bg-positive" : "bg-ink-faint",
                      )}
                    />
                    {active && <Check size={16} className="text-accent" />}
                  </span>
                </button>
              );
            })}
            {providers.length === 0 && (
              <p className="text-xs text-ink-faint">
                No providers reported — backend unreachable.
              </p>
            )}
          </div>
        </SettingRow>

        {/* Persona mode (backend) */}
        <SettingRow
          title="Persona mode"
          description="The relationship mode the backend uses for replies."
        >
          {backendModes.length > 0 ? (
            <div className="grid gap-2 sm:grid-cols-2">
              {backendModes.map((m) => (
                <button
                  key={m}
                  onClick={() => void choosePersona(m)}
                  className={cn(
                    "flex items-center gap-3 rounded p-3 text-left capitalize transition-colors",
                    backendMode === m
                      ? "border border-accent/40 bg-accent/10"
                      : "border border-white/[0.06] hover:bg-white/[0.04]",
                  )}
                >
                  <span
                    className={cn(
                      "grid h-4 w-4 place-items-center rounded-full border",
                      backendMode === m
                        ? "border-accent bg-accent text-canvas"
                        : "border-white/20",
                    )}
                  >
                    {backendMode === m && <Check size={11} />}
                  </span>
                  <span className="text-sm text-ink">{m}</span>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-ink-faint">
              Persona modes unavailable — backend unreachable.
            </p>
          )}
        </SettingRow>

        {/* Local UI mood preset (orb / badge feel) */}
        <SettingRow
          title="Interface mood"
          description="How warm vs. focused the interface feels (local only)."
        >
          <div className="grid gap-2 sm:grid-cols-2">
            {PERSONA_MODES.map((p) => (
              <button
                key={p.mode}
                onClick={() => setMode(p.mode)}
                className={cn(
                  "flex items-start gap-3 rounded p-3 text-left transition-colors",
                  mode === p.mode
                    ? "border border-accent/40 bg-accent/10"
                    : "border border-white/[0.06] hover:bg-white/[0.04]",
                )}
              >
                <span
                  className={cn(
                    "mt-0.5 grid h-4 w-4 place-items-center rounded-full border",
                    mode === p.mode ? "border-accent bg-accent text-canvas" : "border-white/20",
                  )}
                >
                  {mode === p.mode && <Check size={11} />}
                </span>
                <span>
                  <span className="block text-sm text-ink">{p.label}</span>
                  <span className="block text-xs text-ink-faint">{p.blurb}</span>
                </span>
              </button>
            ))}
          </div>
        </SettingRow>

        {/* Lite mode (persisted via PUT /settings) */}
        <SettingRow
          title="Lite mode"
          description="Trim heavy features for low-power devices. Persisted to the backend."
        >
          <button
            onClick={() => void toggleLite()}
            className={cn(
              "flex w-full items-center justify-between rounded px-4 py-3 text-left transition-colors",
              lite ? "border border-accent/40 bg-accent/10" : "border border-white/[0.06]",
            )}
          >
            <span className="text-sm text-ink">{lite ? "Lite mode on" : "Lite mode off"}</span>
            <span
              className={cn(
                "relative h-5 w-9 rounded-full transition-colors",
                lite ? "bg-accent" : "bg-white/15",
              )}
            >
              <span
                className={cn(
                  "absolute top-0.5 h-4 w-4 rounded-full bg-canvas transition-all",
                  lite ? "left-[1.125rem]" : "left-0.5",
                )}
              />
            </span>
          </button>
        </SettingRow>

        {/* Theme (local) */}
        <SettingRow title="Theme" description="Miori is dark by design. Pick your shade of night.">
          <div className="flex gap-2">
            {(["dark", "midnight"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                className={cn(
                  "rounded px-4 py-2 text-sm capitalize transition-colors",
                  theme === t
                    ? "border border-accent/40 bg-accent/10 text-ink"
                    : "border border-white/[0.06] text-ink-soft hover:bg-white/[0.04]",
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </SettingRow>
      </div>
    </PageContainer>
  );
}
