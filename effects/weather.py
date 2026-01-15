"""
Weather Effects - Dynamic weather overlays and effects.

Provides:
- Rain (light drizzle to heavy storm)
- Snow (gentle flakes to blizzard)
- Fog (light mist to dense fog)
- Lightning flashes
- Wind effects
- Weather particle systems
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import lerp_color


class WeatherIntensity(Enum):
    """Weather intensity levels."""
    LIGHT = 'light'
    MODERATE = 'moderate'
    HEAVY = 'heavy'
    STORM = 'storm'


@dataclass
class RainDrop:
    """A single rain drop."""
    x: float
    y: float
    speed: float
    length: int
    angle: float = -0.1  # Slight angle for wind

    def update(self, wind: float = 0):
        """Update rain drop position."""
        self.y += self.speed
        self.x += self.speed * self.angle + wind


@dataclass
class SnowFlake:
    """A single snow flake."""
    x: float
    y: float
    speed: float
    size: int
    wobble_offset: float = 0
    wobble_speed: float = 0.1

    def update(self, wind: float = 0):
        """Update snow flake position."""
        self.y += self.speed
        self.wobble_offset += self.wobble_speed
        self.x += math.sin(self.wobble_offset) * 0.5 + wind


@dataclass
class WeatherConfig:
    """Configuration for weather effects."""
    intensity: str = 'moderate'
    wind: float = 0.0  # Wind strength (-1 to 1)
    color_tint: Tuple[int, int, int, int] = (200, 200, 220, 255)
    particle_count: int = 100
    speed_min: float = 2.0
    speed_max: float = 5.0

    @classmethod
    def light_rain(cls) -> 'WeatherConfig':
        return cls(
            intensity='light',
            wind=0.1,
            color_tint=(180, 190, 210, 200),
            particle_count=30,
            speed_min=3.0,
            speed_max=5.0
        )

    @classmethod
    def heavy_rain(cls) -> 'WeatherConfig':
        return cls(
            intensity='heavy',
            wind=0.3,
            color_tint=(150, 160, 180, 220),
            particle_count=150,
            speed_min=5.0,
            speed_max=8.0
        )

    @classmethod
    def storm_rain(cls) -> 'WeatherConfig':
        return cls(
            intensity='storm',
            wind=0.6,
            color_tint=(100, 110, 140, 240),
            particle_count=200,
            speed_min=7.0,
            speed_max=12.0
        )

    @classmethod
    def light_snow(cls) -> 'WeatherConfig':
        return cls(
            intensity='light',
            wind=0.05,
            color_tint=(240, 245, 255, 180),
            particle_count=40,
            speed_min=0.5,
            speed_max=1.5
        )

    @classmethod
    def heavy_snow(cls) -> 'WeatherConfig':
        return cls(
            intensity='heavy',
            wind=0.2,
            color_tint=(230, 235, 250, 200),
            particle_count=120,
            speed_min=1.0,
            speed_max=2.5
        )

    @classmethod
    def blizzard(cls) -> 'WeatherConfig':
        return cls(
            intensity='storm',
            wind=0.8,
            color_tint=(220, 225, 245, 230),
            particle_count=200,
            speed_min=2.0,
            speed_max=4.0
        )


class RainEffect:
    """Rain weather effect generator."""

    def __init__(self, width: int, height: int, config: WeatherConfig = None,
                 seed: int = 42):
        """Initialize rain effect.

        Args:
            width: Canvas width
            height: Canvas height
            config: Weather configuration
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.config = config or WeatherConfig.light_rain()
        self.rng = random.Random(seed)
        self.drops: List[RainDrop] = []
        self._initialize_drops()

    def _initialize_drops(self):
        """Create initial rain drops."""
        self.drops = []
        for _ in range(self.config.particle_count):
            drop = RainDrop(
                x=self.rng.uniform(0, self.width),
                y=self.rng.uniform(-self.height, self.height),
                speed=self.rng.uniform(self.config.speed_min, self.config.speed_max),
                length=self.rng.randint(3, 8),
                angle=self.config.wind * 0.5
            )
            self.drops.append(drop)

    def update(self):
        """Update rain simulation."""
        for drop in self.drops:
            drop.update(self.config.wind)

            # Reset drops that fall off screen
            if drop.y > self.height + drop.length:
                drop.y = -drop.length
                drop.x = self.rng.uniform(-10, self.width + 10)
            if drop.x < -10:
                drop.x = self.width + 10
            elif drop.x > self.width + 10:
                drop.x = -10

    def render(self) -> Canvas:
        """Render current rain frame.

        Returns:
            Canvas with rain effect (transparent background)
        """
        canvas = Canvas(self.width, self.height)

        for drop in self.drops:
            # Draw rain drop as a line
            x1 = int(drop.x)
            y1 = int(drop.y)
            x2 = int(drop.x + drop.length * drop.angle)
            y2 = int(drop.y + drop.length)

            self._draw_raindrop(canvas, x1, y1, x2, y2)

        return canvas

    def _draw_raindrop(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int):
        """Draw a single rain drop."""
        color = self.config.color_tint

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Fade alpha toward end of drop
                alpha = int(color[3] * (1 - t * 0.5))
                drop_color = (color[0], color[1], color[2], alpha)
                canvas.set_pixel_solid(x, y, drop_color)

    def render_animation(self, frames: int = 8) -> List[Canvas]:
        """Render multiple frames of rain animation.

        Args:
            frames: Number of frames to generate

        Returns:
            List of Canvas frames
        """
        result = []
        for _ in range(frames):
            result.append(self.render())
            self.update()
        return result


