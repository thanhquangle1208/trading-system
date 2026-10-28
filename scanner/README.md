# Scanner Telegram — Vùng Mua / Vùng Bán

Dành cho Tomas (newbie). Chương trình chạy trên **máy Mac của bạn**.  
**Không** tự mua/bán — chỉ báo Telegram khi giá cắt vào vùng.

Chi tiết thiết kế: [`docs/scanner/telegram-sd-alerts.md`](../docs/scanner/telegram-sd-alerts.md).

## Chuẩn bị một lần

1. Có file **`.env`** ở **thư mục gốc repo** (cạnh `README.md`), copy từ `.env.example`:

```bash
TELEGRAM_BOT_TOKEN=dán_token_vào_đây
TELEGRAM_CHAT_ID=dán_chat_id_vào_đây
WATCH_INTERVAL_SEC=45
```

2. Sửa cặp theo dõi: `scanner/watchlist.yaml` (mặc định BTC/ETH/SOL/BNB).

3. Cài Python 3.10+ rồi:

```bash
cd scanner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Mỗi lần bật máy muốn nhận noti

**Cách mới (khuyên dùng — làm việc trên điện thoại):** tự pull khi GitHub có commit mới:

Xem hướng dẫn: [`mac/README.md`](mac/README.md) → chạy `scanner/mac/start_with_autoupdate.sh`

**Cách cũ (thủ công):**

```bash
cd scanner
source .venv/bin/activate
python -m sd_scanner test    # lần đầu: kiểm tra Telegram
python -m sd_scanner scan    # scan 1 lần → tự theo dõi đến khi tắt
```

Giữ cửa sổ terminal **mở**. Tắt máy / Ctrl+C = hết noti.

Trên Telegram khi đang chạy:

| Lệnh | Việc |
|------|------|
| `/add LIT` | Tìm ticker Binance→Bybit, hiện 1 2 3… → gõ số để thêm |
| `/list` | Xem danh sách cặp |
| `/scan` | Rebuild vùng |
| `/status` | Trạng thái |
| `/stop` | Dừng |
| `/cancel` | Hủy bước chọn số sau `/add` |

## Chống spam (đã siết)

- Chỉ báo khi giá **thật sự trong** vùng giá (không đệm mép).
- Lắc nhẹ quanh mép **không** reset nhịp ngay.
- Cùng cặp+khung+vùng: cooldown mặc định **5 phút** (`watchlist.yaml` → `alert.cooldown_minutes`).

## Chi phí

- Telegram + Binance/Bybit public API: **$0**
- Không dùng token AI để quét giá
