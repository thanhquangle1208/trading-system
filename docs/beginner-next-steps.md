# Bước tiếp theo cho Tomas (newbie)

File này nói **bạn đang ở đâu** và **nên làm gì tiếp**, bằng tiếng Việt đơn giản.

## Bạn đang ở đâu?

Agent đã làm **Phase 1 (nền tảng)** trên GitHub:

- Tạo “khung nhà” cho bot (thư mục, cấu hình, nhật ký, sổ SQLite, sàn giả/mock, lệnh paper thử).
- **Chưa** có chỉ báo thật, **chưa** tự vào lệnh theo chiến lược, **chưa** Telegram thật.

PR: nhánh `cursor/phase-1-foundation-fcd8` (xem PR #2 trên GitHub).

## Mục tiêu ngay bây giờ (không phải Phase 2)

**Bạn hiểu và tự chạy được Phase 1 trên máy mình** → rồi bảo agent “Phase 1 OK, làm Phase 2”.

Không cần hiểu hết code. Chỉ cần: mở được repo → chạy vài lệnh → thấy dòng chữ “14 passed” và “Phase 1 smoke xong”.

## Lộ trình siêu ngắn

| Bước | Việc của bạn | Để làm gì? |
|------|--------------|------------|
| A | Mở đúng repo + đúng nhánh trên Cursor | Để nhìn đúng code Phase 1 (không nhìn nhầm bản cũ) |
| B | Tạo “môi trường Python” (venv) + cài thư viện | Để máy bạn có đủ đồ chạy bot thử |
| C | Copy `.env.example` → `.env` | Để bot đọc cấu hình; key bí mật không đưa lên GitHub |
| D | Chạy `pytest` | Kiểm tra Phase 1 còn đúng (như bài kiểm tra tự động) |
| E | Chạy `python -m trading_system` | Thấy bot giả lập lấy giá + lệnh paper |
| F | Trả lời agent: ổn / lỗi gì | Agent sửa hoặc sang Phase 2 |

Agent sẽ **hỏi từng bước** trong chat — không bắt bạn làm hết một lúc.

**Cập nhật (2026-10-21):** Tomas muốn agent **tự chạy** các lệnh cài đặt / test / smoke trên môi trường agent, rồi báo lại. Tomas chỉ cần làm việc “phía người”: mở repo, duyệt, trả lời câu hỏi, tạo key khi cần.

## Phase 2 là gì? (chưa làm)

Phase 2 = viết **chỉ báo** (EMA, RSI, …) — công thức đọc biểu đồ. Chỉ bắt đầu khi bạn nói Phase 1 ổn.
