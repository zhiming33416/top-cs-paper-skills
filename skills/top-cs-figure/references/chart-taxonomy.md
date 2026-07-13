# Chart Taxonomy and Selection

| Evidence question | Family | Preferred variants | Avoid when |
|---|---|---|---|
| Which method is better across tasks? | comparison | grouped bar, dot | values need intervals but bars dominate space |
| What contributes to a total? | composition-stacked | stacked, normalized | readers need precise segment comparison |
| How does a quantity evolve? | trend-scaling | line-band, step, individual runs | x is unordered |
| How variable are runs or cases? | distribution-uncertainty | box, violin, strip, ECDF, histogram | sample size is too small for density claims |
| What is an estimate and interval? | forest-interval | point plus interval | the interval definition is unknown |
| How do paired cases change? | paired-change | slope pairs | pairing IDs are unavailable |
| Where is the operating frontier? | tradeoff-frontier | labeled scatter plus Pareto line | direction of either axis is unclear |
| Are probabilities calibrated? | calibration-reliability | reliability curve plus identity | bins or sample support are absent |
| Which methods rank consistently? | ranking-critical-difference | rank axis with supplied CD | critical difference was not computed externally |
| Which matrix cells matter? | matrix-heatmap | sequential, diverging, annotated, confusion | exact values need easier lookup than color allows |
| What structure exists in an embedding? | embedding-scatter | scatter, labeled, hexbin, bubble | projection uncertainty is hidden |
| How is graph structure organized? | network | node-link | dense topology becomes unreadable |
| What is the declared method flow? | method-schematic | lanes, groups, routed edges | components would need to be inferred |
| What do qualitative cases show? | qualitative-image-plate | fixed-aspect plate | crops or image provenance are missing |
| How do normalized diagnostics compare? | polar-summary | 3-8 normalized axes | raw metrics or precise differences matter |

## Variant rules

- Use dot comparison when zero is not meaningful or intervals are central.
- Use grouped bars for a small category-by-series grid; beyond roughly four series, prefer small multiples or dots.
- Use normalized bars only for composition. Do not normalize benchmark scores merely to make bars equal height.
- Use step lines for discrete state changes and ordinary lines for sampled continuous trends.
- Show individual runs lightly behind an aggregate only when run IDs are available.
- Use ECDF when threshold behavior matters. Use histogram when distribution shape and bin choices can be stated.
- Use violin density only with enough observations and always retain median or raw marks.
- Use diverging heatmaps only around a declared meaningful center.
- Use hexbin for dense unlabeled scatter; do not combine it with categorical point legends.
- Use waterfall only for additive deltas with an explicit baseline and ordered terms.

## Multi-panel recipes

**Benchmark plus ablation:** hero grouped comparison; subordinate trend or ablation dot plot; shared method guide; one metric-direction note.

**Systems scaling plus tradeoff:** hero line-band scaling panel; latency-throughput frontier; resource composition; caption carries hardware and operating-point obligations.

**Calibration plus qualitative evidence:** reliability curve; confidence histogram or interval summary; image plate with stable IDs and crop provenance.

## Refusal cases

Reject rendering when result-like evidence is planned, missing, or unverified. Reject log axes with non-positive data, computed intervals without raw observations, paired charts without complete pairs, polar values outside `[0,1]`, and significance marks without supplied test metadata.
