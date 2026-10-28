# Mac — tự `git pull` khi có code mới (cho làm việc trên điện thoại)

Bạn prompt trên **điện thoại** → agent cloud sửa code → **push GitHub**.  
Script này trên **Mac** (máy bật): mỗi vài phút kiểm tra; **chỉ khi có commit mới** mới `pull` + restart scanner.

## Chi phí

- **$0** thêm  
- Không gọi Binance chỉ vì check git  
- Không restart nếu không có update → pin/CPU gần như chỉ bằng lúc bot đang chạy

## Cài một lần (newbie)

### 1. Vào đúng repo

```bash
cd ~/trading-system
git fetch origin cursor/trading-thesis-pine-de71
git checkout cursor/trading-thesis-pine-de71
git pull origin cursor/trading-thesis-pine-de71
```

### 2. Config

```bash
cd ~/trading-system/scanner/mac
cp config.env.example config.env
nano config.env
```

Sửa nếu cần:

- `REPO_DIR` — mặc định `$HOME/trading-system`  
- `GIT_BRANCH` — `cursor/trading-thesis-pine-de71`  
- `CHECK_EVERY_SEC` — `600` = 10 phút (đổi `300`=5 phút, `900`=15 phút)

Có file `.env` ở gốc repo (token Telegram) như trước.

### 3. Cho phép chạy script

```bash
cd ~/trading-system/scanner/mac
chmod +x *.sh
```

### 4. Bật (cách đơn giản — giữ Terminal mở)

```bash
cd ~/trading-system/scanner/mac
./start_with_autoupdate.sh
```

Giữ cửa sổ Terminal này (hoặc để chạy nền). Mac **không sleep** nếu muốn nhận noti + auto-update liên tục.

Dừng scanner:

```bash
./stop_scanner.sh
```

Log xem tại: `scanner/mac/logs/`

## Quy trình hàng ngày (điện thoại + Mac)

1. Mac bật → chạy `./start_with_autoupdate.sh`  
2. Trên điện thoại: prompt agent sửa code (agent push GitHub)  
3. Trong ≤ 5–15 phút Mac tự pull + restart  
4. Telegram bot dùng bản mới — bạn không cần gõ `git pull` tay

## Lưu ý

- Tắt Mac / sleep sâu → hết auto-update và hết noti  
- Nếu `git pull` báo diverged: trên Mac mở Terminal báo mình (hoặc `git status`)  
- `config.env`, `*.pid`, `logs/` không cần commit lên GitHub
