# Visual QA

Run before final delivery or whenever files are produced.

## Checklist

- SVG exists and text remains editable where possible.
- PDF and PNG preview exist for the same base name.
- TIFF exists when camera-ready or explicitly requested.
- Axes state metric direction, units, and aggregation where needed.
- Legends or direct labels identify all plotted methods and datasets.
- Panel labels are lowercase and consistent with the caption.
- Colors remain interpretable in grayscale or with redundant encodings when categories are decision-critical.
- No chart uses synthetic values without an explicit layout-mockup label.
- Caption and manuscript callout match the evidence shown.
- Source data and script path are reported when available.

Use `scripts/check_figure_bundle.py --base <path-without-extension>` to check the export bundle structure.
