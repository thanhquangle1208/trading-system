"""Watchlist: file Git (cấu hình) + file local (danh sách cặp — không commit)."""

from __future__ import annotations

from pathlib import Path

import yaml

# Cặp do /add và Mac giữ ở đây — gitignore → git pull không bị chặn / không mất cặp.
LOCAL_NAME = "watchlist.local.yaml"


def load_raw(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_raw(path: Path, raw: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(raw, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def save_symbols(path: Path, symbols: list[str]) -> None:
    """Ghi symbols vào path (thường là watchlist.local.yaml)."""
    raw = load_raw(path)
    raw["symbols"] = list(symbols)
    save_raw(path, raw)


def normalize_symbols(raw_list: list | None) -> list[str]:
    out: list[str] = []
    for s in raw_list or []:
        sym = str(s).upper().replace(".P", "").replace("/", "")
        if sym and sym not in out:
            out.append(sym)
    return out


def ensure_local_symbols(scanner_dir: Path, seed_symbols: list[str]) -> tuple[Path, list[str]]:
    """
    Trả (đường_local, symbols).
    - Nếu đã có watchlist.local.yaml → dùng symbols ở đó.
    - Nếu chưa → tạo từ seed (watchlist.yaml) một lần (migrate).
    """
    local_path = scanner_dir / LOCAL_NAME
    if local_path.is_file():
        local_raw = load_raw(local_path)
        syms = normalize_symbols(local_raw.get("symbols"))
        if syms:
            return local_path, syms
        # file rỗng → seed
        syms = normalize_symbols(seed_symbols)
        save_symbols(local_path, syms)
        return local_path, syms

    syms = normalize_symbols(seed_symbols)
    save_symbols(local_path, syms)
    print(f"  watchlist: tạo {local_path.name} ({len(syms)} cặp) — không commit file này")
    return local_path, syms
