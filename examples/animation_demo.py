#!/usr/bin/env python3
"""
Animation Demo - Demonstrates Bitsy's animation system.

Shows:
- Easing functions visualization
- Timeline-based keyframe animation
- Procedural animations (breathing, blinking, etc.)
- Walk/run cycle animations
- Animation to sprite sheet export
"""

import sys
import os
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from animation import (
    # Easing
    apply_easing,
    list_easings,
    EASING_FUNCTIONS,
    # Timeline
    Timeline,
    Track,
    create_oscillation,
    # Procedural
    create_breathing_animation,
    create_bobbing_animation,
    create_shake_animation,
    create_idle_animation,
    list_procedural_animations,
    create_procedural_animation,
    # Cycles
    create_cycle,
    list_cycles,
    AnimationCycle,
)


def create_easing_visualization() -> Canvas:
    """Create a visualization of different easing functions."""
    easings_to_show = [
        'linear', 'ease_in_quad', 'ease_out_quad', 'ease_in_out_quad',
        'ease_in_cubic', 'ease_out_cubic', 'ease_in_out_cubic',
        'ease_in_out_sine', 'ease_out_bounce', 'ease_out_elastic',
    ]

    graph_width = 64
    graph_height = 32
    padding = 4
    cols = 5
    rows = (len(easings_to_show) + cols - 1) // cols

    canvas = Canvas(
        (graph_width + padding) * cols + padding,
        (graph_height + padding) * rows + padding,
        (30, 30, 40, 255)
    )

    for idx, easing_name in enumerate(easings_to_show):
        col = idx % cols
        row = idx // cols
        x_offset = padding + col * (graph_width + padding)
        y_offset = padding + row * (graph_height + padding)

        # Draw background
        for y in range(graph_height):
            for x in range(graph_width):
                canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

        # Draw curve
        prev_px, prev_py = None, None
        for px in range(graph_width):
            t = px / (graph_width - 1)
            eased = apply_easing(t, easing_name)

            # Clamp for visualization (some easings overshoot)
            eased = max(0, min(1, eased))
            py = int((1 - eased) * (graph_height - 1))

            # Draw point
            color = (100, 200, 255, 255)
            canvas.set_pixel(x_offset + px, y_offset + py, color)

            # Draw connecting line
            if prev_px is not None and prev_py is not None:
                dy = py - prev_py
                steps = max(abs(dy), 1)
                for s in range(steps):
                    iy = prev_py + int(dy * s / steps)
                    if 0 <= iy < graph_height:
                        canvas.set_pixel(x_offset + px, y_offset + iy, (80, 160, 220, 255))

            prev_px, prev_py = px, py

    return canvas


