# Rendering API

## Command line

```powershell
python scripts/render_from_figure_spec.py --spec figure.yaml --outdir output
python scripts/check_figure_bundle.py --base output/figure --format json
python scripts/audit_figure_spec.py --spec figure.yaml --base output/figure
```

The renderer accepts v1/v2 inputs through `normalize_spec` and records every migration action. New work should use `spec_version: 3`.

## Internal modules

- `top_cs_figure_core.spec`: strict field validation, migration, source registry resolution.
- `top_cs_figure_core.data`: allow-listed row transforms without expression evaluation.
- `top_cs_figure_core.statistics`: estimators, SD/SE, deterministic percentile bootstrap.
- `top_cs_figure_core.layout`: mosaic/GridSpec axes, scales, annotations, and tick density.
- `top_cs_figure_core.renderers`: one validated-row renderer per visual family.
- `top_cs_figure_core.geometry`: render-time text, line, marker, overlap, canvas, and interval checks.
- `top_cs_figure_core.provenance`: file hashes, plotted-data CSV, schematic geometry, and internal-field cleanup.
- `render_from_figure_spec.py`: orchestration, source resolution, shared guides, export, and manifest assembly.
- `cs_figure_style.py`: semantic identity, target sizes, corpus overlay, export.
- `check_figure_bundle.py`: structural and visual-output QA.
- `audit_figure_spec.py`: hashes, provenance, unresolved inputs, revision diff.

## Render lifecycle

1. Parse YAML and validate/migrate.
2. Resolve each `source_id` relative to the spec.
3. Verify `expected_sha256` when supplied.
4. Load CSV and apply transforms in listed order.
5. Compute declared descriptive statistics from `raw_y` when requested.
6. Validate required columns and scale constraints.
7. Render panels into mosaic or grid axes.
8. Collect shared legends/colorbars and one metric-direction note.
9. Draw the canvas and capture geometry.
10. Export bundle and write provenance files.

## Stable outputs

For output base `figure`, the default production bundle is:

- `figure.svg`, `figure.pdf`, `figure.png`;
- `figure.<panel>.plotted-data.csv` for each data panel;
- `figure.normalized-spec.yaml`;
- `figure.render.json`;
- `figure.figure-audit.json` after audit.

TIFF is opt-in through `export_formats`. SVG preserves text. PDF uses TrueType font embedding. PNG defaults to 300 DPI.

## Extension rule

Add a visual family only when it has a column contract, a renderer, a fragment, a synthetic fixture, a rejection case, and QA expectations. Keep data computation outside the drawing function. A renderer consumes validated plotted rows; it must not fetch data or infer statistics.

## Boundary contracts

### Spec layer

The spec layer owns syntax, migration, and reference integrity. It must reject unknown fields before any source is opened. Migration may add defaults and resolve source IDs, but it must never alter values, infer a metric direction, or silently change a chart family.

Stable responsibilities:

- validate top-level, source, panel, transform, statistics, scale, annotation, and schematic objects;
- require unique source and panel IDs;
- resolve each v3 `source_id` to exactly one registry entry;
- record input and normalized spec versions plus migration actions;
- keep `_`-prefixed implementation fields out of normalized output.

### Data layer

The data layer accepts rows and an ordered transform list. It returns new rows and a transform report containing input/output counts. Transforms are pure with respect to files and process state. The allow-list is deliberately small: filter, sort, group, aggregate, normalize, baseline-delta, and rank.

Do not add expression strings, `eval`, callbacks, imports, SQL, or arbitrary Python. A transform requiring domain logic belongs in a user-owned preprocessing script whose output is then hashed as a source.

### Statistics layer

The statistics layer operates only when `raw_y` is declared. It groups by the encoded x and series/group columns, applies the declared estimator, and emits estimate, `__n`, and optional bounds. It records estimator, uncertainty kind, confidence, bootstrap samples, seed, observation count, and missing policy.

It does not calculate p-values. Significance is accepted only as an explicit source column with a named test and adjustment method.

### Renderer layer

A renderer receives an axes object, plotted rows, a validated panel, and venue style context. It may create Matplotlib artists and return a mappable for a colorbar. It must not:

- read files or network resources, except the image-plate renderer resolving declared image paths;
- aggregate or normalize scientific values unless the visual family defines a display-only denominator, such as normalized composition;
- choose a favorable baseline or frontier direction;
- invent labels, intervals, significance, mechanism nodes, or method terminology;
- save files or modify global random state.

### Layout layer

