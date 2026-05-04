#!/usr/bin/env bash
# =============================================================================
# apply-seed-job.sh — Apply the seed Job manifest for a given environment.
#
# Usage:
#   ./apply-seed-job.sh <env>
#
# Example:
#   ./apply-seed-job.sh uat
#   ./apply-seed-job.sh dev
# =============================================================================

set -euo pipefail

ENV="${1:-}"
HELP_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help) HELP_FLAG="1"; shift ;;
    *) ENV="$1"; shift ;;
  esac
done

if [[ -n "$HELP_FLAG" ]] || [[ -z "$ENV" ]]; then
  echo "Usage: $0 <env>"
  echo "  env   dev or uat"
  exit 0
fi

if [[ "$ENV" != "dev" && "$ENV" != "uat" ]]; then
  echo "ERROR: Invalid environment: $ENV (must be 'dev' or 'uat')" >&2
  exit 1
fi

SCRIPT_DIR="$(dirname "$0")"
sed "s/__ENV__/${ENV}/g" "${SCRIPT_DIR}/seed-env-job.yaml" | kubectl apply -f -
echo "Seed job applied for environment: $ENV"