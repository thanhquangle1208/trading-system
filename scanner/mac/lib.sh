#!/usr/bin/env bash
# Hàm chung Mac — không chạy trực tiếp.
# Auto-update an toàn: giữ watchlist.local + .runtime (cooldown), giết orphan.

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
RUN_LOG="$LOG_DIR/scanner_run.log"
UPDATE_LOG="$LOG_DIR/auto_update.log"
BACKUP_DIR="$MAC_DIR/.pull-backup"
RUNTIME_DIR="$SCANNER_DIR/.runtime"

mkdir -p "$LOG_DIR" "$BACKUP_DIR"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg" | tee -a "$RUN_LOG" >>"$UPDATE_LOG"
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
}

require_code_has_top() {
  if ! grep -q 'cmd == "/top"' "$SCANNER_DIR/sd_scanner/watch.py"; then
    log "ERROR: watch.py KHÔNG có /top — chưa pull đúng hoặc sai repo"
    return 1
  fi
  return 0
}

_list_scanner_pids() {
  pgrep -f "[p]ython.*sd_scanner|[.]venv/bin/python.*sd_scanner" 2>/dev/null || true
}

stop_scanner() {
  local pid orphans
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      log "Dừng scanner pid=$pid"
      kill "$pid" 2>/dev/null || true
      for _ in 1 2 3 4 5; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi
  orphans="$(_list_scanner_pids)"
  if [[ -n "${orphans:-}" ]]; then
    log "Dừng orphan sd_scanner: $orphans"
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
  [[ -n "$(_list_scanner_pids)" ]]
}

# Sao lưu file local trước pull (không đụng .runtime — git đã ignore)
backup_local_state() {
  mkdir -p "$BACKUP_DIR"
  if [[ -f "$SCANNER_DIR/watchlist.local.yaml" ]]; then
    cp -f "$SCANNER_DIR/watchlist.local.yaml" "$BACKUP_DIR/watchlist.local.yaml"
  fi
  # Migrate: nếu user vẫn sửa watchlist.yaml (cặp /add cũ), đổ sang local trước
  if [[ -x "$VENV_PY" ]]; then
    "$VENV_PY" - <<PY || true
from pathlib import Path
import yaml
scanner = Path(r"$SCANNER_DIR")
base = scanner / "watchlist.yaml"
local = scanner / "watchlist.local.yaml"
if not base.is_file():
    raise SystemExit(0)
raw = yaml.safe_load(base.read_text(encoding="utf-8")) or {}
syms = raw.get("symbols") or []
if not local.is_file() and syms:
    local.write_text(
        yaml.safe_dump({"symbols": syms}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print("migrated symbols -> watchlist.local.yaml")
elif local.is_file() and syms:
    # nếu local thiếu cặp mà yaml còn (hiếm) — không ghi đè local
    pass
PY
  fi
  if [[ -f "$SCANNER_DIR/watchlist.local.yaml" ]]; then
    cp -f "$SCANNER_DIR/watchlist.local.yaml" "$BACKUP_DIR/watchlist.local.yaml"
  fi
  # Backup cooldown + /top history (phòng hờ)
  if [[ -d "$RUNTIME_DIR" ]]; then
    mkdir -p "$BACKUP_DIR/runtime"
    cp -f "$RUNTIME_DIR"/* "$BACKUP_DIR/runtime/" 2>/dev/null || true
  fi
}

restore_local_state() {
  if [[ -f "$BACKUP_DIR/watchlist.local.yaml" ]]; then
    cp -f "$BACKUP_DIR/watchlist.local.yaml" "$SCANNER_DIR/watchlist.local.yaml"
    log "Đã giữ watchlist.local.yaml (danh sách cặp)"
  fi
  mkdir -p "$RUNTIME_DIR"
  if [[ -d "$BACKUP_DIR/runtime" ]]; then
    cp -f "$BACKUP_DIR/runtime"/* "$RUNTIME_DIR/" 2>/dev/null || true
    log "Đã giữ .runtime/ (cooldown 30–60p + lịch sử /top) — không spam lại sau restart"
  fi
}

# Trả 0 nếu remote có commit mới (local behind)
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
    return 1
  fi
  if git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
    return 0
  fi
  log "WARN: Local và remote lệch (diverged). local=$local_sha remote=$remote_sha — không auto-pull"
  return 1
}

safe_pull() {
  # Không dùng git stash -u (dễ cuốn mất watchlist.local / .runtime).
  # Backup local → reset --hard theo origin → restore local + cooldown.
  require_repo
  cd "$REPO_DIR"
  backup_local_state

  log "Đồng bộ code với origin/$GIT_BRANCH (reset --hard)…"
  git fetch origin "$GIT_BRANCH" --quiet
  git checkout "$GIT_BRANCH" 2>/dev/null || git checkout -B "$GIT_BRANCH" "origin/$GIT_BRANCH"
  if ! git reset --hard "origin/$GIT_BRANCH"; then
    log "ERROR: reset thất bại — không restart"
    restore_local_state
    return 1
  fi
  log "Code mới: $(git rev-parse --short HEAD)"
  restore_local_state
  require_code_has_top || return 1
  return 0
}

start_scanner() {
  require_repo
  require_code_has_top || return 1
  stop_scanner
  sleep 1

  # Đảm bảo .runtime tồn tại (cooldown sống qua restart)
  mkdir -p "$RUNTIME_DIR"
  if [[ -f "$RUNTIME_DIR/episode_state.json" ]]; then
    log "Cooldown cooldown: có episode_state.json — restart sẽ KHÔNG spam lại trong cửa sổ 30–60p"
  else
    log "Chưa có episode_state.json (lần đầu) — sau noti đầu tiên sẽ tạo"
  fi

  local head_sha
  head_sha="$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo "?")"
  log "Khởi động scanner… REPO=$REPO_DIR HEAD=$head_sha"

  (
    cd "$SCANNER_DIR"
    nohup "$VENV_PY" -m sd_scanner scan >>"$LOG_FILE" 2>&1 &
    echo $! >"$PID_FILE"
  )
  sleep 2
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    log "Scanner OK pid=$(cat "$PID_FILE")"
  else
    log "ERROR: Scanner không lên — xem $LOG_FILE"
    return 1
  fi
}

restart_scanner() {
  stop_scanner
  start_scanner
}
