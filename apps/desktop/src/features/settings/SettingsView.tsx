import { useEffect, useState, type ReactNode } from "react";
import { Check } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { usePersona, PERSONA_MODES } from "@/state/PersonaStore";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { ModelInfo } from "@/lib/types";

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
  const { mode, setMode } = usePersona();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [theme, setTheme] = useState<"dark" | "midnight">("dark");

  useEffect(() => {
    void api.getModels().then((m) => {
      setModels(m);
      setSelectedModel((cur) => cur || m[0]?.id || "");
    });
  }, []);

  return (
    <PageContainer title="Settings" subtitle="Shape how Miori shows up for you.">
      <div className="space-y-5">
        {/* Persona mode */}
        <SettingRow
          title="Persona mode"
          description="How warm vs. focused Miori feels in conversation."
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

        {/* Model select */}
        <SettingRow
          title="Model"
          description="Local models keep everything on-device; remote models are more capable."
        >
          <div className="space-y-2">
            {models.map((m) => (
              <button
                key={m.id}
                onClick={() => setSelectedModel(m.id)}
                className={cn(
                  "flex w-full items-center justify-between rounded px-4 py-2.5 text-left transition-colors",
                  selectedModel === m.id
                    ? "border border-accent/40 bg-accent/10"
                    : "border border-white/[0.06] hover:bg-white/[0.04]",
                )}
              >
                <span>
                  <span className="block text-sm text-ink">{m.label}</span>
                  <span className="block text-xs text-ink-faint">
                    {m.provider} · {(m.contextTokens / 1000).toFixed(0)}k ctx
                    {m.local ? " · local" : ""}
                  </span>
                </span>
                {selectedModel === m.id && <Check size={16} className="text-accent" />}
              </button>
            ))}
          </div>
        </SettingRow>

        {/* Theme */}
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
