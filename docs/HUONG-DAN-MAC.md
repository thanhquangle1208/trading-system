# Hướng dẫn Mac — bot vùng giá gom

Dành cho Tomas. Chỉ làm trên máy Mac. Không cần hiểu hết code.

## Bot này làm gì?

- Đọc Notion **Vùng giá gom token**
- Gửi Telegram khi giá vào vùng, hoặc khi nến ngày đóng dưới mức vô hiệu
- Máy Mac lấy giá Bybit / Binance
- GitHub chỉ chạy khi Mac tắt hơn khoảng 20 phút

## Cài một lần

Mở **Terminal**, gõ từng dòng:

```bash
cd ~/trading-system
git checkout main
git pull
bash scripts/mac/setup_once.sh
```

Nếu `setup_once.sh` bảo thiếu `.env`, mở file, điền 3 dòng rồi lưu:

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
NOTION_TOKEN=...
```

Chạy lại:

```bash
bash scripts/mac/setup_once.sh
```

## Mỗi ngày / mỗi lần mở máy

```bash
cd ~/trading-system
bash scripts/mac/start_buy_zones.sh
```

Xem log:

```bash
tail -n 40 .state/buy_zones.log
```

Tắt bot:

```bash
bash scripts/mac/stop_buy_zones.sh
```

## Nếu lỗi

| Chữ trong Terminal / log | Làm gì |
|--------------------------|--------|
| `No such file ... start_buy_zones.sh` | `git checkout main && git pull` |
| `No module named 'pydantic'` | `bash scripts/mac/setup_once.sh` |
| `CERTIFICATE_VERIFY_FAILED` / SSL | `bash scripts/mac/setup_once.sh` (cần `certifi`) rồi tắt/bật lại bot |
| `Thiếu NOTION_TOKEN` | `open -e .env` rồi điền, lưu |
| `Mac đang chạy` trên GitHub Actions | Bình thường — GitHub đang nhường Mac |
| Bot chạy nhưng log cũ lỗi lặp lại | `bash scripts/mac/stop_buy_zones.sh` rồi `bash scripts/mac/start_buy_zones.sh` |

## Không đụng gì?

- File `.env` — không commit
- Thư mục `.state/` — nhớ đã báo, không commit
- Việc scanner (nhánh `cursor/trading-thesis-pine-de71`) — bot khác, để riêng
