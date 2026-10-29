#!/usr/bin/env bash
# Hàm chung Mac — không chạy trực tiếp.
# Đã BỎ auto git pull / autoupdate (Tomas 2026-10-29).

set -euo pipefail

MAC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
if [[ -f "$MAC_DIR/config.env" ]]; then
  # shellcheck source=/dev/null
  source "$MAC_DIR/config.env"
fi

REPO_DIR="${REPO_DIR:-$HOME/trading-system}"
SCANNER_DIR="$REPO_DIR/scanner"
VENV_PY="$SCANNER_DIR/.venv/bin/python"
PID_FILE="$MAC_DIR/scanner.pid"
LOG_DIR="$MAC_DIR/logs"
LOG_FILE="$LOG_DIR/scanner.log"
RUN_LOG="$LOG_DIR/scanner_run.log"

mkdir -p "$LOG_DIR"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg" | tee -a "$RUN_LOG"
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
  if [[ ! -f "$SCANNER_DIR/sd_scanner/watch.py" ]]; then
    log "ERROR: Không thấy $SCANNER_DIR/sd_scanner/watch.py — sai REPO_DIR?"
    exit 1
  fi
  # Chặn chạy nhầm bản cũ không có /top
  if ! grep -q 'cmd == "/top"' "$SCANNER_DIR/sd_scanner/watch.py"; then
    log "ERROR: watch.py KHÔNG có lệnh /top."
    log "  → cd $REPO_DIR && git pull origin cursor/trading-thesis-pine-de71"
    log "  → Kiểm tra REPO_DIR trong $MAC_DIR/config.env có đúng thư mục vừa pull không"
    exit 1
  fi
}

_list_scanner_pids() {
  # Mọi process đang chạy module sd_scanner (tránh orphan trả lời Telegram bản cũ)
  pgrep -f "[p]ython.*sd_scanner|[.]venv/bin/python.*sd_scanner" 2>/dev/null || true
}

stop_scanner() {
  local pid
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      log "Dừng scanner pid=$pid (từ pid file)"
      kill "$pid" 2>/dev/null || true
      for _ in 1 2 3 4 5; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi

  # Quét orphan — đây là lý do /help vẫn bản cũ dù đã pull
  local orphans
  orphans="$(_list_scanner_pids)"
  if [[ -n "${orphans:-}" ]]; then
    log "Dừng thêm process sd_scanner còn sót: $orphans"
    # shellcheck disable=SC2086
    kill $orphans 2>/dev/null || true
    sleep 1
    orphans="$(_list_scanner_pids)"
    if [[ -n "${orphans:-}" ]]; then
      # shellcheck disable=SC2086
      kill -9 $orphans 2>/dev/null || true
    fi
  fi
  rm -f "$PID_FILE"
}

scanner_running() {
  local pid
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  # còn orphan?
  if [[ -n "$(_list_scanner_pids)" ]]; then
    return 0
  fi
  return 1
}

start_scanner() {
  require_repo
  # Luôn dừng sạch trước khi start (tránh 2 process / bản cũ)
  stop_scanner
  sleep 1

  local head_sha
  head_sha="$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo "?")"
  log "Khởi động scanner…"
  log "  REPO_DIR=$REPO_DIR"
  log "  HEAD=$head_sha (phải có /top trong watch.py)"
  log "  Python=$VENV_PY"

  (
    cd "$SCANNER_DIR"
    nohup "$VENV_PY" -m sd_scanner scan >>"$LOG_FILE" 2>&1 &
    echo $! >"$PID_FILE"
  )
  sleep 2
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    log "Scanner OK pid=$(cat "$PID_FILE") — log: $LOG_FILE"
    log "Trên Telegram: gõ /help — phải thấy /top. Gõ /status xem bản code."
  else
    log "ERROR: Scanner không lên được — xem $LOG_FILE"
    return 1
  fi
}
