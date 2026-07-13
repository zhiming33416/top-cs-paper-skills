# CS Figure Design Theory

## Design from the evidence task

A panel earns space only when it performs one inspectable job: compare methods, expose variation, show scaling, diagnose errors, locate a tradeoff, or explain declared flow. Start with the reader question, then choose marks and channels. Do not begin from a chart template.

Use this priority order for quantitative channels: common-position, aligned length, unaligned position, area, angle, then color intensity. Reserve area and angle for coarse summaries. Never encode a small performance difference only by bubble area or polar angle.

## Reading order

Arrange panels in claim order, normally main result, mechanism or ablation, robustness, then diagnostic evidence. A hero panel receives more width or height because it carries the main claim, not because it is visually attractive. Subordinate panels should share terminology and method identity without competing for attention.

At final print size, a reader should identify within three seconds:

1. what is compared;
2. which metric and direction matter;
3. which mark represents the focal method;
4. where uncertainty or sample size is disclosed;
5. how panels relate to the caption.

## Redundant identity

Color is one channel, not the identity system. Assign method identity across color, marker, line style, and hatch. Reuse these assignments across panels. Use direct labels for two or three lines when they remain legible; use a shared legend for repeated method sets; use local legends only when a panel has a genuinely different vocabulary.

## Scale integrity

Bar charts represent magnitude from a meaningful zero. Dot and interval charts are preferable when a truncated range is necessary. Log scales require positive values and a caption-level rationale. Normalized compositions must state the denominator. Polar summaries require values already normalized to a common diagnostic range and must not compare raw metrics with different units.

## Density and hierarchy

Do not solve crowding by shrinking type. First reduce duplicate labels, move repeated guides to a shared slot, simplify ticks, split incompatible evidence jobs, or enlarge the figure within the manuscript constraint. Six-point type and 0.6-point strokes are hard floors, not design targets.

Use whitespace to separate evidence groups, not as a decorative border. Keep panel labels in a stable safe area. Give a shared legend dedicated bottom space. Keep colorbars adjacent to the matrices they quantify.

## Annotation discipline

Annotations identify declared events, thresholds, operating points, or externally supplied test results. They do not infer causality. Significance symbols require an explicit source column plus test and adjustment metadata. A visual gap is not a statistical test.

## Corpus style boundary

Venue evidence can adjust accent candidates only when both style and palette status permit it. Layout and palette observations are corpus-calibrated defaults, never official rules or acceptance guidance. Generic semantic encodings remain complete without venue evidence.

## Final-size review

Review the actual PDF dimensions, not an enlarged notebook window. Check visual order, labels, legends, uncertainty, grayscale, color-vision simulations, and caption obligations at the target millimeter size. A technically valid file can still fail as a scientific communication artifact.
