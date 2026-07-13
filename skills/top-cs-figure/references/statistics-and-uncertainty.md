# Statistics and Uncertainty

Use an interval only when its source is explicit: `sd`, `se`, deterministic `bootstrap-ci`, or supplied lower/upper bounds. A v3 panel computed from `raw_y` declares estimator, uncertainty, missing policy, seed, and grouping encodings. A supplied interval maps either `error` or both `lower` and `upper` columns.

- Preserve seed/run values when supplied; raw-point overlays are evidence of variation, not a substitute for a statistical test.
- State the unit of aggregation, sample count, and paired/unpaired basis in the caption or panel metadata when available.
- Critical-difference bars require an explicit value and ranking procedure. Do not infer significance from non-overlapping marks, color, or rank distance.
- For systems figures, keep hardware, batch size, sequence length, and operating point in data provenance or caption inputs.
- The renderer computes descriptive intervals only. It never creates p-values; significance consumes an explicit source column with test and adjustment metadata.
