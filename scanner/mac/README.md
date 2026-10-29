# Mac — chạy Scanner (không auto-update)

Agent cloud sửa code → **push GitHub**.  
Trên Mac bạn **`git pull` tay** rồi bật lại scanner.

> **Đã gỡ** `start_with_autoupdate.sh` (hay để sót process cũ → Telegram vẫn trả `/help` bản cũ, không có `/top`).

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
# Sửa REPO_DIR nếu repo không nằm ở ~/trading-system
chmod +x *.sh
```

Có file `.env` ở **gốc repo** (token Telegram).

## Mỗi lần cập nhật code (làm đúng thứ tự)

```bash
cd ~/trading-system
git pull origin cursor/trading-thesis-pine-de71

cd scanner/mac
./stop_scanner.sh
./start_scanner.sh
```

`stop` sẽ **giết cả process orphan** (scanner cũ còn sống ngoài pid file).  
`start` kiểm tra `watch.py` **phải có `/top`** — sai repo/path thì báo lỗi, không chạy nhầm.

## Kiểm tra trên Telegram

1. `/help` → **phải có dòng `/top`**  
2. `/status` → có dòng `Bản code: … /top …`  
3. Nếu `/help` không có `/top` → đang chạy nhầm thư mục hoặc chưa pull: xem `config.env` → `REPO_DIR`

## Log

- `scanner/mac/logs/scanner.log` — output bot  
- `scanner/mac/logs/scanner_run.log` — start/stop  

## Chi phí

$0 — không VPS, không auto-pull.
