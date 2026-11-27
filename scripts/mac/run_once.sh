#!/usr/bin/env bash
# Một vòng trên Mac: lấy sổ chung, ghi nhịp, kiểm tra vùng, đẩy sổ.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
else
  PY="$(command -v python3)"
fi
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

bash "$ROOT/scripts/sync_buy_zone_state.sh" pull
"$PY" -m trading_system.zones --runner local --claim-only
bash "$ROOT/scripts/sync_buy_zone_state.sh" push .state/buy_zones.json

set +e
"$PY" -m trading_system.zones --runner local
code=$?
set -e
bash "$ROOT/scripts/sync_buy_zone_state.sh" push .state/buy_zones.json
exit "$code"
