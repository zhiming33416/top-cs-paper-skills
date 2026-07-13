from __future__ import annotations

from typing import Any

from .numeric import as_float


def _overlap(left: list[float], right: list[float], tolerance: float = 2.0) -> bool:
    lx, ly, lw, lh = left
    rx, ry, rw, rh = right
    return min(lx + lw, rx + rw) - max(lx, rx) > tolerance and min(ly + lh, ry + rh) - max(ly, ry) > tolerance


def geometry_report(fig, axes: dict[str, Any], panel_rows: dict[str, list[dict[str, Any]]], panel_specs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    renderer = fig.canvas.get_renderer()
    width, height = fig.get_size_inches()
    figure_bbox = fig.bbox
    panels: dict[str, Any] = {}
    for panel_id, ax in axes.items():
        bbox = ax.get_window_extent(renderer)
        text_boxes = []
        artists = ax.texts + [ax.title, ax.xaxis.label, ax.yaxis.label] + list(ax.get_xticklabels()) + list(ax.get_yticklabels())
        for item in artists:
            if not item.get_text():
                continue
            text_bbox = item.get_window_extent(renderer)
            text_boxes.append({"text": item.get_text(), "font_pt": round(float(item.get_fontsize()), 3), "bbox_px": [round(value, 2) for value in text_bbox.bounds]})
        overlaps = []
        for left_index, left in enumerate(text_boxes):
            lx, ly, lw, lh = left["bbox_px"]
            for right in text_boxes[left_index + 1:]:
                rx, ry, rw, rh = right["bbox_px"]
                if _overlap(left["bbox_px"], right["bbox_px"]):
                    overlaps.append([left["text"], right["text"]])
        legend = ax.get_legend()
        legend_bbox = list(legend.get_window_extent(renderer).bounds) if legend and legend.get_visible() else None
        legend_text_overlaps = [item["text"] for item in text_boxes if legend_bbox and item["text"] not in {text.get_text() for text in legend.get_texts()} and _overlap(legend_bbox, item["bbox_px"])]
        panel_label = str(panel_specs[panel_id].get("panel_id", panel_id))
        panel_label_boxes = [item for item in text_boxes if item["text"] == panel_label]
        title_boxes = [item for item in text_boxes if item["text"] == ax.get_title() and ax.get_title()]
        panel_label_title_overlap = any(_overlap(left["bbox_px"], right["bbox_px"], 0) for left in panel_label_boxes for right in title_boxes)
        panel = panel_specs[panel_id]
        enc = panel.get("encodings") or {}
        uncertainty_clipped = False
        if enc.get("lower") and enc.get("upper") and panel_rows.get(panel_id):
            interval_on_x = panel.get("visual_family") == "forest-interval"
            lower_limit, upper_limit = ax.get_xlim() if interval_on_x else ax.get_ylim()
            uncertainty_clipped = any(as_float(row[enc["lower"]]) < lower_limit or as_float(row[enc["upper"]]) > upper_limit for row in panel_rows[panel_id])
        widths = [float(line.get_linewidth()) for line in ax.lines]
        widths.extend(float(patch.get_linewidth()) for patch in ax.patches if patch.get_linewidth() is not None)
        panels[panel_id] = {
            "axes_bbox_px": [round(value, 2) for value in bbox.bounds],
            "inside_canvas": bool(bbox.x0 >= figure_bbox.x0 and bbox.y0 >= figure_bbox.y0 and bbox.x1 <= figure_bbox.x1 and bbox.y1 <= figure_bbox.y1),
            "texts": text_boxes, "text_overlaps": overlaps, "uncertainty_clipped": uncertainty_clipped,
            "legend_bbox_px": [round(value, 2) for value in legend_bbox] if legend_bbox else None,
            "legend_text_overlaps": legend_text_overlaps,
            "panel_label_title_overlap": panel_label_title_overlap,
            "line_widths_pt": [round(value, 3) for value in widths],
            "marker_sizes_pt": [round(float(line.get_markersize()), 3) for line in ax.lines if line.get_marker() not in {None, "None", ""}],
        }
    guide_axes = []
    main_axes = set(axes.values())
    for guide in fig.axes:
        if guide in main_axes:
            continue
        bbox = guide.get_window_extent(renderer)
        guide_axes.append({"bbox_px": [round(value, 2) for value in bbox.bounds], "label": guide.get_label(), "text_count": sum(bool(item.get_text()) for item in guide.texts)})
    return {"width_mm": round(width * 25.4, 3), "height_mm": round(height * 25.4, 3), "dpi": float(fig.dpi), "panels": panels, "guide_axes": guide_axes}
