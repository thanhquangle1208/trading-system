"""Chạy một lần kiểm tra vùng giá.

    python -m trading_system.zones --dry-run   # in tin, không gửi
    python -m trading_system.zones --claim-only  # chỉ ghi nhịp "Mac còn sống"
"""

from __future__ import annotations

import argparse
import os

from trading_system.data.http_client import UrllibClient
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.notify.telegram import TelegramNotifier
from trading_system.settings import get_settings
from trading_system.zones.config import load_buy_zone_config
from trading_system.zones.runner import clock_now, run_once
from trading_system.zones.state import GITHUB_RUNNER, LOCAL_RUNNER

log = get_logger("zones")


def resolve_runner(explicit: str | None) -> str:
    """Mac là mặc định. GitHub Actions tự nhận vì có biến GITHUB_ACTIONS."""
    if explicit in {LOCAL_RUNNER, GITHUB_RUNNER}:
        return explicit
    env = (os.getenv("BUY_ZONE_RUNNER") or "").strip().lower()
    if env in {LOCAL_RUNNER, GITHUB_RUNNER}:
        return env
    if os.getenv("GITHUB_ACTIONS") == "true":
        return GITHUB_RUNNER
    return LOCAL_RUNNER


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
    parser.add_argument(
        "--runner",
        choices=(LOCAL_RUNNER, GITHUB_RUNNER),
        default=None,
        help="local = máy Mac (mặc định khi chạy tay). github = máy GitHub.",
    )
    parser.add_argument(
        "--claim-only",
        action="store_true",
        help="Chỉ ghi nhịp còn sống, không đọc Notion và không gửi Telegram",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    setup_logging(settings.log_level)
    config = load_buy_zone_config(timezone=settings.timezone)
    if args.claim_only:
        save = not args.no_save_state
    elif args.no_save_state:
        save = False
    elif args.save_state:
        save = True
    else:
        save = not args.dry_run

    runner = resolve_runner(args.runner)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    report = run_once(
        settings=settings,
        config=config,
        http=UrllibClient(),
        notifier=notifier,
        now=clock_now(),
        dry_run=args.dry_run,
        save=save,
        runner=runner,
        claim_only=args.claim_only,
    )
    if report.yielded:
        log.info("Nhường cho máy đang giữ nhịp.")
        return 0
    if args.dry_run:
        log.info("Dry-run xong, %d tin.", len(report.messages))
    elif report.ok:
        log.info("Xong, đã xử lý %d tin.", len(report.messages))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
