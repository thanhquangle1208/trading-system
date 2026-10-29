# Project context — Trading System

Ngắn gọn cho agent / phiên sau. Cập nhật khi Tomas chốt quyết định.

## Người dùng

- Tomas Le — mới bắt đầu, không nền tảng code.
- Muốn giải thích tiếng Việt, rõ ràng; duyệt thiết kế trước mỗi phase / bước thesis.

## Ưu tiên hiện tại (2026-10-21)

- **Hoãn** trading bot Phase 1–6.
- **Làm trước:** Trading Thesis trên **TradingView + Pine Script** (viết lại từ đầu).
- Phương pháp: **Supply/Demand + Wyckoff + Price Action + Trend line** (confluence) — [`thesis/method-sd-wyckoff-pa.md`](./thesis/method-sd-wyckoff-pa.md).
- Mục tiêu UI: giống ảnh — zones + hộp LONG/SHORT + bảng **THỐNG KÊ** tiếng Việt.
- Chart: **BINANCE:BTCUSDT.P**; vốn paper thesis **$10.000**; TF **5m**; TP **2R**; **volume bắt buộc**.
- Phương pháp **đã OK**; khóa: [`thesis/decisions-locked.md`](./thesis/decisions-locked.md).
- Pine T1: `pine/T1_trendline_volume.pine` + [`../pine/README.md`](../pine/README.md).
- **Pine** = thứ tích hợp vào chart TV. **Python không vẽ được lên chart TV.**

## Mục tiêu sản phẩm (dài hạn — bot, hoãn)

- Watchlist multi-TF: **M15, H1, H4, D1**; **BTC** cặp chính.
- Confluence: điều kiện **AND (required)** + **score ≥ threshold**; strategy bằng **YAML/JSON**.
- Mỗi tín hiệu/lệnh có **`rating` (1–10)** từ luật confluence/risk; hiện Telegram + DB; sau này analytics trung bình.
- Indicator plugins (interface chung): EMA34/89, RSI, MACD, BB, VWAP, ATR, Volume, market structure, S/R, candles/patterns; optional funding/OI/liq; **nhãn hiển thị tùy chỉnh** trong config.
- Layers: data → indicators → signal/confluence → risk → execution → notifier → storage → dashboard.
- Exchange: **CEX qua ccxt**, **Bybit trước** → Binance/CEX khác; toggle bằng `.env` + YAML. **DEX = adapter riêng, sau**.
- Storage: **SQLite trước → Postgres sau**; secrets `.env`; logging đầy đủ.
- Backtest multi-TF **no look-ahead**; fees/slippage/funding; metrics; Optuna + walk-forward.
- Dashboard UI mô phỏng panel thống kê + hộp lệnh — khi làm bot; **không** inject Python vào TradingView.
- Risk: % risk, ATR sizing, partial TP + runner; **perp bắt buộc SL**; limits + kill switch.
- Telegram: multi-channel / multi-TF / multi-method; `display_name`; routing YAML.
- Mỗi phase: **tests + README**; không nhảy phase khi chưa duyệt.

## Quyết định đã chốt

| Mục | Quyết định |
|-----|------------|
| **Ưu tiên** | **Pine thesis trước**; bot **hoãn** |
| Thesis script | Viết lại từ đầu trên TV |
| Thesis chart | **BINANCE:BTCUSDT.P**, TF học **5m** |
| Thesis vốn | **$10.000** |
| Thesis logic | Vừa làm vừa research |
| Ngôn ngữ bot (sau) | **Python** (ccxt, backtest, Optuna) |
| Sàn bot đầu (sau) | Bybit qua ccxt (CEX) |
| DEX | Adapter riêng, **sau** |
| TradingView | **A (Pine) đang làm** để chốt thesis; **B (Python UI)** khi bot |
| Chi phí | Ít opex — xem `cost-estimate.md` |
| Rating / Notifier | Giữ thiết kế — code khi bot |
| DB / Config bot | SQLite; YAML/JSON |
| Code Phase 1–6 | **Chưa / hoãn** — chờ “OK Phase 1” sau thesis |

## Chưa chốt (bot — không chặn thesis)

- Spot vs Perp primary cho **bot**
- Timezone (`Asia/Ho_Chi_Minh` vs UTC)
- Bybit API / testnet sẵn chưa
- Telegram bot token + chat ID; một hay nhiều kênh
- Ngưỡng score confluence mặc định
- Leverage tối đa (perp bot)
- **Rating:** nhãn “Rủi ro” hay “Độ tin cậy”?
- Ưu tiên DEX khi nào (nếu có)
- Chi tiết công thức Pine (trend/entry/TP R/phí/zone) — research trong T1–T5

## Tài liệu liên quan

- **Bàn giao agent (đọc trước):** [`HANDOFF.md`](./HANDOFF.md)
- **Thesis hiện tại:** [`thesis/T0-trading-thesis.md`](./thesis/T0-trading-thesis.md)
- Đề xuất bot (VN): [`architecture-roadmap.md`](./architecture-roadmap.md)
- Dự toán chi phí: [`cost-estimate.md`](./cost-estimate.md)
- Preferences: [`preferences.md`](./preferences.md)
- README repo: `/workspace/README.md`

## Quy ước làm việc

- Trước mỗi bước thesis / phase bot: đề xuất → duyệt → mới code.
- Sau mỗi lần làm: commit + push để agent khác tiếp tục.
- Không viết Pine trước “OK T0”/“OK T1…”. Không Phase 1 bot trước “OK Phase 1”.
