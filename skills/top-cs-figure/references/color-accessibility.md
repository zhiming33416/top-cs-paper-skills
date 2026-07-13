# Color Accessibility and Failure Diagnosis

Color QA is use-specific. Do not apply one contrast threshold to every mark, and do not treat RGB channel distance as perceptual separation.

## Metrics

- Convert sRGB to linear light before luminance and contrast calculations.
- Use OKLab Euclidean distance for approximate perceptual separation.
- Simulate protan, deutan, and tritan views, then measure the simulated colors in OKLab.
- Check grayscale through relative luminance, not desaturated RGB averages.

These checks are screening tools, not clinical models of vision. Preserve marker, line style, hatch, position, and direct labels even when every numeric threshold passes.

## Failure classes

### Low background contrast

Determine whether the color is used as text, a thin line, a marker, or a large fill. A pale sequential endpoint may be valid inside a bounded heatmap but invalid as text on the page background.

### Categorical collision

If a pair is close in OKLab or under any CVD simulation, retain the higher-priority observed anchor and replace the other with an accessible generic token. Record both the rejected anchor and replacement provenance.

### Non-monotonic ramp

Sequential and ordered profiles must move monotonically in lightness. If interpolation leaves the sRGB gamut and clipping reverses adjacent steps, reduce chroma before changing hue.

### Invalid diverging center

Reject a center that is saturated, lacks a declared reference value, or is paired with asymmetric limits without explanation. A neutral midpoint does not imply that the center is statistically or practically equivalent.

### Semantic conflict

The same method must not change color across panels. `positive` and `negative` colors must not be assigned when metric direction is mixed or unavailable. A venue anchor never establishes semantic meaning by itself.

## Audit output

The render manifest stores profile family, final colors, role mapping, provenance layers, contrast by background, pairwise OKLab distances, CVD distances, and fallback reason. The bundle checker reports only colors used by a panel when evaluating categorical collisions; unused library tokens must not fail a two-series figure.