class SnowEffect:
    """Snow weather effect generator."""

    def __init__(self, width: int, height: int, config: WeatherConfig = None,
                 seed: int = 42):
        """Initialize snow effect.

        Args:
            width: Canvas width
            height: Canvas height
            config: Weather configuration
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.config = config or WeatherConfig.light_snow()
        self.rng = random.Random(seed)
        self.flakes: List[SnowFlake] = []
        self._initialize_flakes()

    def _initialize_flakes(self):
        """Create initial snow flakes."""
        self.flakes = []
        for _ in range(self.config.particle_count):
            flake = SnowFlake(
                x=self.rng.uniform(0, self.width),
                y=self.rng.uniform(-self.height, self.height),
                speed=self.rng.uniform(self.config.speed_min, self.config.speed_max),
                size=self.rng.randint(1, 3),
                wobble_offset=self.rng.uniform(0, math.pi * 2),
                wobble_speed=self.rng.uniform(0.05, 0.15)
            )
            self.flakes.append(flake)

    def update(self):
        """Update snow simulation."""
        for flake in self.flakes:
            flake.update(self.config.wind)

            # Reset flakes that fall off screen
            if flake.y > self.height + flake.size:
                flake.y = -flake.size
                flake.x = self.rng.uniform(0, self.width)

            # Wrap horizontally
            if flake.x < -5:
                flake.x = self.width + 5
            elif flake.x > self.width + 5:
                flake.x = -5

    def render(self) -> Canvas:
        """Render current snow frame.

        Returns:
            Canvas with snow effect (transparent background)
        """
        canvas = Canvas(self.width, self.height)

        for flake in self.flakes:
            x = int(flake.x)
            y = int(flake.y)

            # Draw snow flake based on size
            self._draw_snowflake(canvas, x, y, flake.size)

        return canvas

    def _draw_snowflake(self, canvas: Canvas, x: int, y: int, size: int):
        """Draw a single snow flake."""
        color = self.config.color_tint

        if size == 1:
            # Single pixel
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                canvas.set_pixel_solid(x, y, color)
        elif size == 2:
            # 2x2 with some variation
            for dx in range(2):
                for dy in range(2):
                    px, py = x + dx, y + dy
                    if 0 <= px < canvas.width and 0 <= py < canvas.height:
                        alpha = color[3] - self.rng.randint(0, 50)
                        canvas.set_pixel_solid(px, py, (color[0], color[1], color[2], max(0, alpha)))
        else:
            # Cross pattern for larger flakes
            offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in offsets:
                px, py = x + dx, y + dy
                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    canvas.set_pixel_solid(px, py, color)

    def render_animation(self, frames: int = 8) -> List[Canvas]:
        """Render multiple frames of snow animation.

        Args:
            frames: Number of frames to generate

        Returns:
            List of Canvas frames
        """
        result = []
        for _ in range(frames):
            result.append(self.render())
            self.update()
        return result


class FogEffect:
    """Fog/mist weather effect generator."""

    def __init__(self, width: int, height: int, density: float = 0.5,
                 seed: int = 42):
        """Initialize fog effect.

        Args:
            width: Canvas width
            height: Canvas height
            density: Fog density 0.0-1.0
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.density = max(0.0, min(1.0, density))
        self.rng = random.Random(seed)
        self.offset = 0.0

    def render(self, time_offset: float = 0) -> Canvas:
        """Render fog effect.

        Args:
            time_offset: Animation time offset for movement

        Returns:
            Canvas with fog overlay
        """
        canvas = Canvas(self.width, self.height)

        # Fog color based on density
        base_alpha = int(80 + self.density * 150)
        fog_color = (200, 210, 220, base_alpha)

        # Generate layered fog using noise-like patterns
        for y in range(self.height):
            # Fog is denser at bottom
            height_factor = y / self.height
            density_at_height = self.density * (0.3 + height_factor * 0.7)

            for x in range(self.width):
                # Simple noise pattern
                noise = self._fog_noise(x + time_offset * 10, y, scale=0.1)
                noise2 = self._fog_noise(x + time_offset * 5, y, scale=0.05) * 0.5

                combined = (noise + noise2) * density_at_height

                if combined > 0.2:
                    alpha = int(base_alpha * combined)
                    alpha = min(255, max(0, alpha))
                    canvas.set_pixel_solid(x, y, (fog_color[0], fog_color[1], fog_color[2], alpha))

        return canvas

    def _fog_noise(self, x: float, y: float, scale: float = 0.1) -> float:
        """Generate smooth noise for fog pattern."""
        # Simple pseudo-noise using sine waves
        return (
            math.sin(x * scale * 2.3 + y * scale * 1.7) * 0.5 +
            math.sin(x * scale * 1.5 - y * scale * 2.1) * 0.3 +
            math.sin(x * scale * 3.1 + y * scale * 0.8) * 0.2 +
            0.5
        )

    def render_animation(self, frames: int = 8, speed: float = 1.0) -> List[Canvas]:
        """Render multiple frames of fog animation.

        Args:
            frames: Number of frames to generate
            speed: Animation speed multiplier

        Returns:
            List of Canvas frames
        """
        result = []
        for i in range(frames):
            t = i / frames * speed
            result.append(self.render(time_offset=t))
        return result


