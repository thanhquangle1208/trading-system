# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3_wyckoff_pa_thongke.pine`** ← **DÙNG CÁI NÀY** | T3: S/D + Spring/UT + PA + THỐNG KÊ (siết nhất hiện tại) |
| `T2_sd_thongke.pine` | T2: S/D filter (chưa Spring/PA) |
| `T1c_overlay_thongke.pine` | Chỉ bias + volume — nhiều lệnh |
| `T1b_strategy_thongke.pine` | Strategy Tester panel dưới |

## T3 lọc lệnh thế nào?

| Trụ | Điều kiện |
|-----|-----------|
| Bias | SuperTrend đúng hướng |
| S/D | Chạm **Demand** (LONG) / **Supply** (SHORT) |
| Wyckoff | **Spring** (đâm dưới Demand rồi đóng lại) hoặc **Upthrust** (đâm trên Supply rồi đóng lại) — tùy chế độ |
| PA | Reject wick hoặc Engulfing (bắt buộc mặc định) |
| Volume | ≥ SMA × hệ số |
| Cooldown | Có |

**Chế độ vào lệnh** (Settings → Wyckoff / PA):

1. `Zone+PA hoặc Spring/UT` — mặc định  
2. `Chỉ Spring/UT` — ít lệnh nhất  
3. `Zone+PA (như T2+PA)` — không bắt buộc Spring  

Kim cương **Sp** / **UT** trên chart = sự kiện Wyckoff.

## Cách dán

1. Remove script cũ (T2/T1c).  
2. Chart: **BINANCE:BTCUSDT.P** · **5m**.  
3. Dán `T3_wyckoff_pa_thongke.pine` → Add to chart.  
4. So **Tổng lệnh** / Win Rate với T2.

## Đã chốt

Vốn $10k · TP **2R** · volume bắt buộc · 4 trụ S/D + Wyckoff + PA + Trend.
