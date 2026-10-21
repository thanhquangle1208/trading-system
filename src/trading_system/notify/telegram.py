"""Gửi Telegram thật (khi có token); không có token → dry-run."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

from trading_system.logging_setup import get_logger
from trading_system.notify.router import NotifyConfig, load_notify_config, resolve_channel
from trading_system.notify.templates import format_signal_message, format_test_message
from trading_system.settings import Settings, get_settings
from trading_system.signals.models import SignalResult

log = get_logger("notify.telegram")

SendFn = Callable[[str, str, str], dict[str, Any]]


def _http_send(token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


class TelegramNotifier:
    def __init__(
        self,
        settings: Settings | None = None,
        notify_cfg: NotifyConfig | None = None,
        send_fn: SendFn | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.notify_cfg = notify_cfg or load_notify_config()
        self._send_fn = send_fn or _http_send
        # Đồng bộ chat_id từ settings nếu channel trống
        for ch in self.notify_cfg.channels.values():
            if not ch.chat_id and self.settings.telegram_chat_id:
                ch.chat_id = self.settings.telegram_chat_id

    @property
    def configured(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    def render_signal(
        self,
        signal: SignalResult,
        indicator_labels: list[str] | None = None,
    ) -> tuple[str, str | None]:
        """Trả (text, channel_id)."""
        ch = resolve_channel(
            self.notify_cfg,
            timeframe=signal.timeframe,
            strategy_id=signal.strategy_id,
        )
        channel_name = ch.display_name if ch else "main"
        text = format_signal_message(
            channel_name=channel_name,
            timeframe=signal.timeframe,
            strategy_display_name=signal.display_name,
            symbol=signal.symbol,
            direction=signal.direction,
            score=signal.score,
            rating=signal.rating,
            rating_label=self.notify_cfg.rating_label,
            indicator_labels=indicator_labels,
            reason=signal.reason,
            include_rating_bar=self.notify_cfg.include_rating_bar,
        )
        return text, (ch.id if ch else None)

    def send_text(self, text: str, *, channel_id: str | None = None, dry_run: bool = False) -> bool:
        if not self.notify_cfg.enabled:
            log.info("Notifier disabled trong notify.yaml")
            return False

        ch = None
        if channel_id:
            ch = self.notify_cfg.channels.get(channel_id)
        if ch is None:
            ch = resolve_channel(self.notify_cfg)

        chat_id = (ch.chat_id if ch else "") or self.settings.telegram_chat_id
        token = self.settings.telegram_bot_token

        if dry_run or not token or not chat_id:
            log.info("Telegram dry-run (thiếu token/chat hoặc dry_run=True):\n%s", text)
            return False

        try:
            result = self._send_fn(token, chat_id, text)
            ok = bool(result.get("ok"))
            log.info("Telegram gửi %s (channel=%s)", "OK" if ok else "FAIL", ch.id if ch else "?")
            return ok
        except urllib.error.URLError as exc:
            log.error("Telegram lỗi mạng: %s", exc)
            return False

    def send_signal(
        self,
        signal: SignalResult,
        indicator_labels: list[str] | None = None,
        *,
        dry_run: bool | None = None,
    ) -> bool:
        if not signal.fired:
            log.debug("Bỏ qua notify — signal chưa fired")
            return False
        text, channel_id = self.render_signal(signal, indicator_labels)
        if dry_run is None:
            dry_run = not self.configured
        return self.send_text(text, channel_id=channel_id, dry_run=dry_run)

    def send_test(self, dry_run: bool | None = None) -> bool:
        ch = resolve_channel(self.notify_cfg)
        name = ch.display_name if ch else "main"
        text = format_test_message(name)
        if dry_run is None:
            dry_run = not self.configured
        return self.send_text(text, channel_id=ch.id if ch else None, dry_run=dry_run)


# Tương thích Phase 1
TelegramNotifierSkeleton = TelegramNotifier
