"""Mac giữ nhịp thì GitHub nhường. Nhịp cũ thì GitHub chạy và không báo lại vùng đã báo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from trading_system.data.http_client import HttpStatusError
from trading_system.zones.logic import ZoneMemory
from trading_system.zones.runner import run_once
from trading_system.zones.state import (
    AlertState,
    claim_lease,
    lease_blocks_github,
    load_state,
    save_state,
    should_skip_push,
)
from tests.fakes import FakeHttp
from tests.test_buy_zone_runner import Box, _btc, _config, _http, _number, _run, _settings


def test_fresh_local_lease_blocks_github_and_stale_does_not() -> None:
    now = datetime(2026, 11, 27, 10, 0, tzinfo=timezone.utc)
    fresh = AlertState()
    claim_lease(fresh, "local", now - timedelta(minutes=5))
    assert lease_blocks_github(fresh, now, 20 * 60)

    stale = AlertState()
    claim_lease(stale, "local", now - timedelta(minutes=21))
    assert not lease_blocks_github(stale, now, 20 * 60)

    github = AlertState()
    claim_lease(github, "github", now)
    assert not lease_blocks_github(github, now, 20 * 60)


def test_github_skips_push_when_remote_mac_lease_is_fresh() -> None:
    now = datetime(2026, 11, 27, 10, 0, tzinfo=timezone.utc)
    local = {"lease": {"holder": "github", "heartbeat_utc": "2026-11-27T10:00:00Z"}}
    remote = {"lease": {"holder": "local", "heartbeat_utc": "2026-11-27T09:50:00Z"}}
    assert should_skip_push(local, remote, now, 20 * 60)
    old_remote = {"lease": {"holder": "local", "heartbeat_utc": "2026-11-27T09:00:00Z"}}
    assert not should_skip_push(local, old_remote, now, 20 * 60)
    mac_file = {"lease": {"holder": "local", "heartbeat_utc": "2026-11-27T10:00:00Z"}}
    assert not should_skip_push(mac_file, old_remote, now, 20 * 60)


def test_github_yields_while_mac_heartbeat_is_fresh(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    state = AlertState()
    claim_lease(state, "local", now - timedelta(minutes=3))
    save_state(path, state)
    before = path.read_text(encoding="utf-8")

    def explode(*_args, **_kwargs):
        raise AssertionError("GitHub không được gọi mạng khi Mac còn nhịp")

    http = FakeHttp([("POST", "notion", explode)])
    report = run_once(
        settings=_settings(),
        config=_config(),
        http=http,
        notifier=Box(),
        now=now,
        save=True,
        state_path=path,
        runner="github",
    )
    assert report.ok
    assert report.yielded
    assert report.messages == []
    assert path.read_text(encoding="utf-8") == before


def test_stale_mac_lease_lets_github_run_without_repeat_entry(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    state = AlertState(zones={"active": ZoneMemory(inside=True)})
    claim_lease(state, "local", now - timedelta(minutes=30))
    save_state(path, state)

    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]
    report = _run(_http(pages), Box(), path, now, runner="github")
    assert report.ok
    assert report.yielded is False
    assert report.messages == []
    saved = load_state(path)
    assert saved.lease_holder == "github"
    assert saved.zones["active"].inside is True


def test_stale_lease_github_sends_new_entry(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    state = AlertState()
    claim_lease(state, "local", now - timedelta(minutes=40))
    save_state(path, state)
    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]
    box = Box()
    report = _run(_http(pages), box, path, now, runner="github")
    assert len(box.messages) == 1
    assert box.messages[0].startswith("🟢")
    assert load_state(path).lease_holder == "github"
    assert report.yielded is False


def test_claim_only_writes_heartbeat_and_does_not_call_network(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    http = FakeHttp([("GET", "", HttpStatusError(500, "x", "no"))])
    report = run_once(
        settings=_settings(),
        config=_config(),
        http=http,
        notifier=Box(),
        now=now,
        save=True,
        state_path=path,
        runner="local",
        claim_only=True,
    )
    assert report.ok
    assert http.calls == []
    saved = load_state(path)
    assert saved.lease_holder == "local"
    assert saved.heartbeat_utc == "2026-11-27T00:00:00Z"


def test_claim_without_token_does_not_block_github(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "state.json"
    from trading_system.settings import Settings

    report = run_once(
        settings=Settings(notion_token="", telegram_bot_token="", telegram_chat_id=""),
        config=_config(),
        http=FakeHttp([]),
        notifier=Box(),
        now=now,
        save=True,
        state_path=path,
        runner="local",
        claim_only=True,
    )
    assert report.ok is False
    assert not path.exists()


def test_local_run_claims_lease(tmp_path) -> None:
    now = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    pages = [_btc("active", **{"Vô hiệu nếu nến ngày đóng dưới": _number(None)})]
    path = tmp_path / "state.json"
    _run(_http(pages), Box(), path, now, runner="local")
    assert load_state(path).lease_holder == "local"
