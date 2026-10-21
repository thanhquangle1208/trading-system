# HANDOFF — Trading System

**Đọc file này trước** khi làm bất kỳ việc gì trong repo. Sau đó đọc: `architecture-roadmap.md` → `project-context.md` → `cost-estimate.md` → `preferences.md`.

> **Trạng thái:** Kiến trúc đã được xây theo hướng Tomas duyệt (B trước A/Pine; Python; Bybit/ccxt; …) nhưng **Phase 1 CHƯA bắt đầu**. Không viết code giao dịch / scaffold Phase 1 cho đến khi Tomas nói rõ **“OK Phase 1”** và trả lời (hoặc tạm bỏ qua có chủ đích) các câu hỏi còn mở.

---

## Dự án này là gì?

Hệ thống giao dịch cá nhân của **Tomas Le** (người mới bắt đầu, chưa có nền tảng code):

- Theo dõi **BTC**, nhiều khung thời gian (**M15, H1, H4, D1**).
- Tín hiệu khi nhiều chỉ báo **đồng thuận** (confluence: điều kiện AND bắt buộc + điểm ≥ ngưỡng).
- Mỗi tín hiệu/lệnh có **`rating` 1–10** (rủi ro / độ tin cậy — nhãn chưa chốt).
- Quản lý rủi ro rõ ràng; chạy **paper + backtest lịch sử** trước, **live sau**.
- Báo **Telegram** (nhiều kênh, tên method/chỉ báo tùy chỉnh) + **dashboard localhost**.
- Sàn: **CEX qua ccxt, Bybit trước**; DEX là hướng sau (adapter riêng).

Giải thích và tài liệu bằng **tiếng Việt**, chậm rãi, dễ hiểu. Mỗi phase: đề xuất → Tomas duyệt → mới code; mỗi phase có **tests + README**.

---

## Quyết định đã chốt (locked)

| Mục | Quyết định |
|-----|------------|
| TradingView | **B trước** (dashboard / backtest Python) — **A (Pine) tùy chọn sau**; không inject Python vào TV |
| Ngôn ngữ | **Python** (ccxt, backtest, Optuna) |
| Sàn đầu | **Bybit** qua **ccxt** (CEX); Binance/CEX khác sau cùng interface |
| DEX | Adapter riêng, **sau**; Phase 1 chỉ để chỗ cắm |
| DB đầu | **SQLite** → Postgres sau khi cần |
| Chế độ chạy | **Paper + historical backtest trước live**; không dùng tiền thật để thử chỉ báo |
| Chi phí | **Ít opex**: paper + máy nhà ~$0/tháng; không tự thuê VPS / TV Pro / domain trừ khi Tomas yêu cầu |
| Kiến trúc | **Modular / plugins** (chỉ báo, adapter sàn); strategy bằng **YAML/JSON** |
| Rating | Có — field `rating` 1–10; tính/lưu Phase 3; hiện Telegram Phase 6 |
| Notifier | Template + **`display_name`** + multi-route (channel / TF / method) — Phase 6 |
| CEX / DEX | **CEX có ngay** trong kiến trúc; **DEX sau** |
| Code Phase 1–6 | **Chưa** — chờ “OK Phase 1” + câu trả lời còn lại |

Chi tiết đầy đủ: [`architecture-roadmap.md`](./architecture-roadmap.md). Chi phí: [`cost-estimate.md`](./cost-estimate.md).

---

## Câu hỏi vẫn chờ Tomas

Trả lời ngắn trong chat là đủ; agent cập nhật `project-context.md`.

1. **Spot hay Perp** làm primary trước? (có thể hỗ trợ cả hai sau.)
2. **Vốn paper** khởi điểm (USDT)? ví dụ 1.000 / 5.000 / 10.000
3. **Timezone:** `Asia/Ho_Chi_Minh` hay UTC?
4. **Bybit API** (key/secret, quyền) đã tạo chưa? Paper dùng testnet không?
5. **Telegram** bot token + chat ID sẵn chưa?
6. **`rating`:** nhãn **“Rủi ro”** (số cao = rủi ro cao) hay **“Độ tin cậy”** (số cao = tin hơn)?
7. **Một hay nhiều** kênh Telegram từ đầu?
8. **Ngưỡng score confluence** mặc định? (ví dụ 60/100 — đổi được trong YAML)
9. **Leverage tối đa** nếu làm perp trước? (ví dụ 2x–5x)
10. **Pine Script:** làm sau Phase 6 hay chỉ cần dashboard Python?

---

## Trạng thái phase

| Phase | Trạng thái |
|-------|------------|
| Kiến trúc / roadmap | Đã viết & đẩy Git — hướng đã rõ; chờ xác nhận cuối + câu hỏi |
| **Phase 1** (repo skeleton, `.env`, logging, SQLite, Bybit read, paper skeleton) | **CHƯA bắt đầu** |
| Phase 2–6 | Chưa |

**Quy tắc agent:** Không scaffold / không code Phase 1 cho đến khi Tomas gửi kiểu **“OK Phase 1”** (và tốt nhất là trả lời mục câu hỏi). Có thể cập nhật tài liệu nếu được hỏi.

---

## Nhánh Git & commit gần đây

- **Nhánh làm việc:** `cursor/architecture-roadmap-abd1`
- **`main`:** thường **đứng sau** nhánh này (chỉ có commit khởi tạo). Tomas mở nhánh trên **Repositories** hoặc merge bằng PR sau — **không force-merge** trừ khi Tomas yêu cầu.
- **Commit gần đây (kiến trúc, không có code Phase 1):**
  - `docs: add cost estimate and link from README`
  - `Expand architecture for CEX/DEX, TV tracks, rating, notifier templates`
  - `Add Vietnamese architecture roadmap for Trading System`
  - (+ commit handoff pack này)

---

## Instruction cho agent (bắt buộc)

**Before coding, read HANDOFF + architecture-roadmap + project-context + cost-estimate + preferences.**

1. Đọc hết các file trên trong `docs/`.
2. Không bắt đầu Phase 1 nếu Tomas chưa nói OK.
3. Giải thích tiếng Việt, rõ ràng, giả định người mới.
4. Sau mỗi lần làm: commit + push nhánh để agent khác tiếp tục được.
5. Ưu tiên làm việc qua **Git repository** (Repositories), không dựa vào Project chat store.

---

## English summary (for other AIs)

**What:** Beginner-friendly multi-TF BTC trading system (confluence + rating + risk + paper/backtest before live + Telegram + localhost dashboard). Owner: Tomas Le; prefer Vietnamese explanations.

**Locked:** Track **B before A/Pine**; **Python**; **Bybit/ccxt** (CEX yes, DEX later); **SQLite**; paper + historical backtest before live; **low opex**; modular plugins; signal **rating**; notifier **display_name** / multi-route; no Phase 1–6 code yet.

**Open (wait on Tomas):** Spot vs Perp primary; paper capital; timezone; API/Telegram readiness; rating label “Rủi ro” vs “Độ tin cậy”; 1 vs many TG channels; confluence score threshold; max leverage (if perp first); Pine after Phase 6 or Python-only.

**Phase status:** Architecture direction approved in docs; **Phase 1 NOT started**. Wait for explicit **“OK Phase 1”** plus answers (or conscious deferrals).

**Branch:** `cursor/architecture-roadmap-abd1` (ahead of `main`). Do not force-merge to `main` unless asked.

**Must-read before any code:** this file, then `architecture-roadmap.md`, `project-context.md`, `cost-estimate.md`, `preferences.md`.
