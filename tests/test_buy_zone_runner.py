"""Một lần chạy: lọc Notion, không báo trùng, nến ngày, dry-run, file trạng thái."""

from __future__ import annotations

from datetime import datetime, timezone

from trading_system.data.http_client import HttpStatusError
from trading_system.notify.chat_id import extract_chats
from trading_system.notify.telegram import TelegramNotifier
from trading_system.settings import Settings
from trading_system.zones.config import BuyZoneConfig, load_buy_zone_config
from trading_system.zones.runner import run_once
from tests.fakes import FakeHttp
from tests.test_buy_zone_notion import _btc, _number, _select


class Box:
    def __init__(self, ok: bool = True) -> None:
        self.messages: list[str] = []
        self.configured = True
        self.ok = ok

    def send_text(self, text: str, *, channel_id: str | None = None, dry_run: bool = False) -> bool:
        del channel_id, dry_run
        if not self.ok:
            return False
        self.messages.append(text)
        return True


def _settings() -> Settings:
    return Settings(
        telegram_bot_token="tok",
        telegram_chat_id="99",
        notion_token="notion-secret",
        notion_database_id="db",
        notion_data_source_id="ds",
    )


def _config() -> BuyZoneConfig:
    return BuyZoneConfig(
        hysteresis_pct=2,
        approaching_pct=None,
        digest_enabled=True,
        digest_hour_vn=7,
        digest_minute_vn=5,
        state_path=".state/buy_zones.json",
        timezone="Asia/Ho_Chi_Minh",
    )


def _ms(day: int, hour: int = 0) -> int:
    return int(datetime(2026, 11, day, hour, tzinfo=timezone.utc).timestamp() * 1000)


def _http(pages: list[dict], price: str = "60850", klines: list | None = None) -> FakeHttp:
    handlers: list = [
        ("POST", "/v1/data_sources/", {"results": pages, "has_more": False}),
        ("GET", "api.binance.com/api/v3/ticker/price", [{"symbol": "BTCUSDT", "price": price}]),
        (
            "GET",
            "api.bybit.com/v5/market/tickers",
            {"retCode": 0, "result": {"list": []}},
        ),
        ("GET", "okx.com/api/v5/market/tickers", {"code": "0", "data": []}),
        ("GET", "api.coingecko.com/api/v3/search", {"coins": []}),
    ]
    if klines is not None:
        handlers.insert(2, ("GET", "api.binance.com/api/v3/klines", klines))
    return FakeHttp(handlers)


def _run(http, box, path, now, **kwargs):
    return run_once(
        settings=_settings(),
        config=_config(),
        http=http,
        notifier=box,
        now=now,
        dry_run=kwargs.get("dry_run", False),
        save=kwargs.get("save", True),
        state_path=path,
        runner=kwargs.get("runner", "github"),
    )


def test_inactive_rows_skipped_and_entry_deduped_across_restart(tmp_path) -> None:
    pages = [
        _btc("active"),
        _btc("expired", **{"Trạng thái": _select("Hết hiệu lực"), "Ticker": {"type": "rich_text", "rich_text": [{"plain_text": "ETH"}]}}),
        _btc("stale", **{"Trạng thái": _select("Cũ cần cập nhật")}),
        _btc("nolow", **{"Giá dưới": _number(None), "Ticker": {"type": "rich_text", "rich_text": [{"plain_text": "SOL"}]}}),
    ]
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)  # 07:00 VN — trước bản tin 07:05
    path = tmp_path / "state.json"
    box = Box()
    first = _run(_http(pages), box, path, now)
    assert first.ok
    assert len(box.messages) == 1
    assert box.messages[0].startswith("🟢 BTC vào Vùng 1")
    assert "ETH" not in box.messages[0]
    assert "ghi chú" in box.messages[0]

    box2 = Box()
    second = _run(_http(pages, price="60000"), box2, path, now)
    assert second.ok
    assert box2.messages == []

    # Ra khỏi vùng hơn 2% rồi vào lại → báo lần nữa
    box3 = Box()
    _run(_http(pages, price="70000"), box3, path, now)
    assert box3.messages == []
    box4 = Box()
    fourth = _run(_http(pages, price="58000"), box4, path, now)
    assert len(box4.messages) == 1
    assert fourth.messages[0].startswith("🟢 BTC vào Vùng 1")


