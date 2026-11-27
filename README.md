# Hệ thống giao dịch (Trading System)

Repo này là **bộ tài liệu + (sau này) mã nguồn** cho bot giao dịch cá nhân của Tomas: theo dõi **BTC** nhiều khung thời gian, tín hiệu khi chỉ báo **đồng thuận**, quản lý rủi ro, chạy **paper / backtest** trước rồi mới **live**, báo **Telegram** và xem trên **dashboard** máy nhà.

> **Đã chạy được:** cảnh báo **vùng giá gom** (Notion → Telegram), 24/7 trên GitHub Actions, không cần mở máy. Làm theo mục [Cảnh báo vùng giá gom](#cảnh-báo-vùng-giá-gom).
>
> **Phase 1–6** (chỉ báo, paper, dashboard) vẫn nằm ở các PR nháp, **chưa** có trên `main`. Đọc **HANDOFF** trước khi đụng phần đó.

---

## Cảnh báo vùng giá gom

Bot đọc database Notion **「Vùng giá gom token」** mỗi lần chạy. Chỉ xét dòng **Trạng thái = Đang theo dõi**.

- Giá đi vào khoảng **Giá dưới → Giá trên**: gửi **một** tin. Giá phải ra khỏi vùng **hơn 2%** thì mới “cài lại”; lần sau vào vùng sẽ báo tiếp (tránh báo liên tục khi giá đứng sát mép).
- Sau **07:00 giờ Việt Nam** (nến ngày đóng lúc 00:00 UTC): nếu giá đóng **thấp hơn** mức **Vô hiệu nếu nến ngày đóng dưới**, gửi **một** tin. Đây là “vùng không còn đúng, dừng mua và đánh giá lại” — **không** phải cắt lỗ, và bot **không sửa** Notion.
- **07:05** gửi bản tin sáng: những vùng mà giá **đang nằm trong**. GitHub có thể trễ vài phút; trong ngày chỉ gửi một lần.
- Token không lấy được giá (SECZ là cổ phiếu, một số coin nhỏ không có trên sàn) bị **bỏ qua và ghi log**, bot không sập.
- Cột **Chuỗi/sàn tham chiếu** (ví dụ `Spot / Binance BTCUSDT`) chọn sàn. Nếu sàn bị chặn, thử Bybit → Binance → OKX, rồi CoinGecko.

Tin mẫu:

```text
🟢 BTC vào Vùng 1 (55.000–61.000). Giá hiện tại: 60.850. Ghi chú: Z1 vesting … (chỉ tokenomics/vesting/Z1–Z3)
🔴 BTC – Vùng 1 hết hiệu lực: nến ngày đóng 52.700 < 53.000. Dừng mua vùng này, đánh giá lại.
```

Bot này **không nghe lệnh** kiểu `/zones` (GitHub Actions không chạy liên tục để nhận tin nhắn). Thay vào đó là bản tin 07:05.

### Việc Tomas phải làm một lần

Repo công khai. **Không** dán token vào file rồi commit. Chỉ điền GitHub Secrets (và file `.env` trên máy nếu muốn chạy thử).

#### 1. Notion — integration chỉ được đọc

1. Mở [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations) → **New integration**.
2. Tên tùy ý, ví dụ `Vung gia gom`. Quyền: **Read content**. Không cần quyền sửa.
3. Copy **Internal Integration Secret** — đây là `NOTION_TOKEN` (bắt đầu bằng `ntn_` hoặc `secret_`).
4. Mở database **Vùng giá gom token** → menu `•••` góc trên → **Connections** / **Add connections** → chọn integration vừa tạo.  
   Chưa share thì API trả 404, bot không đọc được dòng nào.
5. Id đã gắn sẵn trong code, thường **không cần sửa**:
   - Database: `41e859693b1581cc80bbfbcd6fe9e8c3`
   - Data source: `41e85969-3b15-815a-9e5e-000b774bd208`

Sửa vùng, giá, hoặc đổi Trạng thái trên Notion là đủ. Lần chạy sau (tối đa khoảng 10 phút, cộng độ trễ của GitHub) dùng số mới. Không cần sửa code.

#### 2. Telegram — tạo bot

1. Mở Telegram, nhắn [@BotFather](https://t.me/BotFather) → `/newbot` → đặt tên → copy **token**. Đó là `TELEGRAM_BOT_TOKEN`.
2. Mở chat với bot đó, nhắn `/start` (một chữ cũng được).

#### 3. Lấy chat id

Trên máy bạn, trong thư mục repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Mở `.env`, dán `TELEGRAM_BOT_TOKEN=...`, lưu. Rồi:

```bash
PYTHONPATH=src python -m trading_system.notify.chat_id
```

In ra một số, ví dụ `123456789`. Đó là `TELEGRAM_CHAT_ID`.  
Chat riêng: số dương. Nhóm: thêm bot vào nhóm, nhắn một tin trong nhóm, chạy lại — id nhóm thường có dấu trừ, copy cả dấu trừ.

Nếu lệnh bảo chưa thấy tin: nhắn lại cho bot rồi chạy lại.

#### 4. Thêm 3 secret trên GitHub

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Tên secret | Giá trị |
|------------|---------|
| `NOTION_TOKEN` | secret integration ở bước 1 |
| `TELEGRAM_BOT_TOKEN` | token BotFather |
| `TELEGRAM_CHAT_ID` | số ở bước 3 |

Không bắt buộc: `COINGECKO_API_KEY` (chỉ khi CoinGecko giới hạn giá coin nhỏ).

#### 5. Bật lịch chạy

1. Merge pull request này vào nhánh **`main`**. Lịch của GitHub **chỉ chạy trên nhánh mặc định**.
2. Tab **Actions** → **Cảnh báo vùng giá gom**. Nếu có nút **Enable workflow** thì bấm.
3. Bấm **Run workflow** một lần để thử. Để ô dry-run **tắt** nếu muốn nhận tin thật; bật dry-run nếu chỉ muốn xem log, không gửi Telegram.
4. Lịch GitHub vẫn bật. Đó là bản dự phòng khi Mac tắt. Khi Mac đang chạy, GitHub thấy nhịp và **không gửi thêm**.

Xem log: Actions → lần chạy mới nhất. Dòng `Mac đang chạy` nghĩa là GitHub đang nhường. Dòng `Không lấy được giá SECZ` là bình thường.

### Chạy trên Mac (giá Bybit / Binance), GitHub dự phòng

Hướng dẫn ngắn, từng bước: **[docs/HUONG-DAN-MAC.md](docs/HUONG-DAN-MAC.md)**

Máy GitHub ở Mỹ bị Bybit/Binance chặn nên dùng OKX/CoinGecko. Mac ở Việt Nam dùng Bybit/Binance. Mac ghi nhịp lên nhánh `buy-zone-alert-state`; GitHub chỉ chạy khi nhịp Mac cũ hơn ~20 phút.

Cài một lần:

```bash
cd ~/trading-system
git checkout main
git pull
bash scripts/mac/setup_once.sh
```

Bật / tắt:

```bash
bash scripts/mac/start_buy_zones.sh
bash scripts/mac/stop_buy_zones.sh
tail -n 40 .state/buy_zones.log
```

Script `start` tự báo nếu thiếu `.venv`, thư viện, hoặc token trong `.env`. Không tự viết vòng `while` ngoài `scripts/mac/`.

### Nhớ “đã báo chưa” — vì sao không dùng cache?

File nhớ chỉ có cờ (id trang, đang ở trong vùng hay không, mức vô hiệu đã báo, ngày bản tin, id CoinGecko, và nhịp Mac/GitHub). **Không** có token, không có ghi chú phân tích.

- Trên máy: file `.state/buy_zones.json` (đã nằm trong `.gitignore`, không commit vào nhánh code).
- Trên GitHub: nhánh riêng `buy-zone-alert-state`, file `state/buy_zones.json`. Mac và GitHub cùng sửa file này.

Cache của GitHub Actions có thể bị **xóa** sau vài ngày không đụng tới, rồi bot báo lại từ đầu. Nhánh git không bị xóa như vậy, nên dùng nhánh. Workflow tự tạo và tự cập nhật nhánh đó. Bạn không cần tạo tay.

Đổi ngưỡng 2% hoặc bật tin “đang tiến gần” (mặc định **tắt**): sửa `configs/buy_zones.yaml` (`hysteresis_pct`, `approaching_pct`), rồi merge.

### Kiểm tra code

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m pytest
```

---

## Bắt đầu từ đâu? (quan trọng)

1. Mở nhánh Git: **`cursor/architecture-roadmap-abd1`**
2. Đọc file bàn giao trước tiên:

### → [docs/HANDOFF.md](docs/HANDOFF.md) ← đọc file này trước

Sau đó lần lượt:

| Thứ tự | File | Nội dung |
|--------|------|----------|
| 1 | [docs/HANDOFF.md](docs/HANDOFF.md) | Tóm tắt dự án, quyết định đã chốt, câu hỏi còn mở, trạng thái phase |
| 2 | [docs/architecture-roadmap.md](docs/architecture-roadmap.md) | Kiến trúc đầy đủ + lộ trình 6 phase |
| 3 | [docs/project-context.md](docs/project-context.md) | Ngữ cảnh ngắn cho agent / phiên sau |
| 4 | [docs/cost-estimate.md](docs/cost-estimate.md) | Dự toán chi phí (ưu tiên ~$0 với paper + máy nhà) |
| 5 | [docs/preferences.md](docs/preferences.md) | Cách làm việc Tomas muốn (tiếng Việt, duyệt trước khi code, …) |

---

## Tiếp tục trong Cursor Repositories

1. Trong Cursor: **Repositories** → mở repo này.
2. Checkout nhánh **`cursor/architecture-roadmap-abd1`** (nhánh có tài liệu mới nhất; `main` thường đang đứng sau).
3. Mở **chat mới** trong repo đó và bảo agent đọc `docs/HANDOFF.md` trước.
4. **Chưa** bảo agent code Phase 1 trừ khi bạn đã trả lời câu hỏi còn mở (hoặc chủ động bỏ qua) và nói rõ **“OK Phase 1”**.

Hướng dẫn ngắn + câu prompt mẫu: xem tài liệu Project store `docs/repo-switch-guide.md` (nếu còn dùng Project), hoặc copy prompt trong `docs/HANDOFF.md`.

---

## Lộ trình (tóm tắt)

| Phase | Nội dung | Trạng thái |
|-------|----------|------------|
| Kiến trúc | Layers, CEX/DEX, TV hai hướng, rating, notifier | Đã viết trên nhánh này |
| **1** | Nền tảng: cấu trúc, `.env`, logging, SQLite, Bybit (ccxt), paper skeleton | **Chưa bắt đầu** |
| 2 | Plugin chỉ báo | Chưa |
| 3 | Watchlist multi-TF + confluence + **rating** | Chưa |
| 4 | Risk + execution (paper/live) | Chưa |
| 5 | Backtest multi-TF + Optuna | Chưa |
| 6 | Telegram templates + dashboard | Chưa |

**Add-on sau:** Pine Script (TradingView); DEX adapter riêng.

---

## Chạy phần còn lại của hệ thống

Phase 1–6 (paper, chỉ báo, dashboard) **chưa** nằm trên `main`. Khi các PR đó được merge, README của từng phase có lệnh chạy. Phần **đã** chạy được hôm nay là cảnh báo vùng giá ở trên.

## Bảo mật

Không commit API key / Telegram token / Notion token. Mẫu nằm ở `.env.example`. File `.env` và thư mục `.state/` bị git bỏ qua.
