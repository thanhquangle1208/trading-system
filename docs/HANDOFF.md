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
| Rating | Có — field `rating` 1–10; nhãn **“Độ tin cậy”** (số cao = tin hơn); tính/lưu Phase 3; hiện Telegram Phase 6 |
| Notifier | Template + **`display_name`** + multi-route — **bắt đầu 1 kênh Telegram**, scale thêm kênh sau; Phase 6 |
| CEX / DEX | **CEX có ngay** trong kiến trúc; **DEX sau** |
| Market primary | **Spot trước**; Perp sau |
| Vốn paper | **1.000 USDT** |
| Timezone | **`Asia/Ho_Chi_Minh`** |
| Bybit API | **Chưa có**; paper dùng **cả testnet** (key tạo khi cần; Phase 1 dùng mock / `.env.example`) |
| Telegram credentials | **Chưa có** bot token + chat ID; Phase 1 chỉ skeleton / mẫu env |
| Confluence score | **Đề xuất mặc định 60/100** (đổi được trong YAML; chốt khi Tomas OK) |
| Leverage (khi làm Perp sau) | Tomas muốn khoảng **10x–20x**; **chưa áp dụng** vì đang Spot trước — xem ghi chú rủi ro bên dưới |
| Pine Script | Tomas hỏi ý nghĩa — **không bắt buộc**; giải thích trong chat; mặc định **chỉ cần dashboard Python**, Pine chỉ nếu sau này muốn soi trên TV |
| Code Phase 1–6 | **Chưa** — chờ “OK Phase 1” |

### Ghi chú leverage (khi sau này làm Perp)

Điều chỉnh **ký quỹ / kích thước lệnh** giúp kiểm soát số tiền bỏ ra, nhưng **leverage cao vẫn tăng tốc thanh lý (liquidation)** và làm PnL biến động mạnh hơn cùng một % giá. Với người mới: khi sang Perp, agent sẽ đề xuất **trần leverage trong config** (có thể bắt đầu thấp hơn 10–20x rồi nới dần sau backtest/paper). **Phase Spot không dùng leverage.**

Chi tiết đầy đủ: [`architecture-roadmap.md`](./architecture-roadmap.md). Chi phí: [`cost-estimate.md`](./cost-estimate.md).

---

## Câu hỏi còn mở (nhẹ)

Trả lời ngắn trong chat là đủ; agent cập nhật `project-context.md`.

1. **Ngưỡng confluence 60/100** — Tomas đồng ý làm mặc định không? (có thể đổi sau trong YAML)
2. **Pine Script** — sau khi đọc giải thích: **bỏ qua** (chỉ Python) hay **để optional sau Phase 6**?
3. Khi sẵn sàng: nói rõ **“OK Phase 1”** (Bybit/Telegram chưa có key vẫn OK — Phase 1 dùng mock + `.env.example`)

---

## Trạng thái phase

| Phase | Trạng thái |
|-------|------------|
| Kiến trúc / roadmap | Đã viết; quyết định vận hành đã cập nhật (2026-10-21) |
| **Phase 1** (repo skeleton, `.env`, logging, SQLite, Bybit read, paper skeleton) | **CHƯA bắt đầu** — chờ “OK Phase 1” |
| Phase 2–6 | Chưa |

**Quy tắc agent:** Không scaffold / không code Phase 1 cho đến khi Tomas gửi kiểu **“OK Phase 1”**. Có thể cập nhật tài liệu nếu được hỏi.

---

## Nhánh Git & commit gần đây

- **Nhánh cập nhật quyết định:** `cursor/lock-open-decisions-fcd8` (từ `main`)
- **`main`:** có handoff/architecture docs; **không force-merge** trừ khi Tomas yêu cầu.
- Commit gần đây trên `main`: `Add architecture handoff docs for Trading System`

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

**Locked:** Track **B before A/Pine**; **Python**; **Bybit/ccxt** (CEX yes, DEX later); **SQLite**; paper + historical backtest before live; **low opex**; modular plugins; **Spot first**; paper **1000 USDT**; TZ **Asia/Ho_Chi_Minh**; rating label **Độ tin cậy** (high = more confidence); **1 Telegram channel first**; Bybit/Telegram credentials **not ready yet** (testnet when available); no Phase 1–6 code yet.

**Soft-open:** Confirm confluence default **60/100**; Pine skip vs optional after Phase 6; leverage **10x–20x intent** only when Perp later (Spot has no leverage).

**Phase status:** Architecture + ops answers recorded; **Phase 1 NOT started**. Wait for explicit **“OK Phase 1”**.

**Branch:** `cursor/lock-open-decisions-fcd8` (docs update). Do not force-merge to `main` unless asked.

**Must-read before any code:** this file, then `architecture-roadmap.md`, `project-context.md`, `cost-estimate.md`, `preferences.md`.
