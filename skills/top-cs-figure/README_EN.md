# `top-cs-figure` Skill

[中文说明](README.md) · [Repository home](../../README_EN.md)

Status: **Beta**

Plan, generate, revise, export, and audit computer-science paper figures with a Python-first, spec-driven workflow.

## What To Use It For

- Create comparisons, trends, intervals, heatmaps, scatter plots, networks, method schematics, and multi-panel figures.
- Render from a figure brief, CSV/YAML data, or an existing render spec.
- Export SVG, PDF, PNG, and optional TIFF with plotted data and a render manifest.
- Audit color accessibility, caption and manuscript callouts, consistency, geometry, and figure integrity.

## Typical Requests

- `Create an ICML multi-panel comparison with confidence intervals from comparison.csv.`
- `Turn this figure brief into a strict render spec and export SVG/PDF/PNG.`
- `Audit panel labels, color separation, caption obligations, and source-data correspondence in this bundle.`

## What You Need To Provide

Prefer a figure brief or render spec. Source data, metric meaning, intended takeaway, panel relationships, caption obligations, target venue, and output formats are also accepted.

## Outputs

A normalized spec, panel-level plotted-data CSV files, render manifest, SVG/PDF/PNG, optional TIFF, and QA or revision-audit reports.

## Boundaries

The skill does not invent data, alter image pixels to support a conclusion, or present corpus style as official formatting. Its cross-venue `unified-family` palette is a generic implementation choice, not a venue preference. It does not build interactive dashboards, use Figma or Illustrator as the primary backend, or generate AI graphical abstracts.

## Runtime and Dependencies

Run `python -m pip install -r requirements.txt` before using rendering and QA scripts. The skill also requires `_shared` and derived visual-style evidence; use the complete installation described in [INSTALL.md](../../INSTALL.md).

## Related Skills

- [`top-cs-writing`](../top-cs-writing/README_EN.md): create figure briefs and manuscript callouts.
- [`top-cs-polishing`](../top-cs-polishing/README_EN.md): check captions and LaTeX layout.
- [`top-cs-response`](../top-cs-response/README_EN.md): map figure revisions to review issues.
