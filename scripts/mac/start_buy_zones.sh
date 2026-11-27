#!/usr/bin/env bash
# Bật bot trên Mac. GitHub sẽ nhường khi máy này còn nhịp.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p .state
PID_FILE="$ROOT/.state/buy_zones.pid"
LOG_FILE="$ROOT/.state/buy_zones.log"
rm -f "$ROOT/.state/buy_zones.stop"

if [[ -f "$PID_FILE" ]]; then
  old="$(cat "$PID_FILE" || true)"
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    echo "Bot Mac đang chạy (pid $old). Log: $LOG_FILE"
    exit 0
  fi
fi

nohup bash "$ROOT/scripts/mac/loop_buy_zones.sh" >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Đã bật bot trên Mac (pid $(cat "$PID_FILE"))."
echo "Log: $LOG_FILE"
echo "Tắt bằng: bash scripts/mac/stop_buy_zones.sh"
