# Composition Stacked

Use for parts of a declared total. Require category, segment, and nonnegative value columns.

- `stacked` preserves absolute totals.
- `normalized` compares proportions and must state the denominator.
- Keep segment order, hue, and hatch stable across categories.
- Place the most important or most stable segment at the baseline.
- Use aligned small multiples when precise middle-segment comparison matters.

Caption obligations define denominator, omitted categories, and whether totals vary. QA checks nonnegative values, normalized sums, legend completeness, and non-color redundancy.
