# Palette Profiles

Use `resolve_palette_profile()` rather than selecting individual hex values. A profile resolves colors, semantic roles, observed anchors, constructed tokens, evidence support, accessibility metrics, and a fallback reason.

## Selection table

| Family | Use | Required checks |
|---|---|---|
| `semantic` | proposed method, baselines, ablations, signed states | stable role mapping and non-color redundancy |
| `categorical` | two to eight unordered methods, groups, or datasets | pairwise OKLab/CVD separation |
| `ordered` | model size, data fraction, severity, or other declared order | monotonic lightness and stated direction |
| `sequential` | nonnegative magnitude in matrices or density fields | monotonic lightness and one numeric colorbar |
| `diverging` | signed deviation around a meaningful center | declared center, symmetric limits, neutral midpoint |
| `dark-overlay` | masks, channels, boxes, or trajectories over dark images | contrast on the actual dark background |

## Interface

```python
profile = resolve_palette_profile(
    venue="icml",
    family="categorical",
    series_count=5,
    background="#FFFFFF",
    mode="venue-derived",
    emphasis_role="ours",
)
```

The v3 render spec accepts the same fields under `style.palette_profile`. A panel may override them with `panel.palette_profile` when a composite uses different visual tasks, such as categorical lines plus a diverging heatmap.

## Semantic profile

Declare method roles explicitly whenever names do not identify them. `ours`, `baseline`, `strong_baseline`, `ablation`, and `secondary` describe identity, while `positive` and `negative` require metric direction and a comparison target. Never use signed colors as an implicit significance test.

## Categorical profile

Observed anchors are admitted only when they remain distinguishable from colors already selected. Rejected anchors remain in provenance but are replaced by generic accessible tokens. This is expected behavior: evidence prevalence does not override accessibility.

Use direct labels for two or three stable curves. For four to eight series, preserve marker and line-style identity. Do not create a ninth hue to avoid redesigning an overloaded panel.

## Ordered and sequential profiles

Both use OKLab construction from the primary eligible anchor. Ordered profiles identify discrete levels and may use markers; sequential profiles encode a continuous magnitude and require a colorbar. Do not use an ordered ramp for unrelated methods.

## Diverging profile

The center must have scientific meaning: zero delta, parity, chance-adjusted neutrality, or another declared reference. The resolver builds a light neutral midpoint and two anchor-derived wings. The renderer must use symmetric limits around the center unless the caption explicitly justifies another normalization.

## Dark overlay profile

Set the real background color. Dark-overlay colors are lightness-adjusted constructed tokens, not observed dark-theme venue colors. Keep image pixels intact; palette construction applies only to annotations and overlays.

## Custom profile

`mode: custom` requires two to eight explicit colors. Custom colors pass the same fill contrast and pairwise OKLab/CVD checks. A rejected custom palette is an input error, not permission to disable QA.
