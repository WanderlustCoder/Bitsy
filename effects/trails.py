"""
Trails - Motion trail effects for sprites and particles.

Provides:
- AfterImage trails (ghosting effect)
- Line trails (continuous path)
- Ribbon trails (width-varying paths)
"""

import math
from typing import List, Tuple, Optional, Deque
from collections import deque
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


@dataclass
class TrailPoint:
    """A single point in a trail.

    Attributes:
        x, y: Position
        age: Time since point was created
        alpha: Opacity (0-255)
        size: Size at this point
        color: Color at this point
    """

    x: float
    y: float
    age: float = 0.0
    alpha: int = 255
    size: float = 1.0
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)


class Trail:
    """Base trail class for motion effects."""

    def __init__(self, max_length: int = 20, lifetime: float = 0.5):
        """Initialize trail.

        Args:
            max_length: Maximum number of trail points
            lifetime: How long each point lives (seconds)
        """
        self.max_length = max_length
        self.lifetime = lifetime
        self.points: Deque[TrailPoint] = deque(maxlen=max_length)
        self.color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.fade_out = True

    def add_point(self, x: float, y: float, size: float = 1.0,
                  color: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Add a new point to the trail.

        Args:
            x: X position
            y: Y position
            size: Size at this point
            color: Color (uses default if None)
        """
        self.points.append(TrailPoint(
            x=x,
            y=y,
            age=0.0,
            alpha=255,
            size=size,
            color=color or self.color
        ))

    def update(self, dt: float) -> None:
        """Update trail points.

        Args:
            dt: Delta time in seconds
        """
        # Age all points
        for point in self.points:
            point.age += dt
            if self.fade_out and self.lifetime > 0:
                # Fade based on age
                ratio = 1.0 - (point.age / self.lifetime)
                point.alpha = int(max(0, min(255, ratio * 255)))

        # Remove expired points
        while self.points and self.points[0].age >= self.lifetime:
            self.points.popleft()

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render the trail.

        Args:
            canvas: Target canvas
            offset_x: X offset
            offset_y: Y offset
        """
        for point in self.points:
            self._render_point(canvas, point, offset_x, offset_y)

    def _render_point(self, canvas: Canvas, point: TrailPoint,
                      offset_x: int, offset_y: int) -> None:
        """Render a single trail point."""
        px = int(point.x) + offset_x
        py = int(point.y) + offset_y

        if 0 <= px < canvas.width and 0 <= py < canvas.height:
            color = (
                point.color[0],
                point.color[1],
                point.color[2],
                point.alpha
            )
            canvas.set_pixel(px, py, color)

    def clear(self) -> None:
        """Clear all trail points."""
        self.points.clear()

    @property
    def is_empty(self) -> bool:
        """Check if trail has no points."""
        return len(self.points) == 0


class LineTrail(Trail):
    """Trail that draws connected lines between points."""

    def __init__(self, max_length: int = 20, lifetime: float = 0.5,
                 thickness: int = 1):
        super().__init__(max_length, lifetime)
        self.thickness = thickness

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render connected line segments."""
        if len(self.points) < 2:
            return

        points_list = list(self.points)
        for i in range(len(points_list) - 1):
            p1 = points_list[i]
            p2 = points_list[i + 1]

            # Interpolate alpha between points
            avg_alpha = (p1.alpha + p2.alpha) // 2
            color = (p1.color[0], p1.color[1], p1.color[2], avg_alpha)

            self._draw_line(
                canvas,
                int(p1.x) + offset_x, int(p1.y) + offset_y,
                int(p2.x) + offset_x, int(p2.y) + offset_y,
                color
            )

    def _draw_line(self, canvas: Canvas, x1: int, y1: int,
                   x2: int, y2: int, color: Tuple[int, int, int, int]) -> None:
        """Draw a line between two points."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            # Draw with thickness
            for ty in range(-self.thickness // 2, self.thickness // 2 + 1):
                for tx in range(-self.thickness // 2, self.thickness // 2 + 1):
                    px, py = x + tx, y + ty
                    if 0 <= px < canvas.width and 0 <= py < canvas.height:
                        canvas.set_pixel(px, py, color)


class RibbonTrail(Trail):
    """Trail with varying width, like a ribbon or sword slash."""

    def __init__(self, max_length: int = 20, lifetime: float = 0.5,
                 start_width: float = 1.0, end_width: float = 4.0):
        super().__init__(max_length, lifetime)
        self.start_width = start_width
        self.end_width = end_width

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render ribbon trail with varying width."""
        if len(self.points) < 2:
            return

        points_list = list(self.points)
        num_points = len(points_list)

        for i in range(num_points - 1):
            p1 = points_list[i]
            p2 = points_list[i + 1]

            # Calculate width at this segment
            t = i / (num_points - 1) if num_points > 1 else 0
            width = self.start_width + (self.end_width - self.start_width) * t

            # Calculate perpendicular direction
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                # Normalize and rotate 90 degrees
                nx = -dy / length
                ny = dx / length
            else:
                nx, ny = 0, 1

            # Draw thick line segment
            avg_alpha = (p1.alpha + p2.alpha) // 2
            color = (p1.color[0], p1.color[1], p1.color[2], avg_alpha)

            half_width = width / 2
            for w in range(-int(half_width), int(half_width) + 1):
                x1 = int(p1.x + nx * w) + offset_x
                y1 = int(p1.y + ny * w) + offset_y
                x2 = int(p2.x + nx * w) + offset_x
                y2 = int(p2.y + ny * w) + offset_y

                self._draw_line_simple(canvas, x1, y1, x2, y2, color)

    def _draw_line_simple(self, canvas: Canvas, x1: int, y1: int,
                          x2: int, y2: int, color: Tuple[int, int, int, int]) -> None:
        """Draw a simple 1px line."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                canvas.set_pixel(x, y, color)


class AfterImageTrail:
    """Creates ghost/afterimage effect by storing previous frames.

    Instead of points, stores copies of a sprite at previous positions.
    """

    def __init__(self, max_images: int = 5, lifetime: float = 0.3,
                 interval: float = 0.05):
        """Initialize afterimage trail.

        Args:
            max_images: Maximum number of afterimages
            lifetime: How long each afterimage persists
            interval: Minimum time between capturing new images
        """
        self.max_images = max_images
        self.lifetime = lifetime
        self.interval = interval

        self._images: Deque[Tuple[Canvas, float, float, float]] = deque(maxlen=max_images)
        self._time_since_capture = 0.0

    def capture(self, sprite: Canvas, x: float, y: float) -> None:
        """Capture a new afterimage.

        Args:
            sprite: The sprite to capture
            x: X position
            y: Y position
        """
        if self._time_since_capture >= self.interval:
            self._images.append((sprite.copy(), x, y, 0.0))
            self._time_since_capture = 0.0

    def update(self, dt: float) -> None:
        """Update afterimages.

        Args:
            dt: Delta time in seconds
        """
        self._time_since_capture += dt

        # Age all images and remove expired ones
        new_images = deque(maxlen=self.max_images)
        for sprite, x, y, age in self._images:
            new_age = age + dt
            if new_age < self.lifetime:
                new_images.append((sprite, x, y, new_age))
        self._images = new_images

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all afterimages.

        Args:
            canvas: Target canvas
            offset_x: X offset
            offset_y: Y offset
        """
        for sprite, x, y, age in self._images:
            # Calculate alpha based on age
            alpha_ratio = 1.0 - (age / self.lifetime) if self.lifetime > 0 else 1.0
            alpha = int(alpha_ratio * 128)  # Max 50% opacity for ghosts

            self._render_ghost(canvas, sprite, int(x) + offset_x, int(y) + offset_y, alpha)

    def _render_ghost(self, canvas: Canvas, sprite: Canvas,
                      x: int, y: int, alpha: int) -> None:
        """Render a ghosted sprite."""
        for sy in range(sprite.height):
            for sx in range(sprite.width):
                px = x + sx
                py = y + sy
                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    src = sprite.pixels[sy][sx]
                    if src[3] > 0:  # Only non-transparent pixels
                        # Blend with reduced alpha
                        combined_alpha = (src[3] * alpha) // 255
                        color = (src[0], src[1], src[2], combined_alpha)
                        canvas.set_pixel(px, py, color)

    def clear(self) -> None:
        """Clear all afterimages."""
        self._images.clear()


class MotionBlur:
    """Creates motion blur effect based on velocity."""

    def __init__(self, samples: int = 4, intensity: float = 1.0):
        """Initialize motion blur.

        Args:
            samples: Number of blur samples
            intensity: Blur intensity multiplier
        """
        self.samples = samples
        self.intensity = intensity
        self._prev_x = 0.0
        self._prev_y = 0.0
        self._initialized = False

    def render(self, canvas: Canvas, sprite: Canvas,
               x: float, y: float) -> None:
        """Render sprite with motion blur.

        Args:
            canvas: Target canvas
            sprite: Sprite to render
            x: Current X position
            y: Current Y position
        """
        if not self._initialized:
            self._prev_x = x
            self._prev_y = y
            self._initialized = True
            # Just render normally
            canvas.blit(sprite, int(x), int(y))
            return

        # Calculate motion vector
        dx = x - self._prev_x
        dy = y - self._prev_y

        # Render blur samples
        for i in range(self.samples):
            t = i / self.samples
            sample_x = int(self._prev_x + dx * t * self.intensity)
            sample_y = int(self._prev_y + dy * t * self.intensity)
            alpha = int(255 * (1 - t) / self.samples)

            self._render_with_alpha(canvas, sprite, sample_x, sample_y, alpha)

        # Render current frame at full opacity
        canvas.blit(sprite, int(x), int(y))

        # Store current position
        self._prev_x = x
        self._prev_y = y

    def _render_with_alpha(self, canvas: Canvas, sprite: Canvas,
                           x: int, y: int, alpha: int) -> None:
        """Render sprite with reduced alpha."""
        for sy in range(sprite.height):
            for sx in range(sprite.width):
                px = x + sx
                py = y + sy
                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    src = sprite.pixels[sy][sx]
                    if src[3] > 0:
                        combined_alpha = (src[3] * alpha) // 255
                        if combined_alpha > 0:
                            color = (src[0], src[1], src[2], combined_alpha)
                            canvas.set_pixel(px, py, color)

    def reset(self) -> None:
        """Reset motion blur state."""
        self._initialized = False


class SpeedLines:
    """Generates speed line effects for fast movement."""

    def __init__(self, num_lines: int = 10, length: float = 30,
                 direction: float = 0, spread: float = 20,
                 seed: int = 42):
        """Initialize speed lines.

        Args:
            num_lines: Number of speed lines
            length: Line length in pixels
            direction: Direction in degrees (0 = right)
            spread: Spread angle in degrees
            seed: Random seed
        """
        self.num_lines = num_lines
        self.length = length
        self.direction = direction
        self.spread = spread
        self.seed = seed

        import random
        self.rng = random.Random(seed)
        self._generate_lines()

    def _generate_lines(self) -> None:
        """Generate random line configurations."""
        self.lines = []
        for _ in range(self.num_lines):
            angle = self.direction + self.rng.uniform(-self.spread / 2, self.spread / 2)
            offset = self.rng.uniform(-20, 20)
            line_length = self.length * self.rng.uniform(0.5, 1.0)
            alpha = self.rng.randint(100, 255)
            self.lines.append((angle, offset, line_length, alpha))

    def render(self, canvas: Canvas, center_x: int, center_y: int,
               color: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> None:
        """Render speed lines centered at a position.

        Args:
            canvas: Target canvas
            center_x: Center X position
            center_y: Center Y position
            color: Line color
        """
        for angle, offset, line_length, alpha in self.lines:
            # Calculate line start and end
            angle_rad = math.radians(angle)
            perp_rad = angle_rad + math.pi / 2

            # Offset perpendicular to direction
            ox = math.cos(perp_rad) * offset
            oy = math.sin(perp_rad) * offset

            start_x = int(center_x + ox)
            start_y = int(center_y + oy)
            end_x = int(start_x + math.cos(angle_rad) * line_length)
            end_y = int(start_y + math.sin(angle_rad) * line_length)

            line_color = (color[0], color[1], color[2], alpha)
            self._draw_line(canvas, start_x, start_y, end_x, end_y, line_color)

    def _draw_line(self, canvas: Canvas, x1: int, y1: int,
                   x2: int, y2: int, color: Tuple[int, int, int, int]) -> None:
        """Draw a line."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Fade alpha along line
                fade = 1.0 - (t * 0.5)  # Fade to 50% at end
                final_alpha = int(color[3] * fade)
                canvas.set_pixel(x, y, (color[0], color[1], color[2], final_alpha))

    def regenerate(self) -> None:
        """Regenerate line configurations."""
        self._generate_lines()
