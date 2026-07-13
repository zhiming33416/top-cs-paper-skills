# Distribution and Uncertainty

Use when variation, tails, or threshold behavior matters more than a single estimate. Require group and value columns.

- `box`: median and quartile summary with raw points when feasible.
- `violin`: density shape for adequate sample size; retain median or points.
- `strip`: small samples where every observation matters.
- `histogram`: disclose bins; use step outlines for overlapping groups.
- `ecdf`: compare threshold behavior without arbitrary density smoothing.

Do not label distribution overlap as significance. Caption obligations include observation unit, group n, missing policy, and any bin or density choice. QA checks raw-point visibility and legend identity.
