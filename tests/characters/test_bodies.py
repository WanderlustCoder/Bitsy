from core.canvas import Canvas
from parts.base import PartConfig
from parts.bodies import BodyType, create_body, get_body_proportions
from tests.framework import TestCase


def _get_drawn_bounds_width_height(canvas: Canvas) -> tuple:
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                if min_x is None:
                    min_x = max_x = x
                    min_y = max_y = y
                else:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

    if min_x is None:
        return 0, 0

    return (max_x - min_x + 1, max_y - min_y + 1)


class TestBodyTypes(TestCase):
    def test_create_body_sets_body_type(self):
        """create_body sets body_type on created body."""
        config = PartConfig(outline=False, shading=False)
        body = create_body("simple", config, body_type=BodyType.THIN)

        self.assertEqual(body.body_type, BodyType.THIN)

    def test_create_body_accepts_body_type_string(self):
        """create_body accepts a body type string."""
        config = PartConfig(outline=False, shading=False)
        body = create_body("simple", config, body_type="stocky")

        self.assertEqual(body.body_type, BodyType.STOCKY)

    def test_body_proportions_vary_by_type(self):
        """Different body types produce different proportions."""
        config = PartConfig(outline=False, shading=False)
        canvas_size = 64
        draw_width = 24
        draw_height = 32

        widths = {}
        heights = {}

        for body_type in (BodyType.THIN, BodyType.AVERAGE, BodyType.MUSCULAR, BodyType.STOCKY):
            canvas = Canvas(canvas_size, canvas_size, (0, 0, 0, 0))
            body = create_body("simple", config, body_type=body_type)
            body.draw(canvas, canvas_size // 2, canvas_size // 2, draw_width, draw_height)

            width, height = _get_drawn_bounds_width_height(canvas)
            widths[body_type] = width
            heights[body_type] = height

        self.assertLess(widths[BodyType.THIN], widths[BodyType.AVERAGE])
        self.assertGreater(widths[BodyType.MUSCULAR], widths[BodyType.AVERAGE])
        self.assertGreater(widths[BodyType.STOCKY], widths[BodyType.AVERAGE])

        self.assertGreater(heights[BodyType.THIN], heights[BodyType.AVERAGE])
        self.assertLess(heights[BodyType.STOCKY], heights[BodyType.AVERAGE])

    def test_get_body_proportions(self):
        """get_body_proportions returns per-type proportions."""
        thin = get_body_proportions(BodyType.THIN)
        average = get_body_proportions(BodyType.AVERAGE)

        self.assertNotEqual(thin, average)
