#!/usr/bin/env bash
# Mac 24/7: scanner + tự pull khi GitHub có commit mới (prompt từ iPhone).
# An toàn: giữ watchlist.local + .runtime (cooldown), giết orphan, chỉ ff-only.
set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"

require_repo
log "=== Auto-update ON ==="
log "Repo=$REPO_DIR | Nhánh=$GIT_BRANCH | Mỗi ${CHECK_EVERY_SEC}s"
log "Ctrl+C dừng vòng này. Dừng bot: ./stop_scanner.sh"

start_scanner || true

while true; do
  if remote_has_updates; then
    log "Có commit mới trên GitHub → pull an toàn + restart"
    if safe_pull; then
      restart_scanner || log "Restart thất bại — xem $LOG_FILE"
    else
      log "Pull thất bại — giữ scanner đang chạy (nếu còn)"
      if ! scanner_running; then
        start_scanner || true
      fi
    fi
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Không có update mới" >>"$UPDATE_LOG"
    if ! scanner_running; then
      log "Scanner chết → start lại (giữ .runtime)"
      start_scanner || true
    fi
  fi
  sleep "$CHECK_EVERY_SEC"
done
