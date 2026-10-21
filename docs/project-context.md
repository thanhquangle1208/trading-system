# Project context — Trading System

Ngắn gọn cho agent / phiên sau. Cập nhật khi Tomas chốt quyết định.

## Người dùng

- Tomas Le — mới bắt đầu, không nền tảng code.
- Muốn giải thích tiếng Việt, rõ ràng; duyệt thiết kế trước mỗi phase.

## Mục tiêu sản phẩm

- Watchlist multi-TF: **M15, H1, H4, D1**; **BTC** cặp chính.
- Confluence: điều kiện **AND (required)** + **score ≥ threshold**; strategy bằng **YAML/JSON**.
- Mỗi tín hiệu/lệnh có **`rating` (1–10)** từ luật confluence/risk; hiện Telegram + DB; sau này analytics trung bình.
- Indicator plugins (interface chung): EMA34/89, RSI, MACD, BB, VWAP, ATR, Volume, market structure, S/R, candles/patterns; optional funding/OI/liq; **nhãn hiển thị tùy chỉnh** trong config.
- Layers: data → indicators → signal/confluence → risk → execution → notifier → storage → dashboard.
- Exchange: **CEX qua ccxt**, **Bybit trước** → Binance/CEX khác; toggle bằng `.env` + YAML (`enabled`, `market_type`, data/chart source). **DEX = adapter riêng, sau** (không cùng ccxt).
- Storage: **SQLite trước → Postgres sau**; secrets `.env`; logging đầy đủ.
- Backtest multi-TF **no look-ahead**; fees/slippage/funding; metrics; Optuna + walk-forward.
- Dashboard UI mô phỏng panel thống kê (vốn, winrate, phí) + hộp lệnh LONG/SHORT (SL/TP/Qty) — track Python; **không** inject Python vào TradingView.
- **TradingView:** (A) Pine Script port **tùy chọn, sau**; (B) dashboard/backtest Python là hướng chính. Bridge nếu cần = alerts/webhooks.
- Risk: % risk, ATR sizing, partial TP + runner; hold losers chỉ **spot + manual**; **perp bắt buộc SL**; limits + kill switch.
- Telegram: multi-channel / multi-TF / multi-method; mỗi tin có channel, TF, strategy/method **`display_name`**, indicator labels; routing trong YAML.
- Mỗi phase: **tests + README**; không nhảy phase khi chưa duyệt.

## Quyết định đã chốt (thiết kế)

| Mục | Quyết định |
|-----|------------|
| Ngôn ngữ | **Python** (ccxt, backtest, Optuna) |
| Sàn đầu | Bybit qua ccxt (CEX) |
| DEX | Adapter riêng, **sau** — Phase 1 chỉ chỗ cắm |
| TradingView | **B trước (Python UI chính)**; **A (Pine) tùy chọn sau** — không inject Python vào TV |
| Chi phí | Ưu tiên **ít opex**: paper + máy nhà ~$0/tháng; VPS/TV Pro chỉ khi Tomas chủ động cần — xem `cost-estimate.md` |
| Rating tín hiệu | Có — field `rating` 1–10; Phase 3 tính/lưu; Phase 6 hiện Telegram |
| Notifier | Template + `display_name` + multi-route — Phase 6 |
| DB đầu | SQLite |
| Config | YAML/JSON cho strategy, risk, exchanges, notify |
| Lộ trình | 6 phase (+ Pine/DEX add-on sau) — xem `architecture-roadmap.md` |
| Code Phase 1–6 | **Chưa** — chờ duyệt đề xuất + câu hỏi còn lại |

## Yêu cầu mới (đã ghi vào kiến trúc — chờ Tomas xác nhận)

Các điểm Tomas hỏi đã được **đưa vào roadmap** (không bắt đầu code):

1. CEX + (sau) DEX, toggle API / config, chart/data source chọn được.
2. Backtest + PnL UI kiểu TradingView (panel VN + hộp LONG/SHORT) trên dashboard Python; Pine optional.
3. Rating rủi ro/tin cậy per-signal (kiểu 7/10) + analytics trung bình sau.
4. Multi-channel notify + tên method/indicator tùy chỉnh khi Telegram bắn.

## Chưa chốt (chờ Tomas)

- Spot vs Perp làm primary trước
- Vốn paper (USDT)
- Timezone (`Asia/Ho_Chi_Minh` vs UTC)
- Bybit API / testnet sẵn chưa
- Telegram bot token + chat ID sẵn chưa; một hay nhiều kênh từ đầu
- Ngưỡng score confluence mặc định
- Leverage tối đa (nếu perp trước)
- **Rating:** nhãn “Rủi ro” (số cao = rủi ro cao) hay “Độ tin cậy” (số cao = tin hơn)?
- **Pine Script:** làm sau Phase 6 hay chỉ cần dashboard Python?
- Ưu tiên DEX khi nào (nếu có)

## Tài liệu liên quan

- **Bàn giao agent (đọc trước):** [`HANDOFF.md`](./HANDOFF.md) (trong git repo `docs/`)
- Đề xuất đầy đủ (VN): [`architecture-roadmap.md`](./architecture-roadmap.md)
- Dự toán chi phí: [`cost-estimate.md`](./cost-estimate.md)
- Preferences: [`preferences.md`](./preferences.md) (bản repo: `docs/preferences.md`)
- Hướng dẫn chuyển Repositories: [`repo-switch-guide.md`](./repo-switch-guide.md)
- Trả lời ngắn 4 câu hỏi gap (store internal): [`../internal/architecture-gap-answers.md`](../internal/architecture-gap-answers.md)
- README repo: `/workspace/README.md`

## Quy ước làm việc

- Trước mỗi phase: đề xuất → duyệt → mới code.
- Sau mỗi lần làm: commit + push (nếu có remote) để agent khác tiếp tục.
- Không triển khai logic giao dịch / Phase 1 trước khi Tomas duyệt kiến trúc này.
