#!/usr/bin/env python3
"""
Effects Demo - Demonstrates Bitsy's visual effects system.

Shows:
- Particle effects (spark, explosion, magic, fire, etc.)
- Motion trails (line, ribbon, afterimage)
- Screen effects (shake, flash, fade, vignette)
"""

import sys
import os
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.animation import Animation
from effects import (
    # Particles
    ParticleEmitter,
    ParticleSystem,
    create_effect,
    list_effects,
    ParticleShape,
    EmitterConfig,
    # Trails
    Trail,
    LineTrail,
    RibbonTrail,
    SpeedLines,
    # Screen
    ScreenShake,
    ScreenFlash,
    ScreenFade,
    Vignette,
    ColorFilter,
    Scanlines,
    BlendMode,
    ScreenEffects,
)


def create_particle_effects_showcase() -> Canvas:
    """Create a showcase of all particle effect presets."""
    effects_to_show = ['spark', 'explosion', 'magic', 'fire', 'smoke', 'dust', 'heal', 'lightning']

    frame_size = 48
    padding = 4
    cols = 4
    rows = 2

    # Create canvas
    canvas = Canvas(
        (frame_size + padding) * cols + padding,
        (frame_size + padding) * rows + padding,
        (30, 30, 40, 255)
    )

    for idx, effect_name in enumerate(effects_to_show):
        col = idx % cols
        row = idx // cols
        x_offset = padding + col * (frame_size + padding)
        y_offset = padding + row * (frame_size + padding)

        # Draw frame background
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

        # Create and simulate effect
        emitter = create_effect(effect_name, frame_size // 2, frame_size // 2, seed=42 + idx)

        # Burst for burst effects, let continuous ones run
        if effect_name in ('spark', 'explosion', 'dust', 'lightning'):
            emitter.burst()

        # Simulate a few frames
        for _ in range(8):
            emitter.update(1.0 / 12.0)

        # Render to a temp canvas then blit
        temp = Canvas(frame_size, frame_size, (0, 0, 0, 0))
        emitter.render(temp)

        # Blit with offset
        for y in range(frame_size):
            for x in range(frame_size):
                px = temp.pixels[y][x]
                if px[3] > 0:
                    canvas.set_pixel(x_offset + x, y_offset + y, px)

    return canvas


def create_particle_animation(effect_name: str, frames: int = 12) -> Animation:
    """Create an animation of a particle effect."""
    size = 64
    fps = 12

    anim = Animation(effect_name, fps)
    emitter = create_effect(effect_name, size // 2, size // 2, seed=42)

    # Burst for burst effects
    if effect_name in ('spark', 'explosion', 'dust', 'lightning'):
        emitter.burst()

    dt = 1.0 / fps
    for _ in range(frames):
        canvas = Canvas(size, size, (20, 20, 30, 255))
        emitter.render(canvas)
        anim.add_frame(canvas, 1.0)
        emitter.update(dt)

    return anim


def create_trail_demo() -> Canvas:
    """Create a demonstration of different trail types."""
    width = 128
    height = 64
    canvas = Canvas(width, height, (30, 30, 40, 255))

    # Line trail - sine wave
    line_trail = LineTrail(max_length=30, lifetime=0.5, thickness=1)
    line_trail.color = (100, 200, 255, 255)

    for i in range(30):
        x = 10 + i * 3
        y = 20 + math.sin(i * 0.3) * 10
        line_trail.add_point(x, y)

    line_trail.render(canvas)

    # Ribbon trail - arc
    ribbon_trail = RibbonTrail(max_length=20, lifetime=0.5, start_width=1, end_width=4)
    ribbon_trail.color = (255, 150, 100, 255)

    for i in range(20):
        angle = math.radians(i * 9)
        x = 100 + math.cos(angle) * 20
        y = 32 + math.sin(angle) * 15
        ribbon_trail.add_point(x, y)

    ribbon_trail.render(canvas)

    return canvas


def create_speed_lines_demo() -> Canvas:
    """Create a speed lines effect demonstration."""
    width = 64
    height = 64
    canvas = Canvas(width, height, (30, 30, 40, 255))

    # Create speed lines going left (movement to right)
    speed_lines = SpeedLines(
        num_lines=15,
        length=25,
        direction=180,  # Left
        spread=30,
        seed=42
    )

    speed_lines.render(canvas, width // 2, height // 2, (200, 220, 255, 200))

    return canvas


def create_screen_flash_demo() -> Canvas:
    """Create a demonstration of screen flash effects."""
    frame_size = 48
    padding = 4

    # Show different flash states
    flash_configs = [
        ('White hit', (255, 255, 255, 200), 0.0),
        ('White mid', (255, 255, 255, 200), 0.05),
        ('Red damage', (255, 50, 50, 180), 0.0),
        ('Green heal', (50, 255, 100, 150), 0.0),
    ]

    cols = 4
    canvas = Canvas(
        (frame_size + padding) * cols + padding,
        frame_size + padding * 2,
        (30, 30, 40, 255)
    )

    for idx, (name, color, elapsed) in enumerate(flash_configs):
        x_offset = padding + idx * (frame_size + padding)
        y_offset = padding

        # Draw base scene
        for y in range(frame_size):
            for x in range(frame_size):
                # Simple gradient background
                gray = 60 + (y * 40 // frame_size)
                canvas.set_pixel(x_offset + x, y_offset + y, (gray, gray, gray + 10, 255))

        # Draw a simple shape
        cx, cy = frame_size // 2, frame_size // 2
        for dy in range(-8, 9):
            for dx in range(-8, 9):
                if dx * dx + dy * dy <= 64:
                    canvas.set_pixel(x_offset + cx + dx, y_offset + cy + dy, (100, 150, 200, 255))

        # Apply flash effect
        flash = ScreenFlash(color=color, duration=0.1)
        flash.elapsed = elapsed
        flash.active = True

        # Create temp canvas for flash
        temp = Canvas(frame_size, frame_size)
        for y in range(frame_size):
            for x in range(frame_size):
                temp.pixels[y][x] = canvas.pixels[y_offset + y][x_offset + x]

        flash.apply(temp)

        # Copy back
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, temp.pixels[y][x])

    return canvas


def create_vignette_demo() -> Canvas:
    """Create a demonstration of vignette effect."""
    width = 96
    height = 64
    canvas = Canvas(width, height)

    # Draw a colorful scene
    for y in range(height):
        for x in range(width):
            r = int(100 + math.sin(x * 0.1) * 50)
            g = int(100 + math.sin(y * 0.15) * 50)
            b = int(150 + math.sin((x + y) * 0.08) * 50)
            canvas.set_pixel(x, y, (r, g, b, 255))

    # Apply vignette
    vignette = Vignette(intensity=0.7, radius=0.5)
    vignette.apply(canvas)

    return canvas


def create_filter_comparison() -> Canvas:
    """Create a comparison of different color filters."""
    base_size = 48
    padding = 4

    filters = [
        ('Original', None),
        ('Sepia', ColorFilter((180, 140, 100, 255), BlendMode.MULTIPLY)),
        ('Night', ColorFilter((80, 100, 180, 255), BlendMode.MULTIPLY)),
        ('Warm', ColorFilter((255, 200, 150, 255), BlendMode.MULTIPLY)),
    ]

    cols = len(filters)
    canvas = Canvas(
        (base_size + padding) * cols + padding,
        base_size + padding * 2,
        (30, 30, 40, 255)
    )

    for idx, (name, color_filter) in enumerate(filters):
        x_offset = padding + idx * (base_size + padding)
        y_offset = padding

        # Create base scene
        temp = Canvas(base_size, base_size)
        for y in range(base_size):
            for x in range(base_size):
                # Gradient with some color
                r = 80 + x * 3
                g = 120 + y * 2
                b = 100
                temp.set_pixel(x, y, (r, g, b, 255))

        # Draw a shape
        cx, cy = base_size // 2, base_size // 2
        for dy in range(-10, 11):
            for dx in range(-10, 11):
                if dx * dx + dy * dy <= 100:
                    temp.set_pixel(cx + dx, cy + dy, (200, 180, 150, 255))

        # Apply filter
        if color_filter:
            color_filter.apply(temp)

        # Copy to main canvas
        for y in range(base_size):
            for x in range(base_size):
                canvas.set_pixel(x_offset + x, y_offset + y, temp.pixels[y][x])

    return canvas


def create_scanlines_demo() -> Canvas:
    """Create a CRT scanlines effect demonstration."""
    width = 64
    height = 48

    # Create without scanlines
    original = Canvas(width, height)
    for y in range(height):
        for x in range(width):
            r = 100 + int(math.sin(x * 0.2) * 50)
            g = 150
            b = 100 + int(math.sin(y * 0.2) * 50)
            original.set_pixel(x, y, (r, g, b, 255))

    # Create with scanlines
    with_scanlines = original.copy()
    scanlines = Scanlines(spacing=2, intensity=0.4)
    scanlines.apply(with_scanlines)

    # Combine side by side
    padding = 4
    result = Canvas(width * 2 + padding * 3, height + padding * 2, (30, 30, 40, 255))
    result.blit(original, padding, padding)
    result.blit(with_scanlines, width + padding * 2, padding)

    return result


def create_particle_shapes_demo() -> Canvas:
    """Show all available particle shapes."""
    shapes = [
        ParticleShape.PIXEL,
        ParticleShape.SQUARE,
        ParticleShape.CIRCLE,
        ParticleShape.DIAMOND,
        ParticleShape.STAR,
    ]

    frame_size = 32
    padding = 4
    cols = len(shapes)

    canvas = Canvas(
        (frame_size + padding) * cols + padding,
        frame_size + padding * 2,
        (30, 30, 40, 255)
    )

    for idx, shape in enumerate(shapes):
        x_offset = padding + idx * (frame_size + padding)
        y_offset = padding

        # Draw background
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

        # Create emitter with this shape
        config = EmitterConfig(
            emission_rate=0,
            burst_count=8,
            lifetime=(0.8, 1.0),
            speed=(20, 40),
            direction=270,
            spread=360,
            size=(3, 5),
            colors=[(255, 200, 100, 255), (255, 100, 50, 200)],
            shapes=[shape],
            fade_out=True,
        )
        emitter = ParticleEmitter(frame_size // 2, frame_size // 2, config, seed=42)
        emitter.burst()

        # Simulate
        for _ in range(6):
            emitter.update(1.0 / 12.0)

        # Render
        temp = Canvas(frame_size, frame_size, (0, 0, 0, 0))
        emitter.render(temp)

        for y in range(frame_size):
            for x in range(frame_size):
                px = temp.pixels[y][x]
                if px[3] > 0:
                    canvas.set_pixel(x_offset + x, y_offset + y, px)

    return canvas


def main():
    print("Bitsy - Effects System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Particle effects showcase
    print("\n1. Creating particle effects showcase...")
    particles = create_particle_effects_showcase()
    particles.save(os.path.join(output_dir, "particle_effects.png"))
    particles.scale(2).save(os.path.join(output_dir, "particle_effects_2x.png"))
    print(f"   Available effects: {list_effects()}")
    print("   Saved: output/particle_effects.png")

    # Particle animation (explosion)
    print("\n2. Creating explosion animation...")
    explosion_anim = create_particle_animation('explosion', frames=16)
    explosion_anim.save_spritesheet(os.path.join(output_dir, "explosion_anim.png"), columns=8)
    print("   Saved: output/explosion_anim.png")

    # Trail effects
    print("\n3. Creating trail effects demo...")
    trails = create_trail_demo()
    trails.save(os.path.join(output_dir, "trail_effects.png"))
    trails.scale(2).save(os.path.join(output_dir, "trail_effects_2x.png"))
    print("   Saved: output/trail_effects.png")

    # Speed lines
    print("\n4. Creating speed lines demo...")
    speed_lines = create_speed_lines_demo()
    speed_lines.save(os.path.join(output_dir, "speed_lines.png"))
    speed_lines.scale(2).save(os.path.join(output_dir, "speed_lines_2x.png"))
    print("   Saved: output/speed_lines.png")

    # Screen flash
    print("\n5. Creating screen flash demo...")
    flash_demo = create_screen_flash_demo()
    flash_demo.save(os.path.join(output_dir, "screen_flash.png"))
    flash_demo.scale(2).save(os.path.join(output_dir, "screen_flash_2x.png"))
    print("   Saved: output/screen_flash.png")

    # Vignette
    print("\n6. Creating vignette demo...")
    vignette_demo = create_vignette_demo()
    vignette_demo.save(os.path.join(output_dir, "vignette.png"))
    vignette_demo.scale(2).save(os.path.join(output_dir, "vignette_2x.png"))
    print("   Saved: output/vignette.png")

    # Color filters
    print("\n7. Creating color filter comparison...")
    filters = create_filter_comparison()
    filters.save(os.path.join(output_dir, "color_filters.png"))
    filters.scale(2).save(os.path.join(output_dir, "color_filters_2x.png"))
    print("   Saved: output/color_filters.png")

    # Scanlines
    print("\n8. Creating scanlines demo...")
    scanlines_demo = create_scanlines_demo()
    scanlines_demo.save(os.path.join(output_dir, "scanlines.png"))
    scanlines_demo.scale(2).save(os.path.join(output_dir, "scanlines_2x.png"))
    print("   Saved: output/scanlines.png")

    # Particle shapes
    print("\n9. Creating particle shapes demo...")
    shapes_demo = create_particle_shapes_demo()
    shapes_demo.save(os.path.join(output_dir, "particle_shapes.png"))
    shapes_demo.scale(2).save(os.path.join(output_dir, "particle_shapes_2x.png"))
    print("   Saved: output/particle_shapes.png")

    # Summary
    print("\n" + "=" * 40)
    print("Effects System Summary:")
    print(f"  - Particle effects: {len(list_effects())} presets")
    print("  - Particle shapes: pixel, square, circle, diamond, star, line, spark")
    print("  - Trail types: basic, line, ribbon, afterimage, motion blur")
    print("  - Screen effects: shake, flash, fade, vignette, filters, scanlines")

    print("\nAvailable particle effects:")
    for effect in sorted(list_effects()):
        print(f"    - {effect}")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()
