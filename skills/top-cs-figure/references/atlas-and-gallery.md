# Atlas and Gallery Index

The committed previews are synthetic routing aids, not templates to copy literally and not evidence of venue policy. Every preview is regenerated through the v3 production renderer. Source CSV/YAML are temporary; the manifest retains their hashes, seed, panel count, visual families, renderer hash, and output hash.

## Choosing an atlas

| Atlas | Use it to compare | Do not infer |
|---|---|---|
| `www-palette-atlas` | WWW-calibrated semantic, categorical, ordered, sequential, diverging, and dark-overlay profiles | official WWW colors or reviewer preference |
| `iclr-palette-atlas` | ICLR-calibrated six-family profile behavior | that constructed ramp tokens were directly observed in papers |
| `icml-palette-atlas` | ICML-calibrated six-family profile behavior | that saturated observed anchors are safe for text or thin lines |
| `comparison-composition` | grouped/dot comparisons, normalized composition, intervals, paired deltas | that bars are preferred by a venue |
| `trend-uncertainty` | line/band, steps, runs, learning curves, change over ordered x | that smoothing is scientifically valid |
| `distribution-interval` | box/violin/strip/ECDF and interval summaries | that distribution summaries replace raw sample disclosure |
| `matrix-heatmap` | sequential/diverging/annotated/confusion matrices | that a colormap establishes significance |
| `scatter-tradeoff` | scatter/bubble/labels, Pareto frontiers, calibration relationships | causal relationships from geometry |
| `ranking-calibration` | critical difference, reliability, intervals, normalized diagnostics | that ranks alone establish practical importance |
| `network-matrix` | topology and adjacency-style evidence | that a layout distance is a measured distance |
| `schematic-layout` | groups, lanes, nodes, ports, routed data flow | undeclared mechanisms or tensor operations |
| `qualitative-image` | image identity, crop/aspect integrity, compact evidence plates | that synthetic images are acceptable paper evidence |
| `cs-systems` | latency/throughput/scaling/composition/system tradeoffs | a universal systems benchmark design |

## Choosing a composite gallery

| Gallery | Evidence sequence |
|---|---|
| `www-benchmark-venue` / `www-calibration-venue` | venue-derived benchmark and calibration defaults with live profile gating |
| `iclr-scaling-venue` / `iclr-network-venue` | venue-derived scaling and graph defaults with redundant identity channels |
| `icml-heatmap-venue` / `icml-schematic-venue` | venue-derived continuous maps and constructed schematic tokens |
| `benchmark-ablation` | headline benchmark, subgroup behavior, ablation, uncertainty, paired effect, robustness |
| `systems-scaling-tradeoff` | scaling curve, throughput/latency frontier, resource composition, tail distribution, interval, topology |
| `calibration-qualitative` | reliability, confidence distribution, subgroup matrix, qualitative IDs, interval, failure slice |
| `graph-robustness` | benchmark, perturbation trend, graph view, matrix, distribution, paired degradation |
| `llm-scaling-efficiency` | learning/scaling, quality-cost frontier, composition, task matrix, intervals, normalized profile |
| `retrieval-online-offline` | offline metric, online trend, frontier, query distribution, paired change, matrix |
| `agent-failure-analysis` | outcome comparison, horizon trend, failure composition, transition network, interval, qualitative case IDs |
| `multimodal-evidence` | aggregate result, modality trend, cross-modal matrix, embedding, qualitative IDs, paired effect |

## Selection protocol

1. Write the claim without naming a chart.
2. Identify the comparison unit, ordering, uncertainty unit, and metric direction.
3. Select the smallest atlas whose grammar answers that claim.
4. Use a gallery only when the figure needs an evidence sequence across multiple panel jobs.
5. Copy the panel jobs and contracts, not coordinates, palette, or synthetic values.
6. Render at final print size and remove any panel that does not change the reader's conclusion or calibration.

Palette atlases exercise the production resolver, not fixed swatch constants. Inspect the corresponding render manifest for normal, grayscale, protan, deutan, and tritan accessibility metrics; a visible preview is diagnostic, while the machine-readable pairwise checks are authoritative.

## Asset boundary

Allowed committed assets are compressed synthetic PNG previews under `assets/chart-atlas` and `assets/gallery`. They must be below 350 KB each and 3 MB total, contain no external images, and have a matching record in `assets/generated-manifest.yaml`.

Never commit:

- paper screenshots or cropped figures;
- downloaded PDFs or extracted page images;
- user data, private results, or resolver caches;
- synthetic CSV/YAML source files generated solely for previews;
- a preview rendered by an alternate one-off code path.

Preview assets are checked by pixel dimensions because PNG optimization may remove DPI metadata. Production bundles still carry explicit DPI metadata and are checked at their declared physical size.
