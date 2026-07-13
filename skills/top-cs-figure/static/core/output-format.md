# Output Format

Return these sections for figure creation, revision, export, or audit:

1. `Figure contract`
2. `Generated/updated files`
3. `Caption and manuscript-callout notes`
4. `Visual QA`
5. `Unresolved inputs`

For audit-only tasks, use the same sections and set generated files to `none`. For missing-data tasks, make the unresolved-inputs section concrete enough for the author to supply the data without another clarification round.

For rendered v3 figures, `Generated/updated files` must identify the SVG/PDF/PNG bundle, every panel plotted-data CSV, normalized spec, render manifest, and figure audit when produced. `Visual QA` reports structured findings and target-size verification; do not replace warnings with a generic pass statement.