class LightningEffect:
    """Lightning flash effect."""

    def __init__(self, width: int, height: int, seed: int = 42):
        """Initialize lightning effect.

        Args:
            width: Canvas width
            height: Canvas height
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

    def render_flash(self, intensity: float = 1.0) -> Canvas:
        """Render a lightning flash overlay.

        Args:
            intensity: Flash intensity 0.0-1.0

        Returns:
            Canvas with flash effect
        """
        canvas = Canvas(self.width, self.height)

        alpha = int(200 * intensity)
        flash_color = (255, 255, 255, alpha)

        # Fill with flash
        for y in range(self.height):
            for x in range(self.width):
                canvas.set_pixel_solid(x, y, flash_color)

        return canvas

    def render_bolt(self, start_x: int = None, branches: int = 3) -> Canvas:
        """Render a lightning bolt.

        Args:
            start_x: Starting x position (None for random)
            branches: Number of branch points

        Returns:
            Canvas with lightning bolt
        """
        canvas = Canvas(self.width, self.height)

        if start_x is None:
            start_x = self.rng.randint(self.width // 4, 3 * self.width // 4)

        bolt_color = (255, 255, 255, 255)
        glow_color = (200, 200, 255, 150)

        # Main bolt
        points = self._generate_bolt_points(start_x, 0, self.height, branches)

        # Draw glow first
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self._draw_thick_line(canvas, x1, y1, x2, y2, glow_color, 3)

        # Draw main bolt
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self._draw_thick_line(canvas, x1, y1, x2, y2, bolt_color, 1)

        return canvas

    def _generate_bolt_points(self, start_x: int, start_y: int,
                              end_y: int, branches: int) -> List[Tuple[int, int]]:
        """Generate points for lightning bolt path."""
        points = [(start_x, start_y)]
        current_x = start_x
        current_y = start_y

        segment_height = (end_y - start_y) // (branches + 2)

        for i in range(branches + 2):
            # Jag to the side
            offset = self.rng.randint(-15, 15)
            current_x = max(5, min(self.width - 5, current_x + offset))
            current_y += segment_height + self.rng.randint(-5, 5)
            current_y = min(current_y, end_y)
            points.append((current_x, current_y))

        return points

    def _draw_thick_line(self, canvas: Canvas, x1: int, y1: int,
                         x2: int, y2: int, color: Tuple[int, int, int, int],
                         thickness: int):
        """Draw a thick line."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            for tx in range(-thickness, thickness + 1):
                for ty in range(-thickness, thickness + 1):
                    px, py = x + tx, y + ty
                    if 0 <= px < canvas.width and 0 <= py < canvas.height:
                        canvas.set_pixel_solid(px, py, color)

    def render_sequence(self, flash_frames: int = 3) -> List[Canvas]:
        """Render a lightning flash sequence.

        Args:
            flash_frames: Duration of flash in frames

        Returns:
            List of Canvas frames
        """
        result = []

        # Initial flash
        result.append(self.render_flash(1.0))

        # Bolt
        result.append(self.render_bolt())

        # Fading flashes
        for i in range(flash_frames):
            intensity = 1.0 - (i + 1) / (flash_frames + 1)
            result.append(self.render_flash(intensity))

        # Dark frame
        result.append(Canvas(self.width, self.height))

        return result


