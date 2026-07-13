# Figure Workflow

1. **Intake:** Identify the supplied artifacts: figure brief, manuscript passage, CSV/TSV/JSON/XLSX, plotting script, existing SVG/PDF/PNG, and caption/callout.
2. **Contract:** Lock claim, research question, visual family, panel jobs, metric direction, comparison groups, uncertainty definition, data status, final dimensions, and required exports.
3. **Data boundary:** If data are partial, planned, missing, or unverified, do not render result-like values. Produce missing-inputs or a layout mockup with synthetic values explicitly labeled as non-results.
4. **Design:** Choose the minimum panel set that makes the claim inspectable. Remove panels that do not add a distinct evidence job.
5. **Style evidence:** If a venue is named, inspect the venue-style fragment and load corpus visual evidence when style confidence matters. Do not present preliminary or gap status as official venue style.
6. **Code:** Use `scripts/cs_figure_style.py` helpers or equivalent rcParams. Set editable SVG text before creating figures.
7. **Data execution:** Resolve the v3 source registry, verify declared hashes, apply only allow-listed transforms, and compute declared descriptive statistics. Save the exact plotted rows for every panel.
8. **Composition:** Assign hero/subordinate weights, shared guides, safe panel labels, and one figure-level metric-direction note before rendering.
9. **Render:** Save SVG, PDF, and PNG by default, plus normalized spec and render manifest. Add TIFF for camera-ready or explicit submission bundles.
10. **Align:** Check caption, manuscript callout, panel labels, terminology, units, estimator, interval, sample count, and evidence status against the contract.
11. **QA:** Parse outputs and render geometry. Check editable text, font/line thresholds, crop, DPI, shared guides, grayscale/CVD distinction, log validity, and caption obligations.
12. **Audit:** Record source/spec/style/plotted-data hashes and optional revision differences without judging scientific truth.
13. **Report:** Return generated files, caption/callout notes, QA status, and unresolved inputs. State anything not rendered or verified.
