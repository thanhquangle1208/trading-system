#!/usr/bin/env bash
# Chạy một lần (phù hợp cron/launchd Interval): fetch → pull+restart nếu cần.
set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"

require_repo
if remote_has_updates; then
  log "Có update → pull + restart"
  pull_latest
  restart_scanner
else
  log "Không có update"
  if ! scanner_running; then
    log "Scanner chưa chạy → start"
    start_scanner
  fi
fi
