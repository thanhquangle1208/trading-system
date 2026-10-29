# Mac — Scanner + auto-update an toàn

Prompt trên **iPhone** → agent **push GitHub** → Mac (bật 24/7) tự `pull` + restart.

## Bug cũ đã vá

| Bug cũ | Cách mới |
|--------|----------|
| Reset → quên cooldown → spam tin ~10′ | Cooldown lưu `scanner/.runtime/` — **sống qua restart** |
| `/add` sửa `watchlist.yaml` → `git pull` bị chặn | Cặp nằm ở `watchlist.local.yaml` (**gitignore**) |
| Process cũ sót → `/help` không có `/top` | `stop` **giết hết** orphan `sd_scanner` |
| Pull lệch nhánh | Chỉ `git pull --ff-only`; diverged → **không** tự pull |

**Restart ≠ báo lại toàn bộ.** Luật 30′/60′ vẫn giữ nhờ file cooldown trên đĩa.

## Cài một lần

```bash
cd ~/trading-system
git fetch origin cursor/trading-thesis-pine-de71
git checkout cursor/trading-thesis-pine-de71
git pull origin cursor/trading-thesis-pine-de71

cd scanner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd mac
cp config.env.example config.env
# Sửa REPO_DIR nếu cần
chmod +x *.sh
```

`.env` ở **gốc repo** (token Telegram).

Nếu bạn đang có nhiều cặp trong `watchlist.yaml`: lần chạy đầu bot (hoặc auto-update) sẽ **migrate** sang `watchlist.local.yaml`.

## Chạy 24/7 (khuyên dùng)

```bash
cd ~/trading-system/scanner/mac
./stop_scanner.sh
./start_with_autoupdate.sh
```

Giữ Terminal mở (hoặc chạy nền). Mac **không sleep** sâu.

Dừng bot:

```bash
./stop_scanner.sh
```

## Kiểm tra sau cập nhật

1. `/help` có **`/top`**  
2. `/status` có `Bản code: /top · …`  
3. Log: `scanner/mac/logs/auto_update.log` — dòng “Có commit mới…” khi agent vừa push  

## Chỉ start tay (không vòng pull)

```bash
./start_scanner.sh
```
