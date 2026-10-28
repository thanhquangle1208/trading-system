#!/usr/bin/env bash
set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"
stop_scanner
log "Đã dừng scanner."
