#!/usr/bin/env bash
# Hàm chung — không chạy trực tiếp.

set -euo pipefail

MAC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
if [[ -f "$MAC_DIR/config.env" ]]; then
  # shellcheck source=/dev/null
  source "$MAC_DIR/config.env"
fi

REPO_DIR="${REPO_DIR:-$HOME/trading-system}"
GIT_BRANCH="${GIT_BRANCH:-cursor/trading-thesis-pine-de71}"
CHECK_EVERY_SEC="${CHECK_EVERY_SEC:-600}"

SCANNER_DIR="$REPO_DIR/scanner"
VENV_PY="$SCANNER_DIR/.venv/bin/python"
PID_FILE="$MAC_DIR/scanner.pid"
LOG_DIR="$MAC_DIR/logs"
LOG_FILE="$LOG_DIR/scanner.log"
UPDATE_LOG="$LOG_DIR/auto_update.log"

mkdir -p "$LOG_DIR"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg" | tee -a "$UPDATE_LOG"
}

require_repo() {
  if [[ ! -d "$REPO_DIR/.git" ]]; then
    log "ERROR: Không thấy repo tại $REPO_DIR — sửa REPO_DIR trong config.env"
    exit 1
  fi
  if [[ ! -x "$VENV_PY" ]]; then
    log "ERROR: Chưa có venv. Chạy: cd $SCANNER_DIR && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
  fi
  if [[ ! -f "$REPO_DIR/.env" ]]; then
    log "ERROR: Thiếu $REPO_DIR/.env (TELEGRAM_BOT_TOKEN + CHAT_ID)"
    exit 1
  fi
}

scanner_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

stop_scanner() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      log "Dừng scanner pid=$pid"
      kill "$pid" 2>/dev/null || true
      # chờ tắt gọn
      for _ in 1 2 3 4 5; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi
}

start_scanner() {
  require_repo
  if scanner_running; then
    log "Scanner đã chạy (pid=$(cat "$PID_FILE")) — bỏ qua start"
    return 0
  fi
  log "Khởi động scanner…"
  (
    cd "$SCANNER_DIR"
    # nohup để không chết khi đóng terminal (nếu chạy qua launchd/loop)
    nohup "$VENV_PY" -m sd_scanner scan >>"$LOG_FILE" 2>&1 &
    echo $! >"$PID_FILE"
  )
  sleep 2
  if scanner_running; then
    log "Scanner OK pid=$(cat "$PID_FILE") — log: $LOG_FILE"
  else
    log "ERROR: Scanner không lên được — xem $LOG_FILE"
    return 1
  fi
}

restart_scanner() {
  stop_scanner
  start_scanner
}

# Trả 0 nếu remote có commit mới hơn local
remote_has_updates() {
  require_repo
  cd "$REPO_DIR"
  git fetch origin "$GIT_BRANCH" --quiet
  local local_sha remote_sha
  local_sha="$(git rev-parse HEAD)"
  remote_sha="$(git rev-parse "origin/$GIT_BRANCH" 2>/dev/null || true)"
  if [[ -z "$remote_sha" ]]; then
    log "ERROR: Không thấy origin/$GIT_BRANCH"
    return 1
  fi
  if [[ "$local_sha" == "$remote_sha" ]]; then
    return 1  # không có update (bash: return 1 = false cho "has updates")
  fi
  # local behind remote?
  if git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
    return 0
  fi
  # diverged — vẫn pull với ff-only sẽ fail; báo
  log "WARN: Local và remote lệch nhau (diverged). local=$local_sha remote=$remote_sha"
  return 0
}

pull_latest() {
  require_repo
  cd "$REPO_DIR"
  log "git pull origin $GIT_BRANCH …"
  git checkout "$GIT_BRANCH" 2>/dev/null || git checkout -B "$GIT_BRANCH" "origin/$GIT_BRANCH"
  git pull --ff-only origin "$GIT_BRANCH"
  log "Pull xong: $(git rev-parse --short HEAD)"
}
