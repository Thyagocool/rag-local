# 🧠 RAG + Agentes + MCP + LLMOps

> Plano de desenvolvimento — 15 dias de projeto prático  
> Stack: **FastAPI + LangChain + LangGraph + ChromaDB + Ollama + MCP**

---

## 📋 Contexto

- **Dev:** Thyago — nível Sênior em backend
- **Objetivo:** Aprender na prática o ecossistema de Engenharia de IA (RAG, Agentes, MCP, LLMOps)
- **Projeto:** API completa rodando 100% local (Ollama pra LLM e embeddings), sem custos de API
- **Status atual:** ✅ RAG respondendo perguntas, API rodando 100%, Ollama via Docker, agente com LangGraph funcional, MCP Server no ar
- **Setup:** API local (`uvicorn --reload`) + Ollama no Docker (`docker compose up -d ollama`)

---

## ✅ O QUE JÁ ESTÁ PRONTO

### 1. Infraestrutura
- `Dockerfile` — multi-stage build com Python 3.12-slim
- `docker-compose.yml` — API + Ollama + ChromaDB + Init (com healthcheck)
- `setup.sh` — script automático de setup (venv, deps, modelos, diretórios)
- `requirements.txt` — dependências organizadas por categoria
- `.env.example` — configs via env vars com prefixo `RAG_`

### 2. App (`app/`)
| Módulo | Arquivos | O que faz |
|--------|----------|-----------|
| `config.py` | 1 | Settings com Pydantic (ollama, chroma, debug, etc.) |
| `main.py` | 1 | FastAPI com lifespan, CORS, router |
| **`api/`** | `routes.py`, `schemas.py` | Rotas REST (/ask, /upload, /agent, /health, /clear) + schemas Pydantic |
| **`rag/`** | `embeddings.py`, `vectorstore.py`, `engine.py` | Embeddings via Ollama, ChromaDB persistente, chain de retrieval RAG |
| **`agents/`** | `agent.py`, `tools.py` | LangGraph com grafo (agent -> tools -> agent), 4 tools |
| **`mcp/`** | `server.py` | Servidor MCP via stdio (expõe rag-ask e rag-status) |
| **`memory/`** | `memory.py` | Checkpointer SQLite + in-memory |
| **`observability/`** | `logging.py` | structlog colorido (dev) / JSON (prod) + OpenTelemetry |

### 3. Endpoints da API
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/ask` | Pergunta ao RAG (retorna resposta + fontes) |
| `POST` | `/api/v1/upload` | Upload de documento (PDF, TXT, MD, DOCX) |
| `DELETE` | `/api/v1/clear` | Limpa o banco vetorial |
| `POST` | `/api/v1/agent` | Conversa com o agente (RAG + tools + memória) |
| `GET` | `/api/v1/health` | Health check + lista coleções |

### 4. Tools do Agente (LangGraph)
- `search_documents` — busca no RAG
- `get_current_time` — data/hora atual
- `calculate` — expressões matemáticas (eval seguro)
- `list_available_tools` — auto-descrição

### 5. MCP Server
- Protocolo **MCP (Model Context Protocol)** via stdio
- Ferramentas expostas: `rag-ask`, `rag-status`
- Compatível com Claude Desktop, Cline, etc.

### 6. Correções aplicadas (Dia 1)
- `observability/logging.py` — structlog configurado corretamente (PrintLogger sem `filter_by_level`/`add_logger_name`)
- `main.py` — f-string no lugar de printf-style (%s)
- `docker-compose.yml` — `OLLAMA_HOST` adicionado ao container `ollama-init` pra resolver comunicação entre containers

---

## 🗺️ ROTEIRO — PRÓXIMOS 15 DIAS

```
Dia 1  ─ ✅ Review + alinhamento + projeto rodando + RAG funcional
Dia 2  ─ ⏩ Streaming no RAG (resposta token a token via SSE) ← PRÓXIMO
Dia 3  ─ Streaming no Agente (LangGraph já suporta nativamente)
Dia 4  ─ Chunking esperto + mais formatos de documento
Dia 5  ─ Reranking (melhorar qualidade das respostas)
Dia 6  ─ Web Search Tool (agente pesquisar na internet)
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

## 🔧 COMO RODAR

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

## 🧪 TESTAR SE TUDO FUNCIONA

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

## 💡 PRÓXIMO PASSO (DIA 2)

**Implementar Streaming no RAG** — fazer o endpoint `/ask` responder token a token usando SSE (Server-Sent Events).

### Por que streaming?
- Experiência muito mais profissional
- Impressiona em entrevistas
- Necessário pra chatbots de verdade
- O LangChain já tem suporte nativo via `stream()` no ChatOllama

### Arquivos que vão mudar
- `app/api/routes.py` — novo endpoint `/ask/stream`
- `app/api/schemas.py` — novo schema pra streaming (ou reuso)
- `app/rag/engine.py` — função `ask_stream()` que faz yield dos tokens

---

## 📋 RESUMO — DIA 1 (30/06)

### O que foi feito
- ✅ Projeto revisado e analisado (estrutura completa, 8 módulos)
- ✅ `README.md` criado com documentação completa
- ✅ `PLANO.md` criado com roadmap de 15 dias
- ✅ Dependências instaladas no venv
- ✅ Bug do structlog corrigido (PrintLogger vs stdlib)
- ✅ Bug do `%s` no log corrigido (f-string)
- ✅ Bug do `OLLAMA_HOST` no `ollama-init` corrigido
- ✅ Ollama instalado via Docker + modelos baixados (llama3.2:3b, nomic-embed-text)
- ✅ API rodando com `uvicorn --reload`
- ✅ RAG testado e respondendo pelo Swagger

### Setup atual
- **API:** rodando local via `uvicorn --reload`
- **Ollama:** rodando via `docker compose up -d ollama`
- **ChromaDB:** persistente em `./data/chroma`
- **Portas:** API `:8000`, Ollama `:11434`

### Pra subir amanhã
```bash
docker compose up -d ollama
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

> 🚀 **Pra retomar:** colar o link desse repo num prompt novo falando "Retomando o projeto da pasta RAG" que eu recupero o contexto completo.
