# Figure Archetypes and CS Recipes

Choose an archetype before panel code.

- `quantitative-grid`: aligned comparisons, ablations, distributions, and one shared legend.
- `hero-plus-diagnostics`: a frontier, scaling, or calibration claim in the hero panel, with diagnostics that answer distinct risks.
- `method-plus-evidence`: an explicit schematic followed by panels that validate separate stages or claims.
- `qualitative-plus-quantitative`: user-supplied examples paired with a metric panel; the image plate cannot be the only support for a quantitative claim.

Use a panel only when removing it would remove a distinct evidence step. Prefer shared encodings and one stable method-role map across panels.

## Reusable CS composite recipes

Use these as panel-job patterns, not templates or sources of synthetic result values.

### Benchmark → ablation → robustness

Use a comparison hero panel for the headline task result, a compact ablation panel for the causal contribution of declared components, and a trend, interval, or paired-change panel for robustness. Keep the task grouping and method-role mapping identical across panels. State uncertainty units and any excluded runs.

### Systems scaling → quality-cost frontier → resource diagnosis

Use a scaling or trend hero panel for throughput, latency, or quality over a declared scale. Pair it with a frontier panel only when both axes are measured from supplied data, then add a composition, distribution, or tail-latency diagnostic that explains the operating point. Do not imply that a visual frontier establishes a deployment recommendation without the stated constraints.

### Offline retrieval → online outcome → failure slices

Use one offline comparison, one ordered online trend, and one failure composition, matrix, or paired-change panel. Keep query, task, and time-window definitions explicit. A qualitative case may illustrate the failure slice only when every image or example has an identity and provenance record.

### Method schematic → controlled validation

Use a schematic hero panel only to show supplied modules, data flow, and declared assumptions. Follow it with a comparison or interval panel that validates the central mechanism, plus an ablation or calibration panel that addresses the most likely alternative explanation. Never add nodes, arrows, or claimed mechanisms that are absent from the manuscript or user-provided materials.
