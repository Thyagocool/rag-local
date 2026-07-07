#!/usr/bin/env bash
# =============================================================================
# Deploy — RAG + Agentes + MCP
#
# Modos de uso:
#   ./scripts/deploy.sh              → deploy completo (build + start)
#   ./scripts/deploy.sh build        → só builda as imagens
#   ./scripts/deploy.sh start        → só sobe os containers
#   ./scripts/deploy.sh stop         → para os containers
#   ./scripts/deploy.sh logs         → segue os logs
#   ./scripts/deploy.sh clean        → para + remove volumes
# =============================================================================
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="rag"

# ─── Cores ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

# ─── Help ────────────────────────────────────────────────────────────────────
show_help() {
    cat <<EOF
Uso: ./scripts/deploy.sh [comando]

Comandos:
  build       Builda as imagens Docker
  start       Sobe os containers em modo detached
  stop        Para os containers
  restart     Rebuilda + sobe
  logs        Segue os logs de todos os serviços
  clean       Para e remove containers + volumes
  help        Mostra esta mensagem

Sem argumento, executa build + start.
EOF
}

# ─── Comandos ────────────────────────────────────────────────────────────────
cmd_build() {
    log "Buildando imagens..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --pull
    log "Build concluído!"
}

cmd_start() {
    log "Subindo containers..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    log "Stack rodando!"
    log "API:      http://localhost/api/v1/health"
    log "Swagger:  http://localhost/docs"
}

cmd_stop() {
    log "Parando containers..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    log "Containers parados."
}

cmd_logs() {
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
}

cmd_clean() {
    warn "Parando e removendo tudo (incluindo volumes)..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v
    log "Limpeza concluída."
}

cmd_restart() {
    cmd_build
    cmd_start
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
    cd "$(dirname "$0")/.."

    case "${1:-}" in
        build)   cmd_build ;;
        start)   cmd_start ;;
        stop)    cmd_stop ;;
        restart) cmd_restart ;;
        logs)    cmd_logs ;;
        clean)   cmd_clean ;;
        help)    show_help ;;
        *)
            cmd_build
            cmd_start
            ;;
    esac
}

main "$@"
