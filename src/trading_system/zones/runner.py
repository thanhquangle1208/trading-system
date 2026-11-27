"""Một lần chạy: đọc Notion, lấy giá, quyết định, gửi Telegram, ghi trạng thái."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from trading_system.data.public_prices import fetch_quotes
from trading_system.logging_setup import get_logger
from trading_system.settings import Settings
from trading_system.zones.config import BuyZoneConfig
from trading_system.zones.logic import (
    AlertKind,
    ZoneAlert,
    ZoneMemory,
    decide_zone,
    digest_due,
)
from trading_system.zones.messages import (
    format_approaching,
    format_digest,
    format_entry,
    format_invalidation,
)
from trading_system.zones.models import BuyZone
from trading_system.zones.notion_source import parse_pages, query_pages
from trading_system.zones.reference import parse_reference
from trading_system.zones.state import AlertState, StateError, load_state, save_state

log = get_logger("zones.runner")


class Notifier(Protocol):
    def send_text(
        self,
        text: str,
        *,
        channel_id: str | None = None,
        dry_run: bool = False,
    ) -> bool: ...


@dataclass
class RunReport:
    ok: bool
    messages: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def run_once(
    *,
    settings: Settings,
    config: BuyZoneConfig,
    http: Any,
    notifier: Notifier,
    now: datetime,
    dry_run: bool = False,
    save: bool = True,
    state_path: Path | None = None,
) -> RunReport:
    path = state_path or _resolve_state_path(config.state_path)
    if not settings.notion_token.strip():
        log.error("Thiếu NOTION_TOKEN. Xem README mục cảnh báo vùng giá gom.")
        return RunReport(ok=False)
    if not dry_run and not _notifier_ready(notifier):
        log.error("Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
        return RunReport(ok=False)

    try:
        state = load_state(path)
    except StateError as exc:
        log.error("%s", exc)
        return RunReport(ok=False)

    try:
        pages = query_pages(
            http,
            token=settings.notion_token.strip(),
            database_id=settings.notion_database_id.strip(),
            data_source_id=settings.notion_data_source_id.strip(),
        )
    except Exception as exc:
        log.error("Không đọc được Notion: %s", exc)
        return RunReport(ok=False)

    zones = parse_pages(pages)
    skipped: list[str] = []
    actionable: list[BuyZone] = []
    for zone in zones:
        reason = zone.skip_reason()
        if reason:
            skipped.append(f"{zone.ticker or zone.token_name or zone.page_id}: {reason}")
            log.info("Bỏ qua %s — %s", zone.ticker or zone.page_id, reason)
            continue
        actionable.append(zone)

    targets = [parse_reference(zone.reference, zone.ticker) for zone in actionable]
    need_daily = {
        target
        for zone, target in zip(actionable, targets, strict=True)
        if zone.invalidation is not None
    }
    fetched = fetch_quotes(
        http,
        targets,
        now,
        need_daily=need_daily,
        coingecko_key=settings.coingecko_api_key,
        id_cache=dict(state.coingecko_ids),
    )
    if fetched.outage:
        log.error("Không gọi được nguồn giá nào. Bỏ qua kỳ này, không gửi bản tin.")
        return RunReport(ok=False, skipped=skipped + fetched.unpriced)

    messages: list[str] = []
    failed = False
    new_zones: dict[str, ZoneMemory] = {}
    digest_rows: list[tuple[BuyZone, float, bool]] = []
    unpriced_names: list[str] = []

    for zone, target in zip(actionable, targets, strict=True):
        quote = fetched.quotes.get(target)
        if quote is None:
            unpriced_names.append(zone.ticker)
            log.warning(
                "Không lấy được giá %s (tham chiếu: %s) — bỏ qua, không dừng bot.",
                zone.ticker,
                zone.reference or "mặc định USDT",
            )
            if zone.page_id in state.zones:
                new_zones[zone.page_id] = state.zones[zone.page_id]
            continue

        prev = state.zones.get(zone.page_id, ZoneMemory())
        decision = decide_zone(
            zone,
            prev,
            quote.price,
            quote.daily_close,
            hysteresis=config.hysteresis,
            approaching=config.approaching,
        )
        texts = [_render(alert, config) for alert in decision.alerts]
        if _deliver(texts, notifier, dry_run, messages):
            new_zones[zone.page_id] = decision.memory
        else:
            failed = True
            new_zones[zone.page_id] = prev
            continue

        lo, hi = zone.bounds()
        if lo <= quote.price <= hi:
            invalidated = decision.memory.invalidation_level_key is not None
            digest_rows.append((zone, quote.price, invalidated))

    active_ids = {zone.page_id for zone in actionable}
    new_zones = {pid: mem for pid, mem in new_zones.items() if pid in active_ids}

    new_digest = state.last_digest_date
    if config.digest_enabled:
        due = digest_due(
            now,
            state.last_digest_date,
            hour=config.digest_hour_vn,
            minute=config.digest_minute_vn,
            tz_name=config.timezone,
        )
        if due and not fetched.outage:
            digest_rows.sort(key=_digest_sort)
            text = format_digest(
                digest_rows,
                _unique(unpriced_names),
                hour=config.digest_hour_vn,
                minute=config.digest_minute_vn,
                watching=len(actionable),
            )
            if _deliver([text], notifier, dry_run, messages):
                new_digest = due
            else:
                failed = True

    log.info(
        "Notion %d dòng, đang xét %d, tin %d, bỏ qua %d, không có giá %d",
        len(zones),
        len(actionable),
        len(messages),
        len(skipped),
        len(_unique(unpriced_names)),
    )
    if save:
        updated = AlertState(
            zones=new_zones,
            last_digest_date=new_digest,
            coingecko_ids=fetched.id_cache,
        )
        save_state(path, updated)
    return RunReport(ok=not failed, messages=messages, skipped=skipped + _unique(unpriced_names))


def _deliver(texts: list[str], notifier: Notifier, dry_run: bool, messages: list[str]) -> bool:
    for text in texts:
        if dry_run:
            print(text)
            messages.append(text)
            continue
        if not notifier.send_text(text):
            log.error("Gửi Telegram thất bại — sẽ thử lại lần chạy sau.")
            return False
        messages.append(text)
    return True


def _render(alert: ZoneAlert, config: BuyZoneConfig) -> str:
    if alert.kind is AlertKind.ENTRY:
        return format_entry(alert.zone, alert.price)
    if alert.kind is AlertKind.APPROACHING:
        pct = config.approaching_pct or 0
        return format_approaching(alert.zone, alert.price, pct)
    if alert.kind is AlertKind.INVALIDATION:
        assert alert.daily_close is not None
        return format_invalidation(alert.zone, alert.daily_close)
    raise RuntimeError(f"Không rõ loại tin {alert.kind}")


def _digest_sort(row: tuple[BuyZone, float, bool]) -> tuple[str, int, str]:
    zone = row[0]
    try:
        number = int(zone.zone_no)
    except ValueError:
        number = 999
    return (zone.ticker, number, zone.zone_no)


def _unique(names: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _resolve_state_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        from trading_system.settings import REPO_ROOT

        path = REPO_ROOT / path
    return path


def _notifier_ready(notifier: Notifier) -> bool:
    configured = getattr(notifier, "configured", None)
    if isinstance(configured, bool):
        return configured
    return True


def clock_now() -> datetime:
    return datetime.now(timezone.utc)
