import { useState, useRef, useEffect } from "react";
import { ask, askStream, agentStream, type Source } from "../services/api";

/** Remove duplicacao de texto consecutiva (modelo gaguejando).
 *  Ex: "Foo.Foo." → "Foo."  /  "Foo. Foo." → "Foo."  /  "ABCABC" → "ABC" */
function dedupText(text: string): string {
  for (let len = Math.floor(text.length / 2); len >= 10; len--) {
    const suffix = text.slice(-len);
    const before = text.slice(0, -len);
    // Ignora diferencas de espacos entre as duas metades
    const beforeTrimmed = before.replace(/\s+$/, '');
    const suffixTrimmed = suffix.replace(/^\s+/, '');
    if (beforeTrimmed.endsWith(suffixTrimmed)) {
      return beforeTrimmed + suffix.slice(0, suffix.length - suffixTrimmed.length);
    }
  }
  return text;
}

/** Remove JSON de chamada de ferramenta que o modelo vaza na resposta.
 *  Ex: `{"name": "search_documents", "parameters": {...}}` */
function stripToolJSON(text: string): string {
  const idx = text.search(/\{"name":\s*"/);
  if (idx === -1) return text;
  const end = text.lastIndexOf('}');
  if (end > idx) {
    return text.slice(0, idx) + text.slice(end + 1);
  }
  return text;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface ChatProps {
  mode: "rag" | "agent";
  threadId: string;
}

export default function Chat({ mode, threadId }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        mode === "rag"
          ? "Faça uma pergunta sobre seus documentos."
          : "Pergunte qualquer coisa — posso buscar nos documentos, calcular, pesquisar na web e mais.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState<number | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // Reseta quando troca de modo
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          mode === "rag"
            ? "Faça uma pergunta sobre seus documentos."
            : "Pergunte qualquer coisa — posso buscar nos documentos, calcular, pesquisar na web e mais.",
      },
    ]);
  }, [mode]);

  async function handleSend() {
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      if (mode === "rag") {
        // Tenta streaming primeiro, fallback pra resposta completa
        let streamed = false;
        try {
          for await (const token of askStream(q)) {
            streamed = true;
              setMessages((prev) => {
                const idx = prev.length - 1;
                const last = prev[idx];
                if (last.role === "assistant") {
                  const copy = [...prev];
                  copy[idx] = { ...last, content: last.content + token };
                  return copy;
                }
                return prev;
              });
          }
        } catch {
          // streaming falhou
        }

        if (!streamed) {
          const result = await ask(q);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.content = result.answer;
              last.sources = result.sources;
            }
            return [...updated];
          });
        }
      } else {
        // Agent mode: tool_calls e resultados sao invisiveis pro usuario
        try {
          let lastToken = "";
          for await (const event of agentStream(q, threadId)) {
            if (event.type === "token" && event.content) {
              // Evita duplicacao entre eventos (backend mandou 2x o mesmo token)
              if (event.content === lastToken) continue;
              lastToken = event.content;
              const cleaned = stripToolJSON(dedupText(event.content));
              setMessages((prev) => {
                const idx = prev.length - 1;
                const last = prev[idx];
                if (last.role === "assistant") {
                  // Cria novo objeto — imutavel, evita duplicacao do StrictMode
                  const copy = [...prev];
                  copy[idx] = { ...last, content: last.content + cleaned };
                  return copy;
                }
                return prev;
              });
            }
          }
        } catch {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.content += "\n[Erro ao conectar com o agente]";
            }
            return [...updated];
          });
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          last.content = `Erro: ${msg}`;
        }
        return [...updated];
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function toggleSources(idx: number) {
    setShowSources(showSources === idx ? null : idx);
  }

  return (
    <div className="chat-container">
      <div className="messages" ref={chatRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="avatar">
              {msg.role === "user" ? "U" : "AI"}
            </div>
            <div className="bubble">
              <div className="msg-content">
                {msg.content || (loading && i === messages.length - 1 ? (
                  <span className="typing">pensando</span>
                ) : null)}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <button
                    className="sources-toggle"
                    onClick={() => toggleSources(i)}
                  >
                    Fontes ({msg.sources.length}) {showSources === i ? "▲" : "▼"}
                  </button>
                  {showSources === i && (
                    <div className="sources-list">
                      {msg.sources.map((s, j) => (
                        <div key={j} className="source-item">
                          <p className="source-text">{s.content}</p>
                          {s.metadata?.source != null && (
                            <span className="source-file">
                              {String(s.metadata.source)}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="input-area">
        <textarea
          ref={inputRef}
          className="input-box"
          placeholder={
            mode === "rag"
              ? "Pergunte sobre seus documentos..."
              : "Pergunte qualquer coisa (docs, calculo, web)..."
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          className="btn btn-send"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}
