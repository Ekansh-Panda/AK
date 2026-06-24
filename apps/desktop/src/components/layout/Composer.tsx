import { useRef, useState, type KeyboardEvent } from "react";
import { Paperclip, Mic, ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Input";
import { cn } from "@/lib/cn";

export interface ComposerProps {
  onSend: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

/**
 * Bottom composer: attach + mic + a growing textarea + send.
 * Enter sends, Shift+Enter newlines. The mic is a UI placeholder for now.
 */
export function Composer({ onSend, placeholder = "Talk to Miori…", disabled }: ComposerProps) {
  const [value, setValue] = useState("");
  const [listening, setListening] = useState(false);
  const ref = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const v = value.trim();
    if (!v || disabled) return;
    onSend(v);
    setValue("");
    if (ref.current) ref.current.style.height = "auto";
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const autoGrow = () => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  };

  return (
    <div className="glass rounded-lg p-2">
      <div className="flex items-end gap-2">
        <Button
          variant="ghost"
          size="icon"
          title="Attach file"
          aria-label="Attach file"
          disabled={disabled}
        >
          <Paperclip size={18} />
        </Button>

        <Textarea
          ref={ref}
          rows={1}
          value={value}
          placeholder={placeholder}
          disabled={disabled}
          onChange={(e) => {
            setValue(e.target.value);
            autoGrow();
          }}
          onKeyDown={onKeyDown}
          className="min-h-[2.5rem] border-0 bg-transparent focus:bg-transparent"
        />

        <Button
          variant="ghost"
          size="icon"
          title={listening ? "Stop listening" : "Voice input"}
          aria-label="Voice input"
          disabled={disabled}
          onClick={() => setListening((v) => !v)}
          className={cn(listening && "text-accent")}
        >
          <Mic size={18} className={cn(listening && "animate-orb-pulse")} />
        </Button>

        <Button
          variant="primary"
          size="icon"
          title="Send"
          aria-label="Send message"
          disabled={disabled || !value.trim()}
          onClick={submit}
        >
          <ArrowUp size={18} />
        </Button>
      </div>
    </div>
  );
}
