/// Camada de comunicacao com o backend RAG.

const API_BASE = "/api/v1";

// ─── Tipos ──────────────────────────────────────────────────────────────────

export interface Source {
  content: string;
  metadata: Record<string, unknown>;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  vector_collections: string[];
}

export interface UploadResponse {
  message: string;
  documents_processed: number;
}

// ─── RAG: perguntas ─────────────────────────────────────────────────────────

export async function ask(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Erro ${res.status}: ${text}`);
  }
  return res.json();
}

export async function* askStream(question: string): AsyncGenerator<string> {
  const res = await fetch(`${API_BASE}/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Erro ${res.status}`);

  const reader = res.body?.getReader();
  if (!reader) throw new Error("Sem stream disponivel");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        const payload = trimmed.slice(6);
        if (payload === "[DONE]") return;
        try {
          const parsed = JSON.parse(payload);
          if (parsed.token) yield parsed.token;
        } catch {
          // ignora linhas mal formatadas
        }
      }
    }
  }
}

// ─── Agente ─────────────────────────────────────────────────────────────────

export interface AgentEvent {
  type: string;
  content: string;
  name?: string;
  args?: string;
}

export async function* agentStream(
  message: string,
  threadId?: string,
): AsyncGenerator<AgentEvent> {
  const body: Record<string, unknown> = { message };
  if (threadId) body.thread_id = threadId;

  const res = await fetch(`${API_BASE}/agent/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Erro ${res.status}`);

  const reader = res.body?.getReader();
  if (!reader) throw new Error("Sem stream disponivel");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        const payload = trimmed.slice(6);
        if (payload === "[DONE]") return;
        try {
          const parsed = JSON.parse(payload);
          yield {
            type: parsed.type ?? "token",
            content: parsed.token ?? parsed.content ?? "",
            name: parsed.name,
            args: parsed.args,
          };
        } catch {
          // ignora
        }
      }
    }
  }
}

// ─── Documentos ─────────────────────────────────────────────────────────────

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Erro ${res.status}: ${text}`);
  }
  return res.json();
}

export async function clearDocuments(): Promise<void> {
  const res = await fetch(`${API_BASE}/clear`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Erro ${res.status}`);
}

// ─── Health ─────────────────────────────────────────────────────────────────

export async function health(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}
