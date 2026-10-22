# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Loại | Khi nào dùng |
|------|------|----------------|
| **`T1c_overlay_thongke.pine`** ← **DÙNG CÁI NÀY** | Indicator | Bảng **THỐNG KÊ trên chart** + hộp lệnh — **giống ảnh mẫu** |
| `T1b_strategy_thongke.pine` | Strategy | Có panel Strategy Tester **dưới** chart (không phải bảng mẫu) |
| `T1_trendline_volume.pine` | Indicator | Bản cũ, nhiều mũi tên |

Giải thích 2 loại bảng: [`docs/thesis/thongke-tren-chart.md`](../docs/thesis/thongke-tren-chart.md)

## Đã chốt

Chart **BINANCE:BTCUSDT.P** · TF **5m** · vốn **$10k** · TP **2R** · volume **bắt buộc**.

## Cách dán T1c (giống ảnh mẫu)

1. Gỡ hết script Thesis cũ trên chart (Remove).  
2. Đóng panel Strategy Tester phía dưới nếu đang mở (không cần).  
3. Symbol **BTCUSDT.P** (Binance) · khung **5**.  
4. Pine Editor → dán toàn bộ `T1c_overlay_thongke.pine` → Save → **Add to chart**.  
5. Nhìn **góc phải trên** chart: bảng tím **THỐNG KÊ** (Vốn ban đầu, Win Rate, Max DD…).  
6. Trên nến: hộp LONG/SHORT / WIN/LOSS.
