# 📓 Dia 3 — Streaming no Agente (LangGraph)

> **Data:** 04/07/2026
> **Branch:** `feat/agent-streaming`

---

## 🎯 O que foi feito

Implementação de streaming token a token no endpoint do agente, usando o suporte nativo do LangGraph (`stream_mode="messages"`).

### Arquivos modificados

| Arquivo | O que mudou |
|---------|-------------|
| `app/agents/agent.py` | Nova função `run_agent_stream()` — generator assíncrono que streama tokens, tool_calls e tool_results |
| `app/api/routes.py` | Novo endpoint `POST /agent/stream` com SSE |
| `docs/dia-3-streaming-agente.md` | Este arquivo |

### Novos endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/agent/stream` | Agente com resposta em streaming (SSE) |

---

## 🔧 Como funciona

### `run_agent_stream(message, thread_id)`
Função assíncrona que usa `graph.astream(stream_mode="messages")` para capturar eventos em tempo real:

1. **Tokens de texto** → evento `{"type": "token", "content": "..."}`
2. **Chamadas de ferramenta** → evento `{"type": "tool_call", "name": "...", "args": "..."}`
3. **Resultados de ferramentas** → evento `{"type": "tool_result", "name": "...", "content": "..."}`
4. **Finalização** → evento `{"type": "done"}`

### Formato SSE
```
data: {"type": "token", "content": "Olá"}

data: {"type": "tool_call", "name": "search_documents", "args": "{\"query\": \"...\"}"}

data: {"type": "tool_result", "name": "search_documents", "content": "Resposta: ..."}

data: {"type": "token", "content": "Com base nos documentos..."}

data: {"type": "done"}
```

---

## 🧪 Como testar

```bash
curl -N -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "O que dizem os documentos?", "thread_id": "teste1"}'
```

---

## 📊 Status do projeto após Dia 3

| Módulo | Status |
|--------|--------|
| RAG base (ask, upload, clear) | ✅ |
| Streaming RAG (/ask/stream) | ✅ |
| Agente LangGraph | ✅ |
| **Streaming Agente (/agent/stream)** | **✅ NOVO** |
| MCP Server | ✅ |

## 🗂️ Rotas da API (total: 7)

```
POST /ask           → RAG normal
POST /ask/stream    → RAG com streaming
POST /upload        → Upload de documento
DELETE /clear       → Limpar banco vetorial
POST /agent         → Agente normal
POST /agent/stream  → Agente com streaming  ✨
GET  /health        → Health check
```
