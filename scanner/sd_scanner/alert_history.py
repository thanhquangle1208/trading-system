"""Lưu các tin cảnh báo đã gửi — phục vụ lệnh /top (24h)."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class AlertRecord:
    ts: float
    symbol: str
    timeframe: str
    side: str
    price: float
    zone_bot: float
    zone_top: float
    stl: float
    tp: float | None
    rr: float | None
    depth: float
    confidence: float
    w1_bias: str | None = None
    message_id: int | None = None
    chat_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AlertRecord:
        return cls(
            ts=float(d["ts"]),
            symbol=str(d["symbol"]),
            timeframe=str(d["timeframe"]),
            side=str(d["side"]),
            price=float(d["price"]),
            zone_bot=float(d["zone_bot"]),
            zone_top=float(d["zone_top"]),
            stl=float(d["stl"]),
            tp=float(d["tp"]) if d.get("tp") is not None else None,
            rr=float(d["rr"]) if d.get("rr") is not None else None,
            depth=float(d["depth"]),
            confidence=float(d["confidence"]),
            w1_bias=d.get("w1_bias"),
            message_id=int(d["message_id"]) if d.get("message_id") is not None else None,
            chat_id=str(d["chat_id"]) if d.get("chat_id") is not None else None,
        )


class AlertHistory:
    """JSONL append-only; đọc lọc theo thời gian; tự bỏ bản quá hạn khi ghi."""

    def __init__(self, path: Path, *, keep_sec: float = 48 * 3600) -> None:
        self.path = path
        self.keep_sec = keep_sec

    def append(self, rec: AlertRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        # Thỉnh thoảng dọn (mỗi lần ghi cũng OK với file nhỏ)
        if self.path.stat().st_size > 200_000:
            self.prune()

    def load_since(self, since_ts: float) -> list[AlertRecord]:
        if not self.path.is_file():
            return []
        out: list[AlertRecord] = []
        try:
            text = self.path.read_text(encoding="utf-8")
        except Exception:
            return []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                rec = AlertRecord.from_dict(d)
                if rec.ts >= since_ts:
                    out.append(rec)
            except Exception:
                continue
        return out

    def prune(self) -> None:
        cutoff = time.time() - self.keep_sec
        kept = self.load_since(cutoff)
        tmp = self.path.with_suffix(".tmp")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tmp.open("w", encoding="utf-8") as f:
            for rec in kept:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        tmp.replace(self.path)


def telegram_message_link(chat_id: str | None, message_id: int | None) -> str | None:
    """
    Link tới tin gốc khi có thể (group/supergroup/channel).
    Chat riêng với bot thường không mở được deep-link — trả None.
    """
    if not chat_id or message_id is None:
        return None
    try:
        cid = int(str(chat_id))
    except ValueError:
        return None
    # Private user chat (positive id) — Telegram không có link tin ổn định
    if cid > 0:
        return None
    # Supergroup/channel: -100xxxxxxxxxx → t.me/c/xxxxxxxxxx/msg
    s = str(abs(cid))
    if s.startswith("100"):
        s = s[3:]
    return f"https://t.me/c/{s}/{message_id}"
