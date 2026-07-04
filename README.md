# 🧠 RAG + Agentes + MCP + LLMOps

API completa de **Engenharia de IA** com **RAG**, **Agentes Inteligentes** (LangGraph), **MCP Server** e **Observabilidade** — tudo rodando **100% local e grátis** com Ollama.

> Stack: **FastAPI + LangChain + LangGraph + ChromaDB + Ollama + MCP**

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| 📄 **RAG** | Upload de documentos (PDF, DOCX, TXT, MD), indexação vetorial e perguntas com respostas baseadas nos docs |
| 🤖 **Agentes** | Agente com LangGraph que usa ferramentas (RAG, calculadora, hora atual) e tem memória de conversa |
| 🔌 **MCP** | Servidor no protocolo MCP (Model Context Protocol) — compatível com Claude Desktop, Cline e outros |
| 💾 **Memória** | Persistência de conversas via SQLite |
| 📊 **Observabilidade** | Logs estruturados (structlog) + tracing OpenTelemetry |
| 🐳 **Docker** | Stack completa com Docker Compose |
| 🎯 **100% local** | LLM e embeddings rodando via Ollama — sem API paga, sem dados saindo da sua máquina |

---

## 🏗️ Estrutura do Projeto

```
RAG/
├── app/
│   ├── api/              # Rotas REST + Schemas Pydantic
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── agents/           # Agente LangGraph + Ferramentas
│   │   ├── agent.py
│   │   └── tools.py
│   ├── rag/              # Motor RAG (embeddings, vectorstore, engine)
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   └── engine.py
│   ├── mcp/              # Servidor MCP
│   │   └── server.py
│   ├── memory/           # Gerenciamento de memória
│   │   └── memory.py
│   ├── observability/    # Logging e tracing
│   │   └── logging.py
│   ├── config.py         # Configurações (Pydantic Settings)
│   └── main.py           # App FastAPI
├── docker-compose.yml    # Stack completa: API + Ollama + ChromaDB
├── Dockerfile            # Multi-stage build
├── setup.sh              # Setup automático
├── requirements.txt      # Dependências Python
├── .env.example          # Exemplo de configuração
├── PLANO.md              # Roadmap de desenvolvimento
└── README.md             # <-- Você está aqui
```

---

## 🚀 Como Rodar

### Opção 1 — Docker (recomendado)

**Pré-requisitos:** Docker e Docker Compose instalados.

```bash
# Sobe a stack completa (API + Ollama + ChromaDB)
docker compose up --build

# A API fica disponível em http://localhost:8000
# O Ollama em http://localhost:11434
```

Na primeira execução, o `ollama-init` vai baixar os modelos (`llama3.2:3b` e `nomic-embed-text`) — pode levar alguns minutos.

### Opção 2 — Local (sem Docker)

**Pré-requisitos:** Python 3.12+ e [Ollama](https://ollama.com) instalado.

```bash
# 1. Setup automático
chmod +x setup.sh && ./setup.sh

# 2. Ativa o ambiente e sobe a API
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> ⚠️ Se o Ollama não estiver instalado, o setup.sh avisa. Instale com:
> ```bash
> curl -fsSL https://ollama.com/install.sh | sh
> ```

### Opção 3 — Desenvolvimento (hot reload)

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 Endpoints da API

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Upload de Documento
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@seu-documento.pdf"
```

Formatos aceitos: **PDF, TXT, MD, DOCX**

### Perguntar ao RAG
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'
```

### Conversar com o Agente
```bash
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Resuma os documentos que subi"}'
```

### Limpar Banco Vetorial
```bash
curl -X DELETE http://localhost:8000/api/v1/clear
```

---

## 🔌 MCP Server

O servidor MCP permite que clientes compatíveis (Claude Desktop, Cline, etc.) consumam as ferramentas do RAG remotamente.

```bash
# Inicia o servidor MCP via stdio
python -m app.mcp.server
```

**Ferramentas expostas:**
- `rag-ask` — faz perguntas aos documentos indexados
- `rag-status` — verifica o status do sistema

Para conectar no **Claude Desktop**, adicione no `claude_desktop_config.json`:

```json
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

---

## ⚙️ Configuração

Todas as configs são via variáveis de ambiente com prefixo `RAG_`:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `RAG_OLLAMA_BASE_URL` | `http://localhost:11434` | URL do Ollama |
| `RAG_LLM_MODEL` | `llama3.2:3b` | Modelo de linguagem |
| `RAG_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `RAG_CHROMA_PERSIST_DIR` | `./data/chroma` | Diretório do ChromaDB |
| `RAG_COLLECTION_NAME` | `rag_docs` | Nome da coleção vetorial |
| `RAG_DEBUG` | `true` | Modo debug (logs coloridos) |
| `RAG_OTLP_ENDPOINT` | — | Endpoint OpenTelemetry (opcional) |

Copie o `.env.example` para `.env` e ajuste:

```bash
cp .env.example .env
```

---

## 🧪 Testando

```bash
# Health check
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

# Upload + Pergunta
curl -s -X POST http://localhost:8000/api/v1/upload -F "file=@README.md"
curl -s -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que esse projeto faz?"}'
```

---

## 🗺️ Roadmap

O projeto está em desenvolvimento ativo. Veja o [`PLANO.md`](./PLANO.md) para o roteiro completo.

**Próximos passos:**
- [ ] Streaming nas respostas (SSE)
- [ ] Chunking inteligente de documentos
- [ ] Reranking de resultados
- [ ] Web Search Tool
- [ ] MCP via SSE (HTTP)
- [ ] Frontend (Streamlit)
- [ ] Testes automatizados
- [ ] Deploy

---

## 📦 Dependências

| Categoria | Bibliotecas |
|-----------|-------------|
| **Core** | FastAPI, Uvicorn, Pydantic |
| **RAG & IA** | LangChain, LangChain-Chroma, LangChain-Ollama |
| **Vetorial** | ChromaDB |
| **Agentes** | LangGraph |
| **MCP** | MCP Python SDK |
| **Documentos** | PyPDF, python-docx, unstructured |
| **Observabilidade** | structlog, OpenTelemetry |
| **Utilitários** | httpx, rich, python-multipart |

---

## 📄 Licença

MIT — sinta-se livre pra usar, estudar e modificar.
