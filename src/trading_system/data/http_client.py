"""HTTP JSON nhỏ. SSL qua ssl_util (Keychain Mac / certifi)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from trading_system.data.ssl_util import ssl_context

DEFAULT_HEADERS = {
    "User-Agent": "trading-system-buy-zone/1.0",
    "Accept": "application/json",
}


class HttpStatusError(Exception):
    def __init__(self, status: int, url: str, body: str = "") -> None:
        self.status = status
        self.url = url
        self.body = body
        super().__init__(f"HTTP {status} cho {url}: {body[:180]}")


class UrllibClient:
    def __init__(self) -> None:
        self._ssl = ssl_context()

    def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        timeout: float = 20,
    ) -> Any:
        merged = dict(DEFAULT_HEADERS)
        if headers:
            merged.update(headers)
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            merged.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=data, headers=merged, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=self._ssl) as resp:
                raw = resp.read().decode("utf-8")
                status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise HttpStatusError(exc.code, url, err_body) from None
        except urllib.error.URLError as exc:
            raise HttpStatusError(0, url, str(exc.reason)) from None
        if status >= 400:
            raise HttpStatusError(status, url, raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise HttpStatusError(status, url, f"JSON lỗi: {exc}") from None
