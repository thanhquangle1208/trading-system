"""Đọc database Notion (chỉ đọc). API data source mới, rồi fallback databases/query."""

from __future__ import annotations

import re
from typing import Any

from trading_system.data.http_client import HttpStatusError
from trading_system.logging_setup import get_logger
from trading_system.zones.models import BuyZone
from trading_system.zones.reference import _clean_ticker

log = get_logger("zones.notion")

DATA_SOURCE_VERSION = "2025-09-03"
DATABASE_VERSION = "2022-06-28"

PROP_TOKEN = "Token"
PROP_TICKER = "Ticker"
PROP_ZONE = "Vùng"
PROP_LOWER = "Giá dưới"
PROP_UPPER = "Giá trên"
PROP_INVALID = "Vô hiệu nếu nến ngày đóng dưới"
PROP_STATUS = "Trạng thái"
PROP_REF = "Chuỗi/sàn tham chiếu"
PROP_NOTE = "Điều kiện/ghi chú"
PROP_ANALYSIS_PRICE = "Giá lúc phân tích"
PROP_ANALYSIS_DATE = "Ngày phân tích"
PROP_LINK = "Link phân tích Notion"

# Fallback chỉ khi endpoint data source chưa có (bản API cũ) hoặc id sai.
_FALLBACK_STATUSES = {400, 404}


def notion_headers(token: str, version: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json",
    }


def query_pages(http: Any, *, token: str, database_id: str, data_source_id: str) -> list[dict]:
    """Mọi dòng (kể cả không còn theo dõi). Lọc trạng thái ở tầng sau."""
    if data_source_id:
        url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
        try:
            pages = _paginate(
                http,
                url,
                notion_headers(token, DATA_SOURCE_VERSION),
            )
            log.info("Notion data_sources: %d dòng", len(pages))
            return pages
        except HttpStatusError as exc:
            if exc.status not in _FALLBACK_STATUSES:
                raise
            log.warning(
                "Notion data_sources trả %s — thử databases/query (API 2022-06-28).",
                exc.status,
            )
    if not database_id:
        raise HttpStatusError(0, "notion", "Thiếu NOTION_DATABASE_ID")
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    pages = _paginate(http, url, notion_headers(token, DATABASE_VERSION))
    log.info("Notion databases/query: %d dòng", len(pages))
    return pages


def parse_pages(pages: list[dict]) -> list[BuyZone]:
    zones: list[BuyZone] = []
    for page in pages:
        if page.get("object") not in (None, "page"):
            continue
        zone = parse_page(page)
        if zone is not None:
            zones.append(zone)
    return zones


def parse_page(page: dict) -> BuyZone | None:
    props = page.get("properties")
    if not isinstance(props, dict):
        return None
    page_id = str(page.get("id") or "")
    if not page_id:
        return None
    lower = _number(props.get(PROP_LOWER))
    upper = _number(props.get(PROP_UPPER))
    swapped = False
    if lower is not None and upper is not None and lower > upper:
        lower, upper = upper, lower
        swapped = True
    zone = BuyZone(
        page_id=page_id,
        token_name=_text(props.get(PROP_TOKEN)),
        ticker=_clean_ticker(_text(props.get(PROP_TICKER))),
        zone_no=_zone_no(_text(props.get(PROP_ZONE))),
        lower=lower,
        upper=upper,
        invalidation=_number(props.get(PROP_INVALID)),
        status=_text(props.get(PROP_STATUS)),
        reference=_text(props.get(PROP_REF)),
        note=_text(props.get(PROP_NOTE)),
        link=_url(props.get(PROP_LINK)),
        analysis_price=_number(props.get(PROP_ANALYSIS_PRICE)),
        analysis_date=_date(props.get(PROP_ANALYSIS_DATE)),
    )
    if swapped:
        log.info("Đảo Giá dưới/Giá trên cho %s Vùng %s", zone.ticker, zone.zone_no)
    return zone


def _paginate(http: Any, url: str, headers: dict[str, str]) -> list[dict]:
    pages: list[dict] = []
    cursor: str | None = None
    for _ in range(50):
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = http.request_json("POST", url, headers=headers, body=body)
        if not isinstance(data, dict):
            raise HttpStatusError(0, url, "Notion không trả object")
        pages.extend(data.get("results") or [])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return pages


def _text(prop: object) -> str:
    if not isinstance(prop, dict):
        return ""
    kind = prop.get("type")
    if kind in ("title", "rich_text", "text"):
        chunks = prop.get(kind) or []
        return "".join(str(c.get("plain_text") or "") for c in chunks if isinstance(c, dict))
    if kind == "select":
        selected = prop.get("select") or {}
        return str(selected.get("name") or "") if isinstance(selected, dict) else ""
    if kind == "status":
        selected = prop.get("status") or {}
        return str(selected.get("name") or "") if isinstance(selected, dict) else ""
    if kind == "formula":
        formula = prop.get("formula") or {}
        if isinstance(formula, dict) and formula.get("type") == "string":
            return str(formula.get("string") or "")
    if kind == "url":
        return str(prop.get("url") or "")
    if kind == "number" and prop.get("number") is not None:
        return str(prop.get("number"))
    return ""


def _number(prop: object) -> float | None:
    if not isinstance(prop, dict):
        return None
    kind = prop.get("type")
    if kind == "number":
        value = prop.get("number")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return float(value)
    if kind == "formula":
        formula = prop.get("formula") or {}
        if isinstance(formula, dict) and formula.get("type") == "number":
            value = formula.get("number")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
        if isinstance(formula, dict) and formula.get("type") == "string":
            return _parse_number_text(str(formula.get("string") or ""))
    return _parse_number_text(_text(prop))


def _parse_number_text(text: str) -> float | None:
    raw = text.strip().replace(" ", "").replace("\u00a0", "")
    if not raw:
        return None
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        left, right = raw.split(",", 1)
        if right.isdigit() and len(right) <= 2:
            raw = left.replace(".", "") + "." + right
        else:
            raw = raw.replace(",", "")
    elif raw.count(".") > 1:
        raw = raw.replace(".", "")
    elif "." in raw:
        left, right = raw.split(".", 1)
        if left.isdigit() and right.isdigit() and len(right) == 3:
            raw = left + right
    try:
        return float(raw)
    except ValueError:
        return None


def _url(prop: object) -> str:
    if not isinstance(prop, dict):
        return ""
    if prop.get("type") == "url" and prop.get("url"):
        return str(prop["url"])
    text = _text(prop).strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return ""


def _date(prop: object) -> str | None:
    if not isinstance(prop, dict) or prop.get("type") != "date":
        return None
    date = prop.get("date") or {}
    if isinstance(date, dict) and date.get("start"):
        return str(date["start"])
    return None


def _zone_no(raw: str) -> str:
    text = raw.strip()
    text = re.sub(r"(?i)^vùng\s*", "", text).strip()
    return text or "?"
