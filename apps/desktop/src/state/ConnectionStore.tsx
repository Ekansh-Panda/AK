import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { ConnectionStatus, ContextSnapshot } from "@/lib/types";
import { api } from "@/lib/api";
import { mockContext } from "@/lib/mockData";

interface ConnectionContextValue {
  status: ConnectionStatus;
  /** Aggregate right-panel context (model, tools, memory hits, devices, persona). */
  context: ContextSnapshot;
  refresh: () => void;
}

const ConnectionContext = createContext<ConnectionContextValue | null>(null);

export function ConnectionProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [context, setContext] = useState<ContextSnapshot>(mockContext);

  const refresh = useMemo(
    () => () => {
      setStatus("connecting");
      void api.health().then((ok) => setStatus(ok ? "connected" : "offline"));
      void api.getContext().then(setContext);
    },
    [],
  );

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 30_000);
    return () => clearInterval(id);
  }, [refresh]);

  const value = useMemo<ConnectionContextValue>(
    () => ({ status, context, refresh }),
    [status, context, refresh],
  );

  return (
    <ConnectionContext.Provider value={value}>{children}</ConnectionContext.Provider>
  );
}

export function useConnection(): ConnectionContextValue {
  const ctx = useContext(ConnectionContext);
  if (!ctx) throw new Error("useConnection must be used within ConnectionProvider");
  return ctx;
}