Layout creates stable axes from panel IDs. A mosaic string is an interface: changing characters changes panel identity and must appear in revision audit. Hero weighting affects space, not evidence rank. Shared legends and colorbars are figure-level guides and should not be reconstructed independently in each renderer.

### QA and provenance layers

Geometry is captured after a canvas draw and before export. Provenance is written after all exports succeed. A partially exported bundle is a failure, not a successful result with warnings.

## Renderer dispatch contract

Each visual family has four connected declarations:

1. manifest route and static fragment;
2. schema/spec validator family and variant set;
3. required-column mapping in the orchestrator;
4. renderer dispatch function.

If any declaration is absent, the family is incomplete. Tests must exercise every variant with a valid fixture and at least one family-specific rejection.

Renderer return values:

- ordinary plots: `None`;
- heatmaps or other scalar mappables: the mappable used for local/shared colorbar;
- renderers must not return transformed data; plotted rows are finalized before drawing.

## Source and path behavior

- Relative spec paths resolve against the spec directory.
- Relative output bases resolve against the spec directory unless `--outdir` is supplied.
- v3 source hashes are checked before transforms.
- Image paths inside a qualitative CSV resolve against the spec directory.
- Output directories may be created; source directories are read-only from the renderer's perspective.

The render manifest records absolute working paths for local reproducibility. Public or private regression reports must remove paths and retain only hashes and aggregate metrics.

## Failure behavior

Use `ValueError` for invalid contracts, data, statistics, scales, or rendering preconditions. Use `KeyError` only for a required declared column that unexpectedly disappears after validation. CLI failures return nonzero and must not claim a complete bundle.

Reject before drawing when possible:

- blocking evidence status;
- unknown spec fields or variants;
- missing source IDs, files, hashes, or columns;
- invalid log-domain values;
- uncertainty without raw runs or explicit precomputed bounds;
- incomplete paired observations;
- non-normalized polar values;
- qualitative records missing identity, crop provenance, or aspect ratio.

## Reproducibility invariants

For identical spec bytes, source bytes, dependency versions, and seed:

- plotted-data values and hashes must be identical;
- normalized spec must be identical;
- panel IDs, semantic identity mapping, layout dimensions, and export set must be identical;
- SVG structure and PNG perceptual hash should remain within the declared regression tolerance.

Byte-identical PDF/PNG output is not guaranteed across Matplotlib, Pillow, FreeType, or platform versions. Use structural and perceptual regression metrics rather than exact binary equality.

## Adding a variant

1. Add the variant to `VARIANTS` and the shared schema.
2. State its required encodings and forbidden uses in the family fragment.
3. Implement the variant inside the existing family renderer.
4. Add a compact synthetic source with edge cases, not only a visually easy example.
5. Add numeric assertions for any display transform.
6. Add geometry and accessibility assertions at final print size.
7. Add it to one atlas; regenerate assets and update provenance hashes.
8. Run the full matrix and private regression suite where available.

## Palette resolver

Call `resolve_palette_profile(venue, family, series_count, background, evidence_dir)` rather than selecting hex values or matplotlib colormap names inside a renderer. Supported families are `semantic`, `categorical`, `ordered`, `sequential`, `diverging`, and `dark-overlay`.

The resolver returns colors, semantic roles, observed anchors, constructed tokens, evidence support, pairwise accessibility, and a fallback reason. Venue-derived mode is allowed only when `style_status` is `promoted` and `profile_status` is `usable`. `anchor_status` alone is insufficient because isolated colors do not establish a stable palette relationship.

Use the resolved result by task:

- method comparisons use `semantic` and preserve marker/line/hatch identity;
- unrelated labels use `categorical`, with non-color redundancy above eight series;
- scale or intensity levels use `ordered`;
- magnitude heatmaps use `sequential`;
- signed differences use `diverging` with a neutral center;
- marks over dark qualitative media use `dark-overlay`.

Custom mode passes through the same linear-sRGB contrast, OKLab distance, grayscale ordering, and CVD simulation checks. The render manifest must retain the final colors and their provenance tier so a revision audit can distinguish evidence changes from data or spec changes.

## Adding a visual family

Create a new family only when an existing family plus variant cannot express the evidence question. Besides the extension rule above, define:

- the scientific question the family answers;
- required and optional encodings;
- allowed metric directions and scale types;
- legend/colorbar behavior;
- caption obligations;
- uncertainty and missing-data behavior;
- accessibility redundancy;
- at least one misuse that must be rejected.

Do not add a family solely to match a visual appearance. Families encode evidence grammar, not decorative style.
