---
name: top-cs-figure
description: Create, revise, audit, render, and export publication-ready computer-science paper figures using a Python-first, corpus-calibrated workflow. Use for manuscript figures, multi-panel experimental charts, comparison plots, scaling curves, heatmaps, embeddings, network diagrams, method schematics, executable YAML/CSV figure render specs, figure-brief handoffs, caption/callout alignment, SVG/PDF/PNG/TIFF export bundles, venue-style evidence checks, and visual QA for WWW, ICLR, ICML, or generic top-CS submissions. Prefer an existing top-cs figure brief or render spec when provided; otherwise build a compact figure contract before plotting. Do not use for interactive dashboards, Plotly/Altair/web apps, Illustrator/Figma-first layout, AI-generated graphical abstracts, or result-table writing.
---

# Top CS Figure

Use the skill's static/dynamic layers; do not reconstruct visual grammar or export rules from memory.

## Route the request

1. Read `manifest.yaml` and every path under `always_load`.
2. Detect `venue`, `paper_type`, and `visual_family`; resolve `figure_task`, `data_state`, `output_target`, and `figure_handoff` as runtime parameters.
3. State the route, data boundary, and output target in one short line.
4. Load only the files mapped to the selected axis values.
5. Open `references/` only when an `on_demand` condition applies, especially corpus visual style, statistics, archetypes, accessibility, provenance, revision audit, or spec rendering for figure production tasks.
6. Use `generic` for unsupported venue/year combinations and tell the user to verify current official formatting rules.

## Execute

1. Prefer the shared `figure-brief` contract when present. Preserve `figure_id`, `claim_ids`, research question, evidence status, panel jobs, caption draft, and manuscript callout.
2. If no brief exists, create a minimal figure contract before code: claim, data source, panel map, visual family, metric direction, final size, export formats, and unresolved inputs.
3. Treat data availability as binding. Use supplied data for results; when data are missing, return missing-inputs or a clearly labeled layout mockup without invented values.
4. Use `scripts/render_from_figure_spec.py` when a YAML render spec and CSV/image source can make the figure repeatable. Prefer strict v3 specs; migrate v1/v2 inputs explicitly and record the migration.
5. Use Python/matplotlib for all plotting, previewing, exporting, and visual QA. Do not add R, Plotly, Altair, OpenRouter, or image-generation routes.
6. Keep method colors, dataset labels, metric direction, baseline order, and terminology aligned with the manuscript.
7. Resolve color through `palette_profile`: require promoted style evidence and a usable co-occurrence profile for venue-derived mode; otherwise retain generic semantic roles. Report observed anchors, constructed tokens, accessibility metrics, and fallback reason. Never present corpus defaults as official venue rules or acceptance advice.
8. Export SVG as the primary editable artifact, plus PDF and PNG preview by default; add TIFF only for camera-ready or explicit submission bundles.
9. Require plotted-data CSV, normalized spec, render manifest, SVG/PDF/PNG, and structured QA for produced result figures. Run `scripts/audit_figure_spec.py` for a reproducibility record or revision comparison.
10. Return the fixed output sections from `static/core/output-format.md`, including unresolved inputs and verification status.
