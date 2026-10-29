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

**Khuyên dùng trên Mac** (đã **bỏ** auto-update):

```bash
cd ~/trading-system
git pull origin cursor/trading-thesis-pine-de71
cd scanner/mac
./stop_scanner.sh
./start_scanner.sh
```

Chi tiết: [`mac/README.md`](mac/README.md).

**Hoặc thủ công trong terminal:**

```bash
cd scanner
source .venv/bin/activate
python -m sd_scanner test    # lần đầu: kiểm tra Telegram
python -m sd_scanner scan    # scan 1 lần → tự theo dõi đến khi tắt
```

Giữ process chạy. Tắt máy / Ctrl+C = hết noti.

Trên Telegram khi đang chạy:

| Lệnh | Việc |
|------|------|
| `/add LIT` | Tìm ticker (im lặng); **1 kết quả → thêm luôn** (`✅`); nhiều → chọn 1 2 3… |
| `/list` | Xem danh sách cặp |
| `/top` | **3 lệnh đáng xem nhất** trong 24h (tin đã noti; 1 lần/cặp; xếp đa tiêu chí) |
| `/scan` | Rebuild vùng |
| `/status` | Trạng thái |
| `/stop` | Dừng |
| `/cancel` | Hủy bước chọn số sau `/add` |

## Chất lượng > số lượng (đã siết nhiễu)

Cấu hình trong `watchlist.yaml` → `alert:`:

| Luật | Mặc định |
|------|----------|
| Khung **được phép báo tin** | **H4, D1, W1** (H1 chỉ tính confluence, không tự bắn) |
| Độ sâu tối thiểu | **≥ 7.0/10** (bỏ báo mới chạm mép ~6) |
| Số khung đồng thuận | **≥ 2** (độ tin cậy ≥ 7.0) |
| Cooldown cùng vùng | **30 phút** |
| Cooldown cùng cặp+chiều | **60 phút** (lưu file `scanner/.runtime/` — **không mất khi restart**) |
| Một vùng / một nhịp | **Chỉ 1 tin** (không báo lại khi giá sâu thêm trong cùng vùng) |
| **Nấc 1 — Bias W1** | **EMA 34 tuần**: MUA chỉ khi giá > EMA; BÁN chỉ khi giá < EMA (tin có dòng `🧭 Bias W1`) |
| STL tối thiểu | **Mọi tin** Entry→STL ≥ **2.5%**; mép vùng chỉ khi đã đủ xa; sát thì nới |

## Chi phí

- Telegram + Binance/Bybit public API: **$0**
- Không dùng token AI để quét giá
