"""Chạy một lần kiểm tra vùng giá.

    python -m trading_system.zones            # gửi Telegram, ghi trạng thái
    python -m trading_system.zones --dry-run  # chỉ in tin, không gửi, không ghi trạng thái
"""

from __future__ import annotations

import argparse

from trading_system.data.http_client import UrllibClient
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.notify.telegram import TelegramNotifier
from trading_system.settings import get_settings
from trading_system.zones.config import load_buy_zone_config
from trading_system.zones.runner import clock_now, run_once

log = get_logger("zones")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cảnh báo vùng giá gom (Notion → Telegram)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="In tin ra màn hình, không gửi Telegram và không ghi trạng thái",
    )
    parser.add_argument(
        "--save-state",
        action="store_true",
        help="Vẫn ghi trạng thái khi đang --dry-run",
    )
    parser.add_argument(
        "--no-save-state",
        action="store_true",
        help="Không ghi trạng thái (kể cả lần chạy thật)",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    setup_logging(settings.log_level)
    config = load_buy_zone_config(timezone=settings.timezone)
    if args.no_save_state:
        save = False
    elif args.save_state:
        save = True
    else:
        save = not args.dry_run

    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    report = run_once(
        settings=settings,
        config=config,
        http=UrllibClient(),
        notifier=notifier,
        now=clock_now(),
        dry_run=args.dry_run,
        save=save,
    )
    if args.dry_run:
        log.info("Dry-run xong, %d tin.", len(report.messages))
    elif report.ok:
        log.info("Xong, đã xử lý %d tin.", len(report.messages))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
