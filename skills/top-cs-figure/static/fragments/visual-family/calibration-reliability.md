# Calibration Reliability

Use for predicted confidence versus empirical accuracy. Require confidence and accuracy columns on `[0,1]`, plus optional method series.

- Draw the identity line as a reference, not a model.
- Preserve bin order and disclose binning/support outside the renderer.
- Show multiple methods with stable marker and line identity.
- Do not infer ECE, uncertainty, or calibration significance from the curve.
- Keep axes equally bounded so geometric distance from identity is interpretable.

Caption obligations: bin definition, sample support, estimator, and whether points are per-bin or smoothed. QA rejects out-of-range values and missing calibration metadata when required by the contract.
