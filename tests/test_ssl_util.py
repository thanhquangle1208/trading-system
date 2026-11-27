"""SSL context phải tạo được (truststore hoặc certifi)."""

from trading_system.data.ssl_util import ssl_context


def test_ssl_context_builds() -> None:
    ctx = ssl_context()
    assert ctx is not None
    # Gọi lại phải lấy cache, không lỗi.
    assert ssl_context() is ctx
