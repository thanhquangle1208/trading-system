#!/usr/bin/env bash
# Lặp đến khi stop_buy_zones.sh dừng.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
INTERVAL="${BUY_ZONE_INTERVAL_SEC:-600}"

while true; do
  if [[ -f "$ROOT/.state/buy_zones.stop" ]]; then
    rm -f "$ROOT/.state/buy_zones.stop"
    echo "Đã dừng vòng lặp Mac."
    exit 0
  fi
  bash "$ROOT/scripts/mac/run_once.sh" || echo "Vòng này lỗi, sẽ thử lại."
  sleep "$INTERVAL"
done
