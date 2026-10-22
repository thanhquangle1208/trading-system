# Phương pháp thesis — Supply/Demand + Wyckoff + Price Action + Trend line

**Trạng thái:** Tomas đã **OK phương pháp** (2026-10-21). Đã chốt **TP 2R**, **TF 5m**, **volume bắt buộc**. Pine T1 đã có trong `pine/`.

Agent **có thể tự học / research** các khái niệm này từ tài liệu chuẩn (Wyckoff, S/D confluence, price action) rồi đề xuất luật giao dịch đơn giản → bạn duyệt → mới code. Không cần bạn biết code.

---

## 1. Bốn trụ — nói tiếng thường

| Trụ | Ý tưởng ngắn | Trên chart bạn sẽ thấy gì |
|-----|--------------|---------------------------|
| **Supply / Demand (S/D)** | Giá từng “bật mạnh” từ một vùng → vùng đó còn lệnh lớn. Demand = mua mạnh (đáy). Supply = bán mạnh (đỉnh). | Ô xanh (Demand) / cam (Supply) như ảnh |
| **Wyckoff** | “Cá mập” gom hàng (accumulation) rồi đẩy lên; xả hàng (distribution) rồi đẩy xuống. Quan trọng: **cấu trúc vùng** + **nỗ lực vs kết quả** (volume/spread). | Vùng sideway → Spring (giả gãy đáy) / Upthrust (giả gãy đỉnh) → Markup / Markdown |
| **Price Action (PA)** | Đọc hành vi nến tại vùng quan trọng: rejection wick, engulfing, pin bar… | Nến xác nhận ngay tại zone / trendline |
| **Trend line** | Nối đáy cao dần (uptrend) hoặc đỉnh thấp dần (downtrend). Là **sàn động / trần động**. | Đường chéo hỗ trợ / kháng cự |

**Confluence (đồng thuận):** càng nhiều trụ khớp cùng một chỗ → tín hiệu càng “đáng vào”.

Ví dụ LONG đẹp:

```
Uptrend (trend line hỗ trợ) 
  + giá về Demand còn “tươi” 
  + hành vi kiểu Wyckoff (test / spring / LPS) 
  + nến PA xác nhận (rejection / engulfing)
→ mới LONG
```

SHORT thì ngược lại (Supply + trendline kháng cự + upthrust/test + PA).

---

## 2. Luật Wyckoff cần nhớ (3 luật — đủ để bắt đầu)

1. **Cung–cầu quyết định hướng:** cầu > cung → giá lên; cung > cầu → giá xuống.  
2. **Nguyên nhân → kết quả:** vùng sideway càng lâu / càng “xây nền” → sóng đi sau có thể càng xa (mục tiêu thô).  
3. **Nỗ lực vs kết quả:** volume lớn mà giá không tiến → cảnh báo đảo chiều / hấp thụ.

Vòng đời giá (đơn giản hóa):

```
Accumulation (gom) → Markup (đẩy lên)
Distribution (xả)  → Markdown (đẩy xuống)
```

**Sự kiện hay dùng để vào lệnh (bản rút gọn cho crypto 5m):**

| Sự kiện | Ý nghĩa | Hướng lệnh |
|---------|---------|------------|
| **Spring** | Giả gãy dưới vùng → đóng lại trong vùng | Ưu tiên **LONG** |
| **Upthrust (UT)** | Giả gãy trên vùng → đóng lại trong vùng | Ưu tiên **SHORT** |
| **LPS / LPSY** | Pullback cuối sau dấu hiệu mạnh | Theo hướng markup/markdown |
| **SOS / SOW** | Dấu hiệu mạnh lên / yếu xuống | Xác nhận hướng |

> Bản đầy đủ Wyckoff (PS, SC, AR, ST, Phase A–E…) học dần. Pine **không** cần đầy đủ ngay — bắt đầu bằng **subset** có thể code được.

---

## 3. Supply / Demand — cách nhận vùng (v0)

Pattern nền tảng (base = vài nến sideway trước khi chạy mạnh):

| Pattern | Tên thường | Zone |
|---------|------------|------|
| Rally → Base → Rally | RBR | **Demand** |
| Drop → Base → Drop | DBD | **Supply** |
| Drop → Base → Rally | DBR | Demand (đảo chiều) |
| Rally → Base → Drop | RBD | Supply (đảo chiều) |

**Quy tắc dùng zone (v0):**

- Ưu tiên zone **fresh** (giá chưa quay lại “test” nhiều lần).  
- Zone đã test nhiều lần → yếu dần.  
- Chỉ trade zone **đồng hướng** với trend lớn hơn (hoặc sau Spring/UT rõ).

---

## 4. Trend line — quy tắc vẽ (v0)

| Hướng | Cách vẽ | Dùng để |
|-------|---------|---------|
| Uptrend | Nối ≥ 2 **swing low** cao dần | Hỗ trợ động — tìm LONG gần đường |
| Downtrend | Nối ≥ 2 **swing high** thấp dần | Kháng cự động — tìm SHORT gần đường |

