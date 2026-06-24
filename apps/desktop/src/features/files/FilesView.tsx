import { useEffect, useState } from "react";
import { UploadCloud, FileText, Image as ImageIcon, Music, File as FileIcon } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { api } from "@/lib/api";
import { uid } from "@/lib/mockData";
import { cn } from "@/lib/cn";
import type { FileItem } from "@/lib/types";

const kindIcon = {
  doc: FileText,
  image: ImageIcon,
  audio: Music,
  other: FileIcon,
} as const;

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function inferKind(name: string): FileItem["kind"] {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  if (["png", "jpg", "jpeg", "gif", "webp", "svg"].includes(ext)) return "image";
  if (["mp3", "m4a", "wav", "ogg", "flac"].includes(ext)) return "audio";
  if (["pdf", "txt", "md", "doc", "docx"].includes(ext)) return "doc";
  return "other";
}

export function FilesView() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    void api.getFiles().then(setFiles);
  }, []);

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const next: FileItem[] = Array.from(list).map((f) => ({
      id: uid("file"),
      name: f.name,
      size: f.size,
      kind: inferKind(f.name),
      uploadedAt: Date.now(),
    }));
    setFiles((prev) => [...next, ...prev]);
  };

  return (
    <PageContainer title="Files" subtitle="Things you've shared with Miori.">
      {/* Dropzone */}
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
        className={cn(
          "mb-6 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed py-10 transition-colors",
          dragging
            ? "border-accent/60 bg-accent/5"
            : "border-white/[0.12] hover:border-white/20 hover:bg-white/[0.02]",
        )}
      >
        <UploadCloud size={24} className="text-accent" />
        <span className="text-sm text-ink-soft">Drop files here or click to upload</span>
        <span className="text-xs text-ink-faint">Stored locally for v0.1</span>
        <input
          type="file"
          multiple
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
        />
      </label>

      {/* List */}
      <ul className="space-y-2">
        {files.map((f) => {
          const Icon = kindIcon[f.kind];
          return (
            <li
              key={f.id}
              className="glass-soft flex items-center gap-3 rounded px-4 py-3"
            >
              <Icon size={18} className="text-ink-faint shrink-0" />
              <span className="min-w-0 flex-1 truncate text-sm text-ink">{f.name}</span>
              <span className="text-xs text-ink-faint">{formatSize(f.size)}</span>
            </li>
          );
        })}
        {files.length === 0 && (
          <li className="text-sm text-ink-faint">No files yet.</li>
        )}
      </ul>
    </PageContainer>
  );
}
