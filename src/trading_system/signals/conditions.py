"""Đánh giá một điều kiện trên kết quả chỉ báo."""

from __future__ import annotations

from typing import Any

from trading_system.indicators.base import IndicatorResult
from trading_system.signals.models import ConditionEval, ConditionSpec


def _compare(actual: Any, expected: Any, op: str) -> bool:
    if op == "eq":
        return actual == expected
    if actual is None or expected is None:
        return False
    try:
        a = float(actual)
        b = float(expected)
    except (TypeError, ValueError):
        return False
    if op == "gt":
        return a > b
    if op == "gte":
        return a >= b
    if op == "lt":
        return a < b
    if op == "lte":
        return a <= b
    raise ValueError(f"op không hỗ trợ: {op}")


def evaluate_condition(
    spec: ConditionSpec,
    results: dict[str, IndicatorResult],
) -> ConditionEval:
    ind = results.get(spec.indicator)
    if ind is None:
        return ConditionEval(
            condition_id=spec.id,
            passed=False,
            points_awarded=0.0,
            detail=f"thiếu chỉ báo {spec.indicator}",
        )

    if spec.signal is not None:
        actual = ind.signals.get(spec.signal)
        expected = spec.equals
        passed = _compare(actual, expected, "eq")
        detail = f"signal {spec.signal}={actual!r} (cần {expected!r})"
    elif spec.value_key is not None:
        actual = ind.values.get(spec.value_key)
        expected = spec.compare_to if spec.compare_to is not None else spec.equals
        passed = _compare(actual, expected, spec.op)
        detail = f"value {spec.value_key}={actual!r} {spec.op} {expected!r}"
    else:
        return ConditionEval(
            condition_id=spec.id,
            passed=False,
            points_awarded=0.0,
            detail="điều kiện thiếu signal hoặc value_key",
        )

    points = float(spec.points) if passed else 0.0
    return ConditionEval(
        condition_id=spec.id,
        passed=passed,
        points_awarded=points,
        detail=detail,
    )
