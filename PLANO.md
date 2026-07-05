#  RAG + Agentes + MCP + LLMOps

> Plano de desenvolvimento — 15 dias de projeto prático  
> Stack: **FastAPI + LangChain + LangGraph + ChromaDB + Ollama + MCP**

---

##  Contexto

- **Dev:** Thyago — nível Sênior em backend
- **Objetivo:** Aprender na prática o ecossistema de Engenharia de IA (RAG, Agentes, MCP, LLMOps)
- **Projeto:** API completa rodando 100% local (Ollama pra LLM e embeddings), sem custos de API
- **Status atual:**  RAG respondendo perguntas, API rodando 100%, Ollama via Docker, agente com LangGraph funcional, MCP Server no ar
- **Setup:** API local (`uvicorn --reload`) + Ollama no Docker (`docker compose up -d ollama`)

---

##  O QUE JÁ ESTÁ PRONTO

### 1. Infraestrutura
- `Dockerfile` — multi-stage build com Python 3.12-slim
- `docker-compose.yml` — API + Ollama + ChromaDB + Init (com healthcheck)
- `setup.sh` — script automático de setup (venv, deps, modelos, diretórios)
- `requirements.txt` — dependências organizadas por categoria
- `.env.example` — configs via env vars com prefixo `RAG_`

### 2. App (`app/`)
| Módulo | Arquivos | O que faz |
|--------|----------|-----------|
| `config.py` | 1 | Settings com Pydantic (ollama, chroma, reranking, agente, debug, etc.) |
| `main.py` | 1 | FastAPI com lifespan, CORS, router |
| **`api/`** | `routes.py`, `schemas.py` | Rotas REST (/ask, /upload, /agent, /health, /clear) + schemas Pydantic |
| **`rag/`** | `embeddings.py`, `vector_store/`, `chunking/`, `reranking/`, `loaders.py` | Embeddings via Ollama, ChromaDB persistente (adapter c/ factory), chunking inteligente (4 estrategias), reranking via cross-encoder, loaders pra 15 formatos |
| **`agents/`** | `agent.py`, `tools.py`, `web_search.py` | LangGraph com grafo (agent -> tools -> agent), 5 tools (agora com busca web via DuckDuckGo) |
| **`mcp/`** | `server.py` | Servidor MCP via stdio (expõe rag-ask e rag-status) |

### 3. Endpoints da API
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/ask` | Pergunta ao RAG (retorna resposta + fontes) |
| `POST` | `/api/v1/ask/stream` | Pergunta ao RAG com streaming (SSE) |
| `POST` | `/api/v1/upload` | Upload de documento (PDF, TXT, MD, DOCX, HTML, CSV, JSON, PY, JS, TS, SQL, YAML, XML) |
| `DELETE` | `/api/v1/clear` | Limpa o banco vetorial |
| `POST` | `/api/v1/agent` | Conversa com o agente (RAG + tools + memória) |
| `POST` | `/api/v1/agent/stream` | Conversa com o agente com streaming (SSE) |
| `GET` | `/api/v1/health` | Health check + lista coleções |

### 4. Tools do Agente (LangGraph)
- `search_documents` — busca no RAG
- `get_current_time` — data/hora atual
- `calculate` — expressões matemáticas (eval seguro)
- `search_web_tool` — pesquisa na internet (DuckDuckGo, gratis, sem API key)
- `list_available_tools` — auto-descrição

### 5. MCP Server
- Protocolo **MCP (Model Context Protocol)** via stdio
- Ferramentas expostas: `rag-ask`, `rag-status`
- Compatível com Claude Desktop, Cline, etc.

### 6. Chunking esperto (Dia 4)
- 4 estrategias: Recursive, Markdown, Code, Semantic (placeholder)
- Factory em `app/rag/chunking/` com DI no DocumentUseCase
- Loaders centralizados em `app/rag/loaders.py` — 15 extensoes suportadas
- Rota de upload aceita todos os novos formatos

### 7. Reranking (Dia 5)
- Cross-encoder `ms-marco-MiniLM-L-2-v2` (~80MB, CPU)
- Quando ativo: busca 10 docs, re-ordena por relevancia, retorna top 4
- Configuravel via env var `RAG_RERANKING_ENABLED`

### 8. Web Search no Agente (Dia 6)
- Tool `search_web_tool` via DuckDuckGo (ddgs)
- 100% gratuito, sem API key
- Integrado ao LangGraph como as demais tools

---

##  ROTEIRO — PRÓXIMOS 15 DIAS

```
Dia 1  ─  Review + alinhamento + projeto rodando + RAG funcional
Dia 2  ─  Streaming no RAG (resposta token a token via SSE) ← FEITO
Dia 3  ─  Streaming no Agente (LangGraph + SSE) ← FEITO
Dia 4  ─  Chunking esperto + mais formatos de documento ← FEITO
Dia 5  ─  Reranking (melhorar qualidade das respostas) ← FEITO
Dia 6  ─  Web Search Tool (agente pesquisar na internet) ← FEITO
Dia 7  ─ MCP via SSE (além de stdio, expor via HTTP)
Dia 8  ─ Frontend básico (Streamlit ou Next.js)
Dia 9  ─ Testes unitários e de integração
Dia 10 ─ Rate limiting + validações extras
Dia 11 ─ Deploy (Railway, Render, ou server próprio)
Dia 12 ─ LLMOps: tracing com LangSmith / OpenTelemetry
Dia 13 ─ Documentação + README foda
Dia 14 ─ Polimento + gravar demo
Dia 15 ─ Publicar / mostrar pra geral
```

---

##  COMO RODAR

```bash
# Opção 1 — Híbrido (API local + Ollama em Docker) ← RECOMENDADO P/ DEV
docker compose up -d ollama          # Só o Ollama no Docker
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2 — Docker completo
docker compose up --build

