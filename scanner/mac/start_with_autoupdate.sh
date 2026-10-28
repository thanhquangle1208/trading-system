#!/usr/bin/env bash
# Chạy trên Mac: bật scanner + vòng kiểm tra git mỗi CHECK_EVERY_SEC.
# Chỉ pull + restart khi có commit mới trên GitHub.

set -euo pipefail
MAC_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$MAC_DIR/lib.sh"

require_repo
log "=== Auto-update bật ==="
log "Repo: $REPO_DIR | Nhánh: $GIT_BRANCH | Mỗi ${CHECK_EVERY_SEC}s"
log "Ctrl+C để dừng vòng này (scanner nền có thể vẫn chạy — dùng stop_scanner.sh)"

# Lần đầu: đảm bảo scanner đang chạy
start_scanner || true

while true; do
  if remote_has_updates; then
    log "Phát hiện commit mới trên GitHub → pull + restart scanner"
    if pull_latest; then
      restart_scanner || log "Restart thất bại — xem $LOG_FILE"
    else
      log "Pull thất bại — không restart"
    fi
  else
    # Im: không restart, không Telegram — chỉ ghi 1 dòng vào file log
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Không có update mới" >>"$UPDATE_LOG"
    if ! scanner_running; then
      log "Scanner chết → khởi động lại"
      start_scanner || true
    fi
  fi
  sleep "$CHECK_EVERY_SEC"
done
