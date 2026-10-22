# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3e_trendline.pine`** ← **DÙNG CÁI NÀY** | Tên trên chart: **Thesis T3E** (T3d + Trendline) |
| `T3d_balanced_wr.pine` | Balanced trước khi có TL |
| `T3c_wr60_tp15.pine` | Quá siết |
| `T2_sd_thongke.pine` | S/D |

## Trendline trong T3e

| Thứ | Ý nghĩa |
|-----|---------|
| Đường **teal** chéo | Hỗ trợ (nối **Higher Low**) |
| Đường **cam** chéo | Kháng cự (nối **Lower High**) |
| Chấm tròn nhỏ | Pivot đang dùng cho TL (không phải Sp/Demand) |
| SuperTrend bậc thang | **Không** phải trendline |

**Sp / Demand ≠ điểm TL.** Xem `docs/thesis/trendline-vs-sp.md`.

Settings nhóm **Trendline**:

- **Vẽ trendline** — mặc định bật  
- **Chấm điểm pivot dùng cho TL** — mặc định **tắt** (UI gọn); bật khi muốn debug điểm đang nối  
- **Bắt buộc gần trendline khi vào lệnh** — mặc định **TẮT**

## Cách dán

1. Remove T3d.  
2. **BTCUSDT.P · 5m**.  
3. Dán `T3e_trendline.pine` → Add to chart.  
4. Thấy đường chéo teal/cam + vẫn có Sp/UT, S/D, THỐNG KÊ.
