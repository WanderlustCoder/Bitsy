"""
Particles - Particle system for visual effects.

Provides:
- Individual Particle with physics properties
- ParticleEmitter for spawning and managing particles
- Pre-built effect presets (sparks, explosions, magic, etc.)
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.animation import Animation


class ParticleShape(Enum):
    """Available particle shapes."""
    PIXEL = 'pixel'
    SQUARE = 'square'
    CIRCLE = 'circle'
    DIAMOND = 'diamond'
    STAR = 'star'
    LINE = 'line'
    SPARK = 'spark'


@dataclass
class Particle:
    """A single particle in the particle system.

    Attributes:
        x, y: Position
        vx, vy: Velocity
        ax, ay: Acceleration
        life: Current life remaining
        max_life: Maximum lifetime
        size: Particle size
        color: Current color (RGBA)
        rotation: Current rotation (degrees)
        angular_velocity: Rotation speed (degrees/sec)
        shape: Particle shape
        alpha: Current alpha (0-255)
    """

    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    life: float = 1.0
    max_life: float = 1.0
    size: float = 2.0
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    rotation: float = 0.0
    angular_velocity: float = 0.0
    shape: ParticleShape = ParticleShape.PIXEL
    alpha: float = 255.0

    # For color interpolation
    start_color: Tuple[int, int, int, int] = None
    end_color: Tuple[int, int, int, int] = None

    # For size interpolation
    start_size: float = None
    end_size: float = None

    def __post_init__(self):
        if self.start_color is None:
            self.start_color = self.color
        if self.end_color is None:
            self.end_color = self.color
        if self.start_size is None:
            self.start_size = self.size
        if self.end_size is None:
            self.end_size = self.size

    @property
    def alive(self) -> bool:
        """Check if particle is still alive."""
        return self.life > 0

    @property
    def life_ratio(self) -> float:
        """Get life remaining as ratio (1.0 = full, 0.0 = dead)."""
        return max(0.0, self.life / self.max_life) if self.max_life > 0 else 0.0

    def update(self, dt: float) -> None:
        """Update particle state.

        Args:
            dt: Delta time in seconds
        """
        # Apply acceleration
        self.vx += self.ax * dt
        self.vy += self.ay * dt

        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply rotation
        self.rotation += self.angular_velocity * dt

        # Update life
        self.life -= dt

        # Interpolate color
        t = 1.0 - self.life_ratio
        self.color = self._lerp_color(self.start_color, self.end_color, t)

        # Interpolate size
        self.size = self.start_size + (self.end_size - self.start_size) * t

        # Update alpha based on life
        self.alpha = self.color[3] * self.life_ratio

    def _lerp_color(self, c1: Tuple[int, int, int, int],
                    c2: Tuple[int, int, int, int],
                    t: float) -> Tuple[int, int, int, int]:
        """Linearly interpolate between colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )


@dataclass
class EmitterConfig:
    """Configuration for a particle emitter.

    Attributes:
        emission_rate: Particles per second
        max_particles: Maximum particles alive at once
        lifetime: Particle lifetime range (min, max)
        speed: Initial speed range (min, max)
        direction: Emission direction in degrees
        spread: Spread angle in degrees (360 = all directions)
        gravity: Gravity acceleration (usually positive for down)
        size: Particle size range (min, max)
        size_end: End size range (min, max) - for size over lifetime
        colors: List of colors to interpolate over lifetime
        shapes: List of possible particle shapes
        rotation_speed: Angular velocity range (min, max)
        drag: Velocity drag factor (0-1, 1 = no drag)
        fade_out: Whether particles fade out over lifetime
        burst_count: Particles per burst (0 = continuous emission)
    """

    emission_rate: float = 10.0
    max_particles: int = 100
    lifetime: Tuple[float, float] = (0.5, 1.5)
    speed: Tuple[float, float] = (50.0, 100.0)
    direction: float = 270.0  # Up by default
    spread: float = 30.0
    gravity: float = 0.0
    size: Tuple[float, float] = (2.0, 4.0)
    size_end: Tuple[float, float] = None  # None = same as start
    colors: List[Tuple[int, int, int, int]] = None
    shapes: List[ParticleShape] = None
    rotation_speed: Tuple[float, float] = (0.0, 0.0)
    drag: float = 1.0
    fade_out: bool = True
    burst_count: int = 0

    def __post_init__(self):
        if self.colors is None:
            self.colors = [(255, 255, 255, 255)]
        if self.shapes is None:
            self.shapes = [ParticleShape.PIXEL]
        if self.size_end is None:
            self.size_end = self.size


