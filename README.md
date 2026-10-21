# Hệ thống giao dịch (Trading System)

Bot giao dịch cá nhân của Tomas: theo dõi **BTC** nhiều khung thời gian, tín hiệu khi chỉ báo **đồng thuận** (ngưỡng **60/100**), **Độ tin cậy** 1–10, **paper / backtest** trước live, **Telegram** + dashboard máy nhà.

**Sàn đầu:** Bybit (spot) qua ccxt · **Timezone:** Asia/Ho_Chi_Minh · **Paper:** 1.000 USDT

---

## Trạng thái

| Phase | Nội dung | Trạng thái |
|-------|----------|------------|
| Kiến trúc | Layers, CEX/DEX, TV, rating, notifier | Đã chốt |
| **1** | Nền tảng: cấu trúc, `.env`, logging, SQLite, Bybit/mock, paper skeleton | Xong |
| **2** | Plugin chỉ báo + **Wyckoff cơ bản** | Xong |
| **3** | Confluence AND + score ≥ 60 + **Độ tin cậy** rating | Xong |
| **4** | Risk (ATR sizing, SL/TP, kill switch) + paper | **Đang / vừa xong — chờ Tomas duyệt** |
| 5–6 | Backtest → Telegram/UI | Chưa |
| Add-on | **Pine Script** sau Phase 6; DEX adapter sau | Chưa |

Đọc bàn giao: **[docs/HANDOFF.md](docs/HANDOFF.md)** · Newbie xem **[docs/beginner-next-steps.md](docs/beginner-next-steps.md)** và **[docs/preferences.md](docs/preferences.md)**

---

## Phase 1 — chạy nhanh (máy bạn)

### 1) Tạo môi trường Python

```bash
cd trading-system
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) File bí mật

```bash
cp .env.example .env
```

Mặc định `MOCK_EXCHANGE=true` — **không cần** Bybit/Telegram key để chạy smoke + test.

Khi có key Bybit testnet: điền `BYBIT_API_KEY` / `BYBIT_API_SECRET`, đặt `MOCK_EXCHANGE=false`, `EXCHANGE_TESTNET=true`.

### 3) Chạy test

```bash
pytest
```

### 4) Smoke Phase 1–4

```bash
python -m trading_system
```

Sẽ: mock → confluence → **risk plan** (size/SL/TP hoặc reject) → paper nếu được duyệt.

### Phase 4 — risk & paper

- `%` rủi ro + ATR sizing, SL / TP1 (partial) / TP2 (runner)
- Kill switch, max lệnh, trần lỗ ngày
- Perp: thiếu SL → từ chối (khung sẵn, Spot đang dùng)
- Live stub — **chưa** bật tiền thật
- Config: `configs/risk.yaml` · code: `src/trading_system/risk/`

### Phase 3 — tín hiệu

- Strategy YAML: `configs/strategies/btc_confluence_wyckoff.yaml`
- Luật: mọi **required** phải đúng (AND) **và** score ≥ 60 → `fired`
- `rating` = **Độ tin cậy** 1–10 (chỉ khi fired)
- Engine: `src/trading_system/signals/`

### Phase 2 — chỉ báo có gì?

Plugin trong `src/trading_system/indicators/`: EMA 34/89, RSI, MACD, Bollinger, VWAP, ATR, Volume, market structure, S/R, mẫu nến, **Wyckoff cơ bản** (spring / upthrust / pha đơn giản). Lấy qua `get_indicator("rsi")` — xem `tests/test_indicators_math.py`.

---

## Cấu trúc (Phase 1)

```
configs/          # YAML: watchlist, exchanges, risk, notify, strategies
src/trading_system/
  data/           # ExchangeAdapter + Bybit (ccxt) + Mock + DEX placeholder
  storage/        # SQLite
  execution/      # PaperBroker skeleton
  notify/         # Telegram skeleton (chưa gửi tin thật)
  …               # stubs Phase 2–6
optional/         # Pine sau Phase 6
tests/
docs/
```

---

## Bảo mật

Không commit `.env`, API key, Telegram token. Chỉ commit `.env.example`.

---

## Tài liệu

| File | Nội dung |
|------|----------|
| [docs/HANDOFF.md](docs/HANDOFF.md) | Đọc trước |
| [docs/architecture-roadmap.md](docs/architecture-roadmap.md) | Kiến trúc 6 phase |
| [docs/project-context.md](docs/project-context.md) | Ngữ cảnh ngắn |
| [docs/cost-estimate.md](docs/cost-estimate.md) | Chi phí |
| [docs/preferences.md](docs/preferences.md) | Cách làm việc |
