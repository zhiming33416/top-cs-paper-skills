from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

from cs_figure_style import colormap_for, palette_for, semantic_color_sequence, semantic_style_registry
from top_cs_figure_core.color import adjust_oklab
from .numeric import as_float

def colors_for(panel: dict[str, Any], venue: str, names: Iterable[str]) -> dict[str, str]:
    registry = styles_for(panel, venue, names)
    return {name: str(style["color"]) for name, style in registry.items()}


def styles_for(panel: dict[str, Any], venue: str, names: Iterable[str]) -> dict[str, dict[str, object]]:
    ordered = [str(name) for name in names]
    return semantic_style_registry(venue, ordered, panel.get("semantic_roles") or {})


def uncertainty_values(row: dict[str, str], y_value: float, enc: dict[str, str]) -> tuple[float, float] | None:
    if enc.get("error"):
        error = as_float(row[enc["error"]])
        return error, error
    if enc.get("lower") and enc.get("upper"):
        lower = as_float(row[enc["lower"]])
        upper = as_float(row[enc["upper"]])
        return max(0.0, y_value - lower), max(0.0, upper - y_value)
    return None


def render_comparison(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    x_key, y_key = enc["x"], enc["y"]
    series_key = enc.get("series") or enc.get("group")
    categories = list(dict.fromkeys(row[x_key] for row in rows))
    series = list(dict.fromkeys(row[series_key] for row in rows)) if series_key else ["value"]
    color_map = colors_for(panel, venue, series)
    style_map = styles_for(panel, venue, series)
    variant = panel.get("variant", "grouped-bar")
    if variant == "dot":
        for index, name in enumerate(series):
            selected = [row for row in rows if row.get(series_key, "value") == name]
            xs = [categories.index(row[x_key]) + (index - (len(series) - 1) / 2) * 0.12 for row in selected]
            ys = [as_float(row[y_key]) for row in selected]
            ax.scatter(xs, ys, color=color_map[name], label=name if series_key else None, s=24, marker=style_map[name]["marker"], alpha=style_map[name]["alpha"])
            errors = [uncertainty_values(row, value, enc) for row, value in zip(selected, ys)]
            if any(errors):
                ax.errorbar(xs, ys, yerr=[[item[0] if item else 0 for item in errors], [item[1] if item else 0 for item in errors]], fmt="none", ecolor=color_map[name], linewidth=0.7, capsize=2)
        ax.set_xticks(range(len(categories)), categories)
        ax.set_ylabel(enc.get("ylabel", y_key))
        return
    if variant == "waterfall":
        values = [as_float(row[y_key]) for row in rows]
        starts, total = [], 0.0
        for value in values:
            starts.append(total if value >= 0 else total + value)
            total += value
        colors = [semantic_color_sequence(venue)[4 if value >= 0 else 5] for value in values]
        ax.bar(range(len(values)), [abs(value) for value in values], bottom=starts, color=colors, edgecolor="#30343B", linewidth=0.6)
        ax.axhline(0, color="#30343B", linewidth=0.6)
        ax.set_xticks(range(len(categories)), categories, rotation=20, ha="right")
        ax.set_ylabel(enc.get("ylabel", y_key))
        return
    if variant in {"stacked-bar", "normalized-bar"}:
        bottoms = [0.0] * len(categories)
        totals = [sum(as_float(row[y_key]) for row in rows if row[x_key] == category) for category in categories]
        for index, name in enumerate(series):
            selected = {row[x_key]: row for row in rows if row.get(series_key, "value") == name}
            values = [as_float(selected[category][y_key]) if category in selected else 0.0 for category in categories]
            if variant == "normalized-bar":
                values = [value / total if total else 0.0 for value, total in zip(values, totals)]
            ax.bar(range(len(categories)), values, bottom=bottoms, width=0.72, label=name, color=color_map[name], edgecolor="white", linewidth=0.6, hatch=style_map[name]["hatch"], alpha=style_map[name]["alpha"])
            bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
        ax.set_xticks(range(len(categories)), categories, rotation=20, ha="right")
        ax.set_ylabel(enc.get("ylabel", "fraction" if variant == "normalized-bar" else y_key))
        return
    width = 0.75 / max(1, len(series))
    for index, name in enumerate(series):
        offset = (index - (len(series) - 1) / 2) * width
        selected = {row[x_key]: row for row in rows if row.get(series_key, "value") == name}
        values = [as_float(selected[category][y_key]) if category in selected else math.nan for category in categories]
        positions = [position + offset for position in range(len(categories))]
        ax.bar(positions, values, width=width, label=name if series_key else None, color=color_map[name], edgecolor="black", linewidth=0.6, hatch=style_map[name]["hatch"], alpha=style_map[name]["alpha"])
        errors = [uncertainty_values(selected[category], values[pos], enc) if category in selected else None for pos, category in enumerate(categories)]
        if any(errors):
            lower = [item[0] if item else 0.0 for item in errors]
            upper = [item[1] if item else 0.0 for item in errors]
            ax.errorbar(positions, values, yerr=[lower, upper], fmt="none", ecolor="#30343B", capsize=2, linewidth=0.65)
        if enc.get("raw_y"):
            raw_key = enc["raw_y"]
            raw_source = panel.get("_raw_rows") or rows
            for category_index, category in enumerate(categories):
                raw_rows = [row for row in raw_source if row[x_key] == category and row.get(series_key, "value") == name and row.get(raw_key) not in {None, ""}]
                for raw_index, row in enumerate(raw_rows):
                    jitter = ((raw_index % 5) - 2) * width * 0.08
                    ax.scatter(positions[category_index] + jitter, as_float(row[raw_key]), s=9, color="#30343B", alpha=0.55, zorder=3)
    ax.set_xticks(range(len(categories)), categories, rotation=20, ha="right")
    ax.set_ylabel(enc.get("ylabel", y_key))


def render_trend(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    x_key, y_key = enc["x"], enc["y"]
    series_key = enc.get("series") or enc.get("group")
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row.get(series_key, "value")].append(row)
    color_map = colors_for(panel, venue, groups)
    style_map = styles_for(panel, venue, groups)
    variant = panel.get("variant", "line")
    raw_source = panel.get("_raw_rows") or rows
    for index, (name, items) in enumerate(groups.items()):
        items = sorted(items, key=lambda item: as_float(item[x_key]))
        xs = [as_float(item[x_key]) for item in items]
        ys = [as_float(item[y_key]) for item in items]
        common = {"label": name if series_key else None, "color": color_map[name], "linewidth": 1.35}
        if variant == "step":
            ax.step(xs, ys, where="post", marker="o", markersize=3.2, **common)
        elif variant == "area":
            ax.plot(xs, ys, **common)
            ax.fill_between(xs, [0.0] * len(xs), ys, color=color_map[name], alpha=0.18)
        else:
            ax.plot(xs, ys, marker=style_map[name]["marker"], markersize=3.5, linestyle=style_map[name]["linestyle"], alpha=style_map[name]["alpha"], **common)
        errors = [uncertainty_values(item, y, enc) for item, y in zip(items, ys)]
        if any(errors):
            lower = [y - (item[0] if item else 0.0) for y, item in zip(ys, errors)]
            upper = [y + (item[1] if item else 0.0) for y, item in zip(ys, errors)]
            ax.fill_between(xs, lower, upper, color=color_map[name], alpha=0.16, linewidth=0)
        if variant in {"individual-runs", "learning-curve"} and enc.get("run") and enc.get("raw_y"):
            runs: dict[str, list[dict[str, str]]] = defaultdict(list)
            for raw in raw_source:
                if raw.get(series_key, "value") == name:
                    runs[str(raw[enc["run"]])].append(raw)
            for run_rows in runs.values():
                ordered = sorted(run_rows, key=lambda item: as_float(item[x_key]))
                ax.plot([as_float(item[x_key]) for item in ordered], [as_float(item[enc["raw_y"]]) for item in ordered], color=color_map[name], alpha=0.18, linewidth=0.6)
    ax.set_xlabel(enc.get("xlabel", x_key))
    ax.set_ylabel(enc.get("ylabel", y_key))


def render_heatmap(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str):
    enc = panel["encodings"]
    row_key, col_key, value_key = enc["row"], enc["column"], enc["value"]
    row_names = list(dict.fromkeys(row[row_key] for row in rows))
    col_names = list(dict.fromkeys(row[col_key] for row in rows))
    values = [[math.nan for _ in col_names] for _ in row_names]
    row_index = {name: index for index, name in enumerate(row_names)}
    col_index = {name: index for index, name in enumerate(col_names)}
    for row in rows:
        values[row_index[row[row_key]]][col_index[row[col_key]]] = as_float(row[value_key])
    variant = panel.get("variant", "sequential")
    flat = [value for row_values in values for value in row_values if math.isfinite(value)]
    kwargs: dict[str, Any] = {"cmap": enc.get("cmap") or colormap_for(venue, "matrix-heatmap", variant), "aspect": "auto"}
    if variant == "diverging":
        center = float(enc.get("center", 0.0))
        radius = max(abs(min(flat) - center), abs(max(flat) - center))
        kwargs.update({"vmin": center - radius, "vmax": center + radius})
    image = ax.imshow(values, **kwargs)
    ax.set_xticks(range(len(col_names)), col_names, rotation=30, ha="right")
    ax.set_yticks(range(len(row_names)), row_names)
    if variant in {"annotated", "confusion", "diverging-annotated"} or enc.get("annotate"):
        threshold = (min(flat) + max(flat)) / 2 if flat else 0
        for row_i, row_values in enumerate(values):
            for col_i, value in enumerate(row_values):
                if math.isfinite(value):
                    ax.text(col_i, row_i, enc.get("value_format", "{:.2g}").format(value), ha="center", va="center", fontsize=6, color="white" if value > threshold else "#20242A")
    return image


def render_scatter(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    x_key, y_key = enc["x"], enc["y"]
    label_key = enc.get("series") or enc.get("label")
    size_key = enc.get("size")
    variant = panel.get("variant", "scatter")
    if variant == "hexbin" and not label_key:
        image = ax.hexbin([as_float(row[x_key]) for row in rows], [as_float(row[y_key]) for row in rows], gridsize=int(enc.get("gridsize", 20)), mincnt=1, cmap=enc.get("cmap") or colormap_for(venue, "embedding-scatter", "sequential"))
        ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="count")
    elif label_key:
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            groups[row[label_key]].append(row)
        color_map = colors_for(panel, venue, groups)
        style_map = styles_for(panel, venue, groups)
        for name, items in groups.items():
            sizes = [max(10.0, as_float(item[size_key])) if size_key else 18 for item in items]
            xs, ys = [as_float(item[x_key]) for item in items], [as_float(item[y_key]) for item in items]
            ax.scatter(xs, ys, s=sizes, label=name, color=color_map[name], marker=style_map[name]["marker"], alpha=style_map[name]["alpha"])
            if variant == "labeled":
                for item, x, y in zip(items, xs, ys):
                    ax.annotate(str(item[label_key]), (x, y), xytext=(3, 2), textcoords="offset points", fontsize=6)
    else:
        sizes = [max(10.0, as_float(row[size_key])) if size_key else 18 for row in rows]
        ax.scatter([as_float(row[x_key]) for row in rows], [as_float(row[y_key]) for row in rows], s=sizes, color=semantic_color_sequence(venue)[0], alpha=0.85)
    ax.set_xlabel(enc.get("xlabel", x_key))
    ax.set_ylabel(enc.get("ylabel", y_key))


def render_forest(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    labels = [str(row[enc["label"]]) for row in rows]
    estimates = [as_float(row[enc["estimate"]]) for row in rows]
    lowers = [as_float(row[enc["lower"]]) for row in rows]
    uppers = [as_float(row[enc["upper"]]) for row in rows]
    if any(lower > estimate or estimate > upper for lower, estimate, upper in zip(lowers, estimates, uppers)):
        raise ValueError("forest-interval requires lower <= estimate <= upper")
    colors = colors_for(panel, venue, labels)
    positions = list(range(len(rows)))
    ax.errorbar(estimates, positions, xerr=[[estimate - lower for estimate, lower in zip(estimates, lowers)], [upper - estimate for estimate, upper in zip(estimates, uppers)]], fmt="none", ecolor="#59616C", capsize=2, linewidth=0.8)
    for index, (label, estimate) in enumerate(zip(labels, estimates)):
        ax.scatter(estimate, index, color=colors[label], marker=("o", "s", "^", "D")[index % 4], s=22, zorder=3)
    ax.axvline(float(enc.get("null", 0.0)), color="#70777F", linestyle="--", linewidth=0.7)
    ax.set_yticks(positions, labels)
    ax.set_xlabel(enc.get("xlabel", enc["estimate"]))
    ax.invert_yaxis()


def render_composition(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    x_key, segment_key, value_key = enc["x"], enc["segment"], enc["value"]
    categories = list(dict.fromkeys(str(row[x_key]) for row in rows))
    segments = list(dict.fromkeys(str(row[segment_key]) for row in rows))
    totals = {category: sum(as_float(row[value_key]) for row in rows if str(row[x_key]) == category) for category in categories}
    if any(as_float(row[value_key]) < 0 for row in rows):
        raise ValueError("composition-stacked requires nonnegative values")
    colors = colors_for(panel, venue, segments)
    styles = styles_for(panel, venue, segments)
    bottoms = [0.0] * len(categories)
    normalized = panel.get("variant", "stacked") == "normalized"
    for index, segment in enumerate(segments):
        selected = {str(row[x_key]): as_float(row[value_key]) for row in rows if str(row[segment_key]) == segment}
        values = [selected.get(category, 0.0) for category in categories]
        if normalized:
            values = [value / totals[category] if totals[category] else 0.0 for value, category in zip(values, categories)]
        ax.bar(categories, values, bottom=bottoms, label=segment, color=colors[segment], hatch=styles[segment]["hatch"], alpha=styles[segment]["alpha"], edgecolor="white", linewidth=0.6)
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
    ax.set_ylabel(enc.get("ylabel", "fraction" if normalized else value_key))
    if normalized:
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis="x", rotation=20)


def render_paired(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    pair_key, condition_key, value_key = enc["pair"], enc["condition"], enc["value"]
    conditions = list(dict.fromkeys(str(row[condition_key]) for row in rows))
    if len(conditions) != 2:
        raise ValueError("paired-change requires exactly two conditions")
    pairs: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        pairs[str(row[pair_key])][str(row[condition_key])] = as_float(row[value_key])
    complete = {key: values for key, values in pairs.items() if all(condition in values for condition in conditions)}
    if not complete:
        raise ValueError("paired-change has no complete pairs")
    colors = semantic_color_sequence(venue)
    for index, values in enumerate(complete.values()):
        ys = [values[condition] for condition in conditions]
        direction = 4 if ys[1] >= ys[0] else 5
        ax.plot([0, 1], ys, color=colors[direction], alpha=0.55, linewidth=0.75, marker=("o", "s", "^", "D")[index % 4], markersize=3)
    ax.set_xticks([0, 1], conditions)
    ax.set_ylabel(enc.get("ylabel", value_key))


def render_polar(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    axes = [str(row[enc["axis"]]) for row in rows]
    values = [as_float(row[enc["value"]]) for row in rows]
    if not 3 <= len(axes) <= 8 or any(value < 0 or value > 1 for value in values):
        raise ValueError("polar-summary requires 3-8 explicitly normalized values in [0, 1]")
    angles = [2 * math.pi * index / len(axes) for index in range(len(axes))]
    angles_closed, values_closed = angles + [angles[0]], values + [values[0]]
    color = semantic_color_sequence(venue)[0]
    ax.plot(angles_closed, values_closed, color=color, linewidth=1.2, marker="o", markersize=3)
    ax.fill(angles_closed, values_closed, color=color, alpha=0.18)
    ax.set_xticks(angles, axes)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_rlabel_position(135)
    ax.tick_params(axis="y", labelsize=6, pad=1)


def render_network(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    source_key, target_key = enc["source"], enc["target"]
    nodes = list(dict.fromkeys([row[source_key] for row in rows] + [row[target_key] for row in rows]))
    positions = {node: (math.cos(2 * math.pi * index / len(nodes)), math.sin(2 * math.pi * index / len(nodes))) for index, node in enumerate(nodes)}
    palette = semantic_color_sequence(venue)
    for row in rows:
        x0, y0 = positions[row[source_key]]
        x1, y1 = positions[row[target_key]]
        ax.plot([x0, x1], [y0, y1], color=palette[2], linewidth=0.8, alpha=0.65)
    for node, (x, y) in positions.items():
        ax.scatter([x], [y], s=80, color=palette[0], edgecolor="white", linewidth=0.8)
        ax.text(x, y, node, ha="center", va="center", fontsize=6)
    ax.set_axis_off()
    ax.set_aspect("equal")


def render_distribution(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    group_key, value_key = enc["group"], enc["value"]
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        groups[row[group_key]].append(as_float(row[value_key]))
    labels = list(groups)
    values = [groups[label] for label in labels]
    colors = colors_for(panel, venue, labels)
    variant = panel.get("variant", "box")
    if variant == "violin":
        parts = ax.violinplot(values, positions=range(1, len(values) + 1), showmedians=True, showextrema=False)
        for body, label in zip(parts["bodies"], labels):
            body.set_facecolor(colors[label]); body.set_edgecolor("#30343B"); body.set_alpha(0.55)
        ax.set_xticks(range(1, len(labels) + 1), labels)
    elif variant == "histogram":
        for label, value_list in zip(labels, values):
            ax.hist(value_list, bins=int(panel.get("statistics", {}).get("bins", 12)), histtype="step", linewidth=1.2, color=colors[label], label=label)
        ax.set_xlabel(enc.get("xlabel", value_key))
    elif variant == "ecdf":
        for label, value_list in zip(labels, values):
            ordered = sorted(value_list)
            ys = [(index + 1) / len(ordered) for index in range(len(ordered))]
            ax.step(ordered, ys, where="post", color=colors[label], label=label, linewidth=1.2)
        ax.set_xlabel(enc.get("xlabel", value_key)); ax.set_ylabel("empirical cumulative probability")
        return
    elif variant == "strip":
        ax.set_xticks(range(1, len(labels) + 1), labels)
    else:
        boxes = ax.boxplot(values, patch_artist=True, tick_labels=labels, showfliers=False)
        for box, label in zip(boxes["boxes"], labels):
            box.set(facecolor=colors[label], alpha=0.55, linewidth=0.65)
    if variant in {"box", "violin", "strip"}:
        for index, value_list in enumerate(values, start=1):
            jitter = [index + math.sin(position * 13.0) * 0.08 for position in range(len(value_list))]
            ax.scatter(jitter, value_list, s=10, color="#30343B", alpha=0.55, zorder=3)
    ax.set_ylabel(enc.get("ylabel", value_key))


def pareto_front(points: list[tuple[float, float]], x_direction: str, y_direction: str) -> list[tuple[float, float]]:
    ordered = sorted(points, key=lambda point: point[0], reverse=x_direction == "higher")
    best: float | None = None
    front = []
    for point in ordered:
        y = point[1]
        better = best is None or (y > best if y_direction == "higher" else y < best)
        if better:
            front.append(point)
            best = y
    return front


def render_tradeoff(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    x_key, y_key = enc["x"], enc["y"]
    label_key = enc.get("series") or enc.get("label")
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row.get(label_key, "models")].append(row)
    colors = colors_for(panel, venue, groups)
    for name, items in groups.items():
        points = [(as_float(item[x_key]), as_float(item[y_key])) for item in items]
        ax.scatter([point[0] for point in points], [point[1] for point in points], s=28, color=colors[name], label=name if label_key else None)
        if enc.get("frontier", "true").lower() != "false":
            front = pareto_front(points, enc.get("x_direction", "lower"), enc.get("y_direction", "higher"))
            if len(front) > 1:
                ax.plot([point[0] for point in front], [point[1] for point in front], color=colors[name], linewidth=1.1)
    ax.set_xlabel(enc.get("xlabel", x_key))
    ax.set_ylabel(enc.get("ylabel", y_key))


def render_calibration(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    confidence_key, accuracy_key = enc["confidence"], enc["accuracy"]
    label_key = enc.get("series") or enc.get("label")
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    if any(not 0 <= as_float(row[key]) <= 1 for row in rows for key in (confidence_key, accuracy_key)):
        raise ValueError("calibration-reliability values must be in [0, 1]")
    for row in rows:
        groups[row.get(label_key, "model")].append(row)
    colors = colors_for(panel, venue, groups)
    ax.plot([0, 1], [0, 1], color="#70777F", linewidth=0.8, linestyle="--", label="perfect calibration")
    for name, items in groups.items():
        items = sorted(items, key=lambda item: as_float(item[confidence_key]))
        ax.plot([as_float(item[confidence_key]) for item in items], [as_float(item[accuracy_key]) for item in items], marker="o", markersize=3.2, linewidth=1.2, color=colors[name], label=name if label_key else None)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel(enc.get("xlabel", "confidence"))
    ax.set_ylabel(enc.get("ylabel", "accuracy"))


def render_ranking(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str) -> None:
    enc = panel["encodings"]
    method_key, rank_key = enc["method"], enc["rank"]
    points = sorted([(row[method_key], as_float(row[rank_key])) for row in rows], key=lambda item: item[1])
    max_rank = max(rank for _, rank in points)
    ax.hlines(0, 1, max_rank, color="#30343B", linewidth=0.8)
    ax.set_xlim(0.75, max_rank + 0.25)
    ax.set_ylim(-0.55, 0.55)
    ax.set_xticks(range(1, math.ceil(max_rank) + 1))
    ax.set_yticks([])
    colors = colors_for(panel, venue, [method for method, _ in points])
    for index, (method, rank) in enumerate(points):
        direction = -1 if index % 2 == 0 else 1
        ax.vlines(rank, 0, direction * 0.22, color=colors[method], linewidth=1.2)
        ax.text(rank, direction * 0.28, method, ha="center", va="bottom" if direction > 0 else "top", fontsize=6.2, color=colors[method])
    critical_difference = panel.get("statistics", {}).get("critical_difference")
    if critical_difference is not None:
        cd = as_float(critical_difference)
        ax.annotate("", xy=(1, 0.43), xytext=(1 + cd, 0.43), arrowprops={"arrowstyle": "|-|", "linewidth": 0.9})
        ax.text(1 + cd / 2, 0.47, f"CD={cd:g}", ha="center", va="bottom", fontsize=6)
    ax.set_xlabel(enc.get("xlabel", "average rank (lower is better)"))


def render_image_plate(ax, rows: list[dict[str, str]], panel: dict[str, Any], spec_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment guard
        raise ValueError("Pillow is required for qualitative-image-plate") from exc
    enc = panel["encodings"]
    image_key = enc["image"]
    label_key = enc.get("label")
    columns = max(1, int(panel.get("columns", min(4, len(rows)))))
    total_rows = math.ceil(len(rows) / columns)
    ax.set_axis_off()
    for index, row in enumerate(rows):
        path = Path(row[image_key])
        path = path if path.is_absolute() else (spec_path.parent / path).resolve()
        if not path.is_file():
            raise ValueError(f"qualitative image is missing: {path}")
        image = Image.open(path).convert("RGB")
        if panel.get("_spec_version") == 3:
            for key in ("image_id", "crop_provenance", "aspect_ratio"):
                if not str(row.get(enc[key], "")).strip():
                    raise ValueError(f"qualitative image row requires {key}")
            declared_ratio = as_float(row[enc["aspect_ratio"]])
            actual_ratio = image.width / image.height
            if abs(actual_ratio - declared_ratio) / declared_ratio > 0.02:
                raise ValueError(f"qualitative image aspect ratio mismatch: {path}")
            if enc.get("physical_scale_required") and (not enc.get("scale_bar") or not row.get(enc["scale_bar"])):
                raise ValueError(f"qualitative image requires scale-bar metadata: {path}")
        column = index % columns
        row_index = index // columns
        inset = ax.inset_axes([column / columns, 1 - (row_index + 1) / total_rows, 1 / columns, 1 / total_rows])
        inset.imshow(image)
        inset.set_axis_off()
        if label_key and row.get(label_key):
            inset.set_title(row[label_key], fontsize=6, pad=1.5)


def render_schematic(ax, panel: dict[str, Any], venue: str = "generic") -> None:
    nodes = panel.get("nodes") or []
    edges = panel.get("edges") or []
    if not nodes:
        raise ValueError("method-schematic requires explicit nodes")
    by_id = {str(node.get("id")): node for node in nodes if node.get("id")}
    if len(by_id) != len(nodes):
        raise ValueError("method-schematic nodes require unique ids")
    for edge in edges:
        if str(edge.get("from")) not in by_id or str(edge.get("to")) not in by_id:
            raise ValueError("method-schematic edges must reference declared nodes")
    for lane in panel.get("lanes") or []:
        y, height = float(lane.get("y", 0)), float(lane.get("height", 1))
        ax.add_patch(Rectangle((0, y), 1, height, facecolor=lane.get("color", "#F4F5F7"), edgecolor="#C4C9D0", linewidth=0.6, zorder=-3))
        if lane.get("label"):
            ax.text(0.01, y + height - 0.015, str(lane["label"]), ha="left", va="top", fontsize=6, color="#59616C")
    for group in panel.get("groups") or []:
        x, y = float(group.get("x", 0)), float(group.get("y", 0))
        width, height = float(group.get("width", 1)), float(group.get("height", 1))
        ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.008,rounding_size=0.01", facecolor=group.get("color", "none"), edgecolor="#8A929D", linestyle="--", linewidth=0.6, zorder=-2))
        if group.get("label"):
            ax.text(x + 0.01, y + height - 0.012, str(group["label"]), ha="left", va="top", fontsize=6, color="#59616C")
    semantic = palette_for(venue)
    node_colors = {
        "input": semantic["neutral_light"],
        "process": adjust_oklab(semantic["ours"], 0.84, 0.45),
        "data": adjust_oklab(semantic["strong_baseline"], 0.88, 0.35),
        "output": adjust_oklab(semantic["positive"], 0.86, 0.4),
    }
    for node in nodes:
        x, y = float(node.get("x", 0.5)), float(node.get("y", 0.5))
        width, height = float(node.get("width", 0.18)), float(node.get("height", 0.10))
        kind = str(node.get("kind", "process"))
        color = node_colors.get(kind, semantic["neutral_light"])
        shape = str(node.get("shape", "box"))
        if shape == "circle":
            patch = Circle((x, y), min(width, height) / 2, facecolor=color, edgecolor="#30343B", linewidth=0.7)
        else:
            rounding = 0.04 if shape == "pill" else 0.012
            patch = FancyBboxPatch((x - width / 2, y - height / 2), width, height, boxstyle=f"round,pad=0.01,rounding_size={rounding}", facecolor=color, edgecolor="#30343B", linewidth=0.7)
        ax.add_patch(patch)
        label = str(node.get("label", node["id"]))
        if node.get("shape_label"):
            label += f"\n{node['shape_label']}"
        ax.text(x, y, label, ha="center", va="center", fontsize=6.2, wrap=True)
        for port in node.get("ports") or []:
            offsets = {"left": (-width / 2, 0), "right": (width / 2, 0), "top": (0, height / 2), "bottom": (0, -height / 2)}
            dx, dy = offsets[port]
            ax.add_patch(Circle((x + dx, y + dy), 0.006, facecolor="#30343B", edgecolor="white", linewidth=0.6, zorder=4))
    def anchor(node: dict[str, Any], port: str | None) -> tuple[float, float]:
        x, y = float(node.get("x", 0.5)), float(node.get("y", 0.5))
        width, height = float(node.get("width", 0.18)), float(node.get("height", 0.10))
        dx, dy = {"left": (-width / 2, 0), "right": (width / 2, 0), "top": (0, height / 2), "bottom": (0, -height / 2)}.get(str(port), (0, 0))
        return x + dx, y + dy
    for edge in edges:
        start, end = by_id[str(edge["from"])], by_id[str(edge["to"])]
        connection = "angle3,angleA=0,angleB=90" if edge.get("routing") == "orthogonal" else "arc3"
        start_xy, end_xy = anchor(start, edge.get("from_port")), anchor(end, edge.get("to_port"))
        arrow = FancyArrowPatch(start_xy, end_xy, arrowstyle="-|>", connectionstyle=connection, mutation_scale=8, linewidth=0.8, color="#30343B", shrinkA=2 if edge.get("from_port") else 11, shrinkB=2 if edge.get("to_port") else 11)
        ax.add_patch(arrow)
        if edge.get("label"):
            ax.text((float(start.get("x", 0.5)) + float(end.get("x", 0.5))) / 2, (float(start.get("y", 0.5)) + float(end.get("y", 0.5))) / 2 + 0.035, str(edge["label"]), fontsize=6, ha="center", va="bottom")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()


