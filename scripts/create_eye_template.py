#!/usr/bin/env python3
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core.canvas import Canvas

SECONDARY = (0, 255, 0, 255)
BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)
OUTLINE = (100, 0, 0, 255)


def draw_span(canvas: Canvas, y: int, x_start: int, x_end: int, color) -> None:
    for x in range(x_start, x_end + 1):
        canvas.set_pixel(x, y, color)


def main() -> None:
    canvas = Canvas(12, 10)

    sclera_rows = {
        2: (2, 9),
        3: (1, 10),
        4: (1, 10),
        5: (1, 10),
        6: (2, 9),
    }
    for y, (x_start, x_end) in sclera_rows.items():
        draw_span(canvas, y, x_start, x_end, SECONDARY)

    canvas.fill_circle(6, 4, 3, BASE)
    canvas.fill_rect(4, 2, 5, 2, SHADOW1)
    canvas.fill_circle(6, 5, 1, SHADOW2)
    canvas.fill_rect(4, 3, 2, 2, HIGHLIGHT)
    canvas.set_pixel(5, 2, HIGHLIGHT2)
    canvas.set_pixel(7, 3, HIGHLIGHT2)

    draw_span(canvas, 1, 3, 8, OUTLINE)
    canvas.set_pixel(2, 2, OUTLINE)
    canvas.set_pixel(9, 2, OUTLINE)
    canvas.set_pixel(2, 6, OUTLINE)
    canvas.set_pixel(9, 6, OUTLINE)
    draw_span(canvas, 7, 3, 8, OUTLINE)

    output_path = os.path.join(
        ROOT, "templates", "anime_standard", "eyes", "large.png"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
