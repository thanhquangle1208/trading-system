# Học từ lệnh lãi → lọc lệnh lỗ

**Ý tưởng của Tomas:** nhìn các lệnh **WIN**, tìm điểm chung, biến thành quy tắc để **bớt lệnh lỗ** (và bớt trade nhiễu).

Đây là vòng lặp research chuẩn — làm trên TradingView với script có bảng **THỐNG KÊ** + hộp lệnh.

---

## 1. Vì sao T1 nhiều mũi tên?

T1 cũ (`indicator`) chỉ báo **điểm gần trendline + volume**.  
Chưa phải “một mũi tên = một lệnh có SL/TP/PnL”, nên tín hiệu dày.

Bản mới (`strategy` + THỐNG KÊ): **mỗi vào lệnh thật** (có SL, TP 2R, phí, WIN/LOSS) → số lệnh ít hơn nhiều.

---

## 2. Quy trình 5 bước (bạn làm trên chart)

| Bước | Việc | Ví dụ ghi chú |
|------|------|----------------|
| 1 | Chạy strategy trên **BTCUSDT.P · 5m** | Vốn $10k |
| 2 | Mở các hộp **WIN** (xanh) | Chụp / ghi 5–10 lệnh lãi |
| 3 | Với mỗi WIN, tick checklist bên dưới | Điểm chung |
| 4 | So với hộp **LOSS** (đỏ) | Cái WIN có mà LOSS không có |
| 5 | Bảo agent: “thêm lọc X” | Agent sửa Pine → bạn dán lại |

### Checklist điểm chung (in ra / copy)

Với **mỗi lệnh WIN**, ghi Có/Không:

- [ ] Cùng hướng SuperTrend / bias (không đi ngược trend)
- [ ] Volume nến vào ≥ SMA Volume × hệ số
- [ ] Nến vào có bóng reject / body mạnh (PA)
- [ ] Gần Demand (LONG) hoặc Supply (SHORT)
- [ ] Không vào ngay sau lệnh lỗ (cooldown)
- [ ] Khoảng Entry→SL không quá rộng (% hoặc ATR)
- [ ] Giờ giao dịch (Asia / London / NY) — tùy chọn

→ Những ô **hay Có ở WIN** và **hay Không ở LOSS** = ứng viên quy tắc lọc.

---

## 3. Quy tắc lọc đang gắn sẵn (v0 — sẽ chỉnh theo research)

Trong `pine/T1b_strategy_thongke.pine`:

1. Chỉ vào khi **SuperTrend đổi hướng** (không spam mỗi nến gần line)  
2. **Volume bắt buộc** ≥ SMA × hệ số  
3. **Cooldown** tối thiểu N nến giữa hai lệnh  
4. Một vị thế tại một thời điểm; đảo chiều = đóng cũ rồi mở mới  
5. SL theo ATR; **TP = 2R** (đã chốt)  
6. Risk ~1% vốn / lệnh  

Sau khi bạn gửi “điểm chung WIN”, agent thêm lọc (vd. chỉ LONG khi gần Demand, bắt buộc engulfing…).

---

## 4. Liên hệ ảnh mẫu

Ảnh mẫu = đúng UX cần có:

- Mũi tên vào/ra lệnh  
- Hộp Entry / SL / TP / Qty / phí / Gross–Net / WIN–LOSS  
- Bảng **THỐNG KÊ** (vốn, winrate, PF, Max DD…)  

Script T1b nhắm **giống UX đó**; logic entry sẽ siết dần theo checklist WIN.
