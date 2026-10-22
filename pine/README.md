# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3d_balanced_wr.pine`** ← **DÙNG CÁI NÀY** | T3c bị **0 lệnh** — bản nới cân bằng, vẫn TP 1.5R + Spring/UT |
| `T3c_wr60_tp15.pine` | Quá siết (HTF + knife + reject bắt buộc) |
| `T3b_optimize_thongke.pine` | Chống phí |
| `T2_sd_thongke.pine` | S/D |

Vì sao 0 lệnh: [`docs/thesis/why-zero-trades-t3c.md`](../docs/thesis/why-zero-trades-t3c.md)

## T3d nới gì so với T3c?

| Lọc | T3c | T3d |
|-----|-----|-----|
| PA | Bắt buộc reject mạnh | Reject **hoặc** engulf |
| Volume | ×1.8 | ×1.2 |
| HTF 15m | Bật | **Tắt** (bật lại sau) |
| Chống dao rơi | Bật (chặn Spring) | **Tắt** |
| Cooldown | 48 | 24 |
| TP | 1.5R | 1.5R (giữ) |
| Spring/UT | Có | Có |

Góc phải dưới: dòng **Debug** giải thích Sp/UT chưa thành lệnh.

## Cách dán

1. Remove T3c.  
2. **BTCUSDT.P · 5m**.  
3. Dán `T3d_balanced_wr.pine` → Add to chart.  
4. Có lệnh rồi mới siết từng lọc (HTF → knife → volume).
