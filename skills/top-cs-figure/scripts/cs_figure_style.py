#!/usr/bin/env python3
"""Matplotlib style and evidence-aware palette profiles for top-cs-figure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import yaml
from matplotlib.colors import LinearSegmentedColormap

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from top_cs_figure_core.color import (
    adjust_oklab,
    contrast_ratio,
    interpolate_oklab,
    pairwise_accessibility,
    relative_luminance,
    oklab_distance,
    simulate_cvd,
)


PALETTE = {
    "ours": "#2F5DAA", "baseline": "#6F7785", "strong_baseline": "#D07A35",
    "ablation": "#7A68A6", "secondary": "#2D8C82", "positive": "#3B8C4A",
    "negative": "#B84A4A", "neutral_light": "#D8DCE2", "neutral_dark": "#30343B",
}
GENERIC_PALETTE = dict(PALETTE)
GENERIC_CATEGORICAL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#6A3D9A", "#5B6675"]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / "evidence" / "derived"
FIGURE_SIZES_MM = {"single": (89.0, 55.0), "single_tall": (89.0, 75.0), "double": (183.0, 95.0), "double_tall": (183.0, 125.0), "teaser": (183.0, 70.0)}
PROFILE_FAMILIES = {"semantic", "categorical", "ordered", "sequential", "diverging", "dark-overlay"}
_ACTIVE_RESOLUTION: dict[str, object] | None = None


def size_mm(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / 25.4, height_mm / 25.4


def apply_cs_figure_style(font_size: float = 7.0, line_width: float = 0.8) -> None:
    import matplotlib as mpl
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": font_size,
        "axes.spines.right": False, "axes.spines.top": False, "axes.linewidth": line_width,
        "xtick.major.width": line_width, "ytick.major.width": line_width, "legend.frameon": False,
        "figure.dpi": 120, "savefig.dpi": 300,
    })


def load_style_evidence(evidence_dir: str | Path | None = None) -> dict:
    root = Path(evidence_dir) if evidence_dir else DEFAULT_EVIDENCE_DIR
    path = root / "visual-style-rules.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {"rules": {}} if path.is_file() else {"rules": {}}


def venue_style_status(venue: str = "generic", evidence_dir: str | Path | None = None) -> dict[str, object]:
    key = (venue or "generic").lower()
    evidence = load_style_evidence(evidence_dir)
    rule = evidence.get("rules", {}).get(key, {})
    style_status = rule.get("style_status", rule.get("status", "generic" if key == "generic" else "insufficient"))
    anchor_status = rule.get("anchor_status", rule.get("palette_status", "insufficient"))
    profile_status = rule.get("profile_status", rule.get("palette_status", "insufficient"))
    return {
        "venue": key, "evidence_generated": evidence.get("generated"), "status": style_status,
        "eligible_sources": int(rule.get("eligible_sources", 0)), "anchor_status": anchor_status,
        "profile_status": profile_status, "palette_status": rule.get("palette_status", profile_status),
        "palette_fallback_reason": rule.get("palette_fallback_reason"),
        "palette_candidates": list(rule.get("palette_candidates", [])),
        "palette_candidate_support": list(rule.get("palette_candidate_support", [])),
        "palette_profiles": dict(rule.get("palette_profiles", {})), "guidance": rule.get("guidance"),
    }


def _profile_family_for_visual(visual_family: str, variant: str | None = None) -> str:
    if visual_family == "matrix-heatmap":
        return "diverging" if "diverging" in str(variant) else "sequential"
    if visual_family == "qualitative-image-plate":
        return "dark-overlay"
    if visual_family in {"composition-stacked", "embedding-scatter", "network"}:
        return "categorical"
    return "semantic"


def _ordered(anchor: str, count: int, dark_background: bool = False) -> list[str]:
    count = max(2, min(9, count))
    low, high = ((0.48, 0.88) if dark_background else (0.86, 0.43))
    return [adjust_oklab(anchor, low + (high - low) * index / (count - 1), 0.35 + 0.65 * index / (count - 1)) for index in range(count)]


def _categorical(anchors: list[str], count: int, background: str) -> tuple[list[str], list[dict[str, object]]]:
    count = max(2, min(8, count))
    colors: list[str] = []
    provenance: list[dict[str, object]] = []
    for color in anchors + GENERIC_CATEGORICAL:
        if color.upper() in {item.upper() for item in colors}:
            continue
        if contrast_ratio(color, background) < 1.5:
            continue
        if any(oklab_distance(color, existing) < 0.08 or min(oklab_distance(simulate_cvd(color, mode), simulate_cvd(existing, mode)) for mode in ("protan", "deutan", "tritan")) < 0.05 for existing in colors):
            continue
        colors.append(color)
        provenance.append({"hex": color, "source": "observed_anchor" if color in anchors else "generic_fallback"})
        if len(colors) >= count:
            break
    return colors, provenance


def resolve_palette_profile(
    venue: str = "generic", family: str = "semantic", series_count: int = 6,
    background: str = "#FFFFFF", evidence_dir: str | Path | None = None,
    mode: str = "venue-derived", emphasis_role: str = "ours", custom_colors: Sequence[str] | None = None,
) -> dict[str, object]:
    family = family.lower()
    if family not in PROFILE_FAMILIES:
        raise ValueError(f"unsupported palette profile family: {family}")
    if mode not in {"generic", "venue-derived", "custom"}:
        raise ValueError(f"unsupported palette profile mode: {mode}")
    status = venue_style_status(venue, evidence_dir)
    venue_ready = status["status"] == "promoted" and status["profile_status"] == "usable"
    anchors = list(status["palette_candidates"]) if mode == "venue-derived" and venue_ready else []
    fallback_reason = None
    if mode == "venue-derived" and not venue_ready:
        fallback_reason = status.get("palette_fallback_reason") or "venue-profile-not-usable"
    if mode == "generic":
        fallback_reason = "generic-requested"
    constructed: list[dict[str, object]] = []
    semantic = dict(GENERIC_PALETTE)
    observed = [{"hex": color, "source": "observed_anchor", "venue": venue} for color in anchors]
    if mode == "custom":
        anchors = [str(color).upper() for color in custom_colors or []]
        if len(anchors) < 2:
            raise ValueError("custom palette profile requires at least two colors")
        custom_accessibility = pairwise_accessibility(anchors, background)
        if any(ratio < 1.5 for ratio in custom_accessibility["contrast"].values()):
            raise ValueError("custom palette contains colors with insufficient contrast for large fills")
        if any(pair["oklab_distance"] < 0.08 or min(pair["cvd_distance"].values()) < 0.05 for pair in custom_accessibility["pairs"]):
            raise ValueError("custom palette contains colors that are not sufficiently distinguishable")
        observed = []
        fallback_reason = None
    for role, color in zip(("ours", "strong_baseline", "ablation", "secondary"), anchors):
        semantic[role] = color
    if family == "semantic":
        roles = [emphasis_role, "strong_baseline", "baseline", "ablation", "secondary", "positive", "negative"]
        colors = list(dict.fromkeys(semantic.get(role, semantic["ours"]) for role in roles))
        token_provenance = [{"hex": color, "source": "observed_anchor" if color in anchors else "generic_fallback"} for color in colors]
    elif family == "categorical":
        colors, token_provenance = _categorical(anchors, series_count, background)
    elif family in {"ordered", "sequential"}:
        base = anchors[0] if anchors else semantic["ours"]
        colors = _ordered(base, series_count if family == "ordered" else max(5, series_count), background != "#FFFFFF")
        constructed = [{"hex": color, "source": "constructed_token", "from": base, "operation": "oklab-lightness-ramp"} for color in colors]
        token_provenance = constructed
    elif family == "diverging":
        left = anchors[1] if len(anchors) > 1 else semantic["negative"]
        right = anchors[2] if len(anchors) > 2 else semantic["ours"]
        count = max(7, min(9, series_count))
        center = "#C8CCD3" if background == "#FFFFFF" else "#515761"
        half = count // 2
        colors = [interpolate_oklab(left, center, index / half) for index in range(half)] + [center] + [interpolate_oklab(center, right, index / half) for index in range(1, half + 1)]
        constructed = [{"hex": color, "source": "constructed_token", "from": [left, right], "operation": "oklab-diverging-ramp"} for color in colors]
        token_provenance = constructed
    else:
        bases = anchors or GENERIC_CATEGORICAL[:4]
        colors = [adjust_oklab(color, max(0.72, relative_luminance(color) ** 0.5), 0.9) for color in bases[:max(3, min(6, series_count))]]
        if "#FFFFFF" not in colors:
            colors.append("#FFFFFF")
        constructed = [{"hex": color, "source": "constructed_token", "from": bases, "operation": "dark-overlay-lift"} for color in colors]
        token_provenance = constructed
    if family in {"categorical", "ordered", "dark-overlay"}:
        for role, color in zip(("ours", "strong_baseline", "baseline", "ablation", "secondary", "positive", "negative"), colors):
            semantic[role] = color
    accessibility = pairwise_accessibility(colors, background)
    contrast = accessibility["contrast"]
    thresholds = {"text": 4.5, "thin_line": 3.0, "large_fill": 1.5}
    accessibility["thresholds"] = thresholds
    accessibility["violations"] = {
        use: [color for color, ratio in contrast.items() if ratio < minimum]
        for use, minimum in thresholds.items()
    }
    if mode == "custom":
        if accessibility["violations"]["large_fill"]:
            raise ValueError("custom palette contains colors with insufficient contrast for large fills")
        if any(pair["oklab_distance"] < 0.08 or min(pair["cvd_distance"].values()) < 0.05 for pair in accessibility["pairs"]):
            raise ValueError("custom palette contains colors that are not sufficiently distinguishable")
    return {
        "venue": venue, "family": family, "mode": mode, "series_count": series_count,
        "background": background, "colors": colors, "semantic_roles": semantic,
        "observed_anchors": observed, "constructed_tokens": constructed,
        "token_provenance": token_provenance, "evidence_support": status,
        "accessibility": accessibility, "fallback_reason": fallback_reason,
    }


def set_palette_context(venue: str, visual_family: str, variant: str | None = None, profile: Mapping[str, object] | None = None, evidence_dir: str | Path | None = None) -> dict[str, object]:
    global _ACTIVE_RESOLUTION
    profile = dict(profile or {})
    family = str(profile.get("family") or _profile_family_for_visual(visual_family, variant))
    _ACTIVE_RESOLUTION = resolve_palette_profile(
        venue=venue, family=family, series_count=int(profile.get("series_count", 6)),
        background=str(profile.get("background", "#FFFFFF")), evidence_dir=evidence_dir,
        mode=str(profile.get("mode", "venue-derived")), emphasis_role=str(profile.get("emphasis_role", "ours")),
        custom_colors=profile.get("colors") if isinstance(profile.get("colors"), list) else None,
    )
    return _ACTIVE_RESOLUTION


def active_palette_resolution() -> dict[str, object]:
    return dict(_ACTIVE_RESOLUTION or resolve_palette_profile("generic", "semantic", mode="generic"))


def palette_for(venue: str = "generic", evidence_dir: str | Path | None = None) -> dict[str, str]:
    if _ACTIVE_RESOLUTION and _ACTIVE_RESOLUTION.get("venue") == venue:
        return dict(_ACTIVE_RESOLUTION["semantic_roles"])  # type: ignore[arg-type]
    return dict(resolve_palette_profile(venue, "semantic", evidence_dir=evidence_dir)["semantic_roles"])  # type: ignore[arg-type]


def colormap_for(venue: str, family: str, variant: str | None = None, profile: Mapping[str, object] | None = None) -> LinearSegmentedColormap:
    desired_family = str((profile or {}).get("family") or _profile_family_for_visual(family, variant))
    resolution = _ACTIVE_RESOLUTION if _ACTIVE_RESOLUTION and _ACTIVE_RESOLUTION.get("venue") == venue and _ACTIVE_RESOLUTION.get("family") == desired_family else set_palette_context(venue, family, variant, profile)
    return LinearSegmentedColormap.from_list(f"top_cs_{venue}_{resolution['family']}", resolution["colors"])  # type: ignore[arg-type]


def apply_venue_style(venue: str = "generic", visual_family: str = "comparison", font_size: float | None = None, palette_profile: Mapping[str, object] | None = None, variant: str | None = None) -> dict[str, str]:
    base_font = font_size if font_size is not None else 6.8 if visual_family in {"matrix-heatmap", "network"} else 7.2
    apply_cs_figure_style(font_size=base_font, line_width=0.75)
    set_palette_context(venue, visual_family, variant, palette_profile)
    return palette_for(venue)


def semantic_color_sequence(venue: str = "generic", roles: Sequence[str] | None = None) -> list[str]:
    roles = roles or ("ours", "strong_baseline", "baseline", "ablation", "positive", "negative")
    palette = palette_for(venue)
    return [palette.get(role, palette["baseline"]) for role in roles]


def semantic_style_registry(venue: str = "generic", names: Sequence[str] | None = None, role_map: Mapping[str, str] | None = None) -> dict[str, dict[str, object]]:
    names, role_map = names or ("ours", "strong_baseline", "baseline", "ablation"), role_map or {}
    roles = ("ours", "strong_baseline", "baseline", "ablation", "secondary", "positive", "negative")
    palette = palette_for(venue)
    markers, linestyles, hatches = ("o", "s", "^", "D", "P", "X", "v", "<"), ("-", "--", "-.", ":", (0, (5, 2)), (0, (1, 1)), (0, (3, 1, 1, 1))), ("", "//", "..", "xx", "++", "\\\\", "oo")
    registry = {}
    for index, name in enumerate(names):
        lowered = str(name).lower().strip()
        inferred = {"ours": "ours", "our": "ours", "proposed": "ours", "baseline": "baseline", "strong baseline": "strong_baseline", "ablation": "ablation"}.get(lowered)
        if inferred is None and lowered.startswith(("base", "reference", "control")):
            inferred = "baseline"
        if inferred is None and lowered.startswith(("ours", "proposed", "top-cs")):
            inferred = "ours"
        stable = int(hashlib.sha256(str(name).encode("utf-8")).hexdigest()[:8], 16) % len(roles)
        role = role_map.get(name, inferred or roles[stable]); slot = roles.index(role) if role in roles else index % len(roles)
        registry[str(name)] = {"role": role, "color": palette.get(role, palette["baseline"]), "marker": markers[slot], "linestyle": linestyles[slot], "hatch": hatches[slot], "alpha": 1.0 if role in {"ours", "strong_baseline"} else 0.88}
    return registry


def figure_size(name: str = "single") -> tuple[float, float]:
    return size_mm(*FIGURE_SIZES_MM.get(name, FIGURE_SIZES_MM["single"]))


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    from top_cs_figure_core.color import hex_to_rgb as convert
    return convert(hex_color)


def validate_palette_contrast(palette: Mapping[str, str] | None = None, background: str = "#FFFFFF", minimum: float = 2.0) -> list[str]:
    return [role for role, color in (palette or PALETTE).items() if contrast_ratio(color, background) < minimum]


def add_panel_label(ax, label: str, x: float = -0.08, y: float = 1.04, fontsize: float = 8.0, weight: str = "bold", color: str = "black"):
    return ax.text(x, y, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=fontsize, fontweight=weight, color=color)


def direct_label(ax, x: float, y: float, text: str, color: str = "black", **kwargs):
    defaults = {"ha": "left", "va": "center", "fontsize": 7}; defaults.update(kwargs)
    return ax.text(x, y, text, color=color, **defaults)


def save_figure_bundle(fig, base_path: str | Path, formats: Sequence[str] = ("svg", "pdf", "png"), dpi: int = 300, close: bool = True) -> list[str]:
    base = Path(base_path); base.parent.mkdir(parents=True, exist_ok=True); base = base.with_suffix("") if base.suffix else base
    saved = []
    for fmt in formats:
        out = base.with_suffix("." + fmt.lower().lstrip(".")); kwargs = {"dpi": dpi} if fmt.lower() in {"png", "tif", "tiff", "jpg", "jpeg"} else {}
        fig.savefig(out, **kwargs); saved.append(str(out))
    if close:
        import matplotlib.pyplot as plt
        plt.close(fig)
    return saved


def require_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    available = {column.strip() for column in columns}
    return [column for column in required if column not in available]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-palette", action="store_true")
    parser.add_argument("--venue", default="generic")
    parser.add_argument("--family", choices=sorted(PROFILE_FAMILIES), default="semantic")
    parser.add_argument("--series-count", type=int, default=6)
    args = parser.parse_args()
    if args.print_palette:
        print(json.dumps(resolve_palette_profile(args.venue, args.family, args.series_count), indent=2))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
