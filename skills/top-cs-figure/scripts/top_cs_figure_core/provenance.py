from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_plotted_data(base: Path, panel_id: str, rows: list[dict[str, Any]]) -> Path:
    path = base.parent / f"{base.name}.{panel_id}.plotted-data.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(str(key) for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader(); writer.writerows([{column: row.get(column, "") for column in columns} for row in rows])
    return path


def schematic_records(panel: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten declared schematic geometry without inventing visual semantics."""
    records: list[dict[str, Any]] = []
    for kind in ("lanes", "groups", "nodes"):
        for item in panel.get(kind) or []:
            records.append({"record_type": kind[:-1], **item})
    for edge in panel.get("edges") or []:
        records.append({"record_type": "edge", **edge})
    return records


def clean_internal(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: clean_internal(item) for key, item in value.items() if not str(key).startswith("_") and key != "source_registry"}
    if isinstance(value, list):
        return [clean_internal(item) for item in value]
    return value
