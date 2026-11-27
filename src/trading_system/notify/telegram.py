"""Gửi Telegram thật (khi có token); dry-run thì chỉ in tin.

Cùng kiểu `send_text` với notifier Phase 6 (nhánh phase-6): một hàm gửi
văn bản thuần, không Markdown — giá tiền có dấu chấm không bị nuốt.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

from trading_system.logging_setup import get_logger

log = get_logger("notify.telegram")

SendFn = Callable[[str, str, str], dict[str, Any]]


def _redact(text: str, token: str) -> str:
    if token and token in text:
        return text.replace(token, "***")
    return text


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
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(_redact(f"HTTP {exc.code} {body}", token)) from None
    except urllib.error.URLError as exc:
        raise RuntimeError(_redact(str(exc.reason), token)) from None


class TelegramNotifier:
    def __init__(
        self,
        token: str = "",
        chat_id: str = "",
        send_fn: SendFn | None = None,
    ) -> None:
        self.token = (token or "").strip()
        self.chat_id = str(chat_id or "").strip()
        self._send_fn = send_fn or _http_send

    @property
    def configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_text(
        self,
        text: str,
        *,
        channel_id: str | None = None,
        dry_run: bool = False,
    ) -> bool:
        """Gửi một tin. dry_run hoặc thiếu token → in ra, trả False (không gửi mạng)."""
        del channel_id  # một kênh; giữ tham số cho khớp notifier Phase 6
        if dry_run or not self.configured:
            log.info("Telegram dry-run:\n%s", text)
            print(text)
            return False
        try:
            result = self._send_fn(self.token, self.chat_id, text)
            ok = bool(result.get("ok", True))
            if not ok:
                log.error("Telegram từ chối tin: %s", _redact(str(result), self.token))
            return ok
        except Exception as exc:
            log.error("Telegram lỗi: %s", _redact(str(exc), self.token))
            return False
