"""Gửi / nhận lệnh Telegram (Bot API thuần — không LLM)."""

from __future__ import annotations

from typing import Any

import requests

from .scoring import side_label


class Telegram:
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = str(chat_id)
        self.base = f"https://api.telegram.org/bot{token}"
        self._offset: int | None = None

    def send(self, text: str) -> None:
        r = requests.post(
            f"{self.base}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram lỗi: {data}")

    def send_alert(
        self,
        *,
        symbol: str,
        venue: str,
        timeframe: str,
        side: str,
        price: float,
        zone_bot: float,
        zone_top: float,
        depth: float,
        confidence: float,
        note: str = "",
    ) -> None:
        display = symbol if symbol.endswith("USDT") else symbol
        lines = [
            "🔔 Cảnh báo vùng giá",
            "",
            f"Cặp: {display}.P ({venue})",
            f"Khung: {timeframe}",
            f"Loại: {side_label(side)}",
            f"Giá hiện tại: {self._fmt(price)}",
            f"Vùng giá: {self._fmt(zone_bot)} – {self._fmt(zone_top)}",
            "",
            f"Độ hấp dẫn (độ sâu): {depth:.1f}/10",
            f"Độ tin cậy: {confidence:.1f}/10",
        ]
        if note:
            lines += ["", f"Ghi chú: {note}"]
        self.send("\n".join(lines))

    @staticmethod
    def _fmt(x: float) -> str:
        if x >= 1000:
            return f"{x:,.2f}".replace(",", "")
        if x >= 1:
            return f"{x:.4g}"
        return f"{x:.6g}"

    def poll_commands(self, timeout_sec: int = 0) -> list[str]:
        """Trả list lệnh text từ đúng chat_id (lowercase): /scan /stop /status /help."""
        params: dict[str, Any] = {"timeout": timeout_sec}
        if self._offset is not None:
            params["offset"] = self._offset
        try:
            r = requests.get(f"{self.base}/getUpdates", params=params, timeout=timeout_sec + 10)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []
        if not data.get("ok"):
            return []
        cmds: list[str] = []
        for upd in data.get("result") or []:
            self._offset = int(upd["update_id"]) + 1
            msg = upd.get("message") or upd.get("edited_message") or {}
            chat = msg.get("chat") or {}
            if str(chat.get("id")) != self.chat_id:
                continue
            text = (msg.get("text") or "").strip()
            if not text.startswith("/"):
                continue
            cmd = text.split()[0].split("@")[0].lower()
            cmds.append(cmd)
        return cmds
