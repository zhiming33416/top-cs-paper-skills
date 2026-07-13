# Paired Change

Use for two-condition within-case changes. Require pair ID, condition, and value columns.

- Require exactly two declared conditions.
- Connect only complete matched pairs.
- Keep condition order semantically meaningful and stable.
- Use line direction plus marker identity; do not rely on green/red alone.
- Report any excluded incomplete pairs before rendering.

Caption obligations include pair unit, retained n, condition order, and missing-pair policy. QA rejects unmatched aggregate connections, more than two conditions, empty complete-pair sets, and hidden exclusions.
