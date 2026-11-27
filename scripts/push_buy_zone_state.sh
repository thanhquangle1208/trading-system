#!/usr/bin/env bash
# Đẩy file trạng thái (không bí mật) lên nhánh buy-zone-alert-state.
# Chỉ thêm đúng hai đường dẫn. Không stage phần còn lại của repo.
set -euo pipefail

BRANCH="buy-zone-alert-state"
SRC="${1:-.state/buy_zones.json}"

if [[ ! -f "$SRC" ]]; then
  echo "Không có file trạng thái ($SRC) — bỏ qua."
  exit 0
fi

if grep -E -q 'TELEGRAM_BOT_TOKEN|NOTION_TOKEN|Bearer |xoxb-|secret_' "$SRC"; then
  echo "File trạng thái có vẻ chứa bí mật — không đẩy." >&2
  exit 1
fi

TMP_STATE="$(mktemp)"
cp "$SRC" "$TMP_STATE"

git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git fetch --depth 1 origin "$BRANCH"
  git switch -C "$BRANCH" FETCH_HEAD
else
  git switch --orphan "$BRANCH"
fi

mkdir -p state
cp "$TMP_STATE" state/buy_zones.json
rm -f "$TMP_STATE"

cat > README.md << 'EOF'
# Trạng thái cảnh báo vùng mua

Nhánh này không chứa code và không chứa bí mật.

`state/buy_zones.json` chỉ lưu cờ đã báo / chưa báo: id trang Notion, đang ở trong vùng hay không, mức vô hiệu đã báo, ngày bản tin sáng, và id CoinGecko.

Không có token Telegram, không có Notion token, không có ghi chú phân tích.

GitHub Actions cập nhật file này mỗi lần chạy để không báo trùng sau khi runner tắt.
Cache của GitHub Actions có thể bị xóa sau vài ngày không dùng, nên không dùng cache cho việc này.
EOF

git add -f -- state/buy_zones.json README.md
if git diff --cached --quiet; then
  echo "Trạng thái không đổi."
  exit 0
fi
while IFS= read -r name; do
  [ -z "$name" ] && continue
  case "$name" in
    state/buy_zones.json|README.md) ;;
    *)
      echo "Từ chối commit file lạ trên nhánh trạng thái: $name" >&2
      exit 1
      ;;
  esac
done <<< "$(git diff --cached --name-only)"

git commit -m "Update buy-zone alert dedupe state"
git push origin "HEAD:${BRANCH}"
echo "Đã đẩy nhánh ${BRANCH}."
