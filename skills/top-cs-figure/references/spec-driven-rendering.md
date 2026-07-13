# Spec-Driven Rendering

Use `scripts/render_from_figure_spec.py` when the figure can be regenerated from a YAML render spec and source data.

## Minimal YAML

```yaml
figure_id: Figure 2
claim_ids: [C1]
venue: icml
visual_family: comparison
data_sources: [results.csv]
panel_map:
  - {panel_id: a, job: main comparison, source: results.csv}
encodings: {x: method, y: score, series: dataset}
metric_direction: higher-is-better
output_base: comparison
export_formats: [svg, pdf, png]
evidence_status: available
```

## Data rules

- Resolve data paths relative to the spec file unless `--outdir` only changes outputs.
- Reject missing required columns before plotting.
- Do not render result-like values when `evidence_status` is `planned`, `missing`, or `unverified`.
- Use `layout-mockup` only with visibly synthetic labels and never as result evidence.

Run bundle QA immediately after rendering.
