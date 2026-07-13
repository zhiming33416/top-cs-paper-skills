# Figure Failure Gallery

Use this as a diagnostic index. A failure is defined by an observable artifact or contract violation, not by aesthetic preference.

## Contract and evidence failures

### Result-like figure with missing evidence

- Signal: `evidence_status` is planned, missing, or unverified while axes imply measured values.
- Detection: renderer blocks before loading data.
- Correction: supply verified sources or switch to a clearly labeled layout mockup outside the result renderer.

### Claim-panel mismatch

- Signal: the contract claims robustness but panels only report average accuracy.
- Detection: claim IDs and panel jobs do not map to an observable robustness quantity.
- Correction: revise the contract or add the required slice; do not relabel an unrelated metric.

### Untraceable source

- Signal: CSV path exists but expected hash, source ID, or provenance is absent.
- Detection: v3 source registry or audit finding.
- Correction: register source columns and hash; preserve the user-owned preprocessing step separately.

## Statistical failures

### Error bar without definition

- Signal: intervals are drawn but estimator, interval kind, confidence/spread, n, or unit is missing.
- Detection: statistics and caption obligations disagree.
- Correction: declare raw-run aggregation or explicit lower/upper columns and complete the caption.

### Seed count mistaken for sample count

- Signal: `n` mixes tasks, examples, seeds, or repeated measurements.
- Detection: grouping keys and caption unit differ.
- Correction: record the aggregation hierarchy and state the unit represented by `__n`.

### Pseudo-replication

- Signal: correlated observations are treated as independent raw points.
- Detection: paired/cluster ID exists in source but is omitted from statistics.
- Correction: aggregate or pair at the valid experimental unit before plotting.

### Auto-generated significance

- Signal: stars appear without source column, test name, and adjustment.
- Detection: strict significance contract rejection.
- Correction: calculate tests in an audited analysis; pass explicit results into the figure source.

### Incomplete paired plot

- Signal: some subject/seed IDs occur in only one condition.
- Detection: paired renderer checks exactly two declared conditions per pair.
- Correction: resolve missing pairs or declare and justify a paired missing-data policy upstream.

## Scale and encoding failures

### Nonpositive log data

- Signal: zero or negative values on a log axis disappear or distort.
- Detection: scale validation rejects before rendering.
- Correction: use a justified linear/symlog alternative or revise the measured quantity; do not add an arbitrary epsilon.

### Metric direction duplicated in every panel

- Signal: repeated “higher is better” text consumes title space.
- Detection: shared direction set has one value but panel titles repeat it.
- Correction: use one figure-level note and retain units/direction in axis labels or caption.

### Diverging palette without meaningful center

- Signal: two-sided colors imply positive/negative change around an arbitrary midpoint.
- Detection: diverging variant lacks an explicit reference/null meaning.
- Correction: use sequential color or declare the scientific center.

### Color carries identity alone

- Signal: grayscale/CVD views merge methods.
- Detection: semantic registry lacks marker, line style, or hatch redundancy.
- Correction: assign stable non-color channels and reduce the number of simultaneous identities.

### Polar chart on raw incomparable metrics

- Signal: axes have different ranges but form one polygon.
- Detection: polar renderer rejects values outside declared normalized [0,1].
- Correction: normalize with a stated denominator or use aligned small multiples.

## Layout failures

### No panel hierarchy

- Signal: headline result and diagnostic panels receive equal area and title weight.
- Detection: multi-panel spec lacks a meaningful hero panel or weights.
- Correction: assign the primary evidence job more space; keep diagnostics subordinate.

### Legend ownership ambiguity

- Signal: repeated legends differ in order or one shared legend is visually detached.
- Detection: panel legend modes and shared guide conflict.
- Correction: establish one method registry and a dedicated shared guide location.

### Colorbar mismatch

- Signal: panels share one colorbar but use different limits, centers, or units.
- Detection: common `colorbar_group` with incompatible scales.
- Correction: align scales or use separate labeled colorbars.

### Panel label collision

- Signal: label overlaps title, tick labels, or crop boundary.
- Detection: geometry bounding boxes intersect safe areas.
- Correction: reserve a stable label margin and test final-size export, not notebook view.

### Excess whitespace from a sparse panel

- Signal: one panel has few marks but retains an equal grid cell.
- Detection: low content bbox relative to axes bbox and unbalanced mosaic.
- Correction: change weights, span the hero panel, or combine a genuinely related diagnostic.

## Typography and export failures

### Readable on screen, unreadable in print

- Signal: text falls below 6 pt at final millimeter dimensions.
- Detection: render-time geometry and SVG font-size inspection.
- Correction: reduce labels/panels, widen the figure, or redesign the encoding; do not rely on zoom.

### Hairline marks

- Signal: grid, interval, or frontier lines vanish in PDF print or raster preview.
- Detection: positive line width below 0.6 pt.
- Correction: increase linewidth while preserving hierarchy.

### SVG text converted to paths

- Signal: no `<text>` nodes remain, preventing editing and search.
- Detection: XML inspection.
- Correction: configure SVG font handling and re-export; do not claim editability.

### Raster metadata stripped

- Signal: PNG dimensions are adequate but DPI is absent after optimization.
- Detection: metadata check plus effective DPI from pixel width and declared physical width.
- Correction: preserve DPI on production export; for synthetic previews record physical width in provenance.

### Crop touches content

- Signal: labels or marks contact the canvas edge.
- Detection: non-white content bbox touches a PNG edge or axes exceed canvas.
- Correction: adjust constrained layout/margins and render again at target size.

## Qualitative and schematic failures

### Unidentified qualitative crop

- Signal: an image has no stable ID, crop provenance, or aspect ratio.
- Detection: v3 qualitative precondition rejection.
- Correction: add metadata and preserve source linkage; do not silently crop to fit.

### Misleading aspect ratio

- Signal: displayed image is stretched relative to declared source.
- Detection: declared/actual ratio differs by more than tolerance.
- Correction: fit without distortion or document a crop with new ratio.

### Schematic invents a mechanism

- Signal: renderer or author adds undeclared modules, data flow, tensor shape, or terminology.
- Detection: nodes/edges cannot be traced to the explicit spec and terminology ledger.
- Correction: remove the element or add source-backed declaration; layout code may route but not infer.

### Orphan schematic edge

- Signal: edge endpoint references no declared node/port.
- Detection: renderer validation.
- Correction: repair IDs or explicitly add the missing component.

## Revision failures

### Scientific change hidden as styling

- Signal: plotted-data, transform, scale, or statistics hash changes during a “visual cleanup.”
- Detection: revision diff reports normalized-spec or plotted-data changes.
- Correction: separate data/statistical revision from style revision and review the claim impact.

### Visual regression hidden by stable files

- Signal: all expected files exist but labels, colors, or panel IDs changed unexpectedly.
- Detection: SVG structural diff and PNG dHash/pixel-change metrics.
- Correction: inspect the affected panel and update baseline only after intentional review.

### Binary-equality regression test

- Signal: harmless dependency/font metadata changes fail exact file hash tests.
- Detection: binary hash differs while structural/perceptual metrics remain stable.
- Correction: compare normalized spec, plotted data, SVG structure, geometry, and tolerant perceptual hash.
