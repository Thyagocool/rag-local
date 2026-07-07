# Dia 10 — Rate limiting + validações extras

> **Status: NÃO IMPLEMENTADO**  
> Nenhuma proteção contra abuso. Apenas validação básica com Pydantic.

---

## Rate limiting ❌

### O que não existe

- **Nenhuma dependência** de rate limit no `requirements.txt` (ex: `slowapi`)
- **Nenhum middleware** de rate limit no `main.py` (só tem `CORSMiddleware`)
- **Nenhum decorator** `@limiter.limit(...)` nas rotas
- **Nenhuma configuração** de rate limit no `config.py`
- **Nenhum header** de rate limit (`X-RateLimit-*`) nas respostas

### Recomendação

Usar `slowapi` (FastAPI + Redis opcional):

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@router.post("/ask")
@limiter.limit("10/minute")
def ask_rag(payload: AskRequest):
    ...
```

Sugestão de limites por rota:

| Rota | Limite sugerido | Justificativa |
|------|----------------|---------------|
| `POST /ask` | 10/min | Consulta ao RAG |
| `POST /ask/stream` | 5/min | Streaming é mais pesado |
| `POST /agent` | 10/min | Agente com tools |
| `POST /agent/stream` | 5/min | Streaming do agente |
| `POST /upload` | 10/min 5/upload | Upload de arquivos |
| `DELETE /clear` | 2/min | Operação destrutiva |
| `GET /health` | 30/min | Leve, sem limites |

---

## Validações extras ❌

### O que existe hoje (básico)

**Schemas Pydantic** — apenas validação de tipos obrigatórios:

| Arquivo | Schemas |
|---------|---------|
| `backend/app/rag/schemas.py` | `AskRequest` (question: str), `AskResponse`, `UploadResponse`, `Source` |
| `backend/app/agents/schemas.py` | `AgentRequest` (message: str, thread_id: optional), `AgentResponse` |
| `backend/app/api/routes.py` | `HealthResponse` |
| `backend/app/config.py` | `Settings` com `pydantic-settings` |

**Validações manuais nas rotas:**
- `/upload`: verifica se `filename` não é None e se extensão é suportada
- Demais rotas: sem validações extras além do Pydantic

### O que falta

1. **Validação de tamanho de mensagem:**
   ```python
   class AskRequest(BaseModel):
       question: str = Field(..., min_length=1, max_length=2000)
   ```

2. **Validação de tamanho de upload:**
   ```python
   # No upload route
   if len(content) > 10 * 1024 * 1024:  # 10MB
       raise HTTPException(400, "Arquivo muito grande")
   ```

3. **Sanitização de entrada:**
   - Remoção de caracteres de controle
   - Validação de encoding

4. **Proteção contra injection:**
   - O `calculate()` já tem eval seguro com `{"__builtins__": {}}` ✅
   - Mas merece revisão

5. **Autenticação/Autorização:**
   - API keys? 
   - Headers de autorização?

6. **Headers de segurança:**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Content-Security-Policy`

7. **Validação de `question` vazia:**
   ```python
   class AskRequest(BaseModel):
       question: str = Field(..., min_length=1, strip_whitespace=True)
   ```

### Recomendação de implementação

1. Adicionar `slowapi` no `requirements.txt`
2. Adicionar middleware de rate limit no `main.py`
3. Aprimorar schemas Pydantic com `Field()` validations
4. Adicionar validação de tamanho de upload
5. Adicionar headers de segurança (middleware)
6. Considerar `python-multipart` limits para upload
