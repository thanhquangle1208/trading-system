"""Gửi / nhận lệnh Telegram (Bot API thuần — không LLM)."""

from __future__ import annotations

import html
from typing import Any

import requests


class Telegram:
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = str(chat_id)
        self.base = f"https://api.telegram.org/bot{token}"
        self._offset: int | None = None

    def send(self, text: str, *, use_html: bool = False) -> None:
        payload: dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if use_html:
            payload["parse_mode"] = "HTML"
        r = requests.post(f"{self.base}/sendMessage", json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram lỗi: {data}")

    def send_alert(
        self,
        *,
        symbol: str,
        timeframe: str,
        side: str,
        price: float,
        zone_bot: float,
        zone_top: float,
        stl: float,
        tp: float | None,
        rr: float | None,
        depth: float,
        confidence: float,
    ) -> None:
        display = symbol if symbol.endswith("USDT") else symbol
        if side == "buy":
            action_emoji = "🟢"
            action_word = "MUA"
        else:
            action_emoji = "🔴"
            action_word = "BÁN"

        def e(s: str) -> str:
            return html.escape(s, quote=False)

        pair = e(f"{display}.P")
        tf_e = e(timeframe)
        price_s = e(self._fmt(price))
        zone_s = e(f"{self._fmt(zone_bot)} – {self._fmt(zone_top)}")
        stl_s = e(self._fmt(stl))
        tp_s = e(self._fmt(tp)) if tp is not None else "—"
        rr_s = e(f"1 : {rr:g}") if rr is not None else "—"
        depth_s = e(f"{depth:.1f}/10")
        conf_s = e(f"{confidence:.1f}/10")

        text = "\n".join(
            [
                "🏷️ <b>Phương Pháp Supply &amp; Demand</b>",
                "",
                "📊 <b>PHÂN TÍCH TÍN HIỆU</b>",
                "━━━━━━━━━━━━━━━━",
                f"{action_emoji} <b>{action_word} {pair}</b>",
                f"⏱ <b>Khung:</b> {tf_e}",
                f"📍 <b>Giá / Entry:</b> {price_s}",
                f"📦 <b>Vùng giá:</b> {zone_s}",
                f"🛑 <b>STL:</b> {stl_s}",
                f"✅ <b>TP:</b> {tp_s}",
                f"📐 <b>R:R:</b> {rr_s}",
                "",
                f"⭐ <b>Độ hấp dẫn (độ sâu):</b> {depth_s}",
                f"📈 <b>Độ tin cậy:</b> {conf_s}",
            ]
        )
        self.send(text, use_html=True)

    @staticmethod
    def _fmt(x: float) -> str:
        if x >= 1000:
            return f"{x:,.2f}".replace(",", "")
        if x >= 1:
            return f"{x:.4g}"
        return f"{x:.6g}"

    def poll_messages(self, timeout_sec: int = 0) -> list[str]:
        """Mọi tin nhắn text từ đúng chat_id (không chỉ lệnh /)."""
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
        texts: list[str] = []
        for upd in data.get("result") or []:
            self._offset = int(upd["update_id"]) + 1
            msg = upd.get("message") or upd.get("edited_message") or {}
            chat = msg.get("chat") or {}
            if str(chat.get("id")) != self.chat_id:
                continue
            text = (msg.get("text") or "").strip()
            if text:
                texts.append(text)
        return texts
