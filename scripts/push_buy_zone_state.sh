#!/usr/bin/env bash
# Giữ lệnh cũ. Phần đẩy thật nằm ở sync_buy_zone_state.sh (không đổi nhánh code).
set -euo pipefail
exec "$(cd "$(dirname "$0")" && pwd)/sync_buy_zone_state.sh" push "$@"
