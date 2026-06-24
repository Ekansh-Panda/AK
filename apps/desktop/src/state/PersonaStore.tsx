import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { PersonaMode } from "@/lib/types";

export interface PersonaDescriptor {
  mode: PersonaMode;
  label: string;
  blurb: string;
}

export const PERSONA_MODES: PersonaDescriptor[] = [
  { mode: "warm", label: "Warm", blurb: "Friendly, present, a little tender." },
  { mode: "focused", label: "Focused", blurb: "Direct and economical. Less small talk." },
  { mode: "playful", label: "Playful", blurb: "Light, teasing, quick-witted." },
  { mode: "quiet", label: "Quiet", blurb: "Minimal words. Only speaks when it helps." },
];

interface PersonaContextValue {
  mode: PersonaMode;
  setMode: (mode: PersonaMode) => void;
  descriptor: PersonaDescriptor;
}

const PersonaContext = createContext<PersonaContextValue | null>(null);

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<PersonaMode>("warm");

  const value = useMemo<PersonaContextValue>(() => {
    const descriptor =
      PERSONA_MODES.find((p) => p.mode === mode) ?? PERSONA_MODES[0];
    return { mode, setMode, descriptor };
  }, [mode]);

  return <PersonaContext.Provider value={value}>{children}</PersonaContext.Provider>;
}

export function usePersona(): PersonaContextValue {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error("usePersona must be used within PersonaProvider");
  return ctx;
}
