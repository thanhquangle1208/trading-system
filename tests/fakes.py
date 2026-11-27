"""HTTP giả cho test — không gọi mạng."""

from __future__ import annotations

from trading_system.data.http_client import HttpStatusError


class FakeHttp:
    def __init__(self, handlers: list) -> None:
        self.handlers = handlers
        self.calls: list[dict] = []

    def request_json(self, method, url, *, headers=None, body=None, timeout=20):
        self.calls.append(
            {"method": method, "url": url, "body": body, "headers": headers or {}}
        )
        for spec in self.handlers:
            match_method, needle, resp = spec
            if match_method == method and needle in url:
                if isinstance(resp, Exception):
                    raise resp
                if callable(resp):
                    return resp(method, url, body)
                return resp
        raise HttpStatusError(404, url, "no fake")