class ParticleEmitter:
    """Emits and manages particles.

    Can emit continuously or in bursts.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0,
                 config: Optional[EmitterConfig] = None,
                 seed: int = 42):
        """Initialize emitter.

        Args:
            x: Emitter X position
            y: Emitter Y position
            config: Emitter configuration
            seed: Random seed for reproducibility
        """
        self.x = x
        self.y = y
        self.config = config or EmitterConfig()
        self.seed = seed
        self.rng = random.Random(seed)

        self.particles: List[Particle] = []
        self._emit_accumulator = 0.0
        self.active = True
        self.elapsed_time = 0.0

    def emit(self, count: int = 1) -> None:
        """Emit a specific number of particles.

        Args:
            count: Number of particles to emit
        """
        for _ in range(count):
            if len(self.particles) >= self.config.max_particles:
                break
            self.particles.append(self._create_particle())

    def burst(self, count: Optional[int] = None) -> None:
        """Emit a burst of particles.

        Args:
            count: Number of particles (uses config.burst_count if None)
        """
        burst_count = count or self.config.burst_count or 10
        self.emit(burst_count)

    def update(self, dt: float) -> None:
        """Update emitter and all particles.

        Args:
            dt: Delta time in seconds
        """
        self.elapsed_time += dt

        # Continuous emission
        if self.active and self.config.burst_count == 0:
            self._emit_accumulator += self.config.emission_rate * dt
            while self._emit_accumulator >= 1.0:
                self.emit(1)
                self._emit_accumulator -= 1.0

        # Update particles
        for particle in self.particles:
            # Apply drag
            particle.vx *= self.config.drag
            particle.vy *= self.config.drag

            # Apply gravity
            particle.ay = self.config.gravity

            particle.update(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all particles to canvas.

        Args:
            canvas: Target canvas
            offset_x: X offset for rendering
            offset_y: Y offset for rendering
        """
        for particle in self.particles:
            self._render_particle(canvas, particle, offset_x, offset_y)

    def _create_particle(self) -> Particle:
        """Create a new particle with randomized properties."""
        cfg = self.config

        # Random lifetime
        lifetime = self.rng.uniform(*cfg.lifetime)

        # Random direction within spread
        angle_rad = math.radians(
            cfg.direction + self.rng.uniform(-cfg.spread / 2, cfg.spread / 2)
        )
        speed = self.rng.uniform(*cfg.speed)
        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed

        # Random size
        start_size = self.rng.uniform(*cfg.size)
        end_size = self.rng.uniform(*cfg.size_end)

        # Colors
        if len(cfg.colors) == 1:
            start_color = cfg.colors[0]
            end_color = cfg.colors[0]
        else:
            start_color = cfg.colors[0]
            end_color = cfg.colors[-1]

        # Modify alpha if fade_out
        if cfg.fade_out:
            end_color = (end_color[0], end_color[1], end_color[2], 0)

        # Random rotation
        angular_vel = self.rng.uniform(*cfg.rotation_speed)

        # Random shape
        shape = self.rng.choice(cfg.shapes)

        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=lifetime,
            max_life=lifetime,
            size=start_size,
            start_size=start_size,
            end_size=end_size,
            color=start_color,
            start_color=start_color,
            end_color=end_color,
            angular_velocity=angular_vel,
            shape=shape,
        )

    def _render_particle(self, canvas: Canvas, particle: Particle,
                         offset_x: int, offset_y: int) -> None:
        """Render a single particle."""
        px = int(particle.x) + offset_x
        py = int(particle.y) + offset_y
        size = max(1, int(particle.size))
        alpha = int(particle.alpha)

        # Get color with current alpha
        color = (
            particle.color[0],
            particle.color[1],
            particle.color[2],
            alpha
        )

        if particle.shape == ParticleShape.PIXEL:
            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                canvas.set_pixel(px, py, color)

        elif particle.shape == ParticleShape.SQUARE:
            half = size // 2
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    x, y = px + dx, py + dy
                    if 0 <= x < canvas.width and 0 <= y < canvas.height:
                        canvas.set_pixel(x, y, color)

        elif particle.shape == ParticleShape.CIRCLE:
            half = size // 2
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if dx * dx + dy * dy <= half * half:
                        x, y = px + dx, py + dy
                        if 0 <= x < canvas.width and 0 <= y < canvas.height:
                            canvas.set_pixel(x, y, color)

        elif particle.shape == ParticleShape.DIAMOND:
            half = size // 2
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if abs(dx) + abs(dy) <= half:
                        x, y = px + dx, py + dy
                        if 0 <= x < canvas.width and 0 <= y < canvas.height:
                            canvas.set_pixel(x, y, color)

        elif particle.shape == ParticleShape.STAR:
            # Simple 4-point star
            half = size // 2
            for i in range(-half, half + 1):
                # Horizontal
                x, y = px + i, py
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    canvas.set_pixel(x, y, color)
                # Vertical
                x, y = px, py + i
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    canvas.set_pixel(x, y, color)

        elif particle.shape == ParticleShape.LINE:
            # Line in direction of velocity
            length = size
            if particle.vx != 0 or particle.vy != 0:
                mag = math.sqrt(particle.vx ** 2 + particle.vy ** 2)
                dx = particle.vx / mag
                dy = particle.vy / mag
                for i in range(int(length)):
                    x = int(px - dx * i)
                    y = int(py - dy * i)
                    if 0 <= x < canvas.width and 0 <= y < canvas.height:
                        canvas.set_pixel(x, y, color)

        elif particle.shape == ParticleShape.SPARK:
            # Spark shape - bright center with trail
            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                canvas.set_pixel(px, py, color)
            # Trail
            if particle.vx != 0 or particle.vy != 0:
                mag = math.sqrt(particle.vx ** 2 + particle.vy ** 2)
                dx = particle.vx / mag
                dy = particle.vy / mag
                for i in range(1, min(size, 4)):
                    x = int(px - dx * i)
                    y = int(py - dy * i)
                    trail_alpha = alpha * (1 - i / size)
                    trail_color = (color[0], color[1], color[2], int(trail_alpha))
                    if 0 <= x < canvas.width and 0 <= y < canvas.height:
                        canvas.set_pixel(x, y, trail_color)

    @property
    def particle_count(self) -> int:
        """Get current number of active particles."""
        return len(self.particles)

    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear()

    def stop(self) -> None:
        """Stop emitting new particles."""
        self.active = False

    def start(self) -> None:
        """Start emitting particles."""
        self.active = True


