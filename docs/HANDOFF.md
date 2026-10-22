# HANDOFF — Trading System

**Đọc file này trước** khi làm bất kỳ việc gì trong repo. Sau đó đọc: `architecture-roadmap.md` → `project-context.md` → `cost-estimate.md` → `preferences.md` → **`thesis/T0-trading-thesis.md`** (nếu làm thesis).

> **Trạng thái hiện tại (2026-10-22):** Bot Phase 1 **hoãn**. T3 Gross lãi nhưng Net lỗ vì **phí >> Gross** → **`pine/T3b_optimize_thongke.pine`** (sàn SL, fee cap, Chỉ Spring/UT). Xem `thesis/optimize-from-t3-stats.md`. Chart học **BTCUSDT.P · 5m**.

---

## Dự án này là gì?

Hệ thống giao dịch cá nhân của **Tomas Le** (người mới bắt đầu, chưa có nền tảng code):

- **Ngắn hạn (đang làm):** chốt **thesis** trên TV — chart **BINANCE:BTCUSDT.P**, vốn paper **$10k**, logic vừa làm vừa research.
- **Dài hạn (hoãn):** bot Python (ccxt, Bybit…), paper/live, Telegram, dashboard localhost — xem roadmap Phase 1–6.

Giải thích và tài liệu bằng **tiếng Việt**, chậm rãi, dễ hiểu. Mỗi bước: đề xuất → Tomas duyệt → mới code.

---

## Hiểu đúng: “tích hợp vào chart TV”

| Công cụ | Vai trò |
|---------|---------|
| **Pine Script** | Code **chạy bên trong TradingView** → vẽ mũi tên, hộp LONG/SHORT, bảng THỐNG KÊ **trên chart** như ảnh |
| **Python bot** | Chạy **ngoài** TV (máy bạn) → lấy giá API, đặt lệnh, Telegram — **không** vẽ được vào chart TV |

Muốn UI như ảnh → làm **Pine**. Bot là bước sau khi thesis đã rõ.

Chi tiết: [`thesis/T0-trading-thesis.md`](./thesis/T0-trading-thesis.md).

---

## Quyết định đã chốt (locked)

### Thesis / Pine (ưu tiên hiện tại)

| Mục | Quyết định |
|-----|------------|
| Ưu tiên | **Pine thesis trước**; **bot Phase 1 hoãn** |
| Script | **Viết lại từ đầu** |
| Logic | Vừa làm vừa research (bắt đầu đơn giản) |
| Vốn paper thesis | **$10.000** |
| Chart | **BINANCE:BTCUSDT.P** (perp) |
| TF học | **5m** (đã chốt) |
| TP | **2R** (đã chốt) |
| Volume | **Bắt buộc** (đã chốt) |
| Phương pháp | **S/D + Wyckoff + PA + Trend line** — **OK** — [`thesis/method-sd-wyckoff-pa.md`](./thesis/method-sd-wyckoff-pa.md) |
| Quyết định khóa | [`thesis/decisions-locked.md`](./thesis/decisions-locked.md) |

### Kiến trúc bot dài hạn (vẫn giữ, chưa code)

| Mục | Quyết định |
|-----|------------|
| TradingView dài hạn | **A (Pine)** đang làm trước để chốt thesis; **B (Python dashboard)** khi làm bot |
| Ngôn ngữ bot | **Python** (ccxt, backtest, Optuna) |
| Sàn bot đầu | **Bybit** qua **ccxt** (sau thesis) |
| DEX | Adapter riêng, **sau** |
| DB đầu | **SQLite** → Postgres sau |
| Chế độ | Paper + backtest trước live |
| Chi phí | Ít opex; máy nhà; không tự thuê VPS/TV Pro trừ khi Tomas yêu cầu |
| Rating / Notifier | Thiết kế giữ nguyên — triển khai khi làm bot |
| Code Phase 1–6 | **Chưa** — chờ “OK Phase 1” sau khi thesis ổn |

Chi tiết bot: [`architecture-roadmap.md`](./architecture-roadmap.md). Chi phí: [`cost-estimate.md`](./cost-estimate.md).

---

## Câu hỏi vẫn mở (bot — không chặn thesis)

Trả lời khi quay lại bot; agent cập nhật `project-context.md`.

1. Spot hay Perp primary cho **bot** (thesis đang dùng perp chart Binance)
2. Timezone: `Asia/Ho_Chi_Minh` hay UTC?
3. Bybit API / testnet sẵn chưa?
4. Telegram bot + chat ID; một hay nhiều kênh?
5. `rating`: “Rủi ro” hay “Độ tin cậy”?
6. Ngưỡng confluence mặc định?
7. Leverage tối đa (perp bot)?

**Thesis — còn research dần:** công thức trend/entry/TP R / phí % / zone Supply-Demand sớm hay để T4 — xem T0 §6.

---

## Trạng thái phase / bước

| Bước | Trạng thái |
|------|------------|
| Kiến trúc bot / roadmap | Đã có trong docs; **bot chưa code** |
| **T0** + method | **OK** (Tomas duyệt) |
| **T3** | Wyckoff/PA — Gross + / Net − (phí) |
| **T3b** Optimize phí/SL | **`pine/T3b_optimize_thongke.pine`** ← dùng cái này |
| **Tiếp** | So T3b vs T3; học từ lệnh WIN nếu WR vẫn thấp |
| **Phase 1–6** bot | **HOÃN** |

**Quy tắc agent:** Phương pháp đã OK → được viết T1. T2+ cần Tomas OK từng bước (hoặc bảo “tiếp T2”). Không scaffold Phase 1 bot cho đến “OK Phase 1”.

---

## Nhánh Git & commit gần đây

- **Nhánh thesis:** `cursor/trading-thesis-pine-43e3`
- **Nhánh kiến trúc cũ:** `cursor/architecture-roadmap-abd1`
- **`main`:** có thể đứng sau các nhánh feature — không force-merge trừ khi Tomas yêu cầu.

---

## Instruction cho agent (bắt buộc)

**Before coding, read HANDOFF + architecture-roadmap + project-context + cost-estimate + preferences + thesis/T0.**

1. Giải thích tiếng Việt, rõ ràng, giả định người mới.
2. Ưu tiên hiện tại = **thesis Pine**; bot chỉ khi Tomas mở lại.
3. Mỗi bước T0→T5: đề xuất → duyệt → code.
4. Sau mỗi lần làm: commit + push nhánh.
5. Ưu tiên làm việc qua **Git repository**.

---

## English summary (for other AIs)

**Now:** Method approved (S/D+Wyckoff+PA+trendline). TP **2R**, TF **5m**, volume required. T1 Pine in `pine/T1_trendline_volume.pine`. Bot still paused.

**Next:** Tomas pastes T1 on TV; then “OK T2” for S/D zones. “OK Phase 1” later for bot.

**Branch:** `cursor/trading-thesis-pine-43e3`.