def create_timeline_demo() -> Canvas:
    """Create a visualization of timeline-based animation."""
    # Create a simple oscillation timeline
    timeline = Timeline('demo', fps=12)

    # Position track (oscillating)
    pos_track = Track('position')
    pos_track.add_keyframe(0.0, 0.0, 'ease_in_out_sine')
    pos_track.add_keyframe(1.0, 20.0, 'ease_in_out_sine')
    pos_track.add_keyframe(2.0, 0.0, 'ease_in_out_sine')
    timeline.add_track(pos_track)

    # Scale track
    scale_track = Track('scale')
    scale_track.add_keyframe(0.0, 1.0, 'ease_out_bounce')
    scale_track.add_keyframe(1.0, 1.5, 'ease_out_bounce')
    scale_track.add_keyframe(2.0, 1.0, 'ease_out_bounce')
    timeline.add_track(scale_track)

    timeline.loop = True

    # Render frames
    frame_count = 16
    frame_size = 32
    padding = 2

    canvas = Canvas(
        (frame_size + padding) * frame_count + padding,
        frame_size + padding * 2,
        (30, 30, 40, 255)
    )

    duration = timeline.get_duration()

    for i in range(frame_count):
        t = (i / frame_count) * duration
        values = timeline.get_values_at(t)

        x_offset = padding + i * (frame_size + padding)
        y_offset = padding

        # Draw frame background
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

        # Draw animated circle
        cx = frame_size // 2
        cy = int(frame_size // 2 + values.get('position', 0) * 0.3)
        radius = int(4 * values.get('scale', 1.0))

        # Simple circle drawing
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    px = cx + dx
                    py = cy + dy
                    if 0 <= px < frame_size and 0 <= py < frame_size:
                        canvas.set_pixel(x_offset + px, y_offset + py, (255, 180, 100, 255))

    return canvas


def create_procedural_demo() -> Canvas:
    """Create demonstrations of procedural animations."""
    # Get a few procedural animations to demonstrate
    anims = ['breathing', 'bobbing', 'pulse', 'shake']

    frame_size = 32
    frames_per_anim = 8
    padding = 2

    canvas = Canvas(
        (frame_size + padding) * frames_per_anim + padding,
        (frame_size + padding) * len(anims) + padding,
        (30, 30, 40, 255)
    )

    for row, anim_name in enumerate(anims):
        timeline = create_procedural_animation(anim_name)
        duration = timeline.get_duration()

        for col in range(frames_per_anim):
            t = (col / frames_per_anim) * duration
            values = timeline.get_values_at(t)

            x_offset = padding + col * (frame_size + padding)
            y_offset = padding + row * (frame_size + padding)

            # Draw frame background
            for y in range(frame_size):
                for x in range(frame_size):
                    canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

            # Apply animation values to a simple shape
            offset_x = values.get('offset_x', 0)
            offset_y = values.get('offset_y', 0)
            scale_x = values.get('scale_x', values.get('scale', 1.0))
            scale_y = values.get('scale_y', values.get('scale', 1.0))

            # Draw animated rectangle
            base_w, base_h = 12, 16
            w = int(base_w * scale_x)
            h = int(base_h * scale_y)
            cx = frame_size // 2 + int(offset_x)
            cy = frame_size // 2 + int(offset_y)

            for dy in range(-h // 2, h // 2):
                for dx in range(-w // 2, w // 2):
                    px = cx + dx
                    py = cy + dy
                    if 0 <= px < frame_size and 0 <= py < frame_size:
                        # Color based on animation type
                        colors = {
                            'breathing': (150, 200, 150, 255),
                            'bobbing': (150, 150, 200, 255),
                            'pulse': (200, 150, 150, 255),
                            'shake': (200, 200, 150, 255),
                        }
                        canvas.set_pixel(x_offset + px, y_offset + py,
                                        colors.get(anim_name, (200, 200, 200, 255)))

    return canvas


def create_walk_cycle_demo() -> Canvas:
    """Create a visualization of walk cycle animation data."""
    cycle = create_cycle('walk_6')
    timeline = cycle.to_timeline()

    frame_count = 12
    frame_size = 48
    padding = 2

    canvas = Canvas(
        (frame_size + padding) * frame_count + padding,
        frame_size + padding * 2,
        (30, 30, 40, 255)
    )

    duration = timeline.get_duration()

    for i in range(frame_count):
        t = (i / frame_count) * duration
        values = timeline.get_values_at(t)

        x_offset = padding + i * (frame_size + padding)
        y_offset = padding

        # Draw frame background
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, (40, 40, 50, 255))

        # Get animation values
        root_y = values.get('root_offset_y', 0)
        torso_rot = values.get('torso_rotation', 0)
        left_arm = values.get('left_arm_rotation', 0)
        right_arm = values.get('right_arm_rotation', 0)
        left_leg = values.get('left_leg_rotation', 0)
        right_leg = values.get('right_leg_rotation', 0)

        # Draw stick figure
        cx = frame_size // 2
        cy = frame_size // 2 + int(root_y)

        # Head
        head_y = cy - 12
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    px, py = cx + dx, head_y + dy
                    if 0 <= px < frame_size and 0 <= py < frame_size:
                        canvas.set_pixel(x_offset + px, y_offset + py, (255, 220, 180, 255))

        # Body (torso with rotation hint)
        body_top = head_y + 4
        body_bottom = cy + 4
        lean = int(torso_rot * 0.1)
        for by in range(body_top, body_bottom):
            px = cx + lean
            if 0 <= px < frame_size and 0 <= by < frame_size:
                canvas.set_pixel(x_offset + px, y_offset + by, (100, 150, 200, 255))

        # Arms (simple lines with rotation)
        arm_y = body_top + 2
        arm_len = 8

        # Left arm
        la_angle = math.radians(90 + left_arm)
        la_ex = int(cx + math.cos(la_angle) * arm_len)
        la_ey = int(arm_y + math.sin(la_angle) * arm_len)
        _draw_line(canvas, x_offset + cx, y_offset + arm_y,
                   x_offset + la_ex, y_offset + la_ey, (100, 150, 200, 255))

        # Right arm
        ra_angle = math.radians(90 + right_arm)
        ra_ex = int(cx + math.cos(ra_angle) * arm_len)
        ra_ey = int(arm_y + math.sin(ra_angle) * arm_len)
        _draw_line(canvas, x_offset + cx, y_offset + arm_y,
                   x_offset + ra_ex, y_offset + ra_ey, (100, 150, 200, 255))

        # Legs
        leg_y = body_bottom
        leg_len = 10

        # Left leg
        ll_angle = math.radians(90 + left_leg)
        ll_ex = int(cx - 2 + math.cos(ll_angle) * leg_len)
        ll_ey = int(leg_y + math.sin(ll_angle) * leg_len)
        _draw_line(canvas, x_offset + cx - 2, y_offset + leg_y,
                   x_offset + ll_ex, y_offset + ll_ey, (80, 80, 120, 255))

        # Right leg
        rl_angle = math.radians(90 + right_leg)
        rl_ex = int(cx + 2 + math.cos(rl_angle) * leg_len)
        rl_ey = int(leg_y + math.sin(rl_angle) * leg_len)
        _draw_line(canvas, x_offset + cx + 2, y_offset + leg_y,
                   x_offset + rl_ex, y_offset + rl_ey, (80, 80, 120, 255))

    return canvas


def _draw_line(canvas: Canvas, x1: int, y1: int, x2: int, y2: int, color: tuple):
    """Draw a simple line on canvas."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steps = max(dx, dy, 1)

    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        if 0 <= x < canvas.width and 0 <= y < canvas.height:
            canvas.set_pixel(x, y, color)


def create_cycle_list_demo() -> Canvas:
    """Show available animation cycles."""
    cycles = list_cycles()[:12]  # Show first 12

    frame_size = 24
    padding = 2
    cols = 4
    rows = (len(cycles) + cols - 1) // cols

    canvas = Canvas(
        (frame_size + padding) * cols + padding,
        (frame_size + padding) * rows + padding,
        (30, 30, 40, 255)
    )

    for idx, cycle_name in enumerate(cycles):
        col = idx % cols
        row = idx // cols
        x_offset = padding + col * (frame_size + padding)
        y_offset = padding + row * (frame_size + padding)

        # Draw background
        for y in range(frame_size):
            for x in range(frame_size):
                canvas.set_pixel(x_offset + x, y_offset + y, (45, 45, 55, 255))

        # Draw simple icon representing the cycle type
        cx, cy = frame_size // 2, frame_size // 2

        if 'walk' in cycle_name or 'run' in cycle_name:
            # Two circles for legs motion
            color = (100, 200, 100, 255) if 'walk' in cycle_name else (100, 100, 200, 255)
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if dx * dx + dy * dy <= 9:
                        canvas.set_pixel(x_offset + cx - 4 + dx, y_offset + cy + dy, color)
                        canvas.set_pixel(x_offset + cx + 4 + dx, y_offset + cy + dy, color)
        elif 'attack' in cycle_name:
            # Slash mark
            color = (200, 100, 100, 255)
            for i in range(8):
                canvas.set_pixel(x_offset + cx - 4 + i, y_offset + cy - 4 + i, color)
                canvas.set_pixel(x_offset + cx - 3 + i, y_offset + cy - 4 + i, color)
        elif 'jump' in cycle_name or 'fall' in cycle_name:
            # Up/down arrow
            color = (200, 200, 100, 255)
            for i in range(6):
                canvas.set_pixel(x_offset + cx, y_offset + cy - 3 + i, color)
            if 'jump' in cycle_name:
                canvas.set_pixel(x_offset + cx - 1, y_offset + cy - 2, color)
                canvas.set_pixel(x_offset + cx + 1, y_offset + cy - 2, color)
            else:
                canvas.set_pixel(x_offset + cx - 1, y_offset + cy + 2, color)
                canvas.set_pixel(x_offset + cx + 1, y_offset + cy + 2, color)
        else:
            # Generic circle
            color = (150, 150, 150, 255)
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if dx * dx + dy * dy <= 16:
                        canvas.set_pixel(x_offset + cx + dx, y_offset + cy + dy, color)

    return canvas


def main():
    print("Bitsy - Animation System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Easing visualization
    print("\n1. Creating easing function visualization...")
    easing_vis = create_easing_visualization()
    easing_vis.save(os.path.join(output_dir, "easing_curves.png"))
    easing_vis.scale(2).save(os.path.join(output_dir, "easing_curves_2x.png"))
    print(f"   Available easing functions: {len(list_easings())}")
    print("   Saved: output/easing_curves.png")

    # Timeline demo
    print("\n2. Creating timeline animation demo...")
    timeline_demo = create_timeline_demo()
    timeline_demo.save(os.path.join(output_dir, "timeline_demo.png"))
    timeline_demo.scale(2).save(os.path.join(output_dir, "timeline_demo_2x.png"))
    print("   Saved: output/timeline_demo.png")

    # Procedural animations
    print("\n3. Creating procedural animation demo...")
    procedural_demo = create_procedural_demo()
    procedural_demo.save(os.path.join(output_dir, "procedural_animations.png"))
    procedural_demo.scale(2).save(os.path.join(output_dir, "procedural_animations_2x.png"))
    print(f"   Available procedural animations: {list_procedural_animations()}")
    print("   Saved: output/procedural_animations.png")

    # Walk cycle
    print("\n4. Creating walk cycle demo...")
    walk_demo = create_walk_cycle_demo()
    walk_demo.save(os.path.join(output_dir, "walk_cycle.png"))
    walk_demo.scale(2).save(os.path.join(output_dir, "walk_cycle_2x.png"))
    print("   Saved: output/walk_cycle.png")

    # Cycle list
    print("\n5. Creating animation cycle catalog...")
    cycle_demo = create_cycle_list_demo()
    cycle_demo.save(os.path.join(output_dir, "animation_cycles.png"))
    cycle_demo.scale(2).save(os.path.join(output_dir, "animation_cycles_2x.png"))
    print(f"   Available cycles: {len(list_cycles())}")
    print("   Saved: output/animation_cycles.png")

    # Print summary
    print("\n" + "=" * 40)
    print("Animation System Summary:")
    print(f"  - Easing functions: {len(list_easings())}")
    print(f"  - Procedural animations: {len(list_procedural_animations())}")
    print(f"  - Animation cycles: {len(list_cycles())}")
    print("\nAvailable cycles:")
    for cycle_name in sorted(list_cycles()):
        print(f"    - {cycle_name}")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()
