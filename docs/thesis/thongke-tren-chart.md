# Bảng THỐNG KÊ trên chart vs panel dưới

## Hai thứ khác nhau

| | Ảnh mẫu bạn muốn | Ô đỏ bạn khoanh (T1b) |
|--|------------------|------------------------|
| Là gì? | Bảng **vẽ trên chart** bằng Pine (`table`) | **Strategy Tester** — panel có sẵn của TradingView |
| Nằm đâu? | **Góc phải trên** vùng giá | **Phía dưới** cửa sổ chart |
| Tiêu đề | `THỐNG KÊ` (tím) | `Thesis T1b — …` + Total PnL / Performance graph |
| Cách có | Dùng script **indicator** T1c | Tự hiện khi script là **strategy** |

```
┌─────────────────────────────────────┬──────────────┐
│  Chart nến + hộp LONG/SHORT         │  THỐNG KÊ    │  ← muốn cái này (ảnh mẫu)
│                                     │  trên chart  │
├─────────────────────────────────────┴──────────────┤
│  Strategy Tester (Total PnL, graph…)               │  ← cái bạn khoanh (TV sẵn)
└────────────────────────────────────────────────────┘
```

## Làm sao giống ảnh mẫu?

1. **Gỡ** script T1b (strategy) trên chart.  
2. Dán **`pine/T1c_overlay_thongke.pine`** (indicator).  
3. Chart: **BINANCE:BTCUSDT.P** · khung **5**.  
4. Nhìn **góc phải trên** chart — bảng tím **THỐNG KÊ**.  
5. Có thể **đóng** panel Strategy Tester (X) — không cần cho T1c.
