# Figure QA Contract

QA answers whether the bundle is structurally complete, readable at final size, internally aligned, and reproducible. It does not certify scientific correctness.

## Required checks

1. Required exports exist and are non-empty.
2. SVG parses as XML, has a viewBox, editable text, font declarations, unique IDs, and expected panel labels.
3. PDF has the intended millimeter size and detectable embedded fonts.
4. PNG is nonblank, at least 250 DPI for paper output, and content does not touch the canvas edge.
5. Render geometry keeps axes inside the canvas and text at or above 6 pt.
6. Data lines are at least 0.6 pt and markers remain visible at final size.
7. Shared guides cover the panel vocabulary without duplicate ownership.
8. Expected colors remain distinguishable in grayscale and protan/deutan/tritan simulations, or identity has marker/line/hatch redundancy.
9. Log axes contain no non-positive values.
10. Units, metric direction, panel labels, and caption obligations are present.

## Severity

- **Error:** missing export, invalid XML/signature, blank raster, hash mismatch, clipped panel, illegal scale, missing required evidence metadata.
- **Warning:** weak grayscale/CVD separation, thin marks, crowded labels, uncovered caption obligation, ambiguous legend ownership.
- **Information:** venue style fallback, migration action, optional TIFF omitted.

The CLI returns nonzero when warnings remain because production delivery should not silently pass known defects. Callers may present individual findings but should not rewrite `passed`.

## Geometry limits

Measure at target output size. The SVG/PDF page should match the declared figure dimensions within export tolerance. Prefer layout changes over sub-6-point type. Check panel and legend bounding boxes after a canvas draw; pre-render artist positions are not final geometry.

## Qualitative integrity

Image plates require stable image IDs, source/crop provenance, preserved aspect ratio, and scale bars when physical distance is interpreted. QA must reject a missing image rather than substituting a placeholder.

## Revision QA

Compare normalized specs, source hashes, transforms, scales, statistics, annotations, SVG text/colors/panel IDs, plotted-data hashes, and perceptual raster change. Report changes; do not conclude that a scientific claim improved or regressed.
