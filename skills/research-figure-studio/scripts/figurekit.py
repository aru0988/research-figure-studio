"""Small, editable scientific-diagram primitives. No model or data is inferred."""
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.path import Path as VectorPath
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
from matplotlib.text import Text

PALETTE = {
    "blue": "#35618F", "teal": "#3D7975", "orange": "#AD6431",
    "ink": "#172B42", "line": "#4B6075", "border": "#A4B3C3",
    "canvas": "#FBFCFD", "panel": "#F6F8FA", "neutral": "#E5EAF0",
    "blue_light": "#DFE7F0", "teal_light": "#E0ECE8",
    "orange_light": "#F3E6D7", "representation": "#C5D4E2",
}


def contrast(foreground, background):
    """WCAG relative-luminance ratio; an internal diagnostic, not journal certification."""
    def luminance(color):
        rgb = to_rgb(color)
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))
    a, b = luminance(foreground), luminance(background)
    return (max(a, b) + .05) / (min(a, b) + .05)


def rounded_path(points, radius=7, anchors=()):
    """Round an orthogonal skeleton, preserving endpoints and all supplied junctions.

    Anchor points on a segment are inserted before rounding. An anchored corner
    remains a corner: moving a branch to make it prettier would change the graph.
    Crossings are not automatically interpreted as connected junctions.
    """
    points = [tuple(map(float, p)) for p in points]
    if len(points) < 2 or not math.isfinite(radius) or radius < 0:
        raise ValueError("At least two points and a finite nonnegative radius are required")
    if any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in points):
        raise ValueError("Coordinates must be finite pairs")
    anchors = {tuple(map(float, p)) for p in anchors}
    if any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in anchors):
        raise ValueError("Anchors must be finite coordinate pairs")
    anchors |= {points[0], points[-1]}
    expanded = [points[0]]
    for a, b in zip(points, points[1:]):
        if a == b or (a[0] != b[0] and a[1] != b[1]):
            raise ValueError("Each segment must have positive length and be horizontal or vertical")
        middle = [q for q in anchors if q not in (a, b) and
                  ((a[0] == b[0] == q[0] and min(a[1], b[1]) < q[1] < max(a[1], b[1])) or
                   (a[1] == b[1] == q[1] and min(a[0], b[0]) < q[0] < max(a[0], b[0])))]
        middle.sort(key=lambda q: abs(q[0] - a[0]) + abs(q[1] - a[1]))
        expanded.extend(middle + [b])
    vertices, codes = [expanded[0]], [VectorPath.MOVETO]
    for a, b, c in zip(expanded, expanded[1:], expanded[2:]):
        d1, d2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        if b in anchors or cross == 0 or radius == 0:
            vertices.append(b); codes.append(VectorPath.LINETO)
            continue
        l1, l2 = sum(map(abs, d1)), sum(map(abs, d2))
        r = min(radius, .42 * l1, .42 * l2)
        before = (b[0] - d1[0] / l1 * r, b[1] - d1[1] / l1 * r)
        after = (b[0] + d2[0] / l2 * r, b[1] + d2[1] / l2 * r)
        k = .5522847498307936
        control1 = tuple(v + (target - v) * k for v, target in zip(before, b))
        control2 = tuple(v + (target - v) * k for v, target in zip(after, b))
        vertices.extend([before, control1, control2, after])
        codes.extend([VectorPath.LINETO] + [VectorPath.CURVE4] * 3)
    vertices.append(expanded[-1]); codes.append(VectorPath.LINETO)
    path = VectorPath(vertices, codes)
    assert tuple(path.vertices[0]) == points[0] and tuple(path.vertices[-1]) == points[-1]
    on_route = {q for q in expanded if q in anchors}
    assert on_route <= {tuple(v) for v in path.vertices}
    return path


