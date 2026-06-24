import { useEffect, useState } from "react";
import { Pin } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { MemoryEntry } from "@/lib/types";

export function MemoryView() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    void api.getMemory().then(setEntries);
  }, []);

  const togglePin = (id: string) =>
    setEntries((prev) =>
      prev.map((e) => (e.id === id ? { ...e, pinned: !e.pinned } : e)),
    );

  const q = query.trim().toLowerCase();
  const filtered = entries.filter(
    (e) =>
      !q ||
      e.title.toLowerCase().includes(q) ||
      e.body.toLowerCase().includes(q) ||
      e.tags.some((t) => t.toLowerCase().includes(q)),
  );
  const sorted = [...filtered].sort(
    (a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt,
  );

  return (
    <PageContainer title="Memory" subtitle="What Miori remembers about you — and why.">
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search memory…"
        className="mb-6"
      />

      <div className="grid gap-3 sm:grid-cols-2">
        {sorted.map((e) => (
          <article key={e.id} className="glass-soft rounded p-4">
            <div className="mb-1 flex items-start justify-between gap-2">
              <h3 className="text-sm font-medium text-ink">{e.title}</h3>
              <button
                onClick={() => togglePin(e.id)}
                aria-label={e.pinned ? "Unpin" : "Pin"}
                className={cn(
                  "shrink-0 transition-colors",
                  e.pinned ? "text-accent" : "text-ink-faint hover:text-ink-soft",
                )}
              >
                <Pin size={14} className={cn(e.pinned && "fill-current")} />
              </button>
            </div>
            <p className="text-sm text-ink-soft leading-relaxed">{e.body}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {e.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-white/[0.05] px-2 py-0.5 text-[0.65rem] text-ink-faint"
                >
                  {t}
                </span>
              ))}
            </div>
          </article>
        ))}
        {sorted.length === 0 && (
          <p className="text-sm text-ink-faint">No matching memories.</p>
        )}
      </div>
    </PageContainer>
  );
}
