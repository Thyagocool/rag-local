# Dia 9 — Testes unitários e de integração

> **Status: PARCIALMENTE IMPLEMENTADO**  
> Frontend: testes básicos configurados e funcionando.  
> Backend: nenhum teste automatizado.

---

## Frontend (TypeScript) — Testes iniciados ✅

### Estrutura de teste

| Arquivo | Descrição |
|---------|-----------|
| `frontend/src/App.test.tsx` | Teste do componente App (2 asserts) |
| `frontend/src/test/setup.ts` | Setup do jsdom + mock scrollTo |

### Configuração

**`vite.config.ts`** — integração com Vitest:
```ts
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
}
```

**`package.json`** — scripts:
```json
"test": "vitest run",
"test:watch": "vitest"
```

**Dependências de teste instaladas:**
- `vitest` — framework de testes
- `@testing-library/react` — renderização de componentes React
- `@testing-library/jest-dom` — matchers customizados (`toBeInTheDocument`, etc.)
- `jsdom` — ambiente DOM para Node.js

### Testes existentes

**`App.test.tsx`** — 2 testes:
1. Renderiza o header "RAG Chat"
2. Mostra botões de toggle "RAG" e "Agent"

### Para rodar os testes do frontend

```bash
cd frontend
npm test          # vitest run (uma vez)
npm run test:watch  # modo watch
```

---

## Backend (Python) — Nenhum teste ❌

### O que falta

- **Framework de testes:** `pytest` não está no `requirements.txt`
- **Arquivos de teste:** nenhum `test_*.py` em qualquer diretório
- **Configuração:** sem `pytest.ini`, `conftest.py`, `pyproject.toml` com config de test
- **Testes unitários:** nenhum para use cases (ask, document, chat)
- **Testes de integração:** nenhum para rotas da API
- **Testes de ferramentas:** nenhum para tools do agente (calculate, search, etc.)
- **Testes de MCP:** nenhum para o servidor MCP

### Recomendações

Para implementar testes no backend:

1. **Adicionar dependências:**
   ```
   pytest==8.x
   pytest-asyncio
   httpx  # para TestClient do FastAPI (já está no requirements)
   pytest-cov  # cobertura
   ```

2. **Criar estrutura de testes:**
   ```
   backend/
   └── tests/
       ├── conftest.py        # fixtures compartilhadas
       ├── test_ask.py        # testes do AskUseCase
       ├── test_document.py   # testes do DocumentUseCase
       ├── test_agent.py      # testes do ChatUseCase
       ├── test_tools.py      # testes das ferramentas
       ├── test_api.py        # testes de integração das rotas
       └── test_mcp.py        # testes do servidor MCP
   ```

3. **Áreas prioritárias para testar:**
   - `AskUseCase.ask()` e `AskUseCase.ask_stream()`
   - `DocumentUseCase.load_and_chunk()` com vários formatos
   - `ChatUseCase.run_agent()` e `run_agent_stream()`
   - Tools: `calculate`, `search_documents`, `get_current_time`
   - Rotas da API: `/ask`, `/upload`, `/agent`, `/health`, `/clear`
   - Reranking: `rerank()` com diferentes inputs
   - Estratégias de chunking: Recursive, Markdown, Code, Semantic
