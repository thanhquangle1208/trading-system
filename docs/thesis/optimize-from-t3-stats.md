# Phân tích PnL thất bại (T3) → hướng tối ưu

Số Tomas gửi (ảnh THỐNG KÊ):

| Chỉ số | Giá trị | Ý nghĩa |
|--------|---------|---------|
| Gross LN | **+262 $** | Logic giá **có lãi thô** |
| Tổng phí | **-1.489 $** | Phí **lớn hơn** cả lãi gộp |
| Net LN | **-1.227 $** | Thất bại chủ yếu vì **phí + sizing** |
| Win Rate | 37.5% (9/24) | Với TP 2R, trước phí vẫn có thể hòa/có lãi nhẹ |
| Max DD | 12.4% | Chưa phải thảm họa vốn |

## Nguyên nhân chính (dễ hiểu)

1. **SL quá sát Entry** (zone/Spring sát giá) → khối lượng Qty rất lớn để giữ risk 1%.  
2. Phí = % trên **giá trị lệnh** (Qty × giá), không phải trên risk → Qty lớn = **phí ăn hết**.  
3. Nhiều lệnh (24) → phí cộng dồn.

Ví dụ: risk 100$, SL chỉ 0.2% giá → Qty lớn → phí 1 vòng dễ = vài chục $ → gần bằng 1 lần thua.

## Việc đã làm trong T3b

1. **Sàn SL tối thiểu** (`min SL = max(ATR×, % giá)`) → Qty không nổ.  
2. **Bỏ lệnh** nếu phí ước tính > X% risk (mặc định 25%).  
3. Mặc định chế độ **`Chỉ Spring/UT`** + cooldown cao hơn → ít lệnh hơn.  
4. TP mặc định **2.5R** (vẫn chỉnh được; Tomas đã chốt 2R — đổi lại trong Settings nếu muốn giữ 2R).  
5. Phí mặc định **0.04%/phía** (gần taker Bybit/Binance hơn); chỉnh theo sàn thật.

## Việc Tomas làm tiếp

1. Dán `T3b_optimize_thongke.pine` trên **BTCUSDT.P · 5m**.  
2. So bảng: Gross vs Tổng phí — phí phải nhỏ hơn Gross rõ.  
3. Nếu Win Rate vẫn thấp: gửi vài lệnh LOSS → lọc thêm (học từ WIN).  
4. Không tối ưu bằng cách tắt phí trong script (tự lừa mình).
