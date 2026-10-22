# Hệ thống giao dịch (Trading System)

Repo tài liệu + (sau này) mã nguồn cho Tomas: **chốt trading thesis trên TradingView trước**, rồi mới bot Python / Telegram / dashboard.

> **Hiện tại:** đang làm **Trading Thesis (Pine)** — bot Phase 1 **hoãn**. Đọc **HANDOFF** rồi **T0** trước khi code.

---

## Bắt đầu từ đâu?

1. Checkout nhánh làm việc mới nhất (xem HANDOFF — hiện: **`cursor/trading-thesis-pine-43e3`**).
2. Đọc theo thứ tự:

| Thứ tự | File | Nội dung |
|--------|------|----------|
| 1 | [docs/HANDOFF.md](docs/HANDOFF.md) | Trạng thái, quyết định, quy tắc agent |
| 2 | [docs/thesis/T0-trading-thesis.md](docs/thesis/T0-trading-thesis.md) | Thesis: tích hợp TV = Pine; vốn $10k; BTCUSDT.P |
| 2b | [docs/thesis/method-sd-wyckoff-pa.md](docs/thesis/method-sd-wyckoff-pa.md) | Phương pháp: S/D + Wyckoff + PA + Trend line |
| 3 | [docs/architecture-roadmap.md](docs/architecture-roadmap.md) | Kiến trúc bot dài hạn (hoãn) |
| 4 | [docs/project-context.md](docs/project-context.md) | Ngữ cảnh ngắn |
| 5 | [docs/cost-estimate.md](docs/cost-estimate.md) | Chi phí |
| 6 | [docs/preferences.md](docs/preferences.md) | Cách làm việc |

---

## Hiểu nhanh: chart TV như ảnh

- **Pine Script** chạy **trong** TradingView → vẽ hộp lệnh + bảng THỐNG KÊ lên chart.
- **Python bot** chạy **ngoài** TV → không vẽ vào chart TV; dùng sau khi thesis ổn.

Chart thesis: **BINANCE:BTCUSDT.P**, vốn paper **$10.000**.

---

## Lộ trình

| Bước | Nội dung | Trạng thái |
|------|----------|------------|
| **T0** | Method S/D–Wyckoff–PA | **OK** (TP 2R, TF 5m, volume bắt buộc) |
| **T3c** | WR-first, TP **1.5R**, mục tiêu WR ~60% | **Dùng** [`pine/T3c_wr60_tp15.pine`](pine/T3c_wr60_tp15.pine) |
| **T3b** | Optimize phí/SL | [`pine/T3b_optimize_thongke.pine`](pine/T3b_optimize_thongke.pine) |
| **Tiếp** | Đo WR T3c trên BTCUSDT.P 5m | Đang |
| Phase 1–6 bot | Bybit/ccxt, paper, Telegram, dashboard… | **Hoãn** |

Mỗi bước: Tomas duyệt rồi mới code (vd. “OK T0”, “OK T1”).

---

## Bảo mật

Không commit API key / Telegram token. Bot dùng `.env` khi đến Phase 1.