class Figure:
    """A fixed-coordinate canvas with deferred routing and light local QA.

    Coordinates increase downwards. Lines are finalized only after all endpoints
    are known, which protects a new branch on an earlier route. Visual inspection
    remains necessary: these checks do not establish scientific correctness.
    """
    def __init__(self, width, height, inches=10, palette=None):
        self.width, self.height = width, height
        self.colors = dict(PALETTE, **(palette or {}))
        plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                             "mathtext.fontset": "dejavusans", "svg.fonttype": "none",
                             "svg.hashsalt": "research-figure-studio"})
        self.fig = plt.figure(figsize=(inches, inches * height / width), dpi=120,
                              facecolor=self.colors["canvas"])
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set(xlim=(0, width), ylim=(height, 0)); self.ax.axis("off")
        self.routes, self.boxtexts, self.operators = [], [], []
        self._rendered = False

    def label(self, x, y, text, size=9, bold=False, color=None, **kwargs):
        return self.ax.text(x, y, text, fontsize=size, fontweight="bold" if bold else "normal",
                            ha=kwargs.pop("ha", "center"), va="center", zorder=8,
                            color=color or self.colors["ink"], **kwargs)

    def box(self, x, y, width, height, label="", role="neutral", dark=False,
            shape="round", size=9, fill=None, border=None):
        color = self.colors["line"] if role == "neutral" else self.colors.get(role, self.colors["line"])
        fill = fill or (color if dark else self.colors.get(role + "_light", self.colors["neutral"]))
        if shape in ("trapezoid", "gate"):
            patch = Polygon([(x, y + height), (x + 12, y), (x + width - 12, y), (x + width, y + height)],
                            facecolor=fill, edgecolor=border or color, linewidth=1, zorder=2)
        elif shape == "round":
            patch = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0,rounding_size=5",
                                  facecolor=fill, edgecolor=border or color, linewidth=1, zorder=2)
        else:
            raise ValueError("shape must be 'round' or 'trapezoid' ('gate' is a compatibility alias)")
        self.ax.add_patch(patch)
        if label:
            text = self.label(x + width / 2, y + height / 2, label, size,
                              color="white" if dark else None)
            self.boxtexts.append((label, text, (x, y, width, height)))
        return patch

    def panel(self, x, y, width, height, label):
        patch = self.box(x, y, width, height, fill=self.colors["panel"], border=self.colors["border"])
        patch.set_zorder(0)
        self.label(x + 16, y + 22, label, size=10, bold=True, ha="left")
        return patch

    def operator(self, x, y, symbol="dot", radius=12, role="teal"):
        """Vector glyphs, not a font's baseline-dependent circle character."""
        if symbol not in ("dot", "plus", "times"):
            raise ValueError("symbol must be dot, plus or times")
        color = self.colors[role]
        self.ax.add_patch(Circle((x, y), radius, facecolor=self.colors["canvas"], edgecolor=color,
                                 linewidth=1.1, zorder=5))
        if symbol == "dot":
            self.ax.add_patch(Circle((x, y), radius * .47, fill=False,
                                     edgecolor=self.colors["ink"], linewidth=.85, zorder=7))
            self.ax.add_patch(Circle((x, y), radius * .12, color=self.colors["ink"], zorder=7))
        elif symbol in ("plus", "times"):
            d = radius * .46
            pairs = [((x-d, y), (x+d, y)), ((x, y-d), (x, y+d))] if symbol == "plus" else [
                ((x-d, y-d), (x+d, y+d)), ((x-d, y+d), (x+d, y-d))]
            for a, b in pairs:
                self.ax.plot([a[0], b[0]], [a[1], b[1]], color=self.colors["ink"], lw=1.05, zorder=7)
        self.operators.append({"center": [x, y], "symbol": symbol})

    def route(self, points, role="line", style="solid", arrow=True, radius=7, anchors=()):
        if self._rendered:
            raise RuntimeError("Add every route before render/export")
        if style not in ("solid", "copy", "gradient"):
            raise ValueError("style must be solid, copy or gradient")
        # Materialize generators once; validate now, not only during export.
        points, anchors = [tuple(p) for p in points], [tuple(p) for p in anchors]
        rounded_path(points, radius, anchors)
        self.routes.append(dict(points=points, role=role, style=style, arrow=arrow,
                                radius=radius, anchors=anchors))

    def render(self):
        if self._rendered:
            return
        endpoints = {tuple(p) for e in self.routes for p in (e["points"][0], e["points"][-1])}
        for e in self.routes:
            path = rounded_path(e["points"], e["radius"], endpoints | set(map(tuple, e["anchors"])))
            self.ax.add_patch(FancyArrowPatch(path=path,
                arrowstyle="-|>" if e["arrow"] else "-", mutation_scale=9,
                linewidth=1.05, color=self.colors.get(e["role"], e["role"]),
                linestyle={"solid": "-", "copy": "--", "gradient": ":"}[e["style"]],
                capstyle="round", joinstyle="round", zorder=3))
        self._rendered = True

    def audit(self):
        self.render(); self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        outside, overflow, overlap = [], [], []
        labels = [t for t in self.fig.findobj(Text) if t.get_visible() and t.get_text()]
        bounds = self.fig.bbox
        for t in labels:
            box = t.get_window_extent(renderer)
            if box.x0 < -.5 or box.y0 < -.5 or box.x1 > bounds.width + .5 or box.y1 > bounds.height + .5:
                outside.append(t.get_text())
        for name, text, (x, y, w, h) in self.boxtexts:
            a, b = self.ax.transData.transform((x, y)), self.ax.transData.transform((x+w, y+h))
            bb = text.get_window_extent(renderer)
            if bb.x0 < a[0]+1 or bb.x1 > b[0]-1 or bb.y0 < b[1]+1 or bb.y1 > a[1]-1:
                overflow.append(name)
        for i, a in enumerate(labels):
            for b in labels[i+1:]:
                aa, bb = a.get_window_extent(renderer), b.get_window_extent(renderer)
                if min(aa.x1, bb.x1)-max(aa.x0, bb.x0) > 1 and min(aa.y1, bb.y1)-max(aa.y0, bb.y0) > 1:
                    overlap.append([a.get_text(), b.get_text()])
        return {"outside_text": outside, "overflow_text": overflow, "overlapping_text": overlap,
                "route_count": len(self.routes), "operators": self.operators,
                "scope": "Geometry diagnostics only; model logic and aesthetics require review"}

    def export(self, stem, strict=True, dpi=240):
        stem = Path(stem); stem.parent.mkdir(parents=True, exist_ok=True)
        report = self.audit()
        if strict and any(report[k] for k in ("outside_text", "overflow_text", "overlapping_text")):
            raise ValueError("Layout QA failed: " + json.dumps(report))
        self.fig.savefig(stem.with_suffix(".svg"), metadata={"Date": None})
        self.fig.savefig(stem.with_suffix(".png"), dpi=dpi)
        text = stem.with_suffix(".svg").read_text(encoding="utf8")
        has_labels = any(t.get_text() for t in self.fig.findobj(Text))
        if (has_labels and "<text" not in text) or "<image" in text:
            raise ValueError("Expected editable SVG text without embedded raster")
        return report

    def close(self):
        plt.close(self.fig)
