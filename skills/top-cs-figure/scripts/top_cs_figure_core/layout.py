from __future__ import annotations

from typing import Any, Iterable

from matplotlib.ticker import FixedLocator, MaxNLocator

from .numeric import as_float


def apply_annotations(ax, annotations: Iterable[dict[str, Any]]) -> None:
    for annotation in annotations:
        kind = annotation.get("kind")
        if kind == "vline":
            ax.axvline(float(annotation["value"]), color=annotation.get("color", "#70777F"), linestyle=annotation.get("linestyle", "--"), linewidth=float(annotation.get("linewidth", 0.8)))
        elif kind == "hline":
            ax.axhline(float(annotation["value"]), color=annotation.get("color", "#70777F"), linestyle=annotation.get("linestyle", "--"), linewidth=float(annotation.get("linewidth", 0.8)))
        elif kind == "text":
            ax.text(float(annotation["x"]), float(annotation["y"]), str(annotation["text"]), transform=ax.transAxes if annotation.get("axes_fraction", True) else None, fontsize=float(annotation.get("fontsize", 6)), ha=annotation.get("ha", "left"), va=annotation.get("va", "center"))
        else:
            raise ValueError(f"unsupported annotation kind: {kind}")


def apply_scales(ax, panel: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    if panel.get("visual_family") == "polar-summary":
        return
    scales = panel.get("scales") or {}
    enc = panel.get("encodings") or {}
    for axis in ("x", "y"):
        config = scales.get(axis) or {}
        if not config:
            continue
        scale_type = config.get("type", "linear")
        if scale_type == "categorical":
            continue
        column = enc.get(axis)
        if scale_type == "log" and column:
            values = [as_float(row[column]) for row in rows if row.get(column) not in {None, ""}]
            if values and min(values) <= 0:
                raise ValueError(f"panel {panel['panel_id']} uses log-{axis} with non-positive data")
        if scale_type not in {"linear", "log", "symlog"}:
            raise ValueError(f"unsupported {axis} scale: {scale_type}")
        getattr(ax, f"set_{axis}scale")(scale_type)
        limits = config.get("limits")
        if limits:
            getattr(ax, f"set_{axis}lim")(float(limits[0]), float(limits[1]))
        if config.get("label"):
            getattr(ax, f"set_{axis}label")(str(config["label"]))


def manage_tick_density(ax, panel: dict[str, Any]) -> None:
    scales = panel.get("scales") or {}
    if (scales.get("x") or {}).get("type") != "categorical" and not isinstance(ax.xaxis.get_major_locator(), FixedLocator):
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
    if (scales.get("y") or {}).get("type") != "categorical" and not isinstance(ax.yaxis.get_major_locator(), FixedLocator):
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
    ax.tick_params(axis="y", pad=6)


def create_axes(fig, panels: list[dict[str, Any]], layout: dict[str, Any] | None):
    if not layout:
        axis = fig.add_subplot(111, projection="polar" if panels[0]["visual_family"] == "polar-summary" else None)
        return {str(panels[0]["panel_id"]): axis}
    kind = layout.get("kind", "mosaic")
    panel_ids = [str(panel["panel_id"]) for panel in panels]
    if kind == "mosaic":
        mosaic = layout.get("mosaic")
        if not mosaic:
            raise ValueError("mosaic layout requires layout.mosaic")
        if isinstance(mosaic, list) and all(isinstance(row, str) for row in mosaic):
            mosaic = "\n".join(mosaic)
        per_subplot_kw = {str(panel["panel_id"]): {"projection": "polar"} for panel in panels if panel["visual_family"] == "polar-summary"}
        axes = fig.subplot_mosaic(mosaic, width_ratios=layout.get("width_ratios"), height_ratios=layout.get("height_ratios"), empty_sentinel=".", per_subplot_kw=per_subplot_kw or None)
        if set(axes) != set(panel_ids):
            raise ValueError("layout.mosaic labels must match panel ids exactly")
        return axes
    if kind == "grid":
        rows, columns = int(layout.get("rows", 0)), int(layout.get("columns", 0))
        if rows < 1 or columns < 1 or rows * columns < len(panels):
            raise ValueError("grid layout requires enough positive rows and columns")
        grid = fig.add_gridspec(rows, columns, width_ratios=layout.get("width_ratios"), height_ratios=layout.get("height_ratios"))
        return {panel_ids[index]: fig.add_subplot(grid[index // columns, index % columns], projection="polar" if panels[index]["visual_family"] == "polar-summary" else None) for index in range(len(panel_ids))}
    raise ValueError(f"unsupported layout kind: {kind}")
