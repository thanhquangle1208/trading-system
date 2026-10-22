# Trendline vs Sp / Demand — vì sao chart “có 2 đáy” mà không thấy đường chéo?

## Nhầm thường gặp

| Bạn thấy trên chart | Script dùng để vẽ Trendline? |
|---------------------|------------------------------|
| Nhãn **Sp** / **Demand** | **Không** — đó là zone S/D + Wyckoff |
| Đường bậc thang xanh/cam | **Không** — đó là **SuperTrend** |
| **Chấm tròn nhỏ** dưới đáy / trên đỉnh (T3e mới) | **Có** — đây mới là pivot của Trendline |

Hai đáy mắt bạn thấy (vd. chỗ Sp và chỗ Demand) **không tự động** là 2 điểm nối trendline.

## Luật vẽ Trendline hỗ trợ (TL↑)

Script chỉ nối khi:

1. Có ≥ 2 **pivot low** (theo `Trendline pivot trái/phải`).  
2. Đáy **sau cao hơn** đáy trước (**Higher Low**).  
3. Nếu 2 đáy mới nhất là đáy sau **thấp hơn** → không nối cặp đó; tìm cặp HL khác trong lịch sử pivot.

Kháng cự (TL↓): cần **Lower High** (đỉnh sau thấp hơn).

## Bug đã sửa (T3e)

Trước: xóa đường rồi chỉ vẽ lại khi vừa có pivot mới; nếu cặp mới không phải HL/LH → **mất hết đường**.  
Nay: vẽ lại **mỗi nến**, tìm cặp HL/LH hợp lệ, chấm điểm pivot TL, Debug hiện số đáy/đỉnh + có/chưa TL.

## Việc Tomas làm

1. Dán lại file `pine/T3e_trendline.pine` mới nhất.  
2. Bật **Chấm điểm pivot dùng cho TL**.  
3. Nhìn Debug: `TL đáy:X đỉnh:Y có TL↑/chưa TL↑`.  
4. Nếu muốn nhạy hơn: giảm pivot trái/phải xuống **2** (mặc định mới).
