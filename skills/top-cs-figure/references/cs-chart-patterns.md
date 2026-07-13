# CS Chart Patterns

## Benchmark comparison

Use aligned metric axes, consistent method order, and explicit metric direction. Prefer dots with intervals for many datasets, grouped bars for a small fixed set, and heatmaps for method-by-task matrices.

## Ablation

Order ablations by the component removed or added, not by score alone, unless the manuscript claim is ranking. Label the full model and strongest ablation clearly.

## Efficiency

Separate latency, throughput, memory, and accuracy unless the tradeoff is the claim. Include hardware, batch size, sequence length, and operating point in labels or caption when supplied.

## Scaling

Use log scales only when multiplicative changes matter. Mark training data size, model size, compute budget, or context length units explicitly.

## Error analysis

Use small multiples or stacked categories when the reader must inspect failure modes. Preserve class names and dataset labels from the manuscript.

## Method schematic

Use rectangles for modules, cylinders/tables for data stores, and arrows for real flow. Keep component names identical to manuscript terms.
