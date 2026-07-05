# Dia 6 — Web Search Tool (agente pesquisar na internet)

## O que foi feito

### Problema
O agente so sabia o que estava nos documentos enviados e o que estava no prompt.
Nao conseguia responder perguntas sobre:
- Noticias atuais
- Previsao do tempo
- Cotacoes
- Informacoes que mudam com frequencia

### Solucao: Web Search via DuckDuckGo

Adicionada ferramenta de busca na internet usando DuckDuckGo (gratis, sem API key).

### Arquivo criado

```
app/agents/web_search.py
```

### Como funciona

```python
from app.agents.web_search import search_web

resultado = search_web(
    query="previsao do tempo hoje",
    max_results=5,
)
# Retorna string formatada com:
#   Titulo
#   Snippet (200 chars)
#   URL
```

### Tool do agente

Nova tool `search_web_tool` registrada no agente:

```python
@tool
def search_web_tool(query: str) -> str:
    """Pesquisa na internet em tempo real. Use para perguntas sobre
    noticias atuais, eventos recentes, ou informacoes que mudam com frequencia."""
    return search_web(query)
```

### Tools atualizadas (app/agents/tools.py)

Agora sao 5 tools:

| Tool | Descricao |
|------|-----------|
| `search_documents` | Busca nos documentos indexados (RAG) |
| `get_current_time` | Data e hora atual |
| `calculate` | Expressoes matematicas |
| `search_web_tool` | Pesquisa na internet |
| `list_available_tools` | Auto-descricao |

### Dependencia

Adicionado `ddgs` (DuckDuckGo Search) ao `requirements.txt`:
```
ddgs>=9.0.0
```

100% gratis, sem API key, sem cadastro.

## Como testar

### Direto pela tool
```python
python -c "from app.agents.web_search import search_web; print(search_web('noticias hoje', 3))"
```

### Pelo agente
```bash
curl -N -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Quais as principais noticias de hoje?", "thread_id": "web-test"}'
```

O agente vai decidir se precisa usar a web search ou se responde com os documentos.

## Proximos passos
- Limitar numero de chamadas web por conversa (evitar abuso)
- Cache de buscas recentes (evitar repetir a mesma busca)
- Fallback para Bing API ou SearXNG se DuckDuckGo falhar
