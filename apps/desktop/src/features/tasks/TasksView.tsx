import { useEffect, useState, type FormEvent } from "react";
import { Plus, Check } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { uid } from "@/lib/mockData";
import { cn } from "@/lib/cn";
import type { TaskItem } from "@/lib/types";

export function TasksView() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    void api.getTasks().then(setTasks);
  }, []);

  const add = (e: FormEvent) => {
    e.preventDefault();
    const title = draft.trim();
    if (!title) return;
    setTasks((prev) => [
      { id: uid("task"), title, done: false, createdAt: Date.now() },
      ...prev,
    ]);
    setDraft("");
  };

  const toggle = (id: string) =>
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t)));

  const open = tasks.filter((t) => !t.done);
  const done = tasks.filter((t) => t.done);

  return (
    <PageContainer title="Tasks" subtitle="Small things Miori is helping you track.">
      <form onSubmit={add} className="mb-6 flex gap-2">
        <Input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Add a task…"
        />
        <Button type="submit" variant="primary" size="icon" aria-label="Add task">
          <Plus size={18} />
        </Button>
      </form>

      <ul className="space-y-2">
        {[...open, ...done].map((t) => (
          <li
            key={t.id}
            className="glass-soft flex items-center gap-3 rounded px-4 py-3"
          >
            <button
              onClick={() => toggle(t.id)}
              aria-label={t.done ? "Mark not done" : "Mark done"}
              className={cn(
                "grid h-5 w-5 place-items-center rounded-sm border transition-colors",
                t.done
                  ? "border-accent bg-accent/80 text-canvas"
                  : "border-white/20 hover:border-accent/60",
              )}
            >
              {t.done && <Check size={13} />}
            </button>
            <span
              className={cn(
                "flex-1 text-sm",
                t.done ? "text-ink-faint line-through" : "text-ink",
              )}
            >
              {t.title}
            </span>
          </li>
        ))}
        {tasks.length === 0 && <li className="text-sm text-ink-faint">Nothing yet.</li>}
      </ul>
    </PageContainer>
  );
}
