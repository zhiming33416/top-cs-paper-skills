# Python Workflow

Use Python/matplotlib for all rendering. New executable work uses strict v3 specs; v1/v2 are migration inputs.

## Required setup

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cs_figure_style import apply_cs_figure_style, add_panel_label, save_figure_bundle

apply_cs_figure_style()
```

If importing from the skill directory is inconvenient, copy the small helper functions from `scripts/cs_figure_style.py` into the project plotting script and keep their behavior unchanged.

## Export

- Save SVG first because text should remain editable.
- Save PDF and PNG preview by default.
- Save TIFF only for camera-ready or explicit submission bundles.
- Close figures after saving.

```python
saved = save_figure_bundle(fig, "figures/fig2_results", formats=("svg", "pdf", "png"))
```

## Runtime blockers

If Python or required packages are missing, stop before rendering. Provide the selected-backend script and installation commands, but do not use another plotting backend as a substitute.
