# Revision Audit

Use revision audit to explain what changed between two bundles without judging whether the scientific conclusion is correct.

## Compare

- normalized spec hash and migration;
- source and plotted-data hashes;
- transforms and row counts;
- scales, metric direction, and layout;
- estimator, uncertainty, seed, and significance metadata;
- annotations and caption obligations;
- SVG text, colors, and panel IDs;
- PNG dimensions, perceptual/pixel change fraction, and key geometry.

Separate data changes from presentation changes. A changed data hash with unchanged plotted data can indicate an unused source change; changed plotted data with unchanged source requires a transform/statistics explanation. A label change without terminology approval is a manuscript-alignment issue.

The report must state `scientific_claims_compared: false`. Use the diff to locate review work, not to infer that a result improved, regressed, or became significant.
