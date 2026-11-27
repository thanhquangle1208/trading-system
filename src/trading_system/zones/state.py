"""Nhớ đã báo gì. Không lưu ghi chú, link, hay token."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from trading_system.zones.logic import ZoneMemory


class StateError(Exception):
    pass


@dataclass
class AlertState:
    zones: dict[str, ZoneMemory] = field(default_factory=dict)
    last_digest_date: str | None = None
    coingecko_ids: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> dict[str, object]:
        return {
            "version": 1,
            "zones": {pid: mem.to_json() for pid, mem in sorted(self.zones.items())},
            "last_digest_date": self.last_digest_date,
            "coingecko_ids": {k: self.coingecko_ids[k] for k in sorted(self.coingecko_ids)},
        }


def assert_safe_state(payload: dict) -> None:
    """Chặn nhầm token hoặc nội dung phân tích vào file trạng thái."""
    blob = json.dumps(payload, ensure_ascii=False)
    lowered = blob.lower()
    for marker in ("bearer ", "telegram_bot", "notion_token", "xoxb-", "secret_"):
        if marker in lowered:
            raise StateError("File trạng thái có vẻ chứa bí mật — không ghi.")
    for pid, mem in (payload.get("zones") or {}).items():
        if not isinstance(mem, dict):
            continue
        for key in mem:
            if key not in {"inside", "approach_armed", "invalidation_level_key"}:
                raise StateError(f"Khóa lạ trong trạng thái vùng {pid}: {key}")


def load_state(path: Path) -> AlertState:
    if not path.exists():
        return AlertState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(f"File trạng thái hỏng ({path}). Không chạy tiếp để tránh báo trùng.") from exc
    if not isinstance(raw, dict):
        raise StateError(f"File trạng thái không đúng dạng ({path}).")
    zones_raw = raw.get("zones") or {}
    zones = {
        str(pid): ZoneMemory.from_json(mem)
        for pid, mem in zones_raw.items()
        if isinstance(zones_raw, dict)
    }
    ids_raw = raw.get("coingecko_ids") or {}
    ids = {str(k).upper(): str(v) for k, v in ids_raw.items()} if isinstance(ids_raw, dict) else {}
    last = raw.get("last_digest_date")
    return AlertState(
        zones=zones,
        last_digest_date=str(last) if last else None,
        coingecko_ids=ids,
    )


def save_state(path: Path, state: AlertState) -> None:
    payload = state.to_json()
    assert_safe_state(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
