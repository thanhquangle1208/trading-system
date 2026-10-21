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
- **Chạy lệnh kỹ thuật trên môi trường agent:** Tomas OK để agent **tự chạy** các lệnh kiểu `venv`, `pip`, `cp .env`, `pytest`, `python -m …` trên máy/agent cloud. (2026-10-21)
- **Nhịp báo cáo bắt buộc (Tomas chốt 2026-10-21):**
  1. Agent **tự làm** phần kỹ thuật trong phạm vi đã được phép,
  2. **Báo lại** bằng tiếng Việt: đã làm gì · cái đó là gì · tác dụng gì,
  3. **Hỏi** Tomas có muốn chạy / làm tiếp bước nào không,
  4. **Chỉ tiếp tục khi Tomas confirm** (ví dụ “OK”, “làm tiếp Phase 2”).
  Không tự nhảy phase hay tự mở việc lớn tiếp theo.

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
