"""
Scene Composition - Layer-based scene building and generation.

Provides:
- Layer-based scene assembly
- Parallax background generation
- Lighting and shadow casting
- Time-of-day variations
- Weather overlay integration
"""

from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import random
import math

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Palette, Style
from core.color import lerp_color, darken, lighten, adjust_saturation
from editor.layers import LayerStack, Layer, BlendMode


class TimeOfDay(Enum):
    """Time of day for lighting."""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class WeatherType(Enum):
    """Weather conditions for overlays."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    STORM = "storm"


@dataclass
class SceneLayer:
    """A layer in the scene with parallax and properties."""
    name: str
    canvas: Canvas
    parallax_x: float = 1.0  # 1.0 = normal, <1 = farther, >1 = closer
    parallax_y: float = 1.0
    z_order: int = 0  # Draw order (higher = on top)
    offset_x: int = 0
    offset_y: int = 0
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    is_background: bool = False  # Affected by time-of-day
    casts_shadow: bool = False


@dataclass
class LightSource:
    """A light source in the scene."""
    x: int
    y: int
    radius: int
    color: Tuple[int, int, int, int] = (255, 255, 200, 255)
    intensity: float = 1.0
    falloff: float = 1.0  # Higher = faster falloff


@dataclass
class SceneConfig:
    """Configuration for scene generation."""
    width: int = 320
    height: int = 180
    time_of_day: TimeOfDay = TimeOfDay.NOON
    weather: WeatherType = WeatherType.CLEAR
    ambient_light: float = 1.0  # 0.0 = dark, 1.0 = full light
    seed: Optional[int] = None


class Scene:
    """A composable scene with layers, lighting, and effects."""

    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        """Initialize scene.

        Args:
            width: Scene width in pixels
            height: Scene height in pixels
            seed: Random seed for deterministic generation
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)

        self.layers: List[SceneLayer] = []
        self.lights: List[LightSource] = []
        self.time_of_day = TimeOfDay.NOON
        self.weather = WeatherType.CLEAR
        self.ambient_light = 1.0

    def add_layer(self, layer: SceneLayer) -> None:
        """Add a layer to the scene."""
        self.layers.append(layer)
        self.layers.sort(key=lambda l: l.z_order)

    def add_light(self, light: LightSource) -> None:
        """Add a light source to the scene."""
        self.lights.append(light)

    def set_time_of_day(self, time: TimeOfDay) -> None:
        """Set time of day for lighting."""
        self.time_of_day = time
        self.ambient_light = _get_ambient_for_time(time)

    def set_weather(self, weather: WeatherType) -> None:
        """Set weather conditions."""
        self.weather = weather

    def render(self, camera_x: int = 0, camera_y: int = 0) -> Canvas:
        """Render the scene to a canvas.

        Args:
            camera_x: Camera X offset for parallax
            camera_y: Camera Y offset for parallax

        Returns:
            Rendered scene canvas
        """
        result = Canvas(self.width, self.height, (0, 0, 0, 0))

        # Render layers with parallax
        for layer in self.layers:
            self._render_layer(result, layer, camera_x, camera_y)

        # Apply lighting
        if self.lights or self.ambient_light < 1.0:
            result = self._apply_lighting(result)

        # Apply time-of-day color grading
        result = self._apply_time_grading(result)

        # Apply weather overlay
        if self.weather != WeatherType.CLEAR:
            result = self._apply_weather(result)

        return result

    def _render_layer(self, target: Canvas, layer: SceneLayer,
                      camera_x: int, camera_y: int) -> None:
        """Render a single layer with parallax."""
        # Calculate parallax offset
        px = int(camera_x * (1 - layer.parallax_x))
        py = int(camera_y * (1 - layer.parallax_y))

        # Apply layer offset
        final_x = layer.offset_x + px
        final_y = layer.offset_y + py

        # Create a temp canvas with the layer at the right position
        temp = Canvas(self.width, self.height, (0, 0, 0, 0))

        # Blit layer to temp at calculated position
        for y in range(layer.canvas.height):
            for x in range(layer.canvas.width):
                tx = x + final_x
                ty = y + final_y

                if 0 <= tx < self.width and 0 <= ty < self.height:
                    pixel = layer.canvas.get_pixel(x, y)
                    if pixel and pixel[3] > 0:
                        # Apply layer opacity
                        alpha = int(pixel[3] * layer.opacity)
                        temp.set_pixel(tx, ty, (pixel[0], pixel[1], pixel[2], alpha))

        # Blit to target using blend mode
        _blend_canvas(target, temp, layer.blend_mode)

    def _apply_lighting(self, canvas: Canvas) -> Canvas:
        """Apply lighting from light sources."""
        result = canvas.copy()

        # Create light map
        light_map = [[self.ambient_light for _ in range(self.width)]
                     for _ in range(self.height)]

        # Add contribution from each light
        for light in self.lights:
            for y in range(self.height):
                for x in range(self.width):
                    dist = math.sqrt((x - light.x) ** 2 + (y - light.y) ** 2)
                    if dist < light.radius:
                        # Calculate falloff
                        factor = 1 - (dist / light.radius) ** light.falloff
                        contribution = factor * light.intensity
                        light_map[y][x] = min(1.0, light_map[y][x] + contribution)

        # Apply light map to canvas
        for y in range(self.height):
            for x in range(self.width):
                pixel = result.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    brightness = light_map[y][x]
                    r = int(pixel[0] * brightness)
                    g = int(pixel[1] * brightness)
                    b = int(pixel[2] * brightness)
                    result.set_pixel_solid(x, y, (r, g, b, pixel[3]))

        return result

    def _apply_time_grading(self, canvas: Canvas) -> Canvas:
        """Apply time-of-day color grading."""
        grading = _get_time_grading(self.time_of_day)
        if grading is None:
            return canvas

        result = canvas.copy()
        tint, strength = grading

        for y in range(self.height):
            for x in range(self.width):
                pixel = result.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    # Blend with tint color
                    r = int(pixel[0] * (1 - strength) + tint[0] * strength)
                    g = int(pixel[1] * (1 - strength) + tint[1] * strength)
                    b = int(pixel[2] * (1 - strength) + tint[2] * strength)
                    result.set_pixel_solid(x, y, (r, g, b, pixel[3]))

        return result

    def _apply_weather(self, canvas: Canvas) -> Canvas:
        """Apply weather overlay."""
        result = canvas.copy()

        if self.weather == WeatherType.FOG:
            # Add fog overlay
            fog_color = (200, 200, 210)
            fog_strength = 0.3
            for y in range(self.height):
                for x in range(self.width):
                    pixel = result.get_pixel(x, y)
                    if pixel:
                        r = int(pixel[0] * (1 - fog_strength) + fog_color[0] * fog_strength)
                        g = int(pixel[1] * (1 - fog_strength) + fog_color[1] * fog_strength)
                        b = int(pixel[2] * (1 - fog_strength) + fog_color[2] * fog_strength)
                        result.set_pixel_solid(x, y, (r, g, b, pixel[3]))

        elif self.weather == WeatherType.RAIN:
            # Add rain streaks
            for _ in range(self.width * self.height // 100):
                x = self.rng.randint(0, self.width - 1)
                y = self.rng.randint(0, self.height - 1)
                length = self.rng.randint(3, 8)
                for i in range(length):
                    ry = y + i
                    if 0 <= ry < self.height:
                        pixel = result.get_pixel(x, ry)
                        if pixel:
                            # Lighten for rain streak
                            r = min(255, pixel[0] + 50)
                            g = min(255, pixel[1] + 50)
                            b = min(255, pixel[2] + 60)
                            result.set_pixel_solid(x, ry, (r, g, b, pixel[3]))

        elif self.weather == WeatherType.SNOW:
            # Add snow particles
            for _ in range(self.width * self.height // 80):
                x = self.rng.randint(0, self.width - 1)
                y = self.rng.randint(0, self.height - 1)
                result.set_pixel_solid(x, y, (255, 255, 255, 200))

        return result


def _get_ambient_for_time(time: TimeOfDay) -> float:
    """Get ambient light level for time of day."""
    levels = {
        TimeOfDay.DAWN: 0.6,
        TimeOfDay.MORNING: 0.9,
        TimeOfDay.NOON: 1.0,
        TimeOfDay.AFTERNOON: 0.95,
        TimeOfDay.DUSK: 0.5,
        TimeOfDay.NIGHT: 0.2,
        TimeOfDay.MIDNIGHT: 0.1,
    }
    return levels.get(time, 1.0)


def _get_time_grading(time: TimeOfDay) -> Optional[Tuple[Tuple[int, int, int], float]]:
    """Get color grading for time of day."""
    gradings = {
        TimeOfDay.DAWN: ((255, 200, 150), 0.15),
        TimeOfDay.MORNING: ((255, 250, 230), 0.05),
        TimeOfDay.NOON: None,  # No grading
        TimeOfDay.AFTERNOON: ((255, 240, 200), 0.08),
        TimeOfDay.DUSK: ((255, 150, 100), 0.2),
        TimeOfDay.NIGHT: ((100, 100, 180), 0.25),
        TimeOfDay.MIDNIGHT: ((50, 50, 120), 0.35),
    }
    return gradings.get(time)


def _blend_canvas(base: Canvas, overlay: Canvas, mode: BlendMode) -> None:
    """Blend overlay onto base using blend mode (in-place)."""
    for y in range(min(base.height, overlay.height)):
        for x in range(min(base.width, overlay.width)):
            src = overlay.get_pixel(x, y)
            if not src or src[3] == 0:
                continue

            dst = base.get_pixel(x, y)
            if not dst:
                base.set_pixel(x, y, src)
                continue

            # Simple alpha compositing for now
            src_alpha = src[3] / 255.0
            dst_alpha = dst[3] / 255.0
            out_alpha = src_alpha + dst_alpha * (1 - src_alpha)

            if out_alpha > 0:
                r = int((src[0] * src_alpha + dst[0] * dst_alpha * (1 - src_alpha)) / out_alpha)
                g = int((src[1] * src_alpha + dst[1] * dst_alpha * (1 - src_alpha)) / out_alpha)
                b = int((src[2] * src_alpha + dst[2] * dst_alpha * (1 - src_alpha)) / out_alpha)
                base.set_pixel_solid(x, y, (r, g, b, int(out_alpha * 255)))


# =============================================================================
# Parallax Background Generation
# =============================================================================

def generate_parallax_background(
    width: int,
    height: int,
    layers: int = 3,
    palette: Optional[Palette] = None,
    seed: Optional[int] = None
) -> List[SceneLayer]:
    """Generate parallax background layers.

    Args:
        width: Scene width
        height: Scene height
        layers: Number of parallax layers
        palette: Color palette (uses default sky if None)
        seed: Random seed

    Returns:
        List of SceneLayer objects from back to front
    """
    rng = random.Random(seed)
    result = []

    # Default sky palette
    if palette is None:
        palette = Palette()
        palette.add((135, 206, 235, 255))  # Sky blue
        palette.add((100, 149, 237, 255))  # Cornflower blue
        palette.add((70, 130, 180, 255))   # Steel blue

    # Sky layer (doesn't parallax)
    sky = _generate_sky(width, height, palette, rng)
    result.append(SceneLayer(
        name="sky",
        canvas=sky,
        parallax_x=0.0,
        parallax_y=0.0,
        z_order=-100,
        is_background=True
    ))

    # Generate mountain/hill layers
    for i in range(layers):
        depth = (layers - i) / layers  # 1.0 = farthest, approaching 0 = closest
        parallax = 0.2 + depth * 0.3  # Farther = slower parallax

        # Darken colors for depth
        layer_palette = Palette()
        for j in range(len(palette)):
            color = palette.get(j)
            # Fade to blue-ish for atmospheric perspective
            fade = depth * 0.5
            r = int(color[0] * (1 - fade) + 100 * fade)
            g = int(color[1] * (1 - fade) + 120 * fade)
            b = int(color[2] * (1 - fade) + 180 * fade)
            layer_palette.add((r, g, b, color[3]))

        layer_canvas = _generate_hills(width, height, layer_palette, rng, depth)
        result.append(SceneLayer(
            name=f"hills_{i}",
            canvas=layer_canvas,
            parallax_x=parallax,
            parallax_y=parallax * 0.5,
            z_order=-50 + i * 10,
            is_background=True
        ))

    return result


def _generate_sky(width: int, height: int, palette: Palette,
                  rng: random.Random) -> Canvas:
    """Generate sky gradient."""
    canvas = Canvas(width, height)
    top_color = palette.get(0) if len(palette) > 0 else (135, 206, 235, 255)
    bottom_color = palette.get(1) if len(palette) > 1 else (255, 255, 255, 255)

    for y in range(height):
        t = y / height
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        row_color = (r, g, b, 255)  # Create tuple once per row
        for x in range(width):
            canvas.set_pixel_solid(x, y, row_color)

    return canvas


def _generate_hills(width: int, height: int, palette: Palette,
                    rng: random.Random, depth: float) -> Canvas:
    """Generate a hill silhouette layer."""
    canvas = Canvas(width, height, (0, 0, 0, 0))
    color = palette.get(0) if len(palette) > 0 else (50, 80, 50, 255)

    # Generate hill profile using noise
    base_height = int(height * (0.3 + depth * 0.4))
    hill_heights = []

    x = 0
    while x < width:
        # Random hill width and height
        hill_width = rng.randint(20, 60)
        hill_peak = rng.randint(10, 40)

        for dx in range(hill_width):
            if x + dx >= width:
                break
            # Parabolic hill shape
            t = dx / hill_width
            h = int(4 * hill_peak * t * (1 - t))
            hill_heights.append(base_height - h)

        x += hill_width

    # Pad to width
    while len(hill_heights) < width:
        hill_heights.append(base_height)

    # Draw hills
    for x in range(width):
        start_y = hill_heights[x]
        for y in range(start_y, height):
            canvas.set_pixel_solid(x, y, color)

    return canvas


# =============================================================================
# Convenience Functions
# =============================================================================

def create_scene(width: int = 320, height: int = 180,
                 config: Optional[SceneConfig] = None) -> Scene:
    """Create a new scene with optional configuration."""
    config = config or SceneConfig(width=width, height=height)
    scene = Scene(config.width, config.height, config.seed)
    scene.set_time_of_day(config.time_of_day)
    scene.set_weather(config.weather)
    scene.ambient_light = config.ambient_light
    return scene


def list_times_of_day() -> List[str]:
    """List available times of day."""
    return [t.value for t in TimeOfDay]


def list_weather_types() -> List[str]:
    """List available weather types."""
    return [w.value for w in WeatherType]