# ==================== Lighting Effects ====================

class LightingEffect:
    """Dynamic lighting effect for environments."""

    def __init__(self, width: int, height: int, seed: int = 42):
        """Initialize lighting effect.

        Args:
            width: Canvas width
            height: Canvas height
            seed: Random seed
        """
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

    def apply_time_of_day_lighting(self, canvas: Canvas,
                                   time: str = 'day') -> Canvas:
        """Apply time-of-day lighting tint to a canvas.

        Args:
            canvas: Source canvas
            time: Time of day ('dawn', 'day', 'dusk', 'night')

        Returns:
            New Canvas with lighting applied
        """
        result = canvas.copy()

        tints = {
            'dawn': (255, 200, 180, 40),
            'day': (255, 255, 255, 0),
            'dusk': (255, 150, 100, 60),
            'night': (50, 50, 100, 80),
            'midnight': (20, 20, 60, 100),
        }

        tint = tints.get(time, tints['day'])

        if tint[3] > 0:
            for y in range(result.height):
                for x in range(result.width):
                    pixel = result.get_pixel(x, y)
                    if pixel[3] > 0:
                        # Blend with tint
                        t = tint[3] / 255
                        new_color = (
                            int(pixel[0] * (1 - t) + tint[0] * t),
                            int(pixel[1] * (1 - t) + tint[1] * t),
                            int(pixel[2] * (1 - t) + tint[2] * t),
                            pixel[3]
                        )
                        result.set_pixel_solid(x, y, new_color)

        return result

    def add_point_light(self, canvas: Canvas, x: int, y: int,
                        radius: int, color: Tuple[int, int, int, int],
                        intensity: float = 1.0) -> Canvas:
        """Add a point light source to a canvas.

        Args:
            canvas: Source canvas
            x: Light center x
            y: Light center y
            radius: Light radius
            color: Light color
            intensity: Light intensity 0.0-1.0

        Returns:
            New Canvas with lighting applied
        """
        result = canvas.copy()

        for py in range(max(0, y - radius), min(self.height, y + radius + 1)):
            for px in range(max(0, x - radius), min(self.width, x + radius + 1)):
                dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)

                if dist <= radius:
                    # Calculate light falloff
                    falloff = 1 - (dist / radius)
                    falloff = falloff ** 2 * intensity  # Quadratic falloff

                    pixel = result.get_pixel(px, py)
                    if pixel[3] > 0:
                        # Add light to pixel
                        new_color = (
                            min(255, int(pixel[0] + color[0] * falloff * 0.5)),
                            min(255, int(pixel[1] + color[1] * falloff * 0.5)),
                            min(255, int(pixel[2] + color[2] * falloff * 0.5)),
                            pixel[3]
                        )
                        result.set_pixel_solid(px, py, new_color)

        return result

    def add_ambient_occlusion(self, canvas: Canvas,
                              strength: float = 0.3) -> Canvas:
        """Add simple ambient occlusion shadows.

        Args:
            canvas: Source canvas
            strength: Shadow strength 0.0-1.0

        Returns:
            New Canvas with AO applied
        """
        result = canvas.copy()

        # Check each pixel and darken if surrounded by content
        for y in range(result.height):
            for x in range(result.width):
                pixel = result.get_pixel(x, y)
                if pixel[3] > 0:
                    # Count nearby opaque pixels
                    neighbors = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < result.width and 0 <= ny < result.height:
                                if result.get_pixel(nx, ny)[3] > 128:
                                    neighbors += 1

                    # Darken based on neighbor count
                    if neighbors >= 5:
                        darken_amount = strength * (neighbors / 8)
                        new_color = (
                            int(pixel[0] * (1 - darken_amount)),
                            int(pixel[1] * (1 - darken_amount)),
                            int(pixel[2] * (1 - darken_amount)),
                            pixel[3]
                        )
                        result.set_pixel_solid(x, y, new_color)

        return result

    def add_vignette(self, canvas: Canvas, strength: float = 0.3) -> Canvas:
        """Add vignette (darkened corners) effect.

        Args:
            canvas: Source canvas
            strength: Vignette strength 0.0-1.0

        Returns:
            New Canvas with vignette
        """
        result = canvas.copy()

        cx = self.width / 2
        cy = self.height / 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        for y in range(result.height):
            for x in range(result.width):
                pixel = result.get_pixel(x, y)
                if pixel[3] > 0:
                    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    factor = (dist / max_dist) ** 2 * strength

                    new_color = (
                        int(pixel[0] * (1 - factor)),
                        int(pixel[1] * (1 - factor)),
                        int(pixel[2] * (1 - factor)),
                        pixel[3]
                    )
                    result.set_pixel_solid(x, y, new_color)

        return result


