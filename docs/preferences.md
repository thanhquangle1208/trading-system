# Preferences

## Người dùng (rất quan trọng)

- **Tomas là newbie:** hiểu biết **ít / gần như không** về code, Git, terminal, Python.
- Agent **không được** giả định Tomas biết lệnh, nhánh Git, venv, PR, pytest…
- Mỗi lần bảo Tomas làm gì, agent **bắt buộc** giải thích bằng tiếng Việt, chậm, rõ:
  1. **Làm gì** (từng bước cụ thể),
  2. **Để làm gì** (mục đích bước này trong dự án),
  3. **Dùng để làm gì / tác dụng** (kết quả Tomas sẽ thấy, liên quan bot thế nào).
- **Vừa làm vừa hỏi:** không đổ một lúc 10 lệnh. Một bước → Tomas làm / trả lời → mới bước tiếp.
- Tránh jargon; nếu phải dùng từ kỹ thuật thì giải thích ngay trong ngoặc.
- Không “làm nhanh rồi bỏ lại”: sau mỗi lần agent code, tóm tắt **Tomas cần làm gì tiếp theo** (1–3 việc nhỏ).

## Cách làm việc dự án

- Giải thích bằng tiếng Việt, chậm rãi, chi tiết; giả định người dùng chưa biết code. (2026-10-21)
- Trước mỗi phase: đề xuất / chờ duyệt, rồi mới code; mỗi phase có test + README. (2026-10-21)
- Sau mỗi lần làm việc: lưu file và đẩy lên GitHub để agent khác tiếp tục được. (2026-10-21)
- Ưu tiên kiến trúc mô-đun, plugin chỉ báo, strategy bằng config YAML/JSON. (2026-10-21)
- Làm hướng B (Python) trước; **Pine Script sau Phase 6**. (2026-10-21)
- Ưu tiên ít chi phí vận hành: paper + máy nhà trước; không tự thuê VPS/TV Pro/domain trừ khi được yêu cầu. (2026-10-21)
- Customize/tối ưu chỉ trên backtest lịch sử và paper; không dùng tiền thật để thử chỉ báo. (2026-10-21)
- Ưu tiên làm việc qua Git repository (Repositories); tài liệu/handoff phải nằm trong repo. (2026-10-21)
- **Nhịp làm việc với Tomas:** hướng dẫn từng bước + hỏi xác nhận; không nhảy Phase khi Tomas chưa hiểu / chưa duyệt phase trước. (2026-10-21)
