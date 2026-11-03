"""Observable geometry and export invariants, not an aesthetic score."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/research-figure-studio/scripts"))
from figurekit import Figure, contrast, rounded_path
from matplotlib.path import Path as VectorPath
from matplotlib.patches import Circle
from matplotlib.colors import to_rgba


class GeometryTests(unittest.TestCase):
    def test_curve_preserves_endpoints_and_supplied_junction(self):
        path = rounded_path([(0, 0), (100, 0), (100, 100)], anchors=[(50, 0)])
        vertices = {tuple(v) for v in path.vertices}
        self.assertEqual(tuple(path.vertices[0]), (0, 0))
        self.assertEqual(tuple(path.vertices[-1]), (100, 100))
        self.assertIn((50, 0), vertices)
        self.assertIn(VectorPath.CURVE4, path.codes)

    def test_anchored_corner_is_not_cut_off(self):
        path = rounded_path([(0, 0), (100, 0), (100, 100)], anchors=[(100, 0)])
        self.assertIn((100, 0), {tuple(v) for v in path.vertices})
        self.assertNotIn(VectorPath.CURVE4, path.codes)

    def test_invalid_routes_fail_before_render(self):
        for points in [[(0, 0)], [(0, 0), (1, 1)], [(0, 0), (0, 0)]]:
            with self.assertRaises(ValueError):
                rounded_path(points)
        with self.assertRaises(ValueError):
            rounded_path([(0, 0), (0, 10)], radius=-1)

    def test_contrast_reference_values(self):
        self.assertAlmostEqual(contrast("#000000", "#FFFFFF"), 21)
        self.assertAlmostEqual(contrast("#123456", "#123456"), 1)
        self.assertAlmostEqual(contrast("#FFFFFF", "#123456"), contrast("#123456", "#FFFFFF"))

    def test_invalid_anchors_are_rejected(self):
        for anchors in [[(2,)], [(2, 3, 4)], [(float("nan"), 2)]]:
            with self.assertRaises(ValueError):
                rounded_path([(0, 0), (10, 0)], anchors=anchors)

    def test_neutral_boxes_keep_visible_borders(self):
        f = Figure(200, 160)
        try:
            box = f.box(40, 50, 120, 40, "Fixed")
            self.assertEqual(box.get_edgecolor(), to_rgba(f.colors["line"]))
            self.assertGreater(contrast(f.colors["line"], f.colors["neutral"]), 3)
        finally:
            f.close()

    def test_operator_rings_are_exactly_concentric(self):
        f = Figure(200, 160)
        try:
            f.operator(100, 80)
            circles = [p for p in f.ax.patches if isinstance(p, Circle)]
            self.assertEqual(len(circles), 3)
            self.assertTrue(all(p.center == (100, 80) for p in circles))
        finally:
            f.close()

    def test_overflow_is_detected_and_strict_export_rejects_it(self):
        f = Figure(300, 160)
        try:
            f.box(130, 60, 30, 40, "A label that cannot fit")
            self.assertTrue(f.audit()["overflow_text"])
            with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
                f.export(Path(d) / "must-fail")
        finally:
            f.close()

    def test_svg_is_editable_and_export_is_idempotent(self):
        f = Figure(300, 160)
        try:
            f.box(35, 60, 90, 40, "Source", "blue")
            f.box(175, 60, 90, 40, "Target", "teal")
            f.route([(125, 80), (175, 80)])
            with tempfile.TemporaryDirectory() as d:
                stem = Path(d) / "diagram"
                self.assertFalse(f.export(stem)["overflow_text"])
                svg = stem.with_suffix(".svg").read_text(encoding="utf8")
                self.assertIn("<text", svg)
                self.assertNotIn("<image", svg)
                count = len(f.ax.patches)
                f.export(stem)
                self.assertEqual(count, len(f.ax.patches))
            with self.assertRaises(RuntimeError):
                f.route([(1, 1), (2, 1)])
        finally:
            f.close()


if __name__ == "__main__":
    unittest.main()