# ==================== Convenience Functions ====================

def create_rain_overlay(width: int, height: int, intensity: str = 'moderate',
                        seed: int = 42) -> Canvas:
    """Create a single rain overlay frame.

    Args:
        width: Canvas width
        height: Canvas height
        intensity: Rain intensity ('light', 'moderate', 'heavy', 'storm')
        seed: Random seed

    Returns:
        Canvas with rain overlay
    """
    configs = {
        'light': WeatherConfig.light_rain(),
        'moderate': WeatherConfig(particle_count=60, speed_min=3.0, speed_max=6.0),
        'heavy': WeatherConfig.heavy_rain(),
        'storm': WeatherConfig.storm_rain(),
    }
    config = configs.get(intensity, configs['moderate'])

    rain = RainEffect(width, height, config, seed)
    return rain.render()


def create_snow_overlay(width: int, height: int, intensity: str = 'moderate',
                        seed: int = 42) -> Canvas:
    """Create a single snow overlay frame.

    Args:
        width: Canvas width
        height: Canvas height
        intensity: Snow intensity ('light', 'moderate', 'heavy', 'blizzard')
        seed: Random seed

    Returns:
        Canvas with snow overlay
    """
    configs = {
        'light': WeatherConfig.light_snow(),
        'moderate': WeatherConfig(particle_count=80, speed_min=0.8, speed_max=2.0,
                                  color_tint=(240, 245, 255, 200)),
        'heavy': WeatherConfig.heavy_snow(),
        'blizzard': WeatherConfig.blizzard(),
    }
    config = configs.get(intensity, configs['moderate'])

    snow = SnowEffect(width, height, config, seed)
    return snow.render()


def create_fog_overlay(width: int, height: int, density: float = 0.5,
                       seed: int = 42) -> Canvas:
    """Create a fog overlay.

    Args:
        width: Canvas width
        height: Canvas height
        density: Fog density 0.0-1.0
        seed: Random seed

    Returns:
        Canvas with fog overlay
    """
    fog = FogEffect(width, height, density, seed)
    return fog.render()


def apply_weather_to_scene(scene: Canvas, weather_type: str,
                           intensity: str = 'moderate',
                           seed: int = 42) -> Canvas:
    """Apply weather effect to a scene.

    Args:
        scene: Source scene canvas
        weather_type: Type of weather ('rain', 'snow', 'fog')
        intensity: Weather intensity
        seed: Random seed

    Returns:
        New Canvas with weather applied
    """
    result = scene.copy()

    if weather_type == 'rain':
        overlay = create_rain_overlay(scene.width, scene.height, intensity, seed)
    elif weather_type == 'snow':
        overlay = create_snow_overlay(scene.width, scene.height, intensity, seed)
    elif weather_type == 'fog':
        density_map = {'light': 0.3, 'moderate': 0.5, 'heavy': 0.7, 'storm': 0.9}
        density = density_map.get(intensity, 0.5)
        overlay = create_fog_overlay(scene.width, scene.height, density, seed)
    else:
        return result

    # Composite overlay onto scene
    result.blit(overlay, 0, 0)
    return result


def list_weather_types() -> List[str]:
    """List available weather types."""
    return ['rain', 'snow', 'fog', 'lightning']


def list_intensity_levels() -> List[str]:
    """List available intensity levels."""
    return [i.value for i in WeatherIntensity]
