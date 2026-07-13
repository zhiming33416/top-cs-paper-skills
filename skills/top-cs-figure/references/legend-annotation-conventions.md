# Legend and Annotation Conventions

## Guide ownership

Use one shared legend when panels repeat the same method vocabulary. Aggregate unique labels from all participating panels; never use only the last panel's handles. Reserve a dedicated figure slot so the legend does not cover data.

Use local legends when vocabularies differ or a panel can be read independently. Prefer direct labels for a small number of well-separated lines. A colorbar belongs to its matrix; share it only when panels use the same normalization and semantic range.

## Identity registry

Assign each method a stable semantic role, color, marker, line style, and hatch. The focal method may receive the strongest accent, but its line width and marker must remain comparable to baselines. Do not use color to imply statistical significance.

## Metric direction

State a common direction once at figure level. Put direction in an axis label only when panels have different metrics or directions. Avoid repeating `higher is better` in every panel title.

## Annotation types

- reference lines mark declared thresholds, chance levels, budgets, or operating points;
- text notes identify declared regimes or events;
- interval caps encode supplied or computed uncertainty;
- significance marks consume explicit test-result columns only.

Keep annotations subordinate to data marks. Use short phrases and place detailed definitions in the caption. Every annotation must have a source or a deterministic relationship to plotted data.

## Caption alignment

The caption maps panel ID to evidence job, defines encodings that are not obvious, and discloses estimator, interval, sample count, normalization, and special annotations. The manuscript callout states the conclusion and points to the relevant panels without introducing facts absent from them.
