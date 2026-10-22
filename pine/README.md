# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3c_wr60_tp15.pine`** ← **DÙNG CÁI NÀY** | Ưu tiên **WR ~60%**, TP **1.5R** |
| `T3b_optimize_thongke.pine` | Chống phí ăn PnL (TP cao hơn) |
| `T3_wyckoff_pa_thongke.pine` | T3 gốc |
| `T2_sd_thongke.pine` | S/D |

Doc: [`docs/thesis/wr60-tp15-path.md`](../docs/thesis/wr60-tp15-path.md)

## T3c khác gì?

- TP mặc định **1.5R**  
- **Chỉ Spring / Upthrust** + reject wick mạnh  
- Lọc **HTF 15m** + chống dao rơi  
- Volume / cooldown siết hơn  
- Giữ sàn SL + fee cap  

## Cách dán

1. Remove script cũ.  
2. **BTCUSDT.P · 5m**.  
3. Dán `T3c_wr60_tp15.pine` → Add to chart.  
4. Xem **Win Rate** (xanh khi ≥ 60%) và Net / Phí.
