#!/usr/bin/env bash
# Bật scanner một lần (không vòng auto-update).
set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"
require_repo
log "=== Start scanner (một lần) ==="
start_scanner
