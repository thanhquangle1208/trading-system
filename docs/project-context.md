# Project context — Trading System

Ngắn gọn cho agent / phiên sau. Cập nhật khi Tomas chốt quyết định.

## Người dùng

- Tomas Le — **newbie, gần như không biết code** (terminal, Git, Python, PR…).
- Muốn giải thích tiếng Việt, chậm, rõ; duyệt thiết kế trước mỗi phase.
- Agent phải: **một bước một**, nói **làm gì / để làm gì / tác dụng**, vừa làm vừa hỏi — chi tiết trong `preferences.md`.

## Mục tiêu sản phẩm

- Watchlist multi-TF: **M15, H1, H4, D1**; **BTC** cặp chính.
- Confluence: điều kiện **AND (required)** + **score ≥ 60/100** (tối ưu sau).
- Mỗi tín hiệu/lệnh có **`rating` (1–10)** nhãn **Độ tin cậy**; hiện Telegram + DB.
- Indicator plugins (Phase 2+): EMA34/89, RSI, MACD, BB, VWAP, ATR, Volume, market structure, S/R, candles/patterns; **Wyckoff cơ bản** (cấu trúc + vài tín hiệu đơn giản, cùng lớp plugin — Tomas chọn 2026-10-21); optional funding/OI/liq.
- Exchange: **CEX qua ccxt**, **Bybit spot trước**; DEX adapter riêng sau.
- Storage: **SQLite trước**; secrets `.env`.
- Paper **1000 USDT**; timezone **Asia/Ho_Chi_Minh**.
- Telegram: **1 kênh trước**; credentials chưa có.
- **Pine Script:** có làm **sau Phase 6**.
- Mỗi phase: **tests + README**; không nhảy phase khi chưa duyệt.

## Quyết định đã chốt

| Mục | Quyết định |
|-----|------------|
| Ngôn ngữ | Python |
| Sàn / market | Bybit ccxt; **Spot trước** |
| Vốn paper | **1000 USDT** |
| Timezone | **Asia/Ho_Chi_Minh** |
| Confluence | **60/100** |
| Rating | **Độ tin cậy** (cao = tin hơn) |
| Telegram | 1 kênh trước; chưa có token/chat ID |
| Bybit API | Chưa có; testnet khi có; Phase 1 mock OK |
| Leverage | 10x–20x khi Perp sau |
| Pine | **Sau Phase 6** |
| Phase 1 | Tomas **OK Phase 1** (2026-10-21) |

## Trạng thái code

- Phase 1–3 xong
- Phase 4 risk + paper trên nhánh `cursor/phase-4-risk-execution-fcd8` — chờ Tomas duyệt trước Phase 5

## Tài liệu liên quan

- [`HANDOFF.md`](./HANDOFF.md)
- [`architecture-roadmap.md`](./architecture-roadmap.md)
- [`cost-estimate.md`](./cost-estimate.md)
- [`preferences.md`](./preferences.md)

## Quy ước làm việc

- Trước mỗi phase: đề xuất → duyệt → mới code.
- Sau mỗi lần làm: commit + push.
- Không nhảy Phase 2 trước khi Tomas duyệt Phase 1.