Hợp lệ hơn khi: có ≥ 2–3 lần chạm; giá từng đi xa rồi quay lại chạm (không chỉ “kéo đường cho đẹp”).

---

## 5. Price Action — xác nhận vào lệnh (v0)

Chỉ dùng PA **tại** vùng confluence (không trade PA lung tung giữa chart):

| Tín hiệu | LONG | SHORT |
|----------|------|-------|
| Rejection | Bóng dưới dài, đóng nửa trên | Bóng trên dài, đóng nửa dưới |
| Engulfing | Nến xanh nuốt nến đỏ trước | Nến đỏ nuốt nến xanh trước |
| Close back in range | Sau Spring: đóng lại trong TR | Sau UT: đóng lại trong TR |

Không có PA xác nhận → **không vào** (giảm lệnh nhiễu).

---

## 6. Luật vào / ra lệnh đề xuất (thesis v0 — chờ duyệt)

### Điều kiện LONG (AND)

1. Cấu trúc nghiêng **markup / uptrend** (trend line hỗ trợ còn giữ) **hoặc** vừa có Spring hợp lệ.  
2. Giá chạm / vào **Demand** còn fresh (hoặc LPS sau SOS).  
3. Demand gần **trend line hỗ trợ** (confluence) — nếu lệch quá xa thì bỏ hoặc hạ điểm.  
4. **PA xác nhận** trên TF đang trade (5m lúc học).  
5. SL dưới đáy zone / dưới Spring; TP **2R** (đã chốt; input vẫn cho phép đổi sau).

### Điều kiện SHORT (AND)

1. **Markdown / downtrend** hoặc Upthrust hợp lệ.  
2. Chạm **Supply** fresh (+ gần trend line kháng cự).  
3. PA xác nhận.  
4. SL trên đỉnh zone / trên UT; TP theo R.

### Quản lý vốn (đã chốt trước)

- Vốn paper: **$10.000**  
- Risk / lệnh: ~**1%** (đổi được)  
- Đảo chiều: đóng lệnh cũ trước khi mở ngược  

### Điểm confluence (gắn với roadmap rating sau này)

Mỗi trụ khớp = điểm; chỉ vào khi điểm ≥ ngưỡng (vd. **3/4 trụ**). Chi tiết số điểm chỉnh khi viết Pine.

---

## 7. Pine tự động được bao nhiêu? (thành thật)

| Phần | Pine làm được? | Ghi chú |
|------|----------------|---------|
| Vẽ / detect S/D zones (RBR/DBD…) | **Có** (heuristic) | Không hoàn hảo 100% như mắt người |
| Trend line từ swing | **Có** (pivot) | Cần tham số độ “nhạy” |
| PA: engulfing, wick reject | **Có** | Rõ ràng |
| Spring / Upthrust đơn giản | **Có** (subset) | Đủ để bắt đầu |
| Full Wyckoff Phase A–E + Composite Man | **Một phần** | Phức tạp; học dần, không nhồi hết vào T1 |
| “Cảm nhận” volume tinh tế | **Một phần** | Volume crypto futures nhiễu hơn cổ phiếu |

→ Thesis **chuẩn** = luật rõ + backtest trên TV. Agent research + đề xuất; bạn nhìn chart và bảo chỉnh.

---

## 8. Lộ trình code điều chỉnh (sau khi Tomas OK phương pháp)

| Bước | Việc | Ghi chú |
|------|------|---------|
| **T0** | Chốt doc này + T0 tổng | **OK** |
| **T1 / T1c** | Trend + volume + THỐNG KÊ trên chart | Xong — nhiều lệnh |
| **T2** | S/D zones + lọc vào lệnh | **Đã viết** `pine/T2_sd_thongke.pine` |
| **T3** | Pine: Spring/UT subset + PA confirm → tín hiệu | Confluence thật |
| **T4** | Hộp lệnh VN + SL/TP/Qty/phí | Giống ảnh |
| **T5** | Bảng THỐNG KÊ | Giống ảnh |
| **T6** | Research chỉnh tham số trên BTCUSDT.P 5m | Vừa làm vừa học |

(Bot Python vẫn **hoãn**.)

---

## 9. Nguồn agent đã dựa vào (để học tiếp)

- StockCharts — *The Wyckoff Method: A Tutorial* (3 laws, accumulation/distribution, spring, SOS, LPS…)  
- Confluence S/D + trendline / S-R (PriceActionNinja, ForexBee S/D+trendline)  
- Volume spread ý tưởng no-demand / no-supply (dùng nhẹ, không phụ thuộc sớm)

---

## 10. Câu hỏi — đã trả lời (2026-10-21)

1. 4 trụ — **Đồng ý**  
2. TP — **2R**  
3. TF — **5m**  
4. Volume — **Bắt buộc**  

Xem [`decisions-locked.md`](./decisions-locked.md).
