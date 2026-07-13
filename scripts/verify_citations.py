#!/usr/bin/env python3
"""Repository CLI wrapper for the installed shared citation verifier."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "scripts" / "verify_citations.py"
    runpy.run_path(str(target), run_name="__main__")
