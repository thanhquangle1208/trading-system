#!/usr/bin/env bash
# Cài một lần trên Mac: venv + thư viện + kiểm tra .env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "1) Tạo / dùng môi trường Python (.venv)..."
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

echo "2) Cài thư viện từ requirements.txt..."
python -m pip install --upgrade pip
pip install -r "$ROOT/requirements.txt"

echo "3) Kiểm tra import..."
python - <<'PY'
import certifi
import pydantic
import truststore
import yaml
import dotenv
print("OK — pydantic", pydantic.__version__)
print("OK — certifi", certifi.where())
print("OK — truststore")
PY

echo "4) Kiểm tra file .env..."
if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Đã tạo .env từ .env.example — hãy mở file và điền 3 token rồi chạy lại setup."
  echo "  open -e $ROOT/.env"
  exit 1
fi

missing=0
for key in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID NOTION_TOKEN; do
  val="$(grep -E "^${key}=" "$ROOT/.env" | tail -n1 | cut -d= -f2- || true)"
  if [[ -z "${val// }" ]]; then
    echo "Thiếu giá trị: $key"
    missing=1
  else
    echo "Có: $key"
  fi
done
if [[ "$missing" -ne 0 ]]; then
  echo "Mở .env và điền đủ 3 dòng, lưu lại, rồi chạy lại: bash scripts/mac/setup_once.sh"
  echo "  open -e $ROOT/.env"
  exit 1
fi

echo
echo "Xong. Bật bot bằng:"
echo "  bash scripts/mac/start_buy_zones.sh"
