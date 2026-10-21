"""Kết nối SQLite + khởi tạo schema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from trading_system.logging_setup import get_logger
from trading_system.settings import Settings, get_settings

log = get_logger("storage.db")

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
SCHEMA_VERSION = "1"


class Database:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> Database:
        settings = settings or get_settings()
        return cls(settings.database_file())

    def init_schema(self) -> None:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        self._conn.executescript(sql)
        self._conn.execute(
            "INSERT INTO schema_meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("schema_version", SCHEMA_VERSION),
        )
        self._conn.commit()
        log.info("SQLite schema sẵn sàng (%s) version=%s", self.path, SCHEMA_VERSION)

    def ensure_paper_account(self, name: str, balance: float, currency: str = "USDT") -> int:
        cur = self._conn.execute("SELECT id FROM paper_accounts WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            return int(row["id"])
        cur = self._conn.execute(
            "INSERT INTO paper_accounts(name, balance, currency) VALUES (?, ?, ?)",
            (name, balance, currency),
        )
        self._conn.commit()
        account_id = int(cur.lastrowid)
        log.info("Tạo paper account id=%s name=%s balance=%.2f %s", account_id, name, balance, currency)
        return account_id

    def get_paper_balance(self, account_id: int) -> float:
        cur = self._conn.execute("SELECT balance FROM paper_accounts WHERE id = ?", (account_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"paper account id={account_id} không tồn tại")
        return float(row["balance"])

    def insert_paper_order(
        self,
        account_id: int,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        status: str = "filled",
        rating: int | None = None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO paper_orders(account_id, symbol, side, quantity, price, status, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (account_id, symbol, side, quantity, price, status, rating),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def save_candles(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        candles: list,
    ) -> int:
        rows = [
            (
                exchange,
                symbol,
                timeframe,
                c.timestamp_ms,
                c.open,
                c.high,
                c.low,
                c.close,
                c.volume,
            )
            for c in candles
        ]
        self._conn.executemany(
            """
            INSERT OR REPLACE INTO candles
            (exchange, symbol, timeframe, timestamp_ms, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self._conn.commit()
        return len(rows)

    def insert_signal(
        self,
        *,
        symbol: str,
        timeframe: str,
        direction: str | None,
        score: float | None,
        rating: int | None,
        strategy_id: str | None,
        payload_json: str | None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO signals(symbol, timeframe, direction, score, rating, strategy_id, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (symbol, timeframe, direction, score, rating, strategy_id, payload_json),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def schema_version(self) -> str | None:
        try:
            cur = self._conn.execute(
                "SELECT value FROM schema_meta WHERE key = ?",
                ("schema_version",),
            )
            row = cur.fetchone()
            return str(row["value"]) if row else None
        except sqlite3.Error:
            return None

    def close(self) -> None:
        self._conn.close()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn
