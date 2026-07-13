from __future__ import annotations

import math
from typing import Iterable


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    value = color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"invalid hex color: {color}")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: Iterable[float]) -> str:
    values = [max(0, min(255, round(float(value) * 255))) for value in rgb]
    return "#" + "".join(f"{value:02X}" for value in values[:3])


def _linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def _srgb(value: float) -> float:
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def relative_luminance(color: str) -> float:
    r, g, b = (_linear(value) for value in hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(left: str, right: str) -> float:
    low, high = sorted((relative_luminance(left), relative_luminance(right)))
    return round((high + 0.05) / (low + 0.05), 3)


def rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_linear(value) for value in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (max(0.0, value) ** (1 / 3) for value in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    lightness, a, b = lab
    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    linear = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    return tuple(max(0.0, min(1.0, _srgb(value))) for value in linear)  # type: ignore[return-value]


def interpolate_oklab(left: str, right: str, fraction: float) -> str:
    a = rgb_to_oklab(hex_to_rgb(left))
    b = rgb_to_oklab(hex_to_rgb(right))
    t = max(0.0, min(1.0, float(fraction)))
    return rgb_to_hex(oklab_to_rgb(tuple(x + (y - x) * t for x, y in zip(a, b))))


def adjust_oklab(color: str, lightness: float | None = None, chroma_scale: float = 1.0) -> str:
    l, a, b = rgb_to_oklab(hex_to_rgb(color))
    return rgb_to_hex(oklab_to_rgb((l if lightness is None else lightness, a * chroma_scale, b * chroma_scale)))


def oklab_distance(left: str, right: str) -> float:
    a = rgb_to_oklab(hex_to_rgb(left))
    b = rgb_to_oklab(hex_to_rgb(right))
    return round(math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))), 4)


def simulate_cvd(color: str, mode: str) -> str:
    matrices = {
        "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
        "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
        "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
    }
    if mode not in matrices:
        raise ValueError(f"unsupported CVD mode: {mode}")
    rgb = tuple(_linear(value) for value in hex_to_rgb(color))
    matrix = matrices[mode]
    transformed = tuple(sum(matrix[row][col] * rgb[col] for col in range(3)) for row in range(3))
    return rgb_to_hex(tuple(max(0.0, min(1.0, _srgb(value))) for value in transformed))


def pairwise_accessibility(colors: list[str], background: str = "#FFFFFF") -> dict[str, object]:
    pairs = []
    for index, left in enumerate(colors):
        for right in colors[index + 1:]:
            pairs.append({
                "left": left,
                "right": right,
                "oklab_distance": oklab_distance(left, right),
                "grayscale_delta": round(abs(relative_luminance(left) - relative_luminance(right)), 4),
                "cvd_distance": {mode: oklab_distance(simulate_cvd(left, mode), simulate_cvd(right, mode)) for mode in ("protan", "deutan", "tritan")},
            })
    return {
        "background": background,
        "contrast": {color: contrast_ratio(color, background) for color in colors},
        "pairs": pairs,
    }
