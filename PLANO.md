#  RAG + Agentes + MCP + LLMOps

> Plano de desenvolvimento — 15 dias de projeto prático  
> Stack: **FastAPI + LangChain + LangGraph + ChromaDB + Ollama + MCP**

---

##  Contexto

- **Dev:** Thyago — nível Sênior em backend
- **Objetivo:** Aprender na prática o ecossistema de Engenharia de IA (RAG, Agentes, MCP, LLMOps)
- **Projeto:** API completa rodando 100% local (Ollama pra LLM e embeddings), sem custos de API
- **Status atual:**  RAG + Agente + MCP (stdio + SSE) + Frontend React + Deploy prod-ready
- **Setup:** API local (`uvicorn --reload`) + Ollama no Docker (`docker compose up -d ollama`)

---

##  O QUE JÁ ESTÁ PRONTO

### 1. Infraestrutura
- `backend/Dockerfile` — multi-stage build + non-root user + healthcheck
- `backend/.dockerignore` — build context otimizado
- `backend/docker-compose.yml` — API + Ollama + ChromaDB + Init
- `backend/docker-compose.prod.yml` — Stack de produção com Nginx + limites de recursos
- `backend/nginx/nginx.conf` — Reverse proxy + headers de segurança + suporte SSE
- `backend/scripts/deploy.sh` — Script de deploy automatizado
- `backend/setup.sh` — script automático de setup (venv, deps, modelos, diretórios)
- `backend/requirements.txt` — dependências organizadas por categoria
- `backend/.env.example` — configs via env vars com prefixo `RAG_`

### 2. Backend (`backend/app/`)
| Módulo | Arquivos | O que faz |
|--------|----------|-----------|
| `config.py` | 1 | Settings com Pydantic (ollama, chroma, reranking, agente, debug, etc.) |
| `main.py` | 1 | FastAPI com lifespan, CORS, router + MCP SSE mount |
| **`api/`** | `routes.py` | Agregador de rotas REST + health check |
| **`rag/`** | `embeddings.py`, `vector_store/`, `chunking/`, `reranking/`, `loaders.py`, `routes.py`, `schemas.py`, `use_cases/` | Embeddings via Ollama, ChromaDB persistente (adapter c/ factory), chunking inteligente (4 estrategias), reranking via cross-encoder, loaders pra 15 formatos, casos de uso (ask, document) |
| **`agents/`** | `routes.py`, `schemas.py`, `tools.py`, `web_search.py`, `use_cases/chat_use_case.py` | LangGraph com grafo (agent -> tools -> agent), 5 tools (RAG, tempo, calculo, web search, auto-lista), streaming |
| **`mcp/`** | `server.py`, `transport.py`, `routes.py` | MCP via stdio + SSE/HTTP (MCPServerProvider singleton, MCPSseTransport) |
| **`infra/`** | `llm.py` | LLMFactory compartilhada (cache por temperatura) |

### 3. Endpoints da API
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/ask` | Pergunta ao RAG (retorna resposta + fontes) |
| `POST` | `/api/v1/ask/stream` | Pergunta ao RAG com streaming (SSE) |
| `POST` | `/api/v1/upload` | Upload de documento (15 formatos) |
| `DELETE` | `/api/v1/clear` | Limpa o banco vetorial |
| `POST` | `/api/v1/agent` | Conversa com o agente (RAG + tools + memória) |
| `POST` | `/api/v1/agent/stream` | Conversa com o agente com streaming (SSE) |
| `GET` | `/api/v1/health` | Health check + lista coleções |
| `GET` | `/api/v1/mcp/sse` | Conexão SSE do MCP |
| `POST` | `/api/v1/mcp/message` | Mensagens JSON-RPC do MCP |

### 4. Tools do Agente (LangGraph)
- `search_documents` — busca no RAG
- `get_current_time` — data/hora atual
- `calculate` — expressões matemáticas (eval seguro, com math.\*)
- `search_web_tool` — pesquisa na internet (DuckDuckGo, gratis, sem API key)
- `list_available_tools` — auto-descrição

### 5. MCP Server
- Protocolo **MCP (Model Context Protocol)** via **stdio** e **SSE/HTTP**
- Ferramentas expostas: `rag-ask`, `rag-status`
- Arquitetura: `MCPServerProvider` (singleton) + `MCPSseTransport` + sub-app Starlette
- Compatível com Claude Desktop, Cline, e qualquer cliente MCP via HTTP

### 6. Chunking esperto (Dia 4)
- 4 estrategias: Recursive, Markdown, Code, Semantic (placeholder)
- Factory em `app/rag/chunking/` com DI no DocumentUseCase
- Loaders centralizados em `app/rag/loaders.py` — 15 extensoes suportadas

### 7. Reranking (Dia 5)
- Cross-encoder `ms-marco-MiniLM-L-2-v2` (~80MB, CPU)
- Quando ativo: busca 10 docs, re-ordena por relevancia, retorna top 4
- Configuravel via env var `RAG_RERANKING_ENABLED`

### 8. Web Search no Agente (Dia 6)
- Tool `search_web_tool` via DuckDuckGo (ddgs)
- 100% gratuito, sem API key
- Integrado ao LangGraph como as demais tools

### 9. Frontend React (Dia 8)
- React 19 + Vite 8 + TypeScript 6
- Streaming SSE (RAG e Agente) com fallback
- Upload de documentos, limpeza do banco, multi-threads
- Dedup de tokens, strip de tool JSON vazado
- Proxy Vite → Backend em `/api`

### 10. Deploy Produção (Dia 11)
- Dockerfile otimizado (multi-stage, non-root)
- `docker-compose.prod.yml` com limites de recursos
- Nginx reverse proxy + headers de segurança + suporte SSE
- `scripts/deploy.sh` com comandos build/start/stop/logs/clean
- `.dockerignore` para build leve

### 11. LLMOps / Tracing (Dia 12)
- OpenTelemetry com instrumentação de FastAPI e httpx
- `TracingManager` com suporte a console e OTLP exporters
- `docker-compose.tracing.yml` com Jaeger all-in-one
- Configurável via `RAG_TRACING_ENABLED` e `RAG_TRACING_OTLP_ENDPOINT`

### 12. Documentação (Dia 13)
- README.md completo com início rápido, arquitetura, endpoints
- Docs diários em `docs/` (dias 1 a 15)
- Diagrama ASCII da stack

### 13. Polimento (Dia 14)
- CORS configurável via env var
- Validação de tamanho de upload
- Info do pacote (`__version__`, `__app_name__`)

---

##  ROTEIRO — 15 DIAS (CONCLUÍDO)

```
Dia 1  ─  Review + alinhamento + projeto rodando + RAG funcional           ✅
Dia 2  ─  Streaming no RAG (resposta token a token via SSE)               ✅
Dia 3  ─  Streaming no Agente (LangGraph + SSE)                           ✅
Dia 4  ─  Chunking esperto + mais formatos de documento                   ✅
Dia 5  ─  Reranking (melhorar qualidade das respostas)                    ✅
Dia 6  ─  Web Search Tool (agente pesquisar na internet)                  ✅
Dia 7  ─  MCP via SSE (além de stdio, expor via HTTP)                     ✅
Dia 8  ─  Frontend básico (React + Vite + TypeScript)                     ✅
Dia 9  ─  Testes unitários e de integração                                ⏳ Parcial
Dia 10 ─  Rate limiting + validações extras                               ⏳ Pendente
Dia 11 ─  Deploy (Docker Compose + Nginx + produção)                      ✅
Dia 12 ─  LLMOps: tracing com OpenTelemetry                               ✅
Dia 13 ─  Documentação + README                                           ✅
Dia 14 ─  Polimento + melhorias finais                                    ✅
Dia 15 ─  Publicar                                                        ✅
```

---

##  COMO RODAR

```bash
# Opção 1 — Híbrido (API local + Ollama em Docker) ← RECOMENDADO P/ DEV
cd backend
docker compose up -d ollama          # Só o Ollama no Docker
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2 — Docker completo
docker compose up --build

