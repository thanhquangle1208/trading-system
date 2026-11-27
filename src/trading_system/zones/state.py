"""Nhớ đã báo gì. Không lưu ghi chú, link, hay token."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from trading_system.zones.logic import ZoneMemory

LOCAL_RUNNER = "local"
GITHUB_RUNNER = "github"
DEFAULT_LEASE_MAX_AGE_SEC = 20 * 60


class StateError(Exception):
    pass


@dataclass
class AlertState:
    zones: dict[str, ZoneMemory] = field(default_factory=dict)
    last_digest_date: str | None = None
    coingecko_ids: dict[str, str] = field(default_factory=dict)
    lease_holder: str | None = None
    heartbeat_utc: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "version": 1,
            "zones": {pid: mem.to_json() for pid, mem in sorted(self.zones.items())},
            "last_digest_date": self.last_digest_date,
            "coingecko_ids": {k: self.coingecko_ids[k] for k in sorted(self.coingecko_ids)},
            "lease": {
                "holder": self.lease_holder,
                "heartbeat_utc": self.heartbeat_utc,
            },
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
    holder, heartbeat = _read_lease(raw.get("lease"))
    return AlertState(
        zones=zones,
        last_digest_date=str(last) if last else None,
        coingecko_ids=ids,
        lease_holder=holder,
        heartbeat_utc=heartbeat,
    )


def claim_lease(state: AlertState, holder: str, now: datetime) -> None:
    """Ghi 'máy này còn sống' vào sổ chung. Không đụng vùng giá."""
    moment = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    state.lease_holder = holder
    state.heartbeat_utc = moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lease_blocks_github(
    state: AlertState,
    now: datetime,
    max_age_sec: int = DEFAULT_LEASE_MAX_AGE_SEC,
) -> bool:
    """True khi Mac vừa chạy, GitHub phải nhường."""
    if state.lease_holder != LOCAL_RUNNER:
        return False
    beat = _parse_utc(state.heartbeat_utc)
    if beat is None:
        return False
    moment = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    age = (moment.astimezone(timezone.utc) - beat).total_seconds()
    if age < 0:
        return True
    return age <= max_age_sec


def should_skip_push(
    local_payload: dict,
    remote_payload: dict,
    now: datetime,
    max_age_sec: int = DEFAULT_LEASE_MAX_AGE_SEC,
) -> bool:
    """GitHub không được ghi đè sổ khi Mac vừa giữ nhịp."""
    if not isinstance(local_payload, dict) or not isinstance(remote_payload, dict):
        return False
    if _read_lease(local_payload.get("lease"))[0] != GITHUB_RUNNER:
        return False
    holder, heartbeat = _read_lease(remote_payload.get("lease"))
    remote = AlertState(lease_holder=holder, heartbeat_utc=heartbeat)
    return lease_blocks_github(remote, now, max_age_sec)


def _read_lease(raw: object) -> tuple[str | None, str | None]:
    if not isinstance(raw, dict):
        return None, None
    holder = raw.get("holder")
    beat = raw.get("heartbeat_utc")
    holder_s = str(holder) if holder else None
    beat_s = str(beat) if beat else None
    return holder_s, beat_s


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def save_state(path: Path, state: AlertState) -> None:
    payload = state.to_json()
    assert_safe_state(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
