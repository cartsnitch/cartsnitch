#!/usr/bin/env bash
# Backward-compat wrapper — delegates to seed-env.sh dev
exec "$(dirname "$0")/seed-env.sh" dev "$@"