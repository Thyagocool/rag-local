#  RAG + Agentes + MCP + LLMOps

**API completa de Engenharia de IA** com **RAG**, **Agentes Inteligentes** (LangGraph), **MCP Server** (stdio + SSE), **Frontend React** e **Observabilidade** — tudo rodando **100% local e grátis** com Ollama.

> Stack: **FastAPI + LangChain + LangGraph + ChromaDB + Ollama + MCP**  
> Frontend: **React 19 + Vite 8 + TypeScript 6**

---

##  Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
|  **RAG** | Upload de 15 formatos de documento, chunking inteligente (4 estratégias), reranking por relevância |
|  **Streaming SSE** | Respostas token a token tanto no RAG quanto no Agente |
|  **Agentes LangGraph** | Agente com 5 ferramentas (RAG, calculadora, web search, hora, auto-lista) e memória de conversa |
|  **MCP Server** | Protocolo MCP via **stdio** (Claude Desktop, Cline) e **SSE/HTTP** |
|  **Frontend React** | Interface moderna com streaming, upload, multi-threads e tema escuro |
|  **Observabilidade** | Tracing OpenTelemetry com exportação para Jaeger |
|  **Deploy** | Docker Compose produção com Nginx, limites de recursos e health checks |
|  **100% local** | LLM e embeddings rodando via Ollama — sem API paga, sem dados saindo da sua máquina |

---

##  Stack

```
Frontend (React + Vite)          Backend (FastAPI)
       │                              │
       │  POST /api/v1/*              │
       │◄─────────────────────────────│
       │                              │
       │   SSE (Server-Sent Events)   │
       │◄─────────────────────────────│
       │                              │
       │                    ┌─────────┴─────────┐
       │                    │                   │
       │               ┌────┴────┐        ┌────┴────┐
       │               │ Ollama  │        │ChromaDB │
       │               │(LLM +   │        │(Vector  │
       │               │Embdds)  │        │ Store)  │
       │               └─────────┘        └─────────┘
```

---

##  ⚡ Início Rápido

### Opção 1 — Docker (recomendado)

```bash
cd backend
docker compose up --build
# API → http://localhost:8000
# Swagger → http://localhost:8000/docs
```

### Opção 2 — Desenvolvimento (hot reload)

```bash
# Terminal 1: Ollama via Docker
cd backend
docker compose up -d ollama

# Terminal 2: API local
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3 — Produção

```bash
cd backend
./scripts/deploy.sh
# Acessar: http://localhost/api/v1/health
```

### Opção 4 — Frontend (dev)

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
# Acessar: http://localhost:5173
```

---

##  Endpoints da API

### REST

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Health check + coleções |
| `POST` | `/api/v1/ask` | Pergunta ao RAG |
| `POST` | `/api/v1/ask/stream` | Pergunta ao RAG (SSE streaming) |
| `POST` | `/api/v1/upload` | Upload de documento |
| `DELETE` | `/api/v1/clear` | Limpa banco vetorial |
| `POST` | `/api/v1/agent` | Conversa com agente |
| `POST` | `/api/v1/agent/stream` | Conversa com agente (SSE streaming) |
| `GET` | `/api/v1/mcp/sse` | Conexão SSE do MCP |
| `POST` | `/api/v1/mcp/message` | Mensagens JSON-RPC do MCP |

### Teste rápido

```bash
# Health check
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

# Upload
curl -s -X POST http://localhost:8000/api/v1/upload \
  -F "file=@README.md"

# Pergunta ao RAG
curl -s -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que esse projeto faz?"}'

# Conversa com agente
curl -s -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Resuma os documentos que subi"}'
```

---

##  Arquitetura

```
backend/
├── app/
│   ├── api/routes.py         # Agregador de rotas REST
│   ├── agents/
│   │   ├── routes.py         # Rotas do agente
│   │   ├── tools.py          # 5 ferramentas (RAG, calculo, web, etc.)
│   │   ├── web_search.py     # Busca via DuckDuckGo
│   │   └── use_cases/
│   │       └── chat_use_case.py  # LangGraph orchestrator
│   ├── rag/
│   │   ├── routes.py         # Rotas do RAG
│   │   ├── schemas.py        # Schemas Pydantic
│   │   ├── embeddings.py     # Embeddings via Ollama
│   │   ├── loaders.py        # Loaders para 15 formatos
│   │   ├── chunking/         # 4 estratégias de chunking
│   │   ├── reranking/        # Cross-encoder reranking
│   │   ├── vector_store/     # Adapter Pattern (ChromaDB)
│   │   └── use_cases/
│   │       ├── ask_use_case.py       # Pergunta ao RAG
│   │       └── document_use_case.py  # Upload + chunk + ingest
│   ├── mcp/
│   │   ├── server.py         # MCPServerProvider (singleton)
│   │   ├── transport.py      # MCPSseTransport
│   │   └── routes.py         # Sub-app SSE Starlette
│   ├── infra/
│   │   ├── llm.py            # LLMFactory (cache por temperatura)
│   │   └── tracing.py        # OpenTelemetry tracing
│   ├── config.py             # Pydantic Settings
│   └── main.py               # FastAPI app
├── nginx/nginx.conf          # Reverse proxy (produção)
├── scripts/deploy.sh         # Script de deploy
├── docker-compose.yml        # Stack dev
├── docker-compose.prod.yml   # Stack produção
├── docker-compose.tracing.yml # Jaeger tracing
├── Dockerfile                # Multi-stage build
└── requirements.txt          # Dependências

frontend/
└── src/
    ├── components/
    │   ├── Chat.tsx           # Componente de chat (streaming)
    │   └── Header.tsx         # Upload, modos, threads
    ├── services/
    │   └── api.ts             # Camada de API
    ├── App.tsx                # Componente principal
    └── main.tsx               # Entry point

docs/                          # Documentação diária do desenvolvimento
```

---

##  Agente Inteligente (LangGraph)

O agente usa um grafo com dois nós:

```
  ┌─────────┐
  │ Agent   │ ← Decide qual ferramenta usar (ou responder)
  └────┬────┘
       │
       ▼ (se tool_call)
  ┌─────────┐
  │ Tools   │ ← Executa a ferramenta e volta pro Agent
  └────┬────┘
       │
       ▼ (se resposta final)
       FIM
```

### Ferramentas disponíveis

| Ferramenta | Descrição |
|------------|-----------|
| `search_documents` | Busca nos documentos indexados (RAG) |
| `get_current_time` | Data e hora atual |
| `calculate` | Expressões matemáticas (`sqrt`, `log`, `sin`, `cos`, etc.) |
| `search_web_tool` | Pesquisa na web via DuckDuckGo |
| `list_available_tools` | Auto-descrição |

---

##  MCP Server

O servidor MCP expõe as ferramentas do RAG para clientes compatíveis.

### Via stdio (Claude Desktop, Cline)

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "env": {
        "RAG_OLLAMA_BASE_URL": "http://localhost:11434"
      }
    }
  }
}
```

### Via SSE/HTTP

```bash
# Conecta ao SSE
curl -N http://localhost:8000/api/v1/mcp/sse

# Envia mensagem JSON-RPC
curl -X POST "http://localhost:8000/api/v1/mcp/message?session_id=SEU_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Ferramentas expostas

| Ferramenta | Descrição |
|------------|-----------|
| `rag-ask` | Faz perguntas aos documentos indexados |
| `rag-status` | Verifica status do sistema |

---

##  Observabilidade (OpenTelemetry)

### Ativar tracing

```bash
# Dev (console exporter)
export RAG_TRACING_ENABLED=true

# Produção (com Jaeger)
export RAG_TRACING_ENABLED=true
export RAG_TRACING_OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

### Com Docker + Jaeger

```bash
cd backend
docker compose -f docker-compose.prod.yml -f docker-compose.tracing.yml up -d
# Jaeger UI → http://localhost:16686
```

---

##  Configuração

Variáveis de ambiente com prefixo `RAG_`:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `RAG_OLLAMA_BASE_URL` | `http://localhost:11434` | URL do Ollama |
| `RAG_LLM_MODEL` | `llama3.2:3b` | Modelo de linguagem |
| `RAG_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `RAG_CHROMA_PERSIST_DIR` | `./data/chroma` | Diretório do ChromaDB |
| `RAG_COLLECTION_NAME` | `rag_docs` | Nome da coleção vetorial |
| `RAG_DEBUG` | `true` | Modo debug |
| `RAG_RERANKING_ENABLED` | `true` | Reranking ativo |
| `RAG_TRACING_ENABLED` | `false` | Tracing OpenTelemetry |
| `RAG_TRACING_OTLP_ENDPOINT` | — | Endpoint OTLP (Jaeger) |

---

##  Formatos de Documento Suportados

`PDF`, `TXT`, `MD`, `DOCX`, `HTML`, `CSV`, `JSON`, `PY`, `JS`, `TS`, `SQL`, `YAML`, `XML`

---

##  Roadmap

O projeto segue um plano de 15 dias. Status atual:

| Dia | Feature | Status |
|-----|---------|--------|
| 1 | Setup + RAG funcional | ✅ |
| 2 | Streaming no RAG (SSE) | ✅ |
| 3 | Streaming no Agente | ✅ |
| 4 | Chunking esperto | ✅ |
| 5 | Reranking | ✅ |
| 6 | Web Search Tool | ✅ |
| 7 | MCP via SSE | ✅ |
| 8 | Frontend React | ✅ |
| 9 | Testes | ⏳ |
| 10 | Rate limiting | ⏳ |
| 11 | Deploy produção | ✅ |
| 12 | LLMOps / Tracing | ✅ |
| 13 | Documentação | ✅ |
| 14 | Polimento | ✅ |
| 15 | Publicar | ✅ |

Detalhes em [`PLANO.md`](./PLANO.md) e `docs/`.

---

##  Dependências

| Categoria | Bibliotecas |
|-----------|-------------|
| **Core** | FastAPI, Uvicorn, Pydantic |
| **RAG & IA** | LangChain, ChromaDB, Ollama |
| **Agentes** | LangGraph |
| **MCP** | MCP Python SDK |
| **Documentos** | PyPDF, python-docx, BeautifulSoup, Markdown |
| **Reranking** | Sentence-Transformers |
| **Observabilidade** | OpenTelemetry |
| **Frontend** | React, Vite, TypeScript, Vitest |

---

##  Licença

MIT — sinta-se livre pra usar, estudar e modificar.
