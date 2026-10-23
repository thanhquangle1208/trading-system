"""Chạy từ thư mục scanner/:  python -m sd_scanner test|scan"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scanner Vùng Mua/Bán → Telegram (newbie: dùng test rồi scan)"
    )
    parser.add_argument(
        "command",
        choices=["test", "scan"],
        help="test = gửi tin thử; scan = nạp vùng rồi tự theo dõi",
    )
    args = parser.parse_args()

    from sd_scanner.config import load_settings
    from sd_scanner.telegram_notify import Telegram
    from sd_scanner.watch import Watcher

    settings = load_settings()
    tg = Telegram(settings.telegram_token, settings.telegram_chat_id)

    if args.command == "test":
        tg.send(
            "✅ Test OK — bot Telegram đã nối với máy scanner.\n"
            "Bước sau trên máy: python -m sd_scanner scan"
        )
        print("Đã gửi tin test. Mở Telegram kiểm tra.")
        return

    watcher = Watcher(settings)
    try:
        watcher.run_scan_session()
    except KeyboardInterrupt:
        print("\nĐã dừng (Ctrl+C).")
        try:
            tg.send("⏹ Scanner dừng (Ctrl+C / tắt terminal trên máy).")
        except Exception:
            pass


if __name__ == "__main__":
    main()
