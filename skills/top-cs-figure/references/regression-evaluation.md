# Regression Evaluation

The evaluation system has two layers because public synthetic coverage and private real-world coverage answer different questions.

## Public synthetic matrix

`tests/figure-evals.yaml` is executable configuration. Each case declares:

- fixture and CLI/operation;
- expected files;
- structural assertions;
- numeric assertions;
- QA thresholds;
- expected failure mode.

`run_figure_evals.py` must execute every declared assertion. Unknown assertion names fail immediately. The report lists `assertions_executed` per case, preventing an apparently rich matrix from becoming documentation-only.

Use synthetic cases for exact contracts: migration, transforms, deterministic bootstrap, valid ranges, required provenance, export completeness, schema rejection, and controlled revision differences.

## Private real-figure regressions

Use `run_private_figure_regressions.py` with an external suite conforming to `figure-regression-suite.schema.yaml`. The suite and its specs/data remain outside the repository. Rendering occurs in a temporary directory that is deleted after the run.

The report may contain only:

- anonymized case ID;
- spec/data/normalized-spec hashes;
- panel IDs;
- PNG dHash and distance;
- aggregate geometry metrics;
- finding names and pass/fail counts.

It must not contain source paths, text extracted from figures, raw rows, image crops, captions, or rendered files.

## Baseline policy

Create a baseline only after human review confirms:

- the spec and plotted values represent the intended evidence;
- labels and terminology match the manuscript;
- final-size geometry is acceptable;
- accessibility and export checks pass;
- no private content is copied into the repository.

Updating a baseline is a reviewed change. A changed dHash is not automatically a regression, and a stable dHash is not proof that numeric values are unchanged. Always pair perceptual comparison with normalized-spec and plotted-data hashes.

## Tolerance policy

- Use exact equality for normalized spec and plotted-data hashes when environment and input are expected to be stable.
- Use dHash Hamming distance for broad visual stability across raster encoder changes.
- Use geometry thresholds for minimum text, minimum line width, canvas containment, and uncertainty clipping.
- Use SVG structural diff for text, colors, and panel IDs during explicit revision audits.
- Do not use exact PDF/PNG byte equality across dependency or platform upgrades.

## Failure triage

1. Source/spec hash changed: treat as an input revision before visual investigation.
2. Plotted-data changed: review data/statistics semantics.
3. Geometry failed: inspect layout, labels, guides, and final size.
4. dHash changed with stable data/spec: inspect style or dependency rendering.
5. Only binary hash changed: compare structural/perceptual metrics before updating anything.

The runner reports observable differences and does not judge whether a scientific conclusion is correct.
