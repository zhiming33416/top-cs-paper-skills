from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean, median
from typing import Any


def _numeric(value: Any) -> float:
    return float(value)


def apply_transforms(rows: list[dict[str, Any]], transforms: list[dict[str, Any]] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    current = [dict(row) for row in rows]
    report: list[dict[str, Any]] = []
    for transform in transforms or []:
        kind = transform["kind"]
        before = len(current)
        if kind == "filter":
            column = transform["column"]
            if "equals" in transform:
                current = [row for row in current if row.get(column) == transform["equals"]]
            elif "in" in transform:
                allowed = set(transform["in"])
                current = [row for row in current if row.get(column) in allowed]
            else:
                raise ValueError("filter requires equals or in")
        elif kind == "sort":
            column = transform["by"]
            current.sort(key=lambda row: row.get(column), reverse=bool(transform.get("descending")))
        elif kind == "group":
            columns = transform.get("by") or []
            if not columns:
                raise ValueError("group transform requires by")
            current.sort(key=lambda row: tuple(str(row.get(column, "")) for column in columns))
        elif kind == "aggregate":
            group_by = transform.get("group_by") or []
            metrics = transform.get("metrics") or {}
            groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
            for row in current:
                groups[tuple(row.get(column) for column in group_by)].append(row)
            aggregated: list[dict[str, Any]] = []
            for key, items in groups.items():
                output = dict(zip(group_by, key))
                for name, metric in metrics.items():
                    values = [_numeric(item[metric["column"]]) for item in items]
                    operation = metric["op"]
                    output[name] = {"mean": mean, "median": median, "min": min, "max": max, "sum": sum, "count": len}[operation](values) if operation != "count" else len(values)
                aggregated.append(output)
            current = aggregated
        elif kind == "normalize":
            column = transform["column"]
            output = transform.get("output", column)
            values = [_numeric(row[column]) for row in current]
            method = transform.get("method", "minmax")
            if method == "minmax":
                low, high = min(values), max(values)
                if high == low:
                    raise ValueError("minmax normalization requires non-constant values")
                normalized = [(value - low) / (high - low) for value in values]
            elif method == "zscore":
                center = mean(values)
                variance = sum((value - center) ** 2 for value in values) / max(1, len(values) - 1)
                if variance == 0:
                    raise ValueError("zscore normalization requires non-constant values")
                normalized = [(value - center) / math.sqrt(variance) for value in values]
            else:
                raise ValueError(f"unsupported normalization: {method}")
            for row, value in zip(current, normalized):
                row[output] = value
        elif kind == "baseline-delta":
            column, baseline_column = transform["column"], transform["baseline_column"]
            output = transform.get("output", f"{column}_delta")
            for row in current:
                row[output] = _numeric(row[column]) - _numeric(row[baseline_column])
        elif kind == "rank":
            column = transform["column"]
            output = transform.get("output", f"{column}_rank")
            descending = transform.get("direction", "higher-is-better") == "higher-is-better"
            ordered = sorted(range(len(current)), key=lambda index: _numeric(current[index][column]), reverse=descending)
            for rank, index in enumerate(ordered, 1):
                current[index][output] = rank
        else:
            raise ValueError(f"unsupported transform: {kind}")
        report.append({"kind": kind, "input_rows": before, "output_rows": len(current)})
    return current, report
