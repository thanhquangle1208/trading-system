from __future__ import annotations

from pathlib import Path

from trading_system.storage.db import Database


def test_schema_init_and_paper_account(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    db.init_schema()
    assert db.schema_version() == "2"

    account_id = db.ensure_paper_account("default", 1000.0)
    assert account_id > 0
    assert db.get_paper_balance(account_id) == 1000.0

    # idempotent
    same = db.ensure_paper_account("default", 999.0)
    assert same == account_id
    assert db.get_paper_balance(account_id) == 1000.0

    db.close()
