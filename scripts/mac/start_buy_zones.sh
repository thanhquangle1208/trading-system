#!/usr/bin/env bash
# Bật bot trên Mac. GitHub sẽ nhường khi máy này còn nhịp.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p .state
PID_FILE="$ROOT/.state/buy_zones.pid"
LOG_FILE="$ROOT/.state/buy_zones.log"
rm -f "$ROOT/.state/buy_zones.stop"

if [[ ! -x "$ROOT/scripts/mac/run_once.sh" || ! -x "$ROOT/scripts/mac/loop_buy_zones.sh" ]]; then
  echo "Thiếu script Mac. Anh đang đứng nhánh chưa có scripts/mac/."
  echo "Chạy: git checkout main && git pull"
  echo "Hoặc: git checkout cursor/mac-github-failover-688b"
  exit 1
fi

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Chưa có .venv. Chạy một lần:"
  echo "  bash scripts/mac/setup_once.sh"
  exit 1
fi

if ! "$ROOT/.venv/bin/python" -c "import pydantic, yaml, dotenv, certifi, truststore" 2>/dev/null; then
  echo "Thiếu thư viện Python (vd. pydantic/certifi/truststore). Chạy một lần:"
  echo "  bash scripts/mac/setup_once.sh"
  exit 1
fi

# Dọn process sót trước khi bật mới.
pkill -f "$ROOT/scripts/mac/loop_buy_zones.sh" 2>/dev/null || true
rm -f "$PID_FILE"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Thiếu file .env. Chạy:"
  echo "  bash scripts/mac/setup_once.sh"
  exit 1
fi

for key in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID NOTION_TOKEN; do
  val="$(grep -E "^${key}=" "$ROOT/.env" | tail -n1 | cut -d= -f2- || true)"
  if [[ -z "${val// }" ]]; then
    echo "File .env thiếu $key. Mở và điền rồi lưu:"
    echo "  open -e $ROOT/.env"
    exit 1
  fi
done

: > "$LOG_FILE"
nohup bash "$ROOT/scripts/mac/loop_buy_zones.sh" >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Đã bật bot trên Mac (pid $(cat "$PID_FILE"))."
echo "Log: $LOG_FILE"
echo "Xem log: tail -n 40 $LOG_FILE"
echo "Tắt: bash scripts/mac/stop_buy_zones.sh"
