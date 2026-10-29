# HANDOFF — Trading System

**Đọc file này trước.** Sau đó: `preferences.md` → `scanner/telegram-sd-alerts.md` → `thesis/decisions-locked.md` (nếu đụng thesis/Pine).

> **Cập nhật 2026-10-28:** Ưu tiên hiện tại = **Scanner Telegram S/D trên Mac** (cảnh báo vùng giá, không tự trade). Chart Pine **`pine/T3e.pine`**. Bot Phase 1–6 đầy đủ vẫn **hoãn**.

---

## Dự án là gì?

Hệ thống giao dịch cá nhân của **Tomas Le** (newbie — giải thích tiếng Việt, chậm, rõ).

| Lớp | Vai trò |
|-----|---------|
| **Pine `T3e.pine`** | Vẽ S/D + Sp/UT + THỐNG KÊ trên TradingView (đã **bỏ Trendline**) |
| **Scanner Python** | Máy Mac: theo dõi Perp → Telegram khi giá vào vùng đủ chất lượng |
| **Bot live / Phase 1–6** | **Hoãn** — chưa đặt lệnh thật |

---

## Nhánh Git (bắt buộc)

- **Nhánh làm việc:** `cursor/trading-thesis-pine-de71`
- Base PR thường: `main`
- Sau mỗi lần sửa: `commit` + `push` nhánh này
- **Không** force-merge `main` trừ khi Tomas yêu cầu

---

## Scanner — trạng thái & luật (đã code)

Code: `scanner/` · Docs: `docs/scanner/telegram-sd-alerts.md` · Mac: `scanner/mac/README.md`

| Mục | Đã chốt |
|-----|---------|
| Thị trường | **Perp** — Binance trước, thiếu thì Bybit |
| Watchlist | `scanner/watchlist.yaml` (+ Telegram `/add`) |
| Tin Telegram | Tiếng Việt; tiêu đề **Phương Pháp Supply & Demand**; có Entry, Vùng giá, **STL**, **TP**, **R:R**, độ hấp dẫn, độ tin cậy |
| STL | **Mọi tin** Entry→STL ≥ **2.5%**. Mép vùng chỉ dùng khi đã ≥ 2.5%; sát hơn → nới STL. Không gửi STL &lt; 2.5% |
| TP | Mép vùng đối ứng gần nhất **cùng TF** |
| Chất lượng (ít nhiễu) | Chỉ báo **H4/D1/W1**; độ sâu **≥7**; **≥2 TF**; cooldown vùng 30′ + cặp/chiều 60′ (**lưu đĩa**); mỗi vùng **1 tin/nhịp**; H1 chỉ confluence; **Nấc 1:** Bias **W1 EMA34** |
| `/add TÊN` | Tìm Binance→Bybit; **1 kết quả → thêm luôn**; nhiều → chọn 1,2,3… |
| `/top` | 3 lệnh đáng xem nhất **24h** (đã noti); **1 lần/cặp**; xếp tin cậy + độ sâu + R:R + TF + bias + soft pair (pair không cố định thứ tự) |
| Spam trạng thái | **Không** gửi: bắt đầu/xong scan, “Đã bật…”, “Đang tìm…”, “Xong N vùng…”. Giữ `✅ Đã thêm…` và **cảnh báo vùng** |
| Secrets | `.env` ở root (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) — **gitignored** |
| Mac chạy bot | **`start_with_autoupdate.sh`** (24/7): pull an toàn khi GitHub có commit; giữ `watchlist.local.yaml` + `.runtime/` (cooldown); giết orphan. Hoặc `start_scanner.sh` một lần |
| Restart & spam | Cooldown **lưu đĩa** → restart/auto-update **không** được phép spam lại trong 30–60′ |

**Lưu ý agent cloud:** Sửa code → push GitHub. **Không** SSH Mac. Tomas Mac chạy auto-update hoặc pull tay.

**Pine:** Khi gửi script cho Tomas → **chỉ link GitHub** (raw/blob), không dán full source vào chat.

---

## Pine / thesis

- Script hiện tại: **`pine/T3e.pine`** (không Trendline — Tomas: TL không hiệu quả)
- Chart học: BTCUSDT.P · method S/D + Wyckoff + PA (TL đã bỏ khỏi script)
- Chi tiết: `docs/thesis/*`

---

## Preferences nhanh

- Tiếng Việt, newbie, đề xuất → OK → mới code lớn
- Ít opex; không tự thuê VPS
- Không dùng LLM để quét giá (scanner = code + API sàn)
- Sau mỗi session: commit + push + cập nhật HANDOFF nếu đổi hướng

---

## Việc agent mới nên làm khi vào

1. `git fetch` + checkout **`cursor/trading-thesis-pine-de71`**
2. Đọc HANDOFF + `preferences.md` + `docs/scanner/telegram-sd-alerts.md`
3. Hỏi Tomas task tiếp theo (đừng đoán Phase 1 bot)
4. Nếu sửa scanner: push nhánh; nhắc Tomas `git pull` + `./stop_scanner.sh` + `./start_scanner.sh`

---

## English summary (for other AIs)

**Branch:** `cursor/trading-thesis-pine-de71`  
**Focus:** Mac Telegram SD zone scanner (alerts only, no execution). Quality filters: alert TF H4/D1/W1, depth≥7, ≥2 TF confluence, long cooldowns. `/add` auto-picks single match; `/top` ranks last-24h alerts. Pine: `pine/T3e.pine`. Phase 1–6 bot paused.  
**Mac:** `start_with_autoupdate.sh` — safe pull (preserve watchlist.local + .runtime cooldown), kill orphans, ff/hard sync to origin. Restart must not re-spam within cooldown.  
**Must-read:** this file, `docs/preferences.md`, `docs/scanner/telegram-sd-alerts.md`.
