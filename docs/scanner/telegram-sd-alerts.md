# Scanner Telegram — Vùng Mua / Vùng Bán (HTF)

**Trạng thái (2026-10-23):** Tomas **OK code scanner** (cách A). Code MVP: thư mục [`scanner/`](../../scanner/). Chạy trên máy: `python -m sd_scanner test|scan` (xem `scanner/README.md`).

Mục tiêu: khi giá **cắt ngưỡng** Vùng Mua (Demand) / Vùng Bán (Supply) trên **H1, H4, D1, W1**, báo Telegram. Tomas mở chart → tự quyết định. **Không** tự vào lệnh.

---

## Quyết định đã khóa

| Mục | Quyết định |
|-----|------------|
| Thị trường | **Perp** trước; **Binance** → thiếu cặp thì **Bybit** |
| TF | **H1, H4, D1, W1** từ đầu |
| Điểm | Thang **1–10** (không dùng A/B/C) |
| `depth_score` | Độ **hấp dẫn** theo độ sâu trong vùng giá (1–10) |
| `độ_tin_cậy` | Thang **x/10** (confluence TF + ngữ cảnh); ví dụ 6 / 8 / 9.5 |
| Nhãn tin | **Vùng Mua** / **Vùng Bán** / **Vùng giá** (không ghi L1/L2/L3) |
| Chống spam / chất lượng | Báo **H4/D1/W1** only; sâu ≥7; ≥2 TF; cooldown 30–60′ **persist đĩa** (không mất khi Mac auto-pull restart); **1 tin / vùng / nhịp**; `/add` không “Đang tìm…”; **Bias W1 EMA34** |
| Chạy | Lệnh **scan một lần** → **bật theo dõi** đến khi tắt process / tắt máy |
| Chi phí | **0$** API công khai + Telegram Bot miễn phí; **không** dùng LLM để quét giá |

Chi tiết thesis Pine vẫn: [`../thesis/decisions-locked.md`](../thesis/decisions-locked.md). Script chart: `pine/T3e.pine`.

---

## Tin mẫu (tiếng Việt, HTML đậm trên Telegram)

```
🏷️ Phương Pháp Supply & Demand · Cảnh báo vùng giá

📊 PHÂN TÍCH TÍN HIỆU
━━━━━━━━━━━━━━━━
🟢 MUA ETHUSDT.P
⏱ Khung: H4
📍 Giá / Entry gợi ý: 2382.5
📦 Vùng giá: 2320 – 2390
🛑 STL: 2320
✅ TP: 2510   (mép Vùng Bán gần nhất cùng TF; — nếu chưa có)
📐 R:R: 1 : 2.1

⭐ Độ hấp dẫn (độ sâu): 7.8/10
📈 Độ tin cậy: 6.5/10
```

**STL / TP (gợi ý, không tự lệnh):**
- STL = mép hết vùng (Mua → đáy vùng; Bán → đỉnh vùng).
- TP = mép vào vùng đối ứng gần nhất cùng khung (Mua → Vùng Bán phía trên; Bán → Vùng Mua phía dưới).
- R:R = |TP − giá| / |giá − STL|.

Công thức sơ bộ (chỉnh khi code):

- **Độ hấp dẫn** = `6 + 3 × penetration` (penetration 0→1 trong vùng), làm tròn 1 chữ số.
- **Độ tin cậy** = điểm nền theo số TF cùng phía có vùng gần giá (vd. 1 TF≈5–6, 2 TF≈7–8, 3–4 TF≈8.5–9.5), có thể ± nhẹ theo volume/PA sau.

---

## Cách chạy (ý Tomas — đã chốt)

1. Bật máy Mac → chạy scanner (hoặc mở Telegram gửi `/scan`).
2. **Một lần scan** = nạp watchlist + cache vùng giá + **bật chế độ theo dõi**.
3. Sau đó **tự** so giá với ngưỡng; **chỉ khi cắt threshold** mới gửi Telegram (kiểu “ví có action mới noti”).
4. **Tắt máy / sleep sâu / tắt terminal chạy scanner** → process chết → **không còn noti** (xem mục Mac bên dưới).

Không cần gõ scan liên tục trong phiên đó.

---

## Chi phí thực tế (quan trọng — đừng nhầm “token”)

Có **3 loại “token/chi phí”** khác nhau:

| Loại | Scanner này dùng? | Giá |
|------|-------------------|-----|
| **Telegram Bot API** | Có (gửi tin) | **Miễn phí** |
| **Binance / Bybit REST API** | Có (lấy giá / nến) | **Miễn phí** (giới hạn số request/phút) |
| **Token AI / ChatGPT / Cursor** | **Không** — luật vùng giá bằng code Python, không gọi LLM mỗi lần quét | **0** |

### 100 tin Telegram tốn bao nhiêu?

- **Telegram:** ~**0$**, không trừ “token AI”. Bot cá nhân gửi 100 tin/ngày là bình thường, không mất phí.
- **Binance/Bybit:** tin Telegram **không** tính theo số noti; sàn tính theo **số lần gọi API** (lấy giá). Thiết kế đúng: hầu hết vòng lặp chỉ gọi **ticker** (nhẹ); chỉ khi giá gần vùng mới xử lý sâu + gửi tin → 100 noti ≈ thêm vài trăm request nhỏ, vẫn trong hạn miễn phí.

### Binance / Bybit cho free bao nhiêu? (xấp xỉ, đọc công khai)

Số liệu thay đổi theo thời gian; agent/code phải tôn trọng header rate-limit. Hướng dẫn thực dụng:

