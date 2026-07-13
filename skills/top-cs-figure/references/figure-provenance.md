# Figure Provenance

Treat the figure as a reproducible evidence artifact, not only an image.

## Required chain

1. Original render-spec hash and input version.
2. Migration actions to the v3 internal model.
3. Source registry path, declared SHA, actual SHA, format, and columns.
4. Ordered transform records with input/output row counts.
5. Estimator, uncertainty, confidence, bootstrap samples, seed, n, and missing policy.
6. Per-panel plotted-data path and hash.
7. Venue style status, palette status, and generic fallback reason.
8. Environment versions, target dimensions, export paths, and output hashes.

The render manifest captures execution. The figure audit combines bundle QA, unresolved inputs, style-evidence hashes, and optional revision diff. Keep user data and raw corpus outside the skill package; retain only synthetic atlas inputs/hashes and aggregate evidence permitted by repository policy.

An unresolved source, missing hash, or unverified evidence status must remain visible. Never replace a provenance gap with a guessed result or a success label.
