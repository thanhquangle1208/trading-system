-- Phase 1 schema (SQLite). Mở rộng ở Phase 3+ (signals/rating đầy đủ).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    exchange     TEXT NOT NULL,
    symbol       TEXT NOT NULL,
    timeframe    TEXT NOT NULL,
    timestamp_ms INTEGER NOT NULL,
    open         REAL NOT NULL,
    high         REAL NOT NULL,
    low          REAL NOT NULL,
    close        REAL NOT NULL,
    volume       REAL NOT NULL,
    UNIQUE (exchange, symbol, timeframe, timestamp_ms)
);

CREATE TABLE IF NOT EXISTS paper_accounts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
    balance    REAL NOT NULL,
    currency   TEXT NOT NULL DEFAULT 'USDT',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS paper_orders (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id     INTEGER NOT NULL REFERENCES paper_accounts(id),
    symbol         TEXT NOT NULL,
    side           TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity       REAL NOT NULL,
    price          REAL NOT NULL,
    status         TEXT NOT NULL DEFAULT 'filled',
    rating         INTEGER,  -- Độ tin cậy 1–10
    stop_loss      REAL,
    take_profit_1  REAL,
    take_profit_2  REAL,
    market_type    TEXT DEFAULT 'spot',
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS signals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol        TEXT NOT NULL,
    timeframe     TEXT NOT NULL,
    direction     TEXT,
    score         REAL,
    rating        INTEGER,  -- Độ tin cậy 1–10
    strategy_id   TEXT,
    payload_json  TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