# Opção 3 — Produção (com Nginx)
./scripts/deploy.sh

# Opção 4 — MCP Server (stdio)
python -m app.mcp.server
```

---

##  TESTAR SE TUDO FUNCIONA

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload de documento
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@documento.pdf"

# Pergunta ao RAG
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'

# Conversa com agente
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Resuma os documentos que subi"}'

# MCP via SSE
curl -N http://localhost:8000/api/v1/mcp/sse
```

---

##  HISTÓRICO DE DIAS

### Setup anterior (Dias 1-6)
Ver docs históricos em `docs/dia-1-setup-rag.md` até `docs/dia-6-web-search.md`.

### Dia 7 (06/07) — MCP via SSE
- `app/mcp/server.py` refatorado: `MCPServerProvider` (singleton)
- `app/mcp/transport.py`: `MCPSseTransport` — SSE adaptado pro FastAPI
- `app/mcp/routes.py`: sub-app Starlette com `GET /sse` + `POST /message`
- `app/main.py`: monta sub-app MCP em `/api/v1/mcp`
- `docs/dia-7-mcp-sse-implementado.md`

### Dia 8 (06/07) — Frontend React
- React 19 + Vite 8 + TypeScript 6
- Componentes: `Chat.tsx`, `Header.tsx`, `api.ts`
- Streaming SSE, upload, multi-threads, dedup de tokens
- Build gerado em `frontend/dist/`
- `docs/dia-8-frontend.md`

### Dia 9 — Testes (PENDENTE)
- Frontend: 2 testes no `App.test.tsx` + config Vitest
- Backend: nenhum teste automatizado
- `docs/dia-9-testes.md`

### Dia 10 — Rate limiting + validações (PENDENTE)
- Apenas validação Pydantic básica
- Sem slowapi, sem rate limiting
- `docs/dia-10-rate-limiting-validacoes.md`

### Dia 11 (06/07) — Deploy
- `Dockerfile` otimizado: multi-stage, non-root, healthcheck, labels
- `.dockerignore`: build context leve
- `docker-compose.yml`: healthcheck no API
- `docker-compose.prod.yml`: limites de recursos, logging, nginx
- `nginx/nginx.conf`: reverse proxy + headers segurança + SSE
- `scripts/deploy.sh`: build/start/stop/logs/clean
- `docs/dia-11-deploy.md`

---

### Setup atual
- **API:** rodando local via `uvicorn --reload` ou Docker
- **Ollama:** rodando via `docker compose up -d ollama`
- **ChromaDB:** persistente em `./data/chroma`
- **Frontend:** Vite dev server (`npm run dev`) ou build estático
- **Portas:** API `:8000`, Ollama `:11434`, Frontend `:5173`, Nginx `:80`

### Pra subir (dev)
```bash
docker compose up -d ollama
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Pra subir (produção)
```bash
cd backend
./scripts/deploy.sh
```

---

>  **Pra retomar:** colar o link desse repo num prompt novo falando "Retomando o projeto da pasta RAG" que eu recupero o contexto completo.
