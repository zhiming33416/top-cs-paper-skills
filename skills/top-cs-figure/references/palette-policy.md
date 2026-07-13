# Palette Policy

Use semantic slots rather than copying colors from a single paper.

## Slots

- `ours`: proposed method or primary system.
- `baseline`: ordinary comparator.
- `strong_baseline`: strongest or most relevant comparator.
- `ablation`: removed/modified component.
- `secondary`: a second focal family or explicitly declared auxiliary method.
- `positive`: improvement or allowed pass state.
- `negative`: degradation, failure, or risk state.
- `neutral_light` and `neutral_dark`: grids, text, separators, reference marks.

## Rules

- Use one signal family and one accent family per figure unless multiple independent categories are essential.
- Avoid red/green as the only distinction; pair color with marker, hatch, line style, or label.
- Do not color a result as positive or negative unless metric direction and comparison target are supplied.
- Keep method colors stable across panels, captions, and manuscript callouts.
- Venue palettes are starting points from aggregate evidence, not mandated colors.

## Provenance layers

Every resolved palette declares one of three origins.

- `observed_anchor` is a stable hue family found across independent 2026 papers. It is evidence about corpus prevalence, not about semantic meaning.
- `constructed_token` is generated from anchors with controlled OKLab lightness and chroma. It was not copied from a paper and must not be described as directly observed.
- `generic_fallback` is part of the conservative CS semantic system. It is used when venue evidence is unavailable, unstable, inaccessible, or unnecessary.

Do not infer that an observed red means baseline, failure, or statistical significance. Corpus extraction cannot reliably recover author intent. The figure contract and `semantic_roles` establish meaning; evidence only supplies eligible accent families.

## Resolution protocol

1. Select a palette family from the visual task, not the venue name.
2. Read live `style_status`, `anchor_status`, and `profile_status`.
3. Use venue anchors only for `promoted + profile usable`.
4. Construct the requested profile and run contrast, OKLab, grayscale, and CVD checks.
5. If a candidate fails its use-specific threshold, replace or transform it and retain the fallback reason.
6. Record the final role-to-color mapping in the render manifest.

The legacy `palette_status` remains an anchor-availability compatibility field. New code must gate venue-derived profile injection on `profile_status`.

## Use-specific contrast

- Small text: target at least 4.5:1 against its background.
- Thin lines and small markers: target at least 3:1.
- Large fills: target at least 1.5:1 and preserve an outline, label, hatch, or adjacent boundary.

A color may be valid for a bar fill but invalid for text. In particular, saturated orange, green, and red corpus anchors must not be promoted to annotation text without passing the text threshold.

## Multi-series limit

Categorical profiles support two to eight series. More than eight identities require restructuring the figure. Marker, line style, hatch, direct label, and panel grouping remain mandatory when color separation is decision-critical.
