"""SSL cho Mac: ưu tiên chứng chỉ hệ thống (Keychain), rồi certifi."""

from __future__ import annotations

import ssl
from functools import lru_cache


@lru_cache(maxsize=1)
def ssl_context() -> ssl.SSLContext:
    # truststore = dùng chứng chỉ macOS Keychain (antivirus / proxy công ty cũng được).
    try:
        import truststore

        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        pass
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()
