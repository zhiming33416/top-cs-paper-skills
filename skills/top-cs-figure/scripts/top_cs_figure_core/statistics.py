from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import mean, median, stdev
from typing import Any, Iterable


def estimate(values: list[float], estimator: str) -> float:
    if not values:
        raise ValueError("cannot estimate an empty sample")
    if estimator == "mean":
        return mean(values)
    if estimator == "median":
        return median(values)
    raise ValueError(f"unsupported estimator: {estimator}")


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute percentile of empty values")
    position = (len(ordered) - 1) * quantile
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bootstrap_interval(values: list[float], estimator: str, confidence: float, samples: int, seed: int) -> tuple[float, float]:
    if samples < 100:
        raise ValueError("bootstrap_samples must be at least 100")
    if not 0.5 < confidence < 1:
        raise ValueError("confidence must be between 0.5 and 1")
    rng = random.Random(seed)
    estimates = [estimate([rng.choice(values) for _ in values], estimator) for _ in range(samples)]
    alpha = (1 - confidence) / 2
    return percentile(estimates, alpha), percentile(estimates, 1 - alpha)


def uncertainty(values: list[float], kind: str, estimator: str, confidence: float, samples: int, seed: int) -> tuple[float, float] | None:
    center = estimate(values, estimator)
    if kind in {"none", ""}:
        return None
    if len(values) < 2 and kind in {"sd", "se", "bootstrap-ci"}:
        raise ValueError(f"{kind} requires at least two observations")
    if kind == "sd":
        spread = stdev(values)
        return center - spread, center + spread
    if kind == "se":
        spread = stdev(values) / math.sqrt(len(values))
        return center - spread, center + spread
    if kind == "bootstrap-ci":
        return bootstrap_interval(values, estimator, confidence, samples, seed)
    raise ValueError(f"unsupported computed uncertainty: {kind}")


def summarize_panel_rows(rows: list[dict[str, Any]], panel: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    statistics = panel.get("statistics") or {}
    enc = panel.get("encodings") or {}
    raw_column = enc.get("raw_y")
    if not raw_column:
        return rows, {"computed": False}
    estimator = statistics.get("estimator") or statistics.get("aggregation") or "mean"
    interval = (statistics.get("uncertainty") or {}).get("kind", "none")
    confidence = float((statistics.get("uncertainty") or {}).get("confidence", 0.95))
    samples = int((statistics.get("uncertainty") or {}).get("bootstrap_samples", 2000))
    seed = int((statistics.get("uncertainty") or {}).get("seed", 0))
    missing = statistics.get("missing", "reject")
    group_columns = [column for column in (enc.get("x"), enc.get("series") or enc.get("group")) if column]
    groups: dict[tuple[str, ...], list[float]] = defaultdict(list)
    templates: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(column, "")) for column in group_columns)
        raw = row.get(raw_column)
        if raw in {None, ""}:
            if missing == "drop":
                continue
            raise ValueError(f"missing raw statistic value in column: {raw_column}")
        groups[key].append(float(raw))
        templates.setdefault(key, {column: row.get(column) for column in group_columns})
    output: list[dict[str, Any]] = []
    y_column = enc.get("y") or "value"
    lower_column = enc.get("lower") or "__lower"
    upper_column = enc.get("upper") or "__upper"
    enc["y"] = y_column
    if interval != "none":
        enc["lower"], enc["upper"] = lower_column, upper_column
    for index, (key, values) in enumerate(groups.items()):
        row = dict(templates[key])
        row[y_column] = estimate(values, estimator)
        row["__n"] = len(values)
        bounds = uncertainty(values, interval, estimator, confidence, samples, seed + index)
        if bounds:
            row[lower_column], row[upper_column] = bounds
        output.append(row)
    return output, {
        "computed": True,
        "estimator": estimator,
        "uncertainty": interval,
        "confidence": confidence if interval == "bootstrap-ci" else None,
        "bootstrap_samples": samples if interval == "bootstrap-ci" else None,
        "seed": seed,
        "groups": len(output),
        "observations": sum(len(values) for values in groups.values()),
        "missing_policy": missing,
    }
