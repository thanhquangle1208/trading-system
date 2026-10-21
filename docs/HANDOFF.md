# HANDOFF — Trading System

**Đọc file này trước** khi làm bất kỳ việc gì trong repo. Sau đó đọc: `preferences.md` (newbie) → `beginner-next-steps.md` → `architecture-roadmap.md` → `project-context.md` → `cost-estimate.md`.

> **Trạng thái:** Tomas **OK Phase 1–5** (2026-10-21). Phase 5 trên nhánh `cursor/phase-5-backtest-fcd8`. **Chưa** Phase 6 cho đến khi Tomas confirm.

---

## Dự án này là gì?

Hệ thống giao dịch cá nhân của **Tomas Le** (người mới bắt đầu, chưa có nền tảng code):

- Theo dõi **BTC**, nhiều khung thời gian (**M15, H1, H4, D1**).
- Tín hiệu khi nhiều chỉ báo **đồng thuận** (confluence: điều kiện AND bắt buộc + điểm ≥ ngưỡng **60/100**).
- Mỗi tín hiệu/lệnh có **`rating` 1–10** — nhãn **“Độ tin cậy”** (số cao = tin hơn).
- Quản lý rủi ro rõ ràng; chạy **paper + backtest lịch sử** trước, **live sau**.
- Báo **Telegram** (bắt đầu 1 kênh) + **dashboard localhost**.
- Sàn: **CEX qua ccxt, Bybit trước**; DEX là hướng sau (adapter riêng).
- **Pine Script** (TradingView): làm **sau Phase 6** (add-on).

Giải thích và tài liệu bằng **tiếng Việt**, chậm rãi, dễ hiểu. Tomas là **newbie (gần như không biết code)** — xem `preferences.md`: mỗi lần nhờ Tomas làm gì phải nói **làm gì / để làm gì / tác dụng**, **một bước một**, vừa làm vừa hỏi. Mỗi phase: đề xuất → Tomas duyệt → mới code; mỗi phase có **tests + README**.

---

## Quyết định đã chốt (locked)

| Mục | Quyết định |
|-----|------------|
| TradingView | **B trước** (dashboard / backtest Python) — **A (Pine) sau Phase 6** |
| Ngôn ngữ | **Python** (ccxt, backtest, Optuna) |
| Sàn đầu | **Bybit** qua **ccxt** (CEX) |
| DEX | Adapter riêng, **sau**; Phase 1 chỉ chỗ cắm |
| DB đầu | **SQLite** → Postgres sau khi cần |
| Chế độ chạy | **Paper + historical backtest trước live** |
| Chi phí | **Ít opex**: paper + máy nhà ~$0/tháng |
| Kiến trúc | **Modular / plugins**; strategy **YAML/JSON** |
| Rating | **Độ tin cậy** 1–10 (số cao = tin hơn); Phase 3 tính/lưu; Phase 6 Telegram |
| Notifier | **1 kênh Telegram** trước, scale sau; templates Phase 6 |
| Market primary | **Spot trước**; Perp sau |
| Vốn paper | **1.000 USDT** |
| Timezone | **`Asia/Ho_Chi_Minh`** |
| Bybit API | **Chưa có**; paper dùng **testnet** khi có key |
| Telegram credentials | **Chưa có** |
| Confluence score | **60/100** mặc định (tối ưu sau trong YAML) |
| Leverage | **10x–20x** khi Perp sau; Spot không dùng |
| Pine Script | **Có làm** — add-on **sau Phase 6** |
| Phase 1 | Tomas đã **OK Phase 1** (2026-10-21) |
| Phase 2 phạm vi | Chỉ báo thường **+ Wyckoff cơ bản** — Tomas **OK Phase 2** (2026-10-21) |
| Phase 3 | Confluence + rating — Tomas **OK Phase 3** (2026-10-21) |
| Phase 4 | Risk + paper execution — Tomas **OK Phase 4** (2026-10-21) |
| Phase 5 | Backtest + Optuna — Tomas **OK Phase 5** (2026-10-21) |

### Ghi chú leverage (khi sau này làm Perp)

Điều chỉnh ký quỹ giúp kiểm soát vốn bỏ ra, nhưng leverage cao vẫn tăng tốc thanh lý. **Spot không dùng leverage.**

---

## Câu hỏi còn mở

Không còn câu hỏi chặn Phase 1. Khi sang Perp / Phase 6 sẽ hỏi lại chi tiết leverage trần và Telegram credentials nếu chưa có.

---

## Trạng thái phase

| Phase | Trạng thái |
|-------|------------|
| Kiến trúc / roadmap | Đã chốt |
| **Phase 1–4** | Xong |
| **Phase 5** | Backtest — nhánh `cursor/phase-5-backtest-fcd8` (chờ Tomas duyệt) |
| Phase 6 | Chưa |
| Pine (add-on) | Sau Phase 6 |
| DEX | Sau |

**Quy tắc agent:** Báo cáo → hỏi → chỉ tiếp tục khi Tomas confirm. Không nhảy Phase 6 trước khi Tomas OK.

---

## Nhánh Git & commit gần đây

- **Nhánh Phase 1:** `cursor/phase-1-foundation-fcd8`
- Docs quyết định trước đó: `cursor/lock-open-decisions-fcd8` / PR liên quan
- **Không force-merge** `main` trừ khi Tomas yêu cầu

---

## Instruction cho agent (bắt buộc)

**Before coding, read HANDOFF + architecture-roadmap + project-context + cost-estimate + preferences.**

1. Đọc hết các file trên trong `docs/`.
2. Phase 1 đã được OK — làm đúng phạm vi Phase 1 (chưa DEX code, chưa Pine code, chưa chỉ báo đầy đủ).
3. Giải thích tiếng Việt, rõ ràng; Tomas **newbie không biết code** — mỗi hướng dẫn: làm gì / để làm gì / tác dụng; một bước rồi hỏi lại.
4. Sau mỗi lần làm: commit + push nhánh; **nói Tomas bước tiếp theo là gì** (1–3 việc nhỏ).
5. Ưu tiên làm việc qua **Git repository**.
6. Không nhảy Phase 2+ khi Tomas chưa duyệt / chưa hiểu Phase trước.

---

## English summary (for other AIs)

**What:** Beginner-friendly multi-TF BTC trading system (confluence ≥60 + confidence rating + risk + paper/backtest before live + Telegram + localhost dashboard). Owner: Tomas Le; Vietnamese explanations.

**Locked:** Track B first; Pine **after Phase 6**; Python; Bybit/ccxt; Spot first; paper 1000 USDT; Asia/Ho_Chi_Minh; rating = Độ tin cậy; 1 TG channel first; confluence **60/100**; leverage intent 10–20x for later Perp.

**Phase status:** Tomas said **OK Phase 1**. Implement Phase 1 only; wait for Tomas review before Phase 2.

**Branch:** `cursor/phase-1-foundation-fcd8`.