| Sàn | Kiểu | Gợi ý hạn mức (công khai, có thể đổi) |
|-----|------|----------------------------------------|
| **Binance Futures (Perp)** | Request weight / IP | Thường cỡ **2400 weight / phút** (futures); endpoint ticker/klines mỗi lần tốn vài–vài chục weight |
| **Binance** | API key (public market data) | Market data **không cần** trả tiền; key chỉ cần nếu sau này trade |
| **Bybit** | Rate limit theo endpoint | Public market data miễn phí; thường đủ cho watchlist cá nhân vài–vài chục cặp |

**Ước lượng MVP (ví dụ 20 cặp, đang theo dõi):**

- Mỗi 30–60 giây: 20 lần lấy giá last → rất nhẹ so với hạn mức/phút.
- Rebuild nến H1/H4/D1/W1: thưa (khi nến đóng hoặc lần đầu scan) → vài chục–vài trăm klines/ngày.
- → **Không cần trả phí API** cho mức dùng cá nhân. Nghẽn chỉ xảy ra nếu quét sai kiểu “mỗi 30s tải full mọi TF mọi cặp liên tục không cache”.

### Tối ưu đã chốt (giống bài học ví on-chain)

1. Cache **ranh giới vùng giá**; không tính lại từ đầu mỗi giây.  
2. Vòng theo dõi: chỉ **giá last** vs ngưỡng.  
3. Xa mọi vùng → **im**, không Telegram.  
4. Cắt ngưỡng + đúng luật nhịp → mới noti.

---

## Tắt máy Mac thì sao?

| Tình huống | Còn nhận Telegram? |
|------------|-------------------|
| Mac **bật**, scanner **đang chạy** (terminal / app) | Có — tự noti khi cắt ngưỡng |
| Mac **sleep** (nắp máy, sleep) | Thường **dừng** hoặc rất không ổn định |
| Mac **tắt nguồn** / mất điện | **Không** — process chết, không ai gọi API/Telegram |
| Thuê VPS 24/7 (sau này, nếu Tomas yêu cầu) | Có thể chạy nền; **hiện ưu tiên máy nhà $0** |

**Kết luận:** “Scan một lần rồi tự noti” chỉ đúng **trong lúc chương trình còn sống trên máy**. Tắt Mac = hết theo dõi đến khi bạn bật lại và `/scan` (hoặc start) lần nữa.

---

## Hướng dẫn tạo bot Telegram (newbie — từng bước)

Làm trên điện thoại hoặc máy tính đều được. Cần app **Telegram** đã đăng nhập.

### Bước 1 — Mở BotFather

1. Mở Telegram.  
2. Ô tìm kiếm (kính lúp) gõ: `BotFather`  
3. Chọn tài khoản **BotFather** có dấu ✓ xanh (official).  
4. Bấm **Start** / gửi `/start`.

BotFather là “người tạo bot” của Telegram — miễn phí.

### Bước 2 — Tạo bot mới

1. Gửi đúng chữ: `/newbot`  
2. BotFather hỏi **tên hiển thị** (display name) — đặt gì cũng được, ví dụ: `Tomas SD Alert`  
3. Tiếp theo hỏi **username** — phải kết thúc bằng `bot`, ví dụ: `tomas_sd_alert_bot`  
   - Nếu báo “already taken” → đổi tên khác (thêm số).  
4. Khi thành công, BotFather gửi một dòng **HTTP API token** dạng:

   `123456789:AAH...rất dài...`

5. **Copy giữ riêng.** Đây là chìa khóa bot.  
   - Không gửi token vào group công khai.  
   - Có thể dán vào file `.env` trên máy bạn sau (agent sẽ nói rõ khi code).

### Bước 3 — Nhắn cho bot của bạn lần đầu

1. Trong Telegram, tìm đúng username bot vừa tạo (ví dụ `@tomas_sd_alert_bot`).  
2. Mở chat → bấm **Start** hoặc gửi `/start`.  
   (Nếu chưa Start, bot khó gửi tin cho bạn.)

### Bước 4 — Lấy Chat ID (địa chỉ nhận tin)

Cách đơn giản cho newbie:

1. Tìm bot `@userinfobot` hoặc `@getidsbot` trên Telegram.  
2. Start → nó hiện **Id** (số, có thể là số dương).  
3. Đó là **Chat ID** của bạn — copy lại.

Cách khác (sau khi đã Start bot của mình): mở trình duyệt (khi có token):

`https://api.telegram.org/bot<TOKEN>/getUpdates`

(thay `<TOKEN>` bằng token thật, không khoảng trắng). Trong JSON tìm `"chat":{"id": ........}` — số đó là Chat ID.

### Bước 5 — Báo lại cho agent (khi sẵn sàng code)

Khi làm xong, nhắn trong chat project kiểu:

- “Đã có token + chat id”  
- **Không bắt buộc** dán token lên chat nếu bạn ngại; có thể chỉ nói “đã tạo”, rồi tự dán vào `.env` khi agent tạo file mẫu.

Hoặc (nếu bạn chấp nhận lưu trong môi trường Cloud): gửi token + chat id **một lần** để agent ghi `.env.example` hướng dẫn — **không commit token lên GitHub**.

### Bước 6 — Kiểm tra thử (sau khi có code)

Agent sẽ có lệnh kiểu “gửi tin test”. Bạn chỉ cần xem Telegram có nhận: `Xin chào Tomas — scanner OK` hay không.

---

## Việc tiếp theo (chờ Tomas)

1. Tomas làm Bước 1–4 ở trên.  
2. Nhắn **“OK code scanner”** (+ đã có token/chat id hoặc sẽ tự điền `.env`).  
3. Agent mới scaffold: watchlist YAML, `/scan` bật watch, Binance perp, tin tiếng Việt, depth + độ tin cậy /10.
