"""Lấy TELEGRAM_CHAT_ID bằng getUpdates.

Cách dùng (máy bạn):

1. BotFather → /newbot → copy token vào .env (TELEGRAM_BOT_TOKEN).
2. Mở Telegram, nhắn một tin bất kỳ (ví dụ /start) cho bot vừa tạo.
3. Chạy: python -m trading_system.notify.chat_id
4. Copy số chat id in ra vào TELEGRAM_CHAT_ID.

Nếu không thấy tin: nhắn lại cho bot rồi chạy lại. Nếu bot đang gắn
webhook thì getUpdates trống — đây là bot cảnh báo mới, không cần webhook.
"""

from __future__ import annotations

import json
import urllib.request

from trading_system.logging_setup import get_logger
from trading_system.settings import get_settings

log = get_logger("notify.chat_id")


def extract_chats(payload: dict) -> list[tuple[str, str]]:
    """Trả danh sách (chat_id, tên) duy nhất từ kết quả getUpdates."""
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for upd in payload.get("result") or []:
        msg = (
            upd.get("message")
            or upd.get("edited_message")
            or upd.get("channel_post")
            or {}
        )
        chat = msg.get("chat") or {}
        cid = chat.get("id")
        if cid is None:
            continue
        cid_s = str(cid)
        if cid_s in seen:
            continue
        seen.add(cid_s)
        title = (
            chat.get("title")
            or chat.get("username")
            or chat.get("first_name")
            or ""
        )
        found.append((cid_s, str(title)))
    return found


def fetch_updates(token: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    settings = get_settings()
    token = settings.telegram_bot_token.strip()
    if not token:
        print(
            "Thiếu TELEGRAM_BOT_TOKEN.\n"
            "Tạo bot với @BotFather, copy token vào file .env, rồi chạy lại."
        )
        return 1
    try:
        payload = fetch_updates(token)
    except Exception as exc:
        safe = str(exc).replace(token, "***")
        print(f"Không gọi được Telegram: {safe}")
        return 1
    if not payload.get("ok", True):
        print(f"Telegram trả lỗi: {payload}")
        return 1
    chats = extract_chats(payload)
    if not chats:
        print(
            "Chưa thấy tin nhắn nào.\n"
            "Mở Telegram, tìm bot, nhắn /start (hoặc bất kỳ chữ gì), rồi chạy lại lệnh này.\n"
            "Chat riêng: id là số dương. Nhóm: id thường là số âm — copy nguyên cả dấu trừ."
        )
        return 1
    print("Chat id tìm được (dán vào TELEGRAM_CHAT_ID):\n")
    for cid, title in chats:
        label = f" — {title}" if title else ""
        print(f"  {cid}{label}")
    print(
        "\nNếu có nhiều dòng, chọn đúng cuộc trò chuyện bạn vừa nhắn.\n"
        "Nhóm: thêm bot vào nhóm, nhắn một tin trong nhóm, chạy lại."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
