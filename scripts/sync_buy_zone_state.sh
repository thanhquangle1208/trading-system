#!/usr/bin/env bash
# Kéo / đẩy sổ trạng thái trên nhánh buy-zone-alert-state.
# Không đổi nhánh của thư mục code (an toàn trên máy Mac).
# Cách dùng:
#   scripts/sync_buy_zone_state.sh pull
#   scripts/sync_buy_zone_state.sh push [.state/buy_zones.json]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BRANCH="buy-zone-alert-state"
MODE="${1:-}"
SRC="${2:-.state/buy_zones.json}"

if [[ "$MODE" != "pull" && "$MODE" != "push" ]]; then
  echo "Dùng: $0 pull | push [file]" >&2
  exit 1
fi

branch_exists() {
  git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1
}

write_empty_state() {
  mkdir -p .state
  if [[ ! -f .state/buy_zones.json ]]; then
    printf '%s\n' '{"version":1,"zones":{},"last_digest_date":null,"coingecko_ids":{},"lease":{"holder":null,"heartbeat_utc":null}}' > .state/buy_zones.json
  fi
}

pull_state() {
  mkdir -p .state
  if branch_exists; then
    git fetch --depth 1 origin "$BRANCH"
    if git cat-file -e FETCH_HEAD:state/buy_zones.json 2>/dev/null; then
      git show FETCH_HEAD:state/buy_zones.json > .state/buy_zones.json
      echo "Đã lấy trạng thái từ nhánh ${BRANCH}."
      return 0
    fi
  fi
  write_empty_state
  echo "Chưa có sổ trên GitHub — dùng file local nếu có."
}

github_should_not_overwrite() {
  local remote_file="$1"
  PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 - "$SRC" "$remote_file" <<'PY'
import json
import sys
from datetime import datetime, timezone

from trading_system.zones.state import should_skip_push

def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    return raw if isinstance(raw, dict) else {}

local = load(sys.argv[1])
remote = load(sys.argv[2])
now = datetime.now(timezone.utc)
raise SystemExit(0 if should_skip_push(local, remote, now) else 1)
PY
}

push_state() {
  if [[ ! -f "$SRC" ]]; then
    echo "Không có file trạng thái ($SRC) — bỏ qua."
    return 0
  fi
  if grep -E -q 'TELEGRAM_BOT_TOKEN|NOTION_TOKEN|Bearer |xoxb-|secret_' "$SRC"; then
    echo "File trạng thái có vẻ chứa bí mật — không đẩy." >&2
    return 1
  fi

  if branch_exists; then
    git fetch --depth 1 origin "$BRANCH"
    remote_copy="$(mktemp)"
    if git cat-file -e FETCH_HEAD:state/buy_zones.json 2>/dev/null; then
      git show FETCH_HEAD:state/buy_zones.json > "$remote_copy"
      if github_should_not_overwrite "$remote_copy"; then
        rm -f "$remote_copy"
        echo "Mac đang giữ nhịp — không ghi đè sổ từ GitHub."
        return 0
      fi
    fi
    rm -f "$remote_copy"
  fi

  local_copy="$(mktemp)"
  cp "$SRC" "$local_copy"
  wt="$(mktemp -d)"
  cleanup() {
    git worktree remove --force "$wt" >/dev/null 2>&1 || true
    rm -rf "$wt"
    rm -f "$local_copy"
  }
  trap cleanup RETURN

  if branch_exists; then
    git fetch --depth 1 origin "$BRANCH"
    git worktree add --detach "$wt" FETCH_HEAD
  else
    git worktree add --detach "$wt" HEAD
    git -C "$wt" checkout --orphan "$BRANCH"
    git -C "$wt" rm -rf . >/dev/null 2>&1 || true
  fi

  mkdir -p "$wt/state"
  cp "$local_copy" "$wt/state/buy_zones.json"
  cat > "$wt/README.md" << 'EOF'
# Trạng thái cảnh báo vùng mua

Nhánh này không chứa code và không chứa bí mật.

`state/buy_zones.json` nhớ vùng đã báo, và nhịp `lease` (máy Mac hay GitHub đang chạy).
Không có token Telegram, không có Notion token, không có ghi chú phân tích.

Mac ghi nhịp mỗi lần chạy. GitHub chỉ chạy khi nhịp Mac cũ hơn 20 phút.
EOF

  git -C "$wt" add -f -- state/buy_zones.json README.md
  if git -C "$wt" diff --cached --quiet; then
    echo "Trạng thái không đổi."
    return 0
  fi
  while IFS= read -r name; do
    [ -z "$name" ] && continue
    case "$name" in
      state/buy_zones.json|README.md) ;;
      *)
        echo "Từ chối commit file lạ trên nhánh trạng thái: $name" >&2
        return 1
        ;;
    esac
  done <<< "$(git -C "$wt" diff --cached --name-only)"

  if git config user.email >/dev/null 2>&1; then
    git -C "$wt" commit -m "Update buy-zone alert dedupe state"
  else
    git -C "$wt" -c user.email="github-actions[bot]@users.noreply.github.com" \
      -c user.name="github-actions[bot]" \
      commit -m "Update buy-zone alert dedupe state"
  fi

  if ! git -C "$wt" push origin "HEAD:${BRANCH}"; then
    git -C "$wt" fetch origin "$BRANCH"
    git -C "$wt" rebase FETCH_HEAD
    git -C "$wt" push origin "HEAD:${BRANCH}"
  fi
  echo "Đã đẩy nhánh ${BRANCH}."
}

case "$MODE" in
  pull) pull_state ;;
  push) push_state ;;
esac
