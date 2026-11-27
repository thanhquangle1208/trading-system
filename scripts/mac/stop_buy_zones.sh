#!/usr/bin/env bash
# Tắt bot trên Mac. Khoảng 20 phút sau GitHub tự chạy thay.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PID_FILE="$ROOT/.state/buy_zones.pid"
touch "$ROOT/.state/buy_zones.stop"

if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE" || true)"
  if [[ -n "$pid" ]]; then
    pkill -P "$pid" 2>/dev/null || true
    kill "$pid" 2>/dev/null || true
  fi
  rm -f "$PID_FILE"
fi

# Dọn process sót (pid cũ, hoặc đổi nhánh lúc đang chạy).
pkill -f "$ROOT/scripts/mac/loop_buy_zones.sh" 2>/dev/null || true
pkill -f "$ROOT/scripts/mac/run_once.sh" 2>/dev/null || true

echo "Đã tắt bot Mac. GitHub sẽ nhận việc khi nhịp cũ hơn 20 phút."
