# Data and Statistics Contract

## Source registry

Each v3 source declares `id`, `path`, `format`, `expected_sha256`, and `columns`. CSV is the supported tabular format. A panel refers to `source_id`; paths are not silently searched. Hash mismatch stops rendering.

## Transform DAG

Transforms execute in order and form a linear, auditable DAG. Allowed operations are:

- `filter`: equality or membership only;
- `sort`: stable ordering by one declared column;
- `group`: deterministic row grouping order;
- `aggregate`: mean, median, min, max, sum, or count;
- `normalize`: min-max or sample z-score;
- `baseline-delta`: row-wise declared-column subtraction;
- `rank`: higher- or lower-is-better ordinal rank.

No Python expression, callback, import, query language, or arbitrary function is accepted. Every step records input and output row counts.

Declare categorical axes explicitly as `type: categorical`; the renderer preserves fixed labels and does not replace them with numeric locators. Linear, log, and symlog scales apply only to quantitative axes.

## Raw-run aggregation

Map observations through `encodings.raw_y`. Grouping is derived from declared x and series/group encodings. Declare estimator, uncertainty, missing policy, and seed. The plotted-data output contains the estimate, interval columns when applicable, and `__n`.

Supported estimators are mean and median. Supported computed uncertainty is SD, SE, or percentile bootstrap CI. The default bootstrap uses 2,000 resamples and a deterministic local random generator. Record confidence, sample count, seed, estimator, observations, and missing policy.

## Pairing

Paired displays require an explicit pair column and two complete conditions. Dropping incomplete pairs must be an author-declared preprocessing decision, not an implicit renderer behavior. Report the retained pair count.

## Significance boundary

The system does not calculate p-values. A significance annotation can consume only an explicit source column and must declare test name and multiplicity adjustment. Missing values, unknown tests, or inferred stars are errors.

## Missing values

`reject` is the default. `drop` is permitted only for raw observations and is recorded. Never convert missing values to zero. Empty post-transform data is an error.

## Caption obligations

When statistics are shown, the caption must identify estimator, interval type and confidence when relevant, sample unit/count, aggregation unit, and paired basis. Systems results also need hardware and operating conditions when they affect interpretation.
