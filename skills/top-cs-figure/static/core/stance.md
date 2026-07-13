# Figure Stance

Make the figure defend a manuscript claim. Visual polish is useful only when the evidence, labels, and reading order remain traceable.

- Start from the shared figure brief or a compact figure contract, not from a preferred template.
- Preserve scientific facts from supplied data, manuscript text, code, and figures. Do not invent scores, seeds, confidence intervals, p-values, datasets, hardware, or ablation outcomes.
- Use Python/matplotlib as the only rendering backend. Do not switch to R, Plotly, Altair, browser canvas, or image-generation APIs for previews or fallback outputs.
- Treat a rendered value as the result of a traceable source, allow-listed transform, declared estimator, and captured seed. Never hide computation in arbitrary expressions.
- Prefer sparse, readable panels over dense chart atlases. A CS paper figure should make metric direction, baseline identity, dataset/task grouping, and uncertainty easy to inspect.
- Keep color semantics stable across panels and manuscript text: the proposed method, baselines, datasets, and failure cases should not change colors without reason.
- Treat caption, callout, axis labels, legend, source data, and export files as one artifact. A visually attractive figure with ambiguous evidence status is not ready.
- Treat corpus-derived venue palettes and layout archetypes as confidence-labeled implementation defaults. They are not official policy and do not imply acceptance benefit.
