# Dia 12 — LLMOps: Tracing com OpenTelemetry

> **Status: IMPLEMENTADO** 📊

---

## O que foi implementado

### 1. Módulo de Tracing (`app/infra/tracing.py`)

Classe `TracingManager` com os métodos:

| Método | Descrição |
|--------|-----------|
| `setup()` | Inicializa TracerProvider com resource e exporters |
| `instrument_app(app)` | Instrumenta FastAPI (requests, rotas, status) |
| `instrument_httpx()` | Instrumenta chamadas HTTP (cliente httpx) |
| `get_tracer()` | Retorna tracer para spans manuais |
| `shutdown()` | Finaliza tracing (flush de spans) |
| `create_span()` | Context manager para spans manuais |

### 2. Configuração (`app/config.py`)

```python
tracing_enabled: bool = False
tracing_otlp_endpoint: Optional[str] = None
```

### 3. Integração no `main.py`

- Tracing ativado condicionalmente por `RAG_TRACING_ENABLED`
- Instrumentação automática de FastAPI e httpx
- Shutdown hook para exportar spans pendentes

### 4. Docker Compose para Jaeger (`docker-compose.tracing.yml`)

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.tracing.yml up -d
```

- Adiciona Jaeger all-in-one (UI + collector OTLP)
- Ativa tracing na API com endpoint OTLP

### 5. Dependências adicionadas

```
opentelemetry-api==1.29.0
opentelemetry-sdk==1.29.0
opentelemetry-instrumentation-fastapi==0.50b0
opentelemetry-instrumentation-httpx==0.50b0
opentelemetry-exporter-otlp==1.29.0
```

---

## Como testar

### Dev (console exporter)

```bash
export RAG_TRACING_ENABLED=true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Faça algumas requisições e veja os spans no console
```

### Produção (Jaeger)

```bash
cd backend
docker compose -f docker-compose.prod.yml -f docker-compose.tracing.yml up -d
# Acesse Jaeger UI em http://localhost:16686
```
