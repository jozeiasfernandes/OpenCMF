"""
core.color.color_utils
======================
Funções puras de conversão entre espaços de cor.
Sem dependência de Qt — testáveis de forma isolada.

Convenção interna: todos os valores em float 0.0–1.0,
exceto Hue (0.0–360.0) e canais CMYK / S / V (0.0–1.0).
"""

from __future__ import annotations
from typing import Tuple

RGB  = Tuple[float, float, float]        # r, g, b  ∈ [0, 1]
HSV  = Tuple[float, float, float]        # h ∈ [0, 360], s, v ∈ [0, 1]
CMYK = Tuple[float, float, float, float] # c, m, y, k ∈ [0, 1]


# ── RGB ↔ HSV ────────────────────────────────────────────────────────────────

def rgb_to_hsv(r: float, g: float, b: float) -> HSV:
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    v = cmax
    s = 0.0 if cmax == 0.0 else delta / cmax

    if delta == 0.0:
        h = 0.0
    elif cmax == r:
        h = 60.0 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60.0 * (((b - r) / delta) + 2)
    else:
        h = 60.0 * (((r - g) / delta) + 4)

    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> RGB:
    """h em graus [0, 360), s e v em [0, 1]."""
    if s == 0.0:
        return v, v, v
    h = h % 360.0
    i = int(h / 60.0)
    f = h / 60.0 - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    return (
        (v, t, p, p, q, v)[i],
        (q, v, v, t, p, p)[i],
        (p, p, q, v, v, t)[i],
    )


# ── RGB ↔ CMYK ───────────────────────────────────────────────────────────────

def rgb_to_cmyk(r: float, g: float, b: float) -> CMYK:
    k = 1.0 - max(r, g, b)
    if k >= 1.0:
        return 0.0, 0.0, 0.0, 1.0
    inv = 1.0 - k
    return (inv - r) / inv, (inv - g) / inv, (inv - b) / inv, k


def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> RGB:
    inv = 1.0 - k
    return (1 - c) * inv, (1 - m) * inv, (1 - y) * inv


# ── helpers ──────────────────────────────────────────────────────────────────

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def rgb_clamp(r: float, g: float, b: float) -> RGB:
    return clamp(r), clamp(g), clamp(b)