# Dia 14 — Polimento

> **Status: IMPLEMENTADO** ✨

---

## O que foi feito

### Melhorias de código

| Melhoria | Arquivo | Descrição |
|----------|---------|-----------|
| Configuração de CORS | `app/config.py`, `app/main.py` | `cors_origins` configurável via env var |
| Validação de upload | `app/rag/routes.py` | Limite de tamanho configurável (`max_upload_size_mb`) |
| Info do pacote | `app/__init__.py` | Exporta `__version__` e `__app_name__` |
| .env.example atualizado | `backend/.env.example` | Novas variáveis de tracing e CORS |

### Variáveis de ambiente adicionadas

| Variável | Default | Descrição |
|----------|---------|-----------|
| `RAG_CORS_ORIGINS` | `["*"]` | Origens permitidas no CORS |
| `RAG_MAX_UPLOAD_SIZE_MB` | `10` | Tamanho máximo de upload em MB |
