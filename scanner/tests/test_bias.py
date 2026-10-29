"""Kiểm tra nhanh bias W1 EMA (Nấc 1)."""

from __future__ import annotations

import pandas as pd

from sd_scanner.bias import bias_allows, bias_label, ema_last


def test_ema_last_needs_enough_bars() -> None:
    s = pd.Series([float(i) for i in range(10)])
    assert ema_last(s, 34) is None
    s2 = pd.Series([float(i) for i in range(40)])
    v = ema_last(s2, 34)
    assert v is not None
    assert v > 0


def test_bias_allows_buy_sell() -> None:
    assert bias_allows("buy", 110.0, 100.0) is True
    assert bias_allows("buy", 90.0, 100.0) is False
    assert bias_allows("sell", 90.0, 100.0) is True
    assert bias_allows("sell", 110.0, 100.0) is False


def test_bias_label_vi() -> None:
    assert "tăng" in bias_label(110.0, 100.0, 34)
    assert "giảm" in bias_label(90.0, 100.0, 34)
    assert "EMA34" in bias_label(110.0, 100.0, 34)
