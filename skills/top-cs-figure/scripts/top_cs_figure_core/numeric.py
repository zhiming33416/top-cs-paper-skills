from __future__ import annotations

import math
from typing import Any


def as_float(value: Any) -> float:
    """Parse one finite numeric value with a stable renderer-facing error."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"expected numeric value, got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"expected finite numeric value, got {value!r}")
    return number
