# Hệ thống giao dịch (Trading System)

Repo này là **bộ tài liệu + (sau này) mã nguồn** cho bot giao dịch cá nhân của Tomas: theo dõi **BTC** nhiều khung thời gian, tín hiệu khi chỉ báo **đồng thuận**, quản lý rủi ro, chạy **paper / backtest** trước rồi mới **live**, báo **Telegram** và xem trên **dashboard** máy nhà.

> Hiện **chưa có code Phase 1**. Chỉ có đề xuất kiến trúc và hướng dẫn bàn giao. Đọc **HANDOFF** trước khi làm gì thêm.

---

## Bắt đầu từ đâu? (quan trọng)

1. Mở nhánh Git: **`cursor/architecture-roadmap-abd1`**
2. Đọc file bàn giao trước tiên:

### → [docs/HANDOFF.md](docs/HANDOFF.md) ← đọc file này trước

Sau đó lần lượt:

| Thứ tự | File | Nội dung |
|--------|------|----------|
| 1 | [docs/HANDOFF.md](docs/HANDOFF.md) | Tóm tắt dự án, quyết định đã chốt, câu hỏi còn mở, trạng thái phase |
| 2 | [docs/architecture-roadmap.md](docs/architecture-roadmap.md) | Kiến trúc đầy đủ + lộ trình 6 phase |
| 3 | [docs/project-context.md](docs/project-context.md) | Ngữ cảnh ngắn cho agent / phiên sau |
| 4 | [docs/cost-estimate.md](docs/cost-estimate.md) | Dự toán chi phí (ưu tiên ~$0 với paper + máy nhà) |
| 5 | [docs/preferences.md](docs/preferences.md) | Cách làm việc Tomas muốn (tiếng Việt, duyệt trước khi code, …) |

---

## Tiếp tục trong Cursor Repositories

1. Trong Cursor: **Repositories** → mở repo này.
2. Checkout nhánh **`cursor/architecture-roadmap-abd1`** (nhánh có tài liệu mới nhất; `main` thường đang đứng sau).
3. Mở **chat mới** trong repo đó và bảo agent đọc `docs/HANDOFF.md` trước.
4. **Chưa** bảo agent code Phase 1 trừ khi bạn đã trả lời câu hỏi còn mở (hoặc chủ động bỏ qua) và nói rõ **“OK Phase 1”**.

Hướng dẫn ngắn + câu prompt mẫu: xem tài liệu Project store `docs/repo-switch-guide.md` (nếu còn dùng Project), hoặc copy prompt trong `docs/HANDOFF.md`.

---

## Lộ trình (tóm tắt)

| Phase | Nội dung | Trạng thái |
|-------|----------|------------|
| Kiến trúc | Layers, CEX/DEX, TV hai hướng, rating, notifier | Đã viết trên nhánh này |
| **1** | Nền tảng: cấu trúc, `.env`, logging, SQLite, Bybit (ccxt), paper skeleton | **Chưa bắt đầu** |
| 2 | Plugin chỉ báo | Chưa |
| 3 | Watchlist multi-TF + confluence + **rating** | Chưa |
| 4 | Risk + execution (paper/live) | Chưa |
| 5 | Backtest multi-TF + Optuna | Chưa |
| 6 | Telegram templates + dashboard | Chưa |

**Add-on sau:** Pine Script (TradingView); DEX adapter riêng.

---

## Chạy code sau này

Khi Phase 1 xong sẽ bổ sung lệnh cụ thể (tạo môi trường Python, copy `.env.example`, chạy test). **Hiện chưa có ứng dụng để khởi động.**

## Bảo mật

Không commit API key / Telegram token. Dùng `.env` (mẫu `.env.example` sẽ có ở Phase 1).