def test_state_file_has_no_notes_links_or_secrets(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    _run(_http([_btc("active")]), Box(), path, now)
    raw = path.read_text(encoding="utf-8")
    assert "ghi chú" not in raw
    assert "https://" not in raw
    assert "notion-secret" not in raw
    assert "TELEGRAM" not in raw
    assert "inside" in raw


def test_failed_send_does_not_stick_so_next_run_retries(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]
    failed = _run(_http(pages), Box(ok=False), path, now)
    assert failed.ok is False
    assert failed.messages == []
    retried = _run(_http(pages), Box(), path, now)
    assert len(retried.messages) == 1


def test_invalidation_uses_closed_daily_candle_not_the_open_one(tmp_path) -> None:
    pages = [_btc("active")]
    klines = [
        [_ms(26), "1", "2", "1", "52700", "0"],
        [_ms(27), "1", "2", "1", "99999", "0"],
    ]
    path = tmp_path / "state.json"
    # 23:59 UTC ngày 26: nến ngày chưa đóng
    early = datetime(2026, 11, 26, 23, 59, tzinfo=timezone.utc)
    box = Box()
    early_report = _run(_http(pages, klines=klines), box, path, early)
    assert not any(msg.startswith("🔴") for msg in early_report.messages)
    assert any(msg.startswith("🟢") for msg in early_report.messages)

    # 00:00 UTC ngày 27 = 07:00 VN: nến đóng 52.700 < 53.000
    path2 = tmp_path / "state2.json"
    at = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    box2 = Box()
    report = _run(_http(pages, klines=klines), box2, path2, at)
    reds = [msg for msg in report.messages if msg.startswith("🔴")]
    assert len(reds) == 1
    assert "52.700 < 53.000" in reds[0]
    assert "99999" not in reds[0]
    assert "Dừng mua vùng này" in reds[0]

    box3 = Box()
    again = _run(_http(pages, klines=klines), box3, path2, at)
    assert not any(msg.startswith("🔴") for msg in again.messages)


def test_missing_invalidation_still_enters(tmp_path) -> None:
    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    report = _run(_http(pages), Box(), tmp_path / "s.json", now)
    assert len(report.messages) == 1
    assert report.messages[0].startswith("🟢")
    assert "Vô hiệu" not in report.messages[0]


def test_unpriceable_token_is_skipped_without_crashing(tmp_path, caplog) -> None:
    pages = [
        _btc("secz", **{
            "Ticker": {"type": "rich_text", "rich_text": [{"plain_text": "SECZ"}]},
            "Chuỗi/sàn tham chiếu": {"type": "rich_text", "rich_text": [{"plain_text": ""}]},
            "Vô hiệu nếu nến ngày đóng dưới": _number(None),
        })
    ]
    http = FakeHttp(
        [
            ("POST", "/v1/data_sources/", {"results": pages, "has_more": False}),
            ("GET", "api.binance.com/api/v3/ticker/price", [{"symbol": "BTCUSDT", "price": "1"}]),
            ("GET", "api.bybit.com/v5/market/tickers", {"retCode": 0, "result": {"list": []}}),
            ("GET", "okx.com/api/v5/market/tickers", {"code": "0", "data": []}),
            ("GET", "api.coingecko.com/api/v3/search", {"coins": []}),
        ]
    )
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    caplog.set_level("INFO")
    report = _run(http, Box(), tmp_path / "s.json", now)
    assert report.ok
    assert report.messages == []
    assert "SECZ" in caplog.text


def test_digest_lists_zone_once_per_vietnam_morning(tmp_path) -> None:
    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None), "Link phân tích Notion": {"type": "url", "url": None}})]
    path = tmp_path / "state.json"
    # Đã ở trong vùng từ trước, để bản tin không kèm tin vào vùng
    morning = datetime(2026, 11, 27, 0, 5, tzinfo=timezone.utc)
    # Lần đầu lúc 07:00 chỉ ghi trạng thái inside, chưa tới 07:05
    _run(_http(pages), Box(), path, datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc))
    box = Box()
    report = _run(_http(pages, price="60000"), box, path, morning)
    assert any(msg.startswith("📋") for msg in report.messages)
    digest = next(msg for msg in report.messages if msg.startswith("📋"))
    assert "BTC Vùng 1" in digest
    assert "60.000" in digest or "60.000" in digest.replace(".", "")
    assert "60.000" in digest or "60000" in digest
    box2 = Box()
    later = _run(_http(pages, price="60000"), box2, path, datetime(2026, 11, 27, 1, 0, tzinfo=timezone.utc))
    assert not any(msg.startswith("📋") for msg in later.messages)


