import { useState, useRef, useEffect } from "react";
import { postAPI, fetchAPI } from "../../api/client";

interface ToolCall {
  name: string;
  args: string;
  status: "running" | "done";
}

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCall[];
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

export function ProjectChatPanel({ projectId, uiContext }: { projectId: string; uiContext?: any }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadSessions = () => {
    fetchAPI<ChatSession[]>(`/api/projects/${projectId}/chat/sessions`)
      .then((data) => {
        if (data) setSessions(data);
      })
      .catch((e) => console.error("Failed to load chat sessions", e));
  };

  useEffect(() => {
    // Reset session and load sessions when project changes
    setSessionId(null);
    setMessages([]);
    loadSessions();
  }, [projectId]);

  useEffect(() => {
    if (sessionId) {
      fetchAPI<Message[]>(
        `/api/projects/${projectId}/chat/sessions/${sessionId}`,
      )
        .then((data) => {
          if (data) setMessages(data);
        })
        .catch((e) => console.error("Failed to load chat history", e));
    } else {
      setMessages([]);
    }
  }, [sessionId, projectId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage: Message = { role: "user", content: input.trim() };
    const newMessages = [
      ...messages,
      userMessage,
      { role: "assistant", content: "", toolCalls: [] },
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          session_id: sessionId,
          messages: [userMessage],
          context: uiContext,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No reader available");
      const decoder = new TextDecoder();

      let currentSessionId = sessionId;
      let assistantContent = "";
      let currentToolCalls: ToolCall[] = [];
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        // Keep the last partial line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            if (event.type === "content") {
              assistantContent += event.content;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].content = assistantContent;
                return updated;
              });
            } else if (event.type === "tool_call") {
              currentToolCalls = [
                ...currentToolCalls,
                { name: event.name, args: event.arguments, status: "running" },
              ];
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].toolCalls = currentToolCalls;
                return updated;
              });
            } else if (event.type === "tool_result") {
              if (currentToolCalls.length > 0) {
                const lastIdx = currentToolCalls.length - 1;
                const updatedTools = [...currentToolCalls];
                updatedTools[lastIdx] = {
                  ...updatedTools[lastIdx],
                  status: "done",
                };
                currentToolCalls = updatedTools;

                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1].toolCalls = currentToolCalls;
                  return updated;
                });
              }
            } else if (event.type === "done" && event.session_id) {
              if (!currentSessionId) {
                currentSessionId = event.session_id;
                setSessionId(currentSessionId);
                loadSessions();
              }
            } else if (event.type === "error") {
              assistantContent += `\n❌ Error: ${event.content}`;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].content = assistantContent;
                return updated;
              });
            }
          } catch (e) {
            console.error("Failed to parse line:", line, e);
          }
        }
      }
    } catch (e) {
      console.error("Chat error", e);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].content +=
          "\n❌ Error: Failed to connect to agent.";
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex flex-col h-full bg-[var(--surface)] border-2 border-[var(--border)] rounded-lg overflow-hidden"
      style={{ boxShadow: "4px 4px 0px rgba(0,0,0,1)" }}
    >
      <div
        className="p-3 border-b-2 border-[var(--border)] font-black text-sm uppercase tracking-wider flex flex-col gap-2"
        style={{ background: "var(--border)", color: "var(--bg)" }}
      >
        <div className="flex items-center justify-between">
          <span>Agent Chat</span>
          {loading && (
            <span className="text-[10px] animate-pulse">Thinking...</span>
          )}
        </div>
        <select
          className="text-xs p-1 rounded border-2 border-[var(--bg)] outline-none cursor-pointer"
          style={{ background: "var(--surface)", color: "var(--text)" }}
          value={sessionId || ""}
          onChange={(e) => setSessionId(e.target.value || null)}
        >
          <option value="">-- New Session --</option>
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              {s.title || "Untitled"} (
              {new Date(s.created_at).toLocaleDateString()})
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-[var(--bg)]">
        {messages.length === 0 && (
          <div
            className="text-center text-xs mt-10 font-bold"
            style={{ color: "var(--muted)" }}
          >
            Ask the agent to modify the project, generate scenes, or extract
            assets.
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`text-[10px] font-black uppercase`}
              style={{
                color: msg.role === "user" ? "var(--text)" : "var(--green)",
              }}
            >
              {msg.role}
            </div>
            <div
              className={`text-xs font-semibold p-3 rounded-md max-w-[90%] border-2 border-[var(--border)]`}
              style={{
                background:
                  msg.role === "user" ? "var(--surface)" : "var(--surface)",
                color: "var(--text)",
                boxShadow: "2px 2px 0px rgba(0,0,0,1)",
              }}
            >
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="mb-2 flex flex-col gap-1 border-b-2 border-dashed border-[var(--border)] pb-2">
                  {msg.toolCalls.map((tc, j) => (
                    <div
                      key={j}
                      className="text-[10px] font-mono flex items-center gap-2"
                    >
                      {tc.status === "running" ? (
                        <span className="animate-spin">⚙️</span>
                      ) : (
                        <span>✅</span>
                      )}
                      <span style={{ color: "var(--muted)" }}>{tc.name}</span>
                    </div>
                  ))}
                </div>
              )}
              {msg.content && (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
              {!msg.content && msg.role === "assistant" && loading && (
                <div
                  className="animate-pulse text-[10px]"
                  style={{ color: "var(--muted)" }}
                >
                  Thinking...
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 border-t-2 border-[var(--border)] flex gap-2 bg-[var(--surface)] items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Ask agent (/fk-list)..."
          className="nb-input flex-1 text-xs resize-none overflow-hidden"
          style={{ minHeight: "38px", maxHeight: "120px" }}
          rows={
            input.split("\n").length > 1
              ? Math.min(input.split("\n").length, 5)
              : 1
          }
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="nb-btn text-xs px-3 py-1 font-bold h-[38px]"
          style={{
            background:
              loading || !input.trim() ? "var(--muted)" : "var(--text)",
            color: "var(--bg)",
            borderColor: "var(--border)",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
