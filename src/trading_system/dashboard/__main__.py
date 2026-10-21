"""Chạy: python -m trading_system.dashboard"""

from __future__ import annotations

import uvicorn

from trading_system.logging_setup import setup_logging
from trading_system.settings import get_settings


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    # Localhost only
    uvicorn.run(
        "trading_system.dashboard.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
