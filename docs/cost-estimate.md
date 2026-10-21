# Dự toán chi phí — Trading System

Ưu tiên của Tomas: **ít chi phí vận hành cố định**. Đơn vị tham khảo USD; có thể đổi theo thời điểm.

## Quyết định liên quan

- Hướng chính: **B (Python bot + dashboard localhost + Telegram)**.
- **A (Pine / TradingView):** tùy chọn sau, không bắt buộc để hệ thống chạy.

---

## B vs A — chi phí vận hành

| Khoản | **B (Python)** | **A (TradingView)** |
|-------|----------------|---------------------|
| Phần mềm chart/backtest | $0 (dashboard tự làm) | $0 (free) hoặc ~$15–60/tháng nếu Pro/Pro+ |
| Máy chạy 24/7 | $0 nếu máy nhà; hoặc VPS ~$5–12/tháng | Không cần VPS cho script Pine |
| Telegram | $0 | $0 (nếu chỉ dùng TV alert thì khác) |
| API đọc giá CEX (ccxt công khai) | $0 (có giới hạn tốc độ) | Dữ liệu TV (theo gói TV) |
| Database SQLite | $0 | Không dùng |
| Phí giao dịch sàn | Chỉ khi **live** (theo sàn) | Không vào lệnh trực tiếp |
| Điện máy nhà (nếu 24/7) | Nhỏ, tùy máy | Không |

**Kết luận:** Muốn **rẻ nhất** → chạy **B trên máy cá nhân + paper**, không thuê VPS, chưa live. A rẻ nếu dùng TV free, nhưng **không thay** được bot vào lệnh / DB / multi-channel của B.

---

## Toàn bộ dự án — nhóm chi phí

### 1) Gần như $0 (khuyến nghị giai đoạn đầu)

| Hạng mục | Ghi chú |
|----------|---------|
| Code Python + Git | Repo hiện có |
| SQLite, logging, config YAML | Local |
| Telegram Bot | Tạo bot miễn phí qua BotFather |
| Bybit/Binance API key | Tạo free; **paper/testnet** không tốn phí giao dịch thật |
| Dashboard localhost | Trình duyệt trên máy bạn |
| Backtest trên lịch sử tải về | Băng thông nhỏ; thường free qua API công khai |

**Tổng cố định/tháng giai đoạn paper + máy nhà: ~$0** (ngoài điện + internet sẵn có).

### 2) Tùy chọn (chỉ khi cần)

| Hạng mục | Ước lượng | Khi nào cần |
|----------|-----------|-------------|
| VPS 24/7 (vd 1 vCPU, 1–2 GB) | ~$5–12/tháng | Bot quét thật khi bạn tắt máy |
| TradingView Pro (cho bản A sau) | ~$15–60/tháng | Chỉ nếu làm Pine soi chart |
| Domain + HTTPS | ~$10–15/năm | Chỉ nếu mở dashboard ra ngoài (không khuyến nghị sớm) |
| Postgres managed | ~$0–15/tháng | Khi SQLite không đủ; Phase sau |
| Data premium (ít khi cần) | $0–50+/tháng | Chỉ nếu API free bị giới hạn nặng |

### 3) Chi phí khi giao dịch live (không phải “phí hệ thống”)

| Hạng mục | Ghi chú |
|----------|---------|
| Phí maker/taker Bybit (ví dụ) | Thường ~0.02%–0.1%/lệnh — **theo volume** |
| Funding (perp) | Theo vị thế giữ qua kỳ funding |
| Slippage | Không trả cho ai; làm giảm PnL |
| Lãi/lỗ | Rủi ro vốn — lớn hơn mọi phí phần mềm |

→ Đây là chi phí **trading**, không phải thuê phần mềm. Paper thì **$0**.

### 4) Công cụ làm việc (ngoài hệ thống)

| Hạng mục | Ghi chú |
|----------|---------|
| Cursor / AI agent | Theo gói bạn đang dùng — không tính vào opex bot |
| Thời gian của bạn | Học + duyệt phase |

---

## Kịch bản đề xuất (ít phí)

1. **Phase 1–5 (paper):** chạy trên máy bạn → **~$0/tháng** cố định.  
2. **Phase 6 paper dài hạn:** vẫn máy nhà hoặc VPS rẻ nếu cần 24/7 → **$0 hoặc ~$5–12/tháng**.  
3. **Live vốn nhỏ:** chỉ thêm **phí sàn + rủi ro vốn**; chưa cần Postgres/domain/TV Pro.  
4. **Bản A (Pine):** chỉ khi bạn muốn soi TV → cân nhắc gói TV lúc đó.

---

## Ngân sách “trần” gợi ý (12 tháng đầu, vẫn tiết kiệm)

| Mục | Thấp | Trung bình |
|-----|------|------------|
| Vận hành phần mềm (B, máy nhà) | $0 | $0 |
| VPS (nếu 24/7) | $0 | ~$60–144/năm |
| TradingView (nếu làm A) | $0 | ~$180–720/năm |
| Phí sàn live | Theo lệnh | Theo lệnh |

**Khuyến nghị mặc định cho Tomas:** giữ **Thấp** — B trên máy nhà, paper trước, không thuê gì cho đến khi bot ổn và bạn chủ động muốn 24/7 hoặc live.
