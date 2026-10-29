#!/usr/bin/env bash
# Bật scanner trên Mac (KHÔNG auto git pull).
# Trước đó: git pull tay trong repo, rồi chạy script này.
set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"

require_repo
log "=== Start scanner (không autoupdate) ==="
start_scanner
