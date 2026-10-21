"""Cấu hình logging: console + file trong thư mục logs/."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from trading_system.settings import REPO_ROOT


def setup_logging(level: str = "INFO", log_dir: Path | None = None) -> logging.Logger:
    """Khởi tạo logger gốc `trading_system`. Gọi một lần khi app start."""
    log_dir = log_dir or (REPO_ROOT / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("trading_system")
    root.handlers.clear()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    root.debug("Logging đã sẵn sàng (level=%s)", level)
    return root


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"trading_system.{name}")
    return logging.getLogger("trading_system")
