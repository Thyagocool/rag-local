# Dia 7 — MCP via SSE (expor via HTTP)

> **Status: IMPLEMENTADO** 🎉  
> Projeto refatorado seguindo OOP, Clean Code, DRY e SOLID.

---

## Resumo

O MCP Server, que antes só funcionava via **stdio** (CLI), agora também pode ser acessado via **SSE/HTTP**, permitindo que clientes MCP se conectem remotamente via REST sem depender de um processo separado.

---

## Arquitetura implementada

### Padrões utilizados

| Princípio | Aplicação |
|-----------|-----------|
| **SRP** | Cada arquivo tem uma responsabilidade única: `server.py` define ferramentas, `transport.py` gerencia transporte, `routes.py` expõe rotas |
| **OCP** | Novo transporte SSE foi adicionado sem modificar a definição das ferramentas — aberto pra extensão, fechado pra modificação |
| **DIP** | `MCPSseTransport` depende da abstração `Server` (via `MCPServerProvider`), não de uma implementação concreta |
| **Singleton** | `MCPServerProvider` garante uma única instância do servidor MCP |
| **Factory Method** | `MCPServerProvider._build_server()` centraliza a criação do servidor |
| **DRY** | Ferramentas definidas uma única vez em `server.py`, reutilizadas por stdio e SSE |
| **Clean Code** | Nomes descritivos, responsabilidades claras, sem side effects |

### Estrutura dos arquivos

```
backend/app/mcp/
├── __init__.py          # Exporta MCPServerProvider, MCPSseTransport, mcp_sse_app
├── server.py            # Definição das ferramentas + provider singleton (refatorado)
├── transport.py         # Adaptador SSE (novo)
└── routes.py            # Sub-app Starlette com rotas SSE (novo)
```

### Fluxo de uma conexão MCP via SSE

```
Cliente MCP                      FastAPI + MCP Server
    │                                    │
    │  GET /api/v1/mcp/sse               │
    │──────────────────────────────────▶  │
    │                                    │
    │  event: endpoint                   │
    │  data: /api/v1/mcp/message?session_id=abc123
    │◀──────────────────────────────────  │
    │                                    │
    │  POST /api/v1/mcp/message?session_id=abc123
    │  (JSON-RPC: list_tools)            │
    │──────────────────────────────────▶  │
    │                                    │
    │  event: message                    │
    │  data: {"jsonrpc":"2.0",...}       │
    │◀──────────────────────────────────  │
    │                                    │
    │  POST /api/v1/mcp/message?session_id=abc123
    │  (JSON-RPC: call_tool rag-ask)     │
    │──────────────────────────────────▶  │
    │                                    │
    │  event: message                    │
    │  data: {"result": ...}             │
    │◀──────────────────────────────────  │
```

---

## O que mudou em cada arquivo

### `server.py` — REFATORADO (antes vs depois)

**Antes:** Um único arquivo com lógica misturada (criação do server + definição das tools + execução stdio tudo junto, com funções soltas e dependências implícitas).

**Depois:** Agora segue o padrão **Provider** com `MCPServerProvider`:
- Métodos de classe para obter servidor e opções
- `_build_server()` encapsula a construção
- `run_stdio()` para compatibilidade com CLI legada
- `reset()` para recriação em testes
- Cache singleton da instância do servidor

### `transport.py` — NOVO
- `MCPSseTransport` encapsula o `SseServerTransport` do MCP SDK
- `handle_sse(request)` — estabelece conexão SSE
- `handle_message(request)` — recebe mensagens JSON-RPC
- Totalmente desacoplado da definição das ferramentas

### `routes.py` — NOVO
- Sub-app **Starlette** com duas rotas:
  - `GET /sse` → conexão SSE
  - `POST /message` (via `Mount`) → recebe mensagens
- Exporta `mcp_sse_app` para montagem no FastAPI

### `main.py` — MODIFICADO
- Adicionado `app.mount("/api/v1/mcp", app=mcp_sse_app)`

---

## Como testar

### Via curl (SSE)
```bash
# Conecta ao SSE (fica ouvindo)
curl -N http://localhost:8000/api/v1/mcp/sse
```

### Via MCP Inspector (ferramenta oficial)
```bash
npx @modelcontextprotocol/inspector python -m app.mcp.server
```

### Via stdio (legado, continua funcionando)
```bash
python -m app.mcp.server
```

### Health check da API
```bash
curl http://localhost:8000/api/v1/health
```

---

## Endpoints disponíveis

| Método | Rota | Descrição | Transporte |
|--------|------|-----------|------------|
| `GET` | `/api/v1/mcp/sse` | Conexão SSE | SSE |
| `POST` | `/api/v1/mcp/message` | Mensagens JSON-RPC | SSE |
| `-` | stdin/stdout | Comunicação via CLI | stdio |

## Ferramentas MCP expostas

| Ferramenta | Descrição |
|------------|-----------|
| `rag-ask` | Faz perguntas aos documentos indexados no RAG |
| `rag-status` | Verifica o status do sistema RAG |
