# Dia 11 — Deploy (Produção)

> **Status: IMPLEMENTADO** 🚀  
> Stack completa de produção com Docker Compose + Nginx + health checks.

---

## O que foi implementado

### 1. Dockerfile otimizado para produção
- **Multi-stage build:** estágio builder compila dependências, estágio runtime é enxuto
- **Usuário não-root:** executa como `app` (UID 1001) — segurança
- **Healthcheck:** valida endpoint `/api/v1/health` periodicamente
- **Labels:** metadados na imagem
- **Removido:** `EXPOSE 9000` legado do MCP antigo
- **Variáveis de ambiente:** `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`, etc.

### 2. `.dockerignore`
- Exclui `venv/`, `__pycache__/`, `.git/`, `data/`, `.env` do build context
- Mantém o build leve e rápido

### 3. `docker-compose.yml` (dev) — atualizado
- Healthcheck adicionado ao serviço `api`
- Startup mais robusto

### 4. `docker-compose.prod.yml` — novo (produção)
| Serviço | Função | Limites |
|---------|--------|---------|
| `api` | FastAPI + RAG + Agentes + MCP | 2GB max / 512MB reserverd |
| `ollama` | LLM + Embeddings | 4GB max / 1GB reserved |
| `ollama-init` | Download de modelos (one-shot) | - |
| `nginx` | Reverse proxy + headers de segurança | 128MB max / 64MB reserved |

**Diferenças do dev para produção:**

| Aspecto | Dev | Produção |
|---------|-----|----------|
| Portas | `8000:8000` (direto) | `80:80` (via nginx) |
| Debug | `RAG_DEBUG=true` | `RAG_DEBUG=false` |
| Reranking | padrão | `RAG_RERANKING_ENABLED=true` |
| Logging | padrão Docker | json-file, rotacionado (10MB, 3 arquivos) |
| Recursos | sem limites | limites definidos por serviço |
| Volumes | nomes automáticos | nomes explícitos (`rag_chroma_data`, `rag_ollama_data`) |

### 5. Nginx Reverse Proxy
- Proxy reverso para API em `/api/`
- Headers de segurança: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`
- Suporte a SSE (streaming): `proxy_buffering off`, `chunked_transfer_encoding on`
- Proxy para Swagger UI em `/docs`
- Endpoint `/health` para health checks externos

### 6. `scripts/deploy.sh`
Script de deploy com comandos:

```bash
./scripts/deploy.sh              # build + start
./scripts/deploy.sh build        # só builda
./scripts/deploy.sh start        # só sobe
./scripts/deploy.sh stop         # para
./scripts/deploy.sh restart      # rebuilda + sobe
./scripts/deploy.sh logs         # segue logs
./scripts/deploy.sh clean        # para + remove volumes
```

---

## Como usar

### Desenvolvimento (local)

```bash
cd backend
docker compose up -d ollama        # Só Ollama no Docker
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Stack completa via Docker (dev)

```bash
cd backend
docker compose up --build
```

### Produção (com Nginx)

```bash
cd backend
./scripts/deploy.sh
# ou manualmente:
docker compose -f docker-compose.prod.yml -p rag up -d --build
```

Acessar:
- **API:** `http://localhost/api/v1/health`
- **Swagger:** `http://localhost/docs`
- **Health check externo:** `http://localhost/health`

### Produção com SSL (HTTPS)

Para adicionar SSL com Let's Encrypt:

1. Descomente/configuração SSL no `nginx/nginx.conf` (ou use um proxy externo como Caddy/Traefik)
2. Aponte seu domínio para o servidor
3. Use `certbot` para gerar certificados:
   ```bash
   certbot --nginx -d seu-dominio.com
   ```

---

## Arquivos criados/modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `backend/.dockerignore` | ✨ Novo | Exclusões do build context |
| `backend/Dockerfile` | 🔄 Refatorado | Multi-stage + non-root + labels |
| `backend/docker-compose.yml` | 🔄 Atualizado | Healthcheck no API |
| `backend/docker-compose.prod.yml` | ✨ Novo | Stack de produção com limites |
| `backend/nginx/nginx.conf` | ✨ Novo | Reverse proxy + headers segurança |
| `backend/scripts/deploy.sh` | ✨ Novo | Script de deploy automatizado |
| `docs/dia-11-deploy.md` | ✨ Novo | Documentação do deploy |
