import { Laptop, Smartphone, Monitor, Wifi, WifiOff } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { useConnection } from "@/state/ConnectionStore";
import { connectionTone } from "@/components/ui/StatusBadge";
import { cn } from "@/lib/cn";
import type { DeviceStatus } from "@/lib/types";

const platformIcon = {
  windows: Monitor,
  linux: Monitor,
  macos: Laptop,
  web: Smartphone,
} as const;

function relativeTime(ts: number): string {
  const diff = Date.now() - ts;
  const min = Math.round(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  return `${hr}h ago`;
}

function DeviceCard({ d }: { d: DeviceStatus }) {
  const Icon = platformIcon[d.platform];
  return (
    <article className="glass-soft flex items-center gap-4 rounded-lg p-4">
      <div className="grid h-10 w-10 place-items-center rounded bg-white/[0.05]">
        <Icon size={20} className="text-ink-soft" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-ink">{d.name}</span>
          {d.online ? (
            <Wifi size={13} className="text-positive" />
          ) : (
            <WifiOff size={13} className="text-ink-faint" />
          )}
        </div>
        <div className="mt-0.5 text-xs text-ink-faint">
          {d.platform} · {d.online ? "online" : `seen ${relativeTime(d.lastSeen)}`}
          {typeof d.battery === "number" && ` · ${d.battery}% battery`}
          {typeof d.cpu === "number" && ` · ${d.cpu}% cpu`}
        </div>
      </div>
      <Button variant="subtle" size="sm" disabled={!d.online}>
        {d.online ? "Connect" : "Offline"}
      </Button>
    </article>
  );
}

export function RemoteView() {
  const { context, status, refresh } = useConnection();
  const conn = connectionTone(status);

  return (
    <PageContainer
      title="Remote"
      subtitle="Reach Miori from any of your devices."
      actions={
        <Button variant="subtle" size="sm" onClick={refresh}>
          Refresh
        </Button>
      }
    >
      <div className="glass-soft mb-6 flex items-center justify-between rounded-lg px-4 py-3">
        <span className="text-sm text-ink-soft">Backend link</span>
        <span className="inline-flex items-center gap-2 text-sm text-ink">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              conn.tone === "positive"
                ? "bg-positive"
                : conn.tone === "warn"
                  ? "bg-warn"
                  : "bg-ink-faint",
            )}
          />
          {conn.label}
        </span>
      </div>

      <div className="space-y-3">
        {context.devices.map((d) => (
          <DeviceCard key={d.id} d={d} />
        ))}
      </div>
    </PageContainer>
  );
}