def test_dry_run_prints_and_does_not_send_or_save(tmp_path, capsys) -> None:
    def boom(*_args, **_kwargs):
        raise AssertionError("không được gửi")

    notifier = TelegramNotifier("tok", "1", send_fn=boom)
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    report = run_once(
        settings=_settings(),
        config=_config(),
        http=_http([_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]),
        notifier=notifier,
        now=now,
        dry_run=True,
        save=False,
        state_path=path,
    )
    assert report.ok
    assert report.messages[0].startswith("🟢")
    assert "🟢 BTC vào Vùng 1" in capsys.readouterr().out
    assert not path.exists()


def test_price_outage_does_not_send_empty_digest(tmp_path) -> None:
    http = FakeHttp(
        [
            ("POST", "/v1/data_sources/", {"results": [_btc("active")], "has_more": False}),
            ("GET", "api.binance.com", HttpStatusError(451, "binance", "no")),
            ("GET", "api.bybit.com", HttpStatusError(451, "bybit", "no")),
            ("GET", "okx.com", HttpStatusError(451, "okx", "no")),
            ("GET", "api.coingecko.com", HttpStatusError(429, "cg", "no")),
        ]
    )
    now = datetime(2026, 11, 27, 0, 10, tzinfo=timezone.utc)
    box = Box()
    report = _run(http, box, tmp_path / "s.json", now)
    assert report.ok is False
    assert box.messages == []


def test_yaml_defaults_and_blank_notion_ids(monkeypatch) -> None:
    monkeypatch.delenv("BUY_ZONE_HYSTERESIS_PCT", raising=False)
    monkeypatch.delenv("BUY_ZONE_APPROACHING_PCT", raising=False)
    monkeypatch.delenv("BUY_ZONE_STATE_PATH", raising=False)
    config = load_buy_zone_config()
    assert config.hysteresis_pct == 2
    assert config.approaching is None
    assert (config.digest_hour_vn, config.digest_minute_vn) == (7, 5)
    assert config.lease_max_age_sec == 20 * 60

    settings = Settings(notion_database_id="", notion_data_source_id="  ")
    assert settings.notion_database_id == "41e859693b1581cc80bbfbcd6fe9e8c3"
    assert settings.notion_data_source_id == "41e85969-3b15-815a-9e5e-000b774bd208"


def test_chat_id_extract_and_telegram_redacts_token(caplog) -> None:
    chats = extract_chats(
        {
            "ok": True,
            "result": [
                {"update_id": 1, "message": {"chat": {"id": 123, "first_name": "Tomas"}}},
                {"update_id": 2, "message": {"chat": {"id": 123, "first_name": "Tomas"}}},
                {"update_id": 3, "message": {"chat": {"id": -100, "title": "Nhóm"}}},
            ],
        }
    )
    assert chats == [("123", "Tomas"), ("-100", "Nhóm")]

    def boom(token, _chat, _text):
        raise RuntimeError(f"URL bot{token}/sendMessage")

    caplog.set_level("ERROR")
    notifier = TelegramNotifier("SUPERSECRET", "1", send_fn=boom)
    assert notifier.send_text("xin chào") is False
    assert "SUPERSECRET" not in caplog.text
    assert "***" in caplog.text


def test_workflow_and_state_script_contract() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/buy-zone-alerts.yml").read_text(encoding="utf-8")
    assert 'cron: "*/10 * * * *"' in workflow
    assert "secrets.TELEGRAM_BOT_TOKEN" in workflow
    assert "secrets.TELEGRAM_CHAT_ID" in workflow
    assert "secrets.NOTION_TOKEN" in workflow
    assert "buy-zone-alert-state" in workflow
    script = (root / "scripts/sync_buy_zone_state.sh").read_text(encoding="utf-8")
    assert "git add -A" not in script
    assert "git switch" not in script
    assert "add -f -- state/buy_zones.json" in script
    mac = (root / "scripts/mac/start_buy_zones.sh").read_text(encoding="utf-8")
    assert "loop_buy_zones.sh" in mac
    example = (root / ".env.example").read_text(encoding="utf-8")
    assert "TELEGRAM_BOT_TOKEN=" in example
    assert "NOTION_TOKEN=" in example
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert ".state/" in gitignore
