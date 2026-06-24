import {
  createContext,
  useCallback,
  useContext,
  useReducer,
  type ReactNode,
} from "react";
import type { ChatMessage, PresenceState } from "@/lib/types";
import { mockMessages, uid } from "@/lib/mockData";
import { streamChat } from "@/lib/ws";

interface ChatState {
  messages: ChatMessage[];
  presence: PresenceState;
}

type Action =
  | { type: "add"; message: ChatMessage }
  | { type: "appendChunk"; id: string; chunk: string }
  | { type: "finish"; id: string }
  | { type: "presence"; presence: PresenceState }
  | { type: "clear" };

function reducer(state: ChatState, action: Action): ChatState {
  switch (action.type) {
    case "add":
      return { ...state, messages: [...state.messages, action.message] };
    case "appendChunk":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.id ? { ...m, content: m.content + action.chunk } : m,
        ),
      };
    case "finish":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.id ? { ...m, streaming: false } : m,
        ),
      };
    case "presence":
      return { ...state, presence: action.presence };
    case "clear":
      return { ...state, messages: [] };
    default:
      return state;
  }
}

interface ChatContextValue extends ChatState {
  send: (content: string) => void;
  clear: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, {
    messages: mockMessages,
    presence: "idle",
  });

  const send = useCallback((content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    dispatch({
      type: "add",
      message: { id: uid("msg"), role: "user", content: trimmed, createdAt: Date.now() },
    });

    const replyId = uid("msg");
    dispatch({
      type: "add",
      message: {
        id: replyId,
        role: "miori",
        content: "",
        createdAt: Date.now(),
        streaming: true,
      },
    });
    dispatch({ type: "presence", presence: "thinking" });

    streamChat(trimmed, {
      onChunk: (chunk) => {
        dispatch({ type: "presence", presence: "speaking" });
        dispatch({ type: "appendChunk", id: replyId, chunk });
      },
      onDone: () => {
        dispatch({ type: "finish", id: replyId });
        dispatch({ type: "presence", presence: "idle" });
      },
      onError: () => {
        dispatch({ type: "finish", id: replyId });
        dispatch({ type: "presence", presence: "idle" });
      },
    });
  }, []);

  const clear = useCallback(() => dispatch({ type: "clear" }), []);

  return (
    <ChatContext.Provider value={{ ...state, send, clear }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
}
