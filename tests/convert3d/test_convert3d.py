"""Tests for 3D conversion pipeline."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas, Palette
from convert3d import load_obj, render_sprite
from convert3d.obj_parser import parse_obj_lines, Model
from convert3d.projection import orthographic_projection, isometric_projection
from convert3d.rasterizer import rasterize_triangles


class TestObjParser(TestCase):
    """Tests for OBJ parsing."""

    def test_parse_obj_lines_triangulates(self):
        obj_data = [
            "v 0 0 0\n",
            "v 1 0 0\n",
            "v 1 1 0\n",
            "v 0 1 0\n",
            "f 1 2 3 4\n",
        ]
        model = parse_obj_lines(obj_data)
        self.assertEqual(len(model.vertices), 4)
        self.assertEqual(len(model.faces), 2)
        self.assertEqual(model.faces[0], (0, 1, 2))
        self.assertEqual(model.faces[1], (0, 2, 3))

    def test_load_obj_from_file(self):
        obj_content = "\n".join([
            "v 0 0 0",
            "v 0 1 0",
            "v 1 0 0",
            "f 1 2 3",
        ])
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".obj") as handle:
            handle.write(obj_content)
            path = handle.name
        try:
            model = load_obj(path)
            self.assertEqual(len(model.vertices), 3)
            self.assertEqual(len(model.faces), 1)
        finally:
            os.unlink(path)


class TestProjection(TestCase):
    """Tests for projection helpers."""

    def test_orthographic_views(self):
        vertices = [(1.0, 2.0, 3.0)]
        front, depth_front = orthographic_projection(vertices, view="front")
        side, depth_side = orthographic_projection(vertices, view="side")
        top, depth_top = orthographic_projection(vertices, view="top")

        self.assertEqual(front[0], (1.0, 2.0))
        self.assertEqual(depth_front[0], 3.0)
        self.assertEqual(side[0], (3.0, 2.0))
        self.assertEqual(depth_side[0], 1.0)
        self.assertEqual(top[0], (1.0, 3.0))
        self.assertEqual(depth_top[0], 2.0)

    def test_isometric_symmetry(self):
        verts = [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]
        projected, _ = isometric_projection(verts)
        self.assertTrue(projected[0][0] > 0)
        self.assertTrue(projected[1][0] < 0)
        self.assertEqual(round(projected[0][1], 6), round(projected[1][1], 6))


class TestRasterizer(TestCase):
    """Tests for rasterization."""

    def test_rasterize_triangle_fills_pixels(self):
        canvas = Canvas(8, 8)
        vertices = [(1.0, 1.0), (6.0, 1.0), (1.0, 6.0)]
        faces = [(0, 1, 2)]
        colors = [(255, 0, 0, 255)]
        depths = [0.0, 0.0, 0.0]
        rasterize_triangles(canvas, vertices, faces, colors, depths)

        self.assertTrue(canvas.get_pixel(2, 2)[3] > 0)
        self.assertTrue(canvas.get_pixel(1, 1)[3] > 0)
        self.assertTrue(canvas.get_pixel(6, 6)[3] == 0)


class TestRenderer(TestCase):
    """Tests for high-level renderer."""

    def test_render_sprite_outputs_canvas(self):
        model = Model(
            vertices=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
        )
        palette = Palette([(0, 0, 0, 255), (255, 255, 255, 255)])
        sprite = render_sprite(
            model,
            width=16,
            height=16,
            projection="orthographic",
            view="front",
            light_direction=(0, 0, 1),
            outline=True,
            palette=palette,
        )
        self.assertIsInstance(sprite, Canvas)

        non_transparent = 0
        outline_pixels = 0
        for y in range(sprite.height):
            for x in range(sprite.width):
                color = sprite.get_pixel(x, y)
                if color and color[3] > 0:
                    non_transparent += 1
                    if color == (0, 0, 0, 255):
                        outline_pixels += 1
        self.assertTrue(non_transparent > 0)
        self.assertTrue(outline_pixels > 0)

    def test_quantization_limits_colors(self):
        model = Model(
            vertices=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
        )
        palette = Palette([(0, 0, 0, 255), (255, 255, 255, 255)])
        sprite = render_sprite(
            model,
            width=12,
            height=12,
            projection="orthographic",
            view="front",
            light_direction=(0, 0, 1),
            outline=False,
            palette=palette,
        )

        allowed = set(palette.colors)
        for y in range(sprite.height):
            for x in range(sprite.width):
                color = sprite.get_pixel(x, y)
                if color and color[3] > 0:
                    self.assertIn(color, allowed)


if __name__ == '__main__':
    import traceback

    test_classes = [
        TestObjParser,
        TestProjection,
        TestRasterizer,
        TestRenderer,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for name in dir(instance):
            if name.startswith('test_'):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, name, e, traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")

    if errors:
        print(f"\nFailed tests:")
        for cls_name, test_name, error, tb in errors:
            print(f"\n{cls_name}.{test_name}:")
            print(tb)

    exit(0 if failed == 0 else 1)