class ParticleSystem:
    """Manages multiple particle emitters."""

    def __init__(self):
        self.emitters: List[ParticleEmitter] = []

    def add_emitter(self, emitter: ParticleEmitter) -> None:
        """Add an emitter to the system."""
        self.emitters.append(emitter)

    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """Remove an emitter from the system."""
        if emitter in self.emitters:
            self.emitters.remove(emitter)

    def update(self, dt: float) -> None:
        """Update all emitters."""
        for emitter in self.emitters:
            emitter.update(dt)

    def render(self, canvas: Canvas, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all emitters."""
        for emitter in self.emitters:
            emitter.render(canvas, offset_x, offset_y)

    def clear(self) -> None:
        """Clear all emitters and particles."""
        for emitter in self.emitters:
            emitter.clear()
        self.emitters.clear()

    def render_animation(self, width: int, height: int,
                         duration: float, fps: int = 12) -> Animation:
        """Render particle system to an animation.

        Args:
            width: Frame width
            height: Frame height
            duration: Animation duration in seconds
            fps: Frames per second

        Returns:
            Animation with rendered frames
        """
        anim = Animation("particles", fps)
        frame_count = int(duration * fps)
        dt = 1.0 / fps

        for _ in range(frame_count):
            canvas = Canvas(width, height, (0, 0, 0, 0))
            self.render(canvas)
            anim.add_frame(canvas, 1.0)
            self.update(dt)

        return anim


# =============================================================================
# Effect Presets
# =============================================================================

def create_spark_emitter(x: float = 0, y: float = 0,
                         seed: int = 42) -> ParticleEmitter:
    """Create a spark/hit effect emitter."""
    config = EmitterConfig(
        emission_rate=0,
        burst_count=12,
        max_particles=50,
        lifetime=(0.2, 0.4),
        speed=(80, 150),
        direction=270,
        spread=360,
        gravity=200,
        size=(1, 2),
        size_end=(0, 1),
        colors=[
            (255, 255, 200, 255),
            (255, 200, 100, 255),
            (255, 100, 50, 128),
        ],
        shapes=[ParticleShape.SPARK, ParticleShape.PIXEL],
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_explosion_emitter(x: float = 0, y: float = 0,
                             seed: int = 42) -> ParticleEmitter:
    """Create an explosion effect emitter."""
    config = EmitterConfig(
        emission_rate=0,
        burst_count=30,
        max_particles=100,
        lifetime=(0.3, 0.8),
        speed=(60, 120),
        direction=270,
        spread=360,
        gravity=50,
        size=(2, 5),
        size_end=(1, 2),
        colors=[
            (255, 255, 200, 255),
            (255, 200, 50, 255),
            (255, 100, 20, 200),
            (100, 50, 20, 100),
        ],
        shapes=[ParticleShape.CIRCLE, ParticleShape.SQUARE],
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_magic_emitter(x: float = 0, y: float = 0,
                         seed: int = 42) -> ParticleEmitter:
    """Create a magic/sparkle effect emitter."""
    config = EmitterConfig(
        emission_rate=15,
        max_particles=50,
        lifetime=(0.5, 1.0),
        speed=(20, 40),
        direction=270,
        spread=60,
        gravity=-20,  # Float upward
        size=(1, 3),
        size_end=(0, 1),
        colors=[
            (200, 150, 255, 255),
            (150, 100, 255, 200),
            (100, 50, 200, 100),
        ],
        shapes=[ParticleShape.DIAMOND, ParticleShape.STAR],
        rotation_speed=(-180, 180),
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_fire_emitter(x: float = 0, y: float = 0,
                        seed: int = 42) -> ParticleEmitter:
    """Create a fire effect emitter."""
    config = EmitterConfig(
        emission_rate=20,
        max_particles=60,
        lifetime=(0.4, 0.8),
        speed=(30, 60),
        direction=270,  # Up
        spread=30,
        gravity=-50,  # Rise
        size=(2, 4),
        size_end=(1, 2),
        colors=[
            (255, 255, 150, 255),
            (255, 200, 50, 255),
            (255, 100, 20, 200),
            (150, 50, 10, 50),
        ],
        shapes=[ParticleShape.CIRCLE, ParticleShape.SQUARE],
        drag=0.95,
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_smoke_emitter(x: float = 0, y: float = 0,
                         seed: int = 42) -> ParticleEmitter:
    """Create a smoke effect emitter."""
    config = EmitterConfig(
        emission_rate=8,
        max_particles=40,
        lifetime=(1.0, 2.0),
        speed=(10, 30),
        direction=270,
        spread=40,
        gravity=-15,
        size=(3, 6),
        size_end=(6, 10),
        colors=[
            (100, 100, 100, 150),
            (80, 80, 80, 100),
            (60, 60, 60, 50),
        ],
        shapes=[ParticleShape.CIRCLE],
        drag=0.98,
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_rain_emitter(x: float = 0, y: float = 0,
                        width: int = 100, seed: int = 42) -> ParticleEmitter:
    """Create a rain effect emitter."""
    config = EmitterConfig(
        emission_rate=30,
        max_particles=200,
        lifetime=(0.5, 1.0),
        speed=(150, 200),
        direction=100,  # Slightly angled down-right
        spread=10,
        gravity=300,
        size=(1, 3),
        colors=[(150, 180, 255, 200), (100, 150, 255, 150)],
        shapes=[ParticleShape.LINE],
        fade_out=False,
    )
    emitter = ParticleEmitter(x, y, config, seed)
    # Override position to span width
    emitter._original_x = x
    emitter._width = width
    return emitter


def create_snow_emitter(x: float = 0, y: float = 0,
                        width: int = 100, seed: int = 42) -> ParticleEmitter:
    """Create a snow effect emitter."""
    config = EmitterConfig(
        emission_rate=10,
        max_particles=100,
        lifetime=(2.0, 4.0),
        speed=(10, 30),
        direction=90,  # Down
        spread=60,
        gravity=20,
        size=(1, 2),
        colors=[(255, 255, 255, 220), (240, 240, 255, 180)],
        shapes=[ParticleShape.CIRCLE, ParticleShape.PIXEL],
        rotation_speed=(-90, 90),
        drag=0.99,
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_dust_emitter(x: float = 0, y: float = 0,
                        seed: int = 42) -> ParticleEmitter:
    """Create a dust cloud effect emitter."""
    config = EmitterConfig(
        emission_rate=0,
        burst_count=15,
        max_particles=30,
        lifetime=(0.3, 0.6),
        speed=(30, 60),
        direction=270,
        spread=120,
        gravity=100,
        size=(1, 3),
        size_end=(2, 4),
        colors=[
            (180, 160, 140, 150),
            (150, 130, 110, 100),
            (120, 100, 80, 50),
        ],
        shapes=[ParticleShape.CIRCLE],
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_heal_emitter(x: float = 0, y: float = 0,
                        seed: int = 42) -> ParticleEmitter:
    """Create a healing effect emitter."""
    config = EmitterConfig(
        emission_rate=12,
        max_particles=40,
        lifetime=(0.6, 1.2),
        speed=(20, 40),
        direction=270,
        spread=90,
        gravity=-30,
        size=(2, 3),
        size_end=(0, 1),
        colors=[
            (100, 255, 150, 255),
            (50, 255, 100, 200),
            (20, 200, 80, 100),
        ],
        shapes=[ParticleShape.DIAMOND, ParticleShape.CIRCLE],
        rotation_speed=(-60, 60),
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


def create_lightning_emitter(x: float = 0, y: float = 0,
                             seed: int = 42) -> ParticleEmitter:
    """Create a lightning/electric effect emitter."""
    config = EmitterConfig(
        emission_rate=0,
        burst_count=8,
        max_particles=30,
        lifetime=(0.1, 0.3),
        speed=(100, 200),
        direction=0,
        spread=360,
        gravity=0,
        size=(1, 2),
        colors=[
            (255, 255, 255, 255),
            (200, 220, 255, 255),
            (150, 180, 255, 200),
        ],
        shapes=[ParticleShape.SPARK, ParticleShape.LINE],
        fade_out=True,
    )
    return ParticleEmitter(x, y, config, seed)


# =============================================================================
# Effect Presets Registry
# =============================================================================

EFFECT_PRESETS = {
    'spark': create_spark_emitter,
    'explosion': create_explosion_emitter,
    'magic': create_magic_emitter,
    'fire': create_fire_emitter,
    'smoke': create_smoke_emitter,
    'rain': create_rain_emitter,
    'snow': create_snow_emitter,
    'dust': create_dust_emitter,
    'heal': create_heal_emitter,
    'lightning': create_lightning_emitter,
}


def create_effect(name: str, x: float = 0, y: float = 0,
                  seed: int = 42, **kwargs) -> ParticleEmitter:
    """Create an effect emitter by preset name.

    Args:
        name: Preset name
        x: Emitter X position
        y: Emitter Y position
        seed: Random seed
        **kwargs: Additional arguments for specific presets

    Returns:
        Configured ParticleEmitter
    """
    if name not in EFFECT_PRESETS:
        available = ', '.join(sorted(EFFECT_PRESETS.keys()))
        raise ValueError(f"Unknown effect '{name}'. Available: {available}")

    return EFFECT_PRESETS[name](x, y, seed=seed, **kwargs)


def list_effects() -> List[str]:
    """Get list of available effect preset names."""
    return sorted(EFFECT_PRESETS.keys())
