# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3e_trendline.pine`** ← **DÙNG CÁI NÀY** | T3d + **Trendline** (đường xu hướng) |
| `T3d_balanced_wr.pine` | Balanced trước khi có TL |
| `T3c_wr60_tp15.pine` | Quá siết |
| `T2_sd_thongke.pine` | S/D |

## Trendline trong T3e

| Thứ | Ý nghĩa |
|-----|---------|
| Đường **teal** chéo | Hỗ trợ (nối swing low cao dần) |
| Đường **cam** chéo | Kháng cự (nối swing high thấp dần) |
| Khác SuperTrend | SuperTrend = bậc thang ATR; Trendline = nối pivot |

Settings nhóm **Trendline**:

- **Vẽ trendline** — mặc định bật  
- **Bắt buộc gần trendline khi vào lệnh** — mặc định **TẮT** (chỉ vẽ; bật sau nếu muốn siết confluence)

## Cách dán

1. Remove T3d.  
2. **BTCUSDT.P · 5m**.  
3. Dán `T3e_trendline.pine` → Add to chart.  
4. Thấy đường chéo teal/cam + vẫn có Sp/UT, S/D, THỐNG KÊ.
