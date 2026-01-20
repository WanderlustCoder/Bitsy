"""Generate oval face template with placeholder colors."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.canvas import Canvas  # noqa: E402

BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
OUTLINE = (100, 0, 0, 255)

WIDTH = 32
HEIGHT = 40


def inside_ellipse(x: int, y: int, cx: int, cy: int, rx: int, ry: int) -> bool:
    if rx <= 0 or ry <= 0:
        return False
    dx = (x - cx) / rx
    dy = (y - cy) / ry
    return dx * dx + dy * dy <= 1.0


def main() -> None:
    canvas = Canvas(WIDTH, HEIGHT)
    cx, cy = 16, 20
    rx, ry = 12, 16

    canvas.fill_ellipse(cx, cy, rx, ry, BASE)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if not inside_ellipse(x, y, cx, cy, rx, ry):
                continue
            if x <= cx - 4 or y >= cy + 8:
                canvas.set_pixel(x, y, SHADOW1)
            if x >= cx + 3 and y <= cy - 6:
                canvas.set_pixel(x, y, HIGHLIGHT)

    outline_rx = rx - 1
    outline_ry = ry - 1
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if inside_ellipse(x, y, cx, cy, rx, ry) and not inside_ellipse(
                x, y, cx, cy, outline_rx, outline_ry
            ):
                canvas.set_pixel(x, y, OUTLINE)

    output_path = ROOT / "templates" / "anime_standard" / "faces" / "oval.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(output_path))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
