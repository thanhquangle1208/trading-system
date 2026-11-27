"""Đọc Notion: data source mới, fallback database cũ, dòng thiếu trường."""

from __future__ import annotations

from trading_system.data.http_client import HttpStatusError
from trading_system.zones.notion_source import (
    DATA_SOURCE_VERSION,
    DATABASE_VERSION,
    parse_page,
    query_pages,
)
from tests.fakes import FakeHttp


def _title(text: str) -> dict:
    return {"type": "title", "title": [{"plain_text": text}]}


def _rich(text: str) -> dict:
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def _select(name: str | None) -> dict:
    return {"type": "select", "select": None if name is None else {"name": name}}


def _number(value) -> dict:
    return {"type": "number", "number": value}


def _page(pid: str, **props) -> dict:
    return {"object": "page", "id": pid, "properties": props}


def _btc(pid: str = "p1", **overrides) -> dict:
    props = {
        "Token": _title("Bitcoin"),
        "Ticker": _rich("btc"),
        "Vùng": _select("1"),
        "Giá dưới": _number(55000),
        "Giá trên": _number(61000),
        "Vô hiệu nếu nến ngày đóng dưới": _number(53000),
        "Trạng thái": _select("Đang theo dõi"),
        "Chuỗi/sàn tham chiếu": _rich("Spot / Binance BTCUSDT"),
        "Điều kiện/ghi chú": _rich("Vesting team 24 tháng. Tokenomics FDV cao."),
        "Link phân tích Notion": {"type": "url", "url": "https://www.notion.so/abc"},
        "Giá lúc phân tích": _number(60000),
        "Ngày phân tích": {"type": "date", "date": {"start": "2026-01-02"}},
        "Vốn hóa (USD)": _number(1_000_000_000),
        "Thứ hạng vốn hóa": _number(1),
        "Nhóm điểm": _rich("lõi"),
    }
    props.update(overrides)
    return _page(pid, **props)


def test_parse_active_row_and_missing_invalidation() -> None:
    zone = parse_page(_btc())
    assert zone is not None
    assert zone.ticker == "BTC"
    assert zone.zone_no == "1"
    assert zone.lower == 55000
    assert zone.invalidation == 53000
    assert zone.active
    assert zone.link.startswith("https://")
    assert zone.analysis_date == "2026-01-02"

    missing = parse_page(_btc(pid="p2", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)}))
    assert missing is not None
    assert missing.invalidation is None
    assert missing.skip_reason() is None


def test_parse_inactive_missing_bounds_and_swapped_text_prices() -> None:
    expired = parse_page(_btc(**{"Trạng thái": _select("Hết hiệu lực")}))
    stale = parse_page(_btc(pid="p3", **{"Trạng thái": _select("Cũ cần cập nhật")}))
    assert expired is not None and expired.skip_reason()
    assert stale is not None and stale.skip_reason()

    missing_low = parse_page(_btc(**{"Giá dưới": _number(None)}))
    assert missing_low is not None
    assert missing_low.skip_reason()

    swapped = parse_page(
        _btc(
            **{
                "Giá dưới": {"type": "rich_text", "rich_text": [{"plain_text": "61.000"}]},
                "Giá trên": {"type": "rich_text", "rich_text": [{"plain_text": "55.000"}]},
                "Vùng": _select("Vùng 2"),
            }
        )
    )
    assert swapped is not None
    assert swapped.bounds() == (55000, 61000)
    assert swapped.zone_no == "2"


def test_query_uses_data_source_then_falls_back() -> None:
    pages = {"results": [_btc()], "has_more": False, "next_cursor": None}
    ok = FakeHttp([("POST", "/v1/data_sources/", pages)])
    got = query_pages(ok, token="tok", database_id="db", data_source_id="ds")
    assert len(got) == 1
    assert ok.calls[0]["headers"]["Notion-Version"] == DATA_SOURCE_VERSION
    assert ok.calls[0]["headers"]["Authorization"] == "Bearer tok"
    assert "/v1/data_sources/ds/query" in ok.calls[0]["url"]

    fallback = FakeHttp(
        [
            ("POST", "/v1/data_sources/", HttpStatusError(404, "ds", "missing")),
            ("POST", "/v1/databases/", pages),
        ]
    )
    got = query_pages(fallback, token="tok", database_id="db", data_source_id="ds")
    assert len(got) == 1
    assert fallback.calls[1]["headers"]["Notion-Version"] == DATABASE_VERSION
    assert "/v1/databases/db/query" in fallback.calls[1]["url"]


def test_query_paginates() -> None:
    seen: list[dict] = []

    def respond(_method, _url, body):
        seen.append(body or {})
        if not body or not body.get("start_cursor"):
            return {"results": [_btc("a")], "has_more": True, "next_cursor": "cursor-2"}
        return {"results": [_btc("b")], "has_more": False, "next_cursor": None}

    http = FakeHttp([("POST", "/v1/data_sources/", respond)])
    pages = query_pages(http, token="tok", database_id="db", data_source_id="ds")
    assert [p["id"] for p in pages] == ["a", "b"]
    assert seen[1]["start_cursor"] == "cursor-2"


def test_auth_error_is_not_swallowed() -> None:
    http = FakeHttp(
        [("POST", "/v1/data_sources/", HttpStatusError(401, "ds", "unauthorized"))]
    )
    try:
        query_pages(http, token="tok", database_id="db", data_source_id="ds")
        raised = False
    except HttpStatusError as exc:
        raised = exc.status == 401
    assert raised
    assert len(http.calls) == 1