# Opção 3 — MCP Server separado
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
```

---

##  DIAS 2 e 3 — Streaming (RAG + Agente) — CONCLUÍDOS

**Streaming no RAG (`/ask/stream`)** — endpoint que responde token a token via SSE.
**Streaming no Agente (`/agent/stream`)** — endpoint que streama tokens, tool_calls e tool_results.

### Arquivos criados/modificados
- `app/rag/engine.py` → `ask_stream()` — generator de tokens do RAG
- `app/api/routes.py` → endpoints `/ask/stream` e `/agent/stream`
- `app/agents/agent.py` → `run_agent_stream()` — generator assíncrono de eventos do agente
- `docs/dia-2-streaming-rag.md` — descritivo do Dia 2
- `docs/dia-3-streaming-agente.md` — descritivo do Dia 3

### Como testar
```bash
# Streaming RAG
curl -N -X POST http://localhost:8000/api/v1/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'

# Streaming Agente
curl -N -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Resuma os documentos", "thread_id": "teste"}'
```

---

##  HISTÓRICO DE DIAS

### Dia 1 (30/06) — Setup + RAG funcional
-  Projeto revisado e estruturado (8 módulos)
-  `README.md` + `PLANO.md`
-  Ollama via Docker + modelos baixados
-  API rodando com `uvicorn --reload`
-  RAG respondendo via Swagger

### Dia 2 (04/07) — Streaming no RAG
-  `app/rag/engine.py` → `ask_stream()` com generator de tokens
-  `POST /api/v1/ask/stream` → SSE token a token
-  Limpeza do código: removido observability/ e memory/

### Dia 3 (04/07) — Streaming no Agente
-  `app/agents/agent.py` → `run_agent_stream()` assíncrono
-  `POST /api/v1/agent/stream` → SSE com tokens, tool_calls, tool_results
-  Criação de `docs/` com descritivos diários

### Dia 4 (05/07) — Chunking esperto + mais formatos
-  `app/rag/chunking/` com 4 estrategias (Recursive, Markdown, Code, Semantic)
-  `app/rag/loaders.py` — 15 extensoes de documento suportadas
-  DocumentUseCase com pipeline load -> chunk -> ingest
-  `docs/dia-4-chunking-esperto.md`

### Dia 5 (05/07) — Reranking
-  `app/rag/reranking/reranker.py` — CrossEncoder (ms-marco-MiniLM-L-2-v2)
-  Integrado ao AskUseCase: busca 10, re-ordena, top 4
-  Configuravel via env var `RAG_RERANKING_ENABLED`
-  `docs/dia-5-reranking.md`

### Dia 6 (05/07) — Web Search no Agente
-  `app/agents/web_search.py` — DuckDuckGo search (ddgs)
-  Tool `search_web_tool` registrada no LangGraph
-  Agora sao 5 tools disponiveis
-  `docs/dia-6-web-search.md`

### Setup atual
- **API:** rodando local via `uvicorn --reload`
- **Ollama:** rodando via `docker compose up -d ollama`
- **ChromaDB:** persistente em `./data/chroma`
- **Portas:** API `:8000`, Ollama `:11434`

### Pra subir
```bash
docker compose up -d ollama
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

>  **Pra retomar:** colar o link desse repo num prompt novo falando "Retomando o projeto da pasta RAG" que eu recupero o contexto completo.
