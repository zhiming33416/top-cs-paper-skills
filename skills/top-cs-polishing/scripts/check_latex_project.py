#!/usr/bin/env python3
"""Compile a multi-file LaTeX project in an isolated temporary output directory."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ENGINES = ("xelatex", "pdflatex", "lualatex")


def find_root(project: Path, explicit: Path | None = None) -> Path:
    if explicit:
        root = explicit if explicit.is_absolute() else project / explicit
        if not root.is_file():
            raise ValueError(f"root TeX file not found: {root}")
        return root.resolve()
    candidates = []
    for path in project.glob("*.tex"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\\documentclass(?:\[[^]]*\])?\{[^}]+\}", text):
            candidates.append(path)
    if len(candidates) != 1:
        raise ValueError(f"expected exactly one root TeX file, found {len(candidates)}; pass --root")
    return candidates[0].resolve()


def choose_engine(requested: str) -> str | None:
    if requested != "auto":
        return shutil.which(requested)
    for engine in ENGINES:
        executable = shutil.which(engine)
        if executable:
            return executable
    return None


def command_for(engine: str, root: Path, output_dir: Path) -> list[str]:
    return [
        engine,
        "-no-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={output_dir}",
        root.name,
    ]


def analyze_log(log: str) -> dict[str, Any]:
    return {
        "undefined_citations": sorted(set(re.findall(r"Citation [`']([^`']+)[`'].*undefined", log, re.IGNORECASE))),
        "undefined_references": sorted(set(re.findall(r"Reference [`']([^`']+)[`'].*undefined", log, re.IGNORECASE))),
        "overfull_boxes": len(re.findall(r"Overfull \\[hv]box", log)),
        "latex_errors": re.findall(r"(?m)^! (.+)$", log),
        "rerun_warning": bool(re.search(r"Rerun to get cross-references right|Label\(s\) may have changed", log, re.IGNORECASE)),
    }


def compile_project(project: Path, root_arg: Path | None, engine_arg: str, timeout: int) -> dict[str, Any]:
    project = project.resolve()
    if not project.is_dir():
        raise ValueError(f"project directory not found: {project}")
    root = find_root(project, root_arg)
    try:
        root.relative_to(project)
    except ValueError as exc:
        raise ValueError("root TeX file must remain inside the project") from exc
    engine = choose_engine(engine_arg)
    if not engine:
        return {"status": "engine-unavailable", "requested_engine": engine_arg, "root": root.name, "compiled": False}
    with tempfile.TemporaryDirectory(prefix="top-cs-latex-") as tmp:
        output_dir = Path(tmp)
        logs = []
        return_codes = []
        for _ in range(2):
            completed = subprocess.run(
                command_for(engine, root, output_dir),
                cwd=project,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
            return_codes.append(completed.returncode)
            logs.append(completed.stdout + "\n" + completed.stderr)
            if completed.returncode != 0:
                break
        log_path = output_dir / f"{root.stem}.log"
        combined = "\n".join(logs) + ("\n" + log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else "")
        findings = analyze_log(combined)
        pdf = output_dir / f"{root.stem}.pdf"
        return {
            "status": "compiled" if pdf.is_file() and all(code == 0 for code in return_codes) else "compile-failed",
            "compiled": pdf.is_file() and all(code == 0 for code in return_codes),
            "engine": Path(engine).name,
            "root": root.name,
            "passes": len(return_codes),
            "return_codes": return_codes,
            "shell_escape": False,
            "project_modified": False,
            "findings": findings,
        }


def as_text(result: dict[str, Any]) -> str:
    lines = [f"status: {result['status']}", f"compiled: {result.get('compiled', False)}", f"root: {result.get('root')}"]
    if result.get("findings"):
        for key, value in result["findings"].items():
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--engine", choices=("auto",) + ENGINES, default="auto")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    try:
        result = compile_project(args.project, args.root, args.engine, args.timeout)
    except (ValueError, subprocess.TimeoutExpired) as exc:
        result = {"status": "error", "compiled": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else as_text(result))
    return 0 if result.get("compiled") else 2 if result.get("status") == "engine-unavailable" else 1


if __name__ == "__main__":
    raise SystemExit(main())
