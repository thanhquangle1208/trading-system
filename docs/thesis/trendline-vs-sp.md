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

## Vì sao có 2 đường teal song song?

Settings **Số trendline mỗi phía** mặc định = **2**.

| Đường | Ý nghĩa |
|-------|---------|
| TL↑ **mới** (thường sát giá hơn) | Nối 2 đáy Higher Low gần nhất — dễ nhìn, có chấm tròn |
| TL↑ **thứ 2** (thường thấp hơn) | Cặp HL **khác** (thường pivot cũ hơn) → kéo dài về phía phải; đoạn nhìn thấy có thể **không** đi qua 2 đáy rõ trên màn hình → trông “chả nối gì” |

Không phải bug vẽ lệch: script cố ý vẽ tối đa N đường. Muốn chỉ 1 đường rõ: Settings → **Số trendline mỗi phía = 1**.

## Việc Tomas làm

1. Dán lại file `pine/T3e_trendline.pine` mới nhất (tên chart: **Thesis T3E**).  
2. (Tuỳ chọn) Bật **Chấm điểm pivot dùng cho TL** nếu muốn debug — mặc định **tắt**.  
3. Nhìn Debug: `TL đáy:X đỉnh:Y có TL↑/chưa TL↑`.  
4. Nếu muốn nhạy hơn: giảm pivot trái/phải xuống **2** (mặc định mới).  
5. Nếu đường thứ 2 gây rối: đặt **Số trendline mỗi phía = 1**.
