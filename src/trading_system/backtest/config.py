"""Đọc configs/backtest.yaml."""

from __future__ import annotations

from dataclasses import dataclass

from trading_system.config_loader import load_yaml


@dataclass(frozen=True)
class BacktestConfig:
    initial_balance_usdt: float
    warmup_bars: int
    fee_bps: float
    slippage_bps: float
    funding_bps_per_bar: float
    train_ratio: float
    optuna_n_trials: int
    score_threshold_min: float
    score_threshold_max: float


def load_backtest_config() -> BacktestConfig:
    raw = load_yaml("backtest.yaml")
    wf = raw.get("walk_forward") or {}
    opt = raw.get("optuna") or {}
    return BacktestConfig(
        initial_balance_usdt=float(raw.get("initial_balance_usdt", 1000)),
        warmup_bars=int(raw.get("warmup_bars", 100)),
        fee_bps=float(raw.get("fee_bps", 10)),
        slippage_bps=float(raw.get("slippage_bps", 5)),
        funding_bps_per_bar=float(raw.get("funding_bps_per_bar", 0)),
        train_ratio=float(wf.get("train_ratio", 0.7)),
        optuna_n_trials=int(opt.get("n_trials", 8)),
        score_threshold_min=float(opt.get("score_threshold_min", 50)),
        score_threshold_max=float(opt.get("score_threshold_max", 80)),
    )
