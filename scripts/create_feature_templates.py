#!/usr/bin/env python3
"""Create small feature templates (nose/mouth) for anime_standard."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas

OUTLINE = (100, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)


def create_dot_nose(path: str) -> None:
    canvas = Canvas(4, 3)

    # Small triangular shadow for a dot nose.
    canvas.set_pixel_solid(1, 1, SHADOW1)
    canvas.set_pixel_solid(2, 1, SHADOW1)
    canvas.set_pixel_solid(1, 2, SHADOW1)

    canvas.save(path)


def create_neutral_mouth(path: str) -> None:
    canvas = Canvas(8, 4)

    # Simple mouth line with a slight shadow beneath.
    for x in range(2, 6):
        canvas.set_pixel_solid(x, 1, OUTLINE)
        canvas.set_pixel_solid(x, 2, SHADOW1)

    canvas.save(path)


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    nose_path = os.path.join(root, "templates", "anime_standard", "noses", "dot.png")
    mouth_path = os.path.join(root, "templates", "anime_standard", "mouths", "neutral.png")

    os.makedirs(os.path.dirname(nose_path), exist_ok=True)
    os.makedirs(os.path.dirname(mouth_path), exist_ok=True)

    create_dot_nose(nose_path)
    create_neutral_mouth(mouth_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
