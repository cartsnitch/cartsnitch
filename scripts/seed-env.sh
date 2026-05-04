#!/usr/bin/env bash
# =============================================================================
# seed-env.sh — Run the CartSnitch seed runner against any CartSnitch database.
#
# Usage:
#   ./seed-env.sh [--env dev|uat] [--dry-run] [--help]
#   ./seed-env.sh uat --dry-run   Run dry-run against UAT
#   ./seed-env.sh dev            Run full seed against dev (default)
#
# Prerequisites:
#   - kubectl configured for the target cluster
#   - Namespace cartsnitch-<env> exists (CNPG Postgres must be running)
#
# What it does:
#   1. Starts a background port-forward to cartsnitch-pg-rw:5432
#   2. Waits for the tunnel to be ready
#   3. Runs python -m cartsnitch_common.seed with --database-url pointing
#      to localhost:<forwarded-port>/cartsnitch
#   4. Cleans up the port-forward on exit (normal, interrupt, or error)
# =============================================================================

set -euo pipefail

# --- Config -------------------------------------------------------------------
ENV="${1:-dev}"
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV="$2"; shift 2 ;;
    --dry-run|--help) break ;;
    *) break ;;
  esac
done

NAMESPACE="cartsnitch-${ENV}"
SVC_NAME="cartsnitch-pg-rw"
LOCAL_PORT="5433"
DB_NAME="cartsnitch"
PG_USER="cartsnitch"
PG_PASSWORD="$(
  kubectl get secret cartsnitch-pg-credentials \
    -n "$NAMESPACE" \
    -o jsonpath='{.data.password}' \
  | base64 -d
)"
DB_URL="postgresql://${PG_USER}:${PG_PASSWORD}@localhost:${LOCAL_PORT}/${DB_NAME}"

# --- Helpers ------------------------------------------------------------------
log()  { echo "[seed-env] [$ENV] $*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

cleanup() {
  if [[ -n "${PF_PID:-}" ]]; then
    log "Stopping port-forward (PID $PF_PID)..."
    kill "$PF_PID" 2>/dev/null || true
    wait "$PF_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# --- Args ---------------------------------------------------------------------
DRY_RUN=""
HELP_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN="--dry-run"; shift ;;
    --help)     HELP_FLAG="1"; shift ;;
    *)          fail "Unknown argument: $1";;
  esac
done

if [[ -n "$HELP_FLAG" ]]; then
  echo "Usage: $0 [--env dev|uat] [--dry-run] [--help]"
  echo ""
  echo "Positional / keyword arguments:"
  echo "  --env dev|uat    Target environment (default: dev)"
  echo "  --dry-run        Show planned record counts without writing"
  echo "  --help           Show this help"
  echo ""
  echo "Additional arguments are passed through to the seed runner."
  echo "Common seed-runner options:"
  echo "  --seed N         Set random seed (default: 42)"
  exit 0
fi

# --- Validate env --------------------------------------------------------------
if [[ "$ENV" != "dev" && "$ENV" != "uat" ]]; then
  fail "Invalid environment: $ENV (must be 'dev' or 'uat')"
fi

# --- Prerequisites ------------------------------------------------------------
if ! command -v kubectl &>/dev/null; then
  fail "kubectl not found — must be installed and configured."
fi

# --- Port-forward -------------------------------------------------------------
log "Starting port-forward ${SVC_NAME}:5432 -> localhost:${LOCAL_PORT} ..."
kubectl port-forward \
  -n "$NAMESPACE" \
  svc/"$SVC_NAME" \
  "${LOCAL_PORT}:5432" \
  &>/dev/null &
PF_PID=$!

sleep 2

if ! kill -0 "$PF_PID" 2>/dev/null; then
  fail "Port-forward failed to start."
fi
log "Port-forward active (PID $PF_PID) on localhost:${LOCAL_PORT}"

# --- Seed --------------------------------------------------------------------
log "Running seed against ${ENV} database..."
set -x
python -m cartsnitch_common.seed --database-url "$DB_URL" $DRY_RUN
set +x

log "Done."