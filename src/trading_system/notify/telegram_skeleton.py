"""Skeleton Telegram — chưa gửi tin thật nếu thiếu token (Phase 6 sẽ hoàn thiện)."""

from __future__ import annotations

from trading_system.logging_setup import get_logger
from trading_system.settings import Settings, get_settings

log = get_logger("notify.telegram")


class TelegramNotifierSkeleton:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    def send_test(self, text: str = "Trading System Phase 1 — test") -> bool:
        """
        Phase 1: chỉ kiểm tra cấu hình.
        Có token → log cảnh báo 'chưa gửi HTTP' (tránh phụ thuộc mạng/bot lúc scaffold).
        Thiếu token → return False, không lỗi.
        """
        if not self.configured:
            log.info("Telegram chưa cấu hình (thiếu TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID)")
            return False
        log.info(
            "Telegram đã có credentials — gửi tin thật sẽ làm ở Phase 6. Nội dung mẫu: %s",
            text,
        )
        return True
