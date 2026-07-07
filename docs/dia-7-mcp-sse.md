# Dia 7 — MCP via SSE (expor via HTTP)

> **Status: NÃO IMPLEMENTADO**  
> Apenas o MCP via stdio está funcionando. A exposição via SSE/HTTP é o próximo passo.

---

## O que existe hoje

### MCP via stdio ✅ (Dias 1-6)

O servidor MCP atual está em `backend/app/mcp/server.py` e funciona exclusivamente via **stdio**:

- **Transporte:** `mcp.server.stdio.stdio_server()` 
- **Inicialização:** `python -m app.mcp.server` (processo separado)
- **Ferramentas expostas:**
  - `rag-ask` — faz perguntas ao RAG
  - `rag-status` — verifica status do sistema
- **Compatível com:** Claude Desktop, Cline, e outros clientes MCP via stdio

### Arquivos existentes

| Arquivo | Descrição |
|---------|-----------|
| `backend/app/mcp/__init__.py` | Vazio (apenas marca como pacote) |
| `backend/app/mcp/server.py` | Servidor MCP via stdio (105 linhas) |

---

## O que falta (Dia 7)

Para implementar MCP via SSE/HTTP, é necessário:

1. **Endpoint SSE:** `GET /api/v1/mcp/sse` — estabelece conexão SSE
2. **Endpoint de mensagens:** `POST /api/v1/mcp/message` — recebe mensagens do cliente MCP
3. **Transporte SSE:** usando `mcp.server.sse` do pacote `mcp` (já está no `requirements.txt` como `mcp==1.2.1`)
4. **Integração com FastAPI:** o servidor MCP precisa rodar junto com a API (não em processo separado)
5. **Mesmas tools:** reutilizar `rag-ask` e `rag-status` já implementadas

### Dependência já instalada
```
mcp==1.2.1     ← já tem suporte a SSE transport
```

### Referência
- [MCP Python SDK — SSE Transport](https://github.com/modelcontextprotocol/python-sdk)
- MCP spec: transporte SSE usa `GET /sse` e `POST /message`
