"""
Hair Cluster Rendering - Bezier-based hair strand clusters.

Creates realistic hair with:
- Individual strand clusters using bezier curves
- Varied width profiles along each cluster
- Proper overlap ordering (back to front)
- Highlight strips on light-facing curves
- Natural variation using Perlin-like noise
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from core.color import Color


class HairStyle(Enum):
    """Hair style templates."""
    WAVY = "wavy"
    STRAIGHT = "straight"
    CURLY = "curly"
    SHORT = "short"
    PONYTAIL = "ponytail"
    BRAIDED = "braided"
    LONG = "long"
    BUN = "bun"


@dataclass
class HairCluster:
    """A single hair strand cluster defined by bezier control points."""

    # Bezier control points: [(x, y), ...]
    # Typically 3-4 points for quadratic/cubic curves
    control_points: List[Tuple[float, float]]

    # Width profile along the path (0.0-1.0 normalized positions)
    # Each entry is (t, width) where t is position along curve
    width_profile: List[Tuple[float, float]] = field(default_factory=lambda: [
        (0.0, 3.0),   # Root: medium width
        (0.3, 4.0),   # Slightly wider
        (0.7, 3.0),   # Taper
        (1.0, 1.0),   # Tip: narrow
    ])

    # Z-depth for ordering (higher = more in front)
    z_depth: float = 0.0

    # Color variation offset (-1.0 to 1.0, affects ramp index)
    color_offset: float = 0.0

    # Is this cluster on the light-facing side?
    is_highlight: bool = False


def bezier_quadratic(p0: Tuple[float, float], p1: Tuple[float, float],
                     p2: Tuple[float, float], t: float) -> Tuple[float, float]:
    """Evaluate quadratic bezier curve at parameter t."""
    mt = 1 - t
    x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
    y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
    return (x, y)


def bezier_cubic(p0: Tuple[float, float], p1: Tuple[float, float],
                 p2: Tuple[float, float], p3: Tuple[float, float],
                 t: float) -> Tuple[float, float]:
    """Evaluate cubic bezier curve at parameter t."""
    mt = 1 - t
    mt2 = mt * mt
    mt3 = mt2 * mt
    t2 = t * t
    t3 = t2 * t

    x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
    y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
    return (x, y)


def bezier_tangent_cubic(p0: Tuple[float, float], p1: Tuple[float, float],
                         p2: Tuple[float, float], p3: Tuple[float, float],
                         t: float) -> Tuple[float, float]:
    """Get tangent vector of cubic bezier at parameter t."""
    mt = 1 - t
    mt2 = mt * mt
    t2 = t * t

    # Derivative of cubic bezier
    dx = 3 * mt2 * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t2 * (p3[0] - p2[0])
    dy = 3 * mt2 * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t2 * (p3[1] - p2[1])

    return (dx, dy)


def get_width_at_t(width_profile: List[Tuple[float, float]], t: float) -> float:
    """Interpolate width from profile at parameter t."""
    if not width_profile:
        return 2.0

    # Find surrounding profile points
    prev_t, prev_w = width_profile[0]
    for curr_t, curr_w in width_profile[1:]:
        if curr_t >= t:
            # Interpolate between prev and curr
            if curr_t == prev_t:
                return curr_w
            ratio = (t - prev_t) / (curr_t - prev_t)
            return prev_w + ratio * (curr_w - prev_w)
        prev_t, prev_w = curr_t, curr_w

    return width_profile[-1][1]


def simple_noise(x: float, y: float, seed: int = 0) -> float:
    """Simple pseudo-random noise for variation."""
    n = int(x * 127 + y * 311 + seed * 997)
    n = (n << 13) ^ n
    return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0


def generate_wavy_clusters(center_x: float, top_y: float,
                           width: float, length: float,
                           count: int = 20,
                           rng: Optional[random.Random] = None) -> List[HairCluster]:
    """Generate wavy hair clusters."""
    if rng is None:
        rng = random.Random()

    clusters = []

    for i in range(count):
        # Distribute starting points across the head width
        t = (i + 0.5) / count  # 0 to 1
        start_x = center_x - width / 2 + t * width

        # Add some randomness to start position
        start_x += rng.uniform(-width * 0.05, width * 0.05)
        start_y = top_y + rng.uniform(0, length * 0.1)

        # Wave parameters
        wave_amplitude = rng.uniform(width * 0.05, width * 0.15)
        wave_frequency = rng.uniform(1.5, 2.5)
        phase = rng.uniform(0, math.pi * 2)

        # Side bias (clusters on edges curve outward)
        side_bias = (t - 0.5) * 2  # -1 to 1

        # Control points for cubic bezier
        # Adjust length based on position (shorter at edges)
        edge_factor = 1.0 - abs(side_bias) * 0.3
        cluster_length = length * edge_factor

        p0 = (start_x, start_y)
        p1 = (
            start_x + side_bias * width * 0.1 + wave_amplitude * math.sin(phase),
            start_y + cluster_length * 0.33
        )
        p2 = (
            start_x + side_bias * width * 0.2 + wave_amplitude * math.sin(phase + wave_frequency),
            start_y + cluster_length * 0.66
        )
        p3 = (
            start_x + side_bias * width * 0.25 + wave_amplitude * math.sin(phase + wave_frequency * 2),
            start_y + cluster_length
        )

        # Width profile with variation
        base_width = rng.uniform(2.5, 4.5)
        width_profile = [
            (0.0, base_width * 0.8),
            (0.2, base_width),
            (0.5, base_width * 0.9),
            (0.8, base_width * 0.5),
            (1.0, base_width * 0.2),
        ]

        # Z-depth based on position (center clusters in front)
        z_depth = 1.0 - abs(side_bias)

        # Color variation
        color_offset = rng.uniform(-0.3, 0.3)

        # Highlight clusters on light-facing side
        is_highlight = side_bias > 0.3

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=z_depth,
            color_offset=color_offset,
            is_highlight=is_highlight,
        )
        clusters.append(cluster)

    # Sort by z-depth (back to front)
    clusters.sort(key=lambda c: c.z_depth)

    return clusters


def generate_straight_clusters(center_x: float, top_y: float,
                               width: float, length: float,
                               count: int = 18,
                               rng: Optional[random.Random] = None) -> List[HairCluster]:
    """Generate straight hair clusters with minimal wave."""
    if rng is None:
        rng = random.Random()

    clusters = []

    for i in range(count):
        t = (i + 0.5) / count
        start_x = center_x - width / 2 + t * width
        start_x += rng.uniform(-width * 0.03, width * 0.03)
        start_y = top_y + rng.uniform(0, length * 0.05)

        # Minimal wave
        slight_wave = rng.uniform(-width * 0.02, width * 0.02)
        side_bias = (t - 0.5) * 2

        edge_factor = 1.0 - abs(side_bias) * 0.25
        cluster_length = length * edge_factor

        p0 = (start_x, start_y)
        p1 = (start_x + side_bias * width * 0.05 + slight_wave, start_y + cluster_length * 0.33)
        p2 = (start_x + side_bias * width * 0.1 + slight_wave, start_y + cluster_length * 0.66)
        p3 = (start_x + side_bias * width * 0.15, start_y + cluster_length)

        base_width = rng.uniform(3.0, 5.0)
        width_profile = [
            (0.0, base_width * 0.9),
            (0.3, base_width),
            (0.7, base_width * 0.7),
            (1.0, base_width * 0.15),
        ]

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=1.0 - abs(side_bias),
            color_offset=rng.uniform(-0.2, 0.2),
            is_highlight=side_bias > 0.4,
        )
        clusters.append(cluster)

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_curly_clusters(center_x: float, top_y: float,
                            width: float, length: float,
                            count: int = 25,
                            rng: Optional[random.Random] = None) -> List[HairCluster]:
    """Generate curly hair clusters with tight spirals."""
    if rng is None:
        rng = random.Random()

    clusters = []

    for i in range(count):
        t = (i + 0.5) / count
        start_x = center_x - width / 2 + t * width
        start_x += rng.uniform(-width * 0.05, width * 0.05)
        start_y = top_y + rng.uniform(0, length * 0.1)

        # Tighter curls
        curl_amplitude = rng.uniform(width * 0.08, width * 0.2)
        curl_frequency = rng.uniform(3.0, 5.0)
        phase = rng.uniform(0, math.pi * 2)

        side_bias = (t - 0.5) * 2
        cluster_length = length * (0.6 + rng.uniform(0, 0.3))  # More length variation

        p0 = (start_x, start_y)
        p1 = (
            start_x + curl_amplitude * math.sin(phase) + side_bias * width * 0.1,
            start_y + cluster_length * 0.25
        )
        p2 = (
            start_x + curl_amplitude * math.sin(phase + curl_frequency) + side_bias * width * 0.15,
            start_y + cluster_length * 0.5
        )
        p3 = (
            start_x + curl_amplitude * math.sin(phase + curl_frequency * 2) + side_bias * width * 0.2,
            start_y + cluster_length
        )

        base_width = rng.uniform(2.0, 3.5)
        width_profile = [
            (0.0, base_width),
            (0.25, base_width * 1.1),
            (0.5, base_width * 0.9),
            (0.75, base_width * 0.6),
            (1.0, base_width * 0.3),
        ]

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=0.5 + rng.uniform(0, 0.5),  # More z variation for curls
            color_offset=rng.uniform(-0.4, 0.4),
            is_highlight=rng.random() > 0.6,
        )
        clusters.append(cluster)

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_long_clusters(center_x: float, top_y: float,
                           width: float, length: float,
                           count: int = 22,
                           rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate long flowing hair clusters that extend past shoulders.

    Creates:
    - Long strands that flow down past the face
    - Gentle waves with natural movement
    - Hair that spreads outward at the sides
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    # Long hair extends significantly past normal length
    extended_length = length * 1.4

    for i in range(count):
        t = (i + 0.5) / count
        start_x = center_x - width / 2 + t * width
        start_x += rng.uniform(-width * 0.04, width * 0.04)
        start_y = top_y + rng.uniform(0, length * 0.08)

        # Gentle wave for natural flow
        wave_amplitude = rng.uniform(width * 0.03, width * 0.08)
        wave_frequency = rng.uniform(1.0, 2.0)
        phase = rng.uniform(0, math.pi * 2)

        # Side bias - hair on edges spreads outward more
        side_bias = (t - 0.5) * 2  # -1 to 1

        # Edge strands are longer and spread more
        edge_factor = 1.0 + abs(side_bias) * 0.15
        cluster_length = extended_length * edge_factor

        # Outward spread increases with length
        spread_factor = side_bias * width * 0.35

        p0 = (start_x, start_y)
        p1 = (
            start_x + spread_factor * 0.2 + wave_amplitude * math.sin(phase),
            start_y + cluster_length * 0.33
        )
        p2 = (
            start_x + spread_factor * 0.5 + wave_amplitude * math.sin(phase + wave_frequency),
            start_y + cluster_length * 0.66
        )
        p3 = (
            start_x + spread_factor * 0.8 + wave_amplitude * math.sin(phase + wave_frequency * 2),
            start_y + cluster_length
        )

        # Thicker base strands that taper to thin tips
        base_width = rng.uniform(3.0, 5.0)
        width_profile = [
            (0.0, base_width * 0.85),
            (0.2, base_width),
            (0.5, base_width * 0.85),
            (0.75, base_width * 0.5),
            (0.9, base_width * 0.25),
            (1.0, base_width * 0.1),
        ]

        # Z-depth: center strands slightly in front
        z_depth = 0.9 - abs(side_bias) * 0.4

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=z_depth,
            color_offset=rng.uniform(-0.25, 0.25),
            is_highlight=side_bias > 0.3,
        )
        clusters.append(cluster)

    # Add some inner strands for depth
    inner_count = count // 4
    for i in range(inner_count):
        t = (i + 0.5) / inner_count * 0.6 + 0.2  # Center portion only
        start_x = center_x - width / 3 + t * width * 0.66
        start_y = top_y + rng.uniform(length * 0.05, length * 0.15)

        cluster_length = extended_length * rng.uniform(0.85, 1.0)
        wave = rng.uniform(-width * 0.04, width * 0.04)

        p0 = (start_x, start_y)
        p1 = (start_x + wave, start_y + cluster_length * 0.33)
        p2 = (start_x + wave * 1.5, start_y + cluster_length * 0.66)
        p3 = (start_x + wave * 2, start_y + cluster_length)

        base_width = rng.uniform(2.5, 4.0)
        width_profile = [
            (0.0, base_width * 0.9),
            (0.3, base_width),
            (0.6, base_width * 0.7),
            (0.85, base_width * 0.35),
            (1.0, base_width * 0.1),
        ]

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=0.3 + rng.uniform(0, 0.2),
            color_offset=rng.uniform(-0.15, 0.15),
            is_highlight=False,
        ))

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_braided_clusters(center_x: float, top_y: float,
                              width: float, length: float,
                              count: int = 18,
                              rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate a braided hairstyle using interwoven strand clusters.

    Creates:
    - Three primary strands that weave around each other
    - Alternating z-depth to simulate crossings
    - A hanging braid that can sit to one side or at the back
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    # Decide whether the braid hangs to one side or straight down the back.
    hang_roll = rng.random()
    if hang_roll < 0.35:
        side = 0
    else:
        side = rng.choice([-1, 1])

    base_x = center_x + side * width * 0.25
    base_y = top_y + length * 0.05
    braid_length = length * 1.15
    braid_width = width * 0.22
    strand_offset = braid_width * 0.45

    segments = max(4, count // 3)
    wave_cycles = 2.2

    for strand_idx in range(3):
        phase = (strand_idx / 3.0) * 2 * math.pi

        for seg in range(segments):
            t0 = seg / segments
            t1 = (seg + 1) / segments
            mid_t = (t0 + t1) * 0.5

            # Centerline drift for a gentle side hang.
            drift0 = side * width * 0.12 * t0
            drift1 = side * width * 0.12 * t1
            drift_mid = side * width * 0.12 * mid_t

            # Interwoven offsets for the three strands.
            offset0 = strand_offset * math.sin(2 * math.pi * wave_cycles * t0 + phase)
            offset1 = strand_offset * math.sin(2 * math.pi * wave_cycles * t1 + phase)
            offset_mid = strand_offset * math.sin(2 * math.pi * wave_cycles * mid_t + phase)

            y0 = base_y + braid_length * t0
            y1 = base_y + braid_length * t1

            # Slight sway to avoid perfectly straight braid.
            sway = math.sin(mid_t * math.pi) * width * 0.03

            p0 = (base_x + drift0 + offset0 + sway, y0)
            p1 = (base_x + drift_mid + offset_mid * 1.1 + sway, y0 + (y1 - y0) * 0.33)
            p2 = (base_x + drift_mid + offset_mid * 0.9 + sway, y0 + (y1 - y0) * 0.66)
            p3 = (base_x + drift1 + offset1 + sway, y1)

            base_width = rng.uniform(2.3, 3.6)
            width_profile = [
                (0.0, base_width * 0.85),
                (0.4, base_width),
                (0.8, base_width * 0.75),
                (1.0, base_width * 0.6),
            ]

            # Alternate crossings by flipping z-depth per segment and strand.
            crossing = (seg + strand_idx) % 2 == 0
            z_depth = 0.65 if crossing else 0.35
            z_depth += rng.uniform(-0.05, 0.05)

            is_highlight = (base_x + drift_mid + offset_mid) > center_x + width * 0.05

            clusters.append(HairCluster(
                control_points=[p0, p1, p2, p3],
                width_profile=width_profile,
                z_depth=z_depth,
                color_offset=rng.uniform(-0.2, 0.2),
                is_highlight=is_highlight,
            ))

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_bun_clusters(center_x: float, top_y: float,
                          width: float, length: float,
                          count: int = 40,
                          rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate a bun/updo hairstyle with volumetric circular hair mass.

    Creates:
    - Multi-layer circular bun with highlights
    - Supporting hair swept up from sides
    - Wispy edge strands for natural look
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    # Bun parameters - larger and more prominent
    bun_cx = center_x
    bun_cy = top_y - width * 0.18
    bun_radius = width * 0.28

    # Layer 1: Inner bun mass (dense core)
    inner_count = count // 3
    for i in range(inner_count):
        angle = (i / inner_count) * 2 * math.pi + rng.uniform(-0.3, 0.3)
        r_factor = rng.uniform(0.3, 0.6)

        start_x = bun_cx + bun_radius * r_factor * math.cos(angle)
        start_y = bun_cy + bun_radius * r_factor * 0.7 * math.sin(angle)

        curve_angle = angle + math.pi * rng.uniform(0.3, 0.7)
        curve_len = bun_radius * rng.uniform(0.2, 0.4)

        p0 = (start_x, start_y)
        p1 = (bun_cx + curve_len * math.cos(curve_angle), bun_cy + curve_len * 0.6 * math.sin(curve_angle))
        p2 = (bun_cx + curve_len * 0.5 * math.cos(curve_angle + 0.8), bun_cy + curve_len * 0.4 * math.sin(curve_angle + 0.8))
        p3 = (start_x + rng.uniform(-2, 2), start_y + rng.uniform(-2, 2))

        base_width = rng.uniform(2.5, 4.0)
        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=[(0.0, base_width), (0.5, base_width * 1.1), (1.0, base_width * 0.4)],
            z_depth=0.5 + rng.uniform(0, 0.15),
            color_offset=rng.uniform(-0.15, 0.15),
            is_highlight=False,
        ))

    # Layer 2: Outer bun surface (visible texture)
    outer_count = count // 2
    for i in range(outer_count):
        angle = (i / outer_count) * 2 * math.pi + rng.uniform(-0.15, 0.15)
        r_factor = rng.uniform(0.7, 0.95)

        start_x = bun_cx + bun_radius * r_factor * math.cos(angle)
        start_y = bun_cy + bun_radius * r_factor * 0.6 * math.sin(angle)

        # Swirling curves around bun
        swirl = math.pi * 0.4 + rng.uniform(-0.2, 0.2)
        p0 = (start_x, start_y)
        p1 = (
            bun_cx + bun_radius * 0.5 * math.cos(angle + swirl * 0.3),
            bun_cy + bun_radius * 0.35 * math.sin(angle + swirl * 0.3)
        )
        p2 = (
            bun_cx + bun_radius * 0.3 * math.cos(angle + swirl * 0.6),
            bun_cy + bun_radius * 0.2 * math.sin(angle + swirl * 0.6)
        )
        p3 = (
            bun_cx + bun_radius * 0.4 * math.cos(angle + swirl),
            bun_cy + bun_radius * 0.3 * math.sin(angle + swirl)
        )

        base_width = rng.uniform(2.0, 3.5)
        # Top half of bun gets highlights
        is_top = -0.5 * math.pi < angle < 0.5 * math.pi

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=[(0.0, base_width), (0.4, base_width * 1.2), (0.8, base_width * 0.7), (1.0, base_width * 0.2)],
            z_depth=0.65 + rng.uniform(0, 0.25),
            color_offset=rng.uniform(-0.2, 0.2),
            is_highlight=is_top,
        ))

    # Layer 3: Highlight wisps on top
    highlight_count = count // 6
    for i in range(highlight_count):
        angle = rng.uniform(-0.4 * math.pi, 0.4 * math.pi)  # Top area only
        r = bun_radius * rng.uniform(0.6, 0.9)

        start_x = bun_cx + r * math.cos(angle)
        start_y = bun_cy + r * 0.5 * math.sin(angle) - bun_radius * 0.1

        p0 = (start_x, start_y)
        p1 = (start_x + rng.uniform(-3, 3), start_y - rng.uniform(2, 5))
        p2 = (bun_cx + rng.uniform(-5, 5), bun_cy - bun_radius * 0.2)
        p3 = (bun_cx + rng.uniform(-3, 3), bun_cy)

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=[(0.0, 1.5), (0.5, 2.0), (1.0, 0.5)],
            z_depth=0.9 + rng.uniform(0, 0.1),
            color_offset=0.3 + rng.uniform(0, 0.2),  # Lighter
            is_highlight=True,
        ))

    # Supporting hair swept up from sides
    side_count = count // 4
    for i in range(side_count):
        side = 1 if i % 2 == 0 else -1
        t = (i // 2) / max(1, side_count // 2)

        start_x = center_x + side * width * 0.4 * (0.7 + t * 0.3)
        start_y = top_y + length * 0.15 * t

        p0 = (start_x, start_y)
        p1 = (start_x + side * width * 0.08, start_y - length * 0.12)
        p2 = (bun_cx + side * bun_radius * 0.6, bun_cy + bun_radius * 0.4)
        p3 = (bun_cx + side * bun_radius * 0.35 + rng.uniform(-2, 2), bun_cy + rng.uniform(-2, 4))

        base_width = rng.uniform(2.5, 4.0)
        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=[(0.0, base_width * 0.7), (0.4, base_width), (0.8, base_width * 0.5), (1.0, base_width * 0.15)],
            z_depth=0.25 + rng.uniform(0, 0.15),
            color_offset=rng.uniform(-0.1, 0.1),
            is_highlight=side > 0,
        ))

    # Wispy edge strands (loose strands around bun)
    wisp_count = count // 8
    for i in range(wisp_count):
        angle = rng.uniform(0, 2 * math.pi)
        start_x = bun_cx + bun_radius * 1.1 * math.cos(angle)
        start_y = bun_cy + bun_radius * 0.7 * math.sin(angle)

        # Short wispy strand
        end_x = start_x + rng.uniform(-6, 6)
        end_y = start_y + rng.uniform(3, 8)

        p0 = (start_x, start_y)
        p1 = ((start_x + end_x) / 2 + rng.uniform(-2, 2), (start_y + end_y) / 2)
        p2 = (end_x, end_y)

        clusters.append(HairCluster(
            control_points=[p0, p1, p2],  # Quadratic
            width_profile=[(0.0, 1.5), (0.5, 1.0), (1.0, 0.3)],
            z_depth=0.85 + rng.uniform(0, 0.1),
            color_offset=rng.uniform(-0.1, 0.2),
            is_highlight=rng.random() > 0.5,
        ))

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_ponytail_clusters(center_x: float, top_y: float,
                                width: float, length: float,
                                count: int = 30,
                                rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate a ponytail hairstyle with swept-back hair and a hanging tail.

    Creates:
    - Hair swept back from the front/sides
    - A gathered point at the back of the head
    - A flowing tail extending downward
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    # Ponytail gather point (back of head, slightly elevated)
    gather_x = center_x
    gather_y = top_y + length * 0.15
    tail_length = length * 1.2

    # 1. Swept-back side hair leading to gather point
    side_count = count // 3
    for i in range(side_count):
        side = 1 if i % 2 == 0 else -1
        t = (i // 2) / max(1, side_count // 2)

        # Start from the hairline on the side
        start_x = center_x + side * width * (0.35 + t * 0.15)
        start_y = top_y + length * 0.02 * t

        # Curve toward the gather point
        p0 = (start_x, start_y)
        p1 = (
            start_x + side * width * 0.05,
            start_y + length * 0.08
        )
        p2 = (
            gather_x + side * width * 0.08,
            gather_y - length * 0.05
        )
        p3 = (
            gather_x + rng.uniform(-3, 3),
            gather_y + rng.uniform(-2, 2)
        )

        base_width = rng.uniform(2.5, 4.0)
        width_profile = [
            (0.0, base_width * 0.75),
            (0.3, base_width),
            (0.7, base_width * 0.6),
            (1.0, base_width * 0.25),
        ]

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=0.2 + rng.uniform(0, 0.15),
            color_offset=rng.uniform(-0.15, 0.15),
            is_highlight=side > 0,
        ))

    # 2. Top hair swept back
    top_count = count // 4
    for i in range(top_count):
        t = (i + 0.5) / top_count
        start_x = center_x - width * 0.25 + t * width * 0.5
        start_y = top_y - length * 0.02

        p0 = (start_x, start_y)
        p1 = (start_x + rng.uniform(-2, 2), start_y + length * 0.06)
        p2 = (gather_x + rng.uniform(-5, 5), gather_y - length * 0.04)
        p3 = (gather_x + rng.uniform(-2, 2), gather_y + rng.uniform(-1, 2))

        base_width = rng.uniform(2.8, 4.2)
        width_profile = [
            (0.0, base_width * 0.8),
            (0.35, base_width),
            (0.7, base_width * 0.55),
            (1.0, base_width * 0.2),
        ]

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=0.3 + rng.uniform(0, 0.1),
            color_offset=rng.uniform(-0.2, 0.2),
            is_highlight=t > 0.5,
        ))

    # 3. The ponytail itself (flowing downward from gather point)
    tail_count = count // 2
    tail_width = width * 0.35

    for i in range(tail_count):
        t = (i + 0.5) / tail_count
        # Distribute across the tail width
        offset_x = (t - 0.5) * tail_width

        start_x = gather_x + offset_x + rng.uniform(-2, 2)
        start_y = gather_y + rng.uniform(-2, 3)

        # Tail hangs down with gentle wave
        wave_amp = rng.uniform(width * 0.02, width * 0.06)
        wave_phase = rng.uniform(0, math.pi * 2)

        strand_length = tail_length * rng.uniform(0.85, 1.0)

        # Side strands spread outward slightly
        spread = offset_x * 0.6

        p0 = (start_x, start_y)
        p1 = (
            start_x + spread * 0.3 + wave_amp * math.sin(wave_phase),
            start_y + strand_length * 0.33
        )
        p2 = (
            start_x + spread * 0.6 + wave_amp * math.sin(wave_phase + 1.5),
            start_y + strand_length * 0.66
        )
        p3 = (
            start_x + spread * 0.8 + wave_amp * math.sin(wave_phase + 3.0),
            start_y + strand_length
        )

        base_width = rng.uniform(2.2, 3.8)
        width_profile = [
            (0.0, base_width * 0.9),
            (0.25, base_width),
            (0.55, base_width * 0.85),
            (0.8, base_width * 0.5),
            (1.0, base_width * 0.15),
        ]

        # Center strands in front, edge strands behind
        z_depth = 0.5 - abs(t - 0.5) * 0.3 + rng.uniform(0, 0.1)

        clusters.append(HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=z_depth,
            color_offset=rng.uniform(-0.25, 0.25),
            is_highlight=(t - 0.5) > 0.15,
        ))

    # 4. Hair tie/scrunchie band at gather point (rendered as thick short clusters)
    band_count = 6
    band_radius = width * 0.08
    for i in range(band_count):
        angle = (i / band_count) * 2 * math.pi
        bx = gather_x + band_radius * math.cos(angle) * 0.5
        by = gather_y + band_radius * math.sin(angle) * 0.3

        p0 = (bx, by)
        p1 = (gather_x, gather_y)
        p2 = (
            gather_x + band_radius * math.cos(angle + math.pi) * 0.5,
            gather_y + band_radius * math.sin(angle + math.pi) * 0.3
        )

        clusters.append(HairCluster(
            control_points=[p0, p1, p2],
            width_profile=[(0.0, 3.0), (0.5, 4.0), (1.0, 3.0)],
            z_depth=0.7,  # In front of tail
            color_offset=-0.4,  # Darker for band
            is_highlight=False,
        ))

    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_hair_clusters(style: HairStyle, center_x: float, top_y: float,
                           width: float, length: float,
                           count: int = 20,
                           seed: Optional[int] = None) -> List[HairCluster]:
    """Generate hair clusters based on style."""
    rng = random.Random(seed) if seed is not None else random.Random()

    if style == HairStyle.WAVY:
        return generate_wavy_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.STRAIGHT:
        return generate_straight_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.CURLY:
        return generate_curly_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.SHORT:
        # Short hair: reduced length
        return generate_wavy_clusters(center_x, top_y, width, length * 0.4, int(count * 0.8), rng)
    elif style == HairStyle.PONYTAIL:
        return generate_ponytail_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.BRAIDED:
        return generate_braided_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.LONG:
        return generate_long_clusters(center_x, top_y, width, length, count, rng)
    elif style == HairStyle.BUN:
        return generate_bun_clusters(center_x, top_y, width, length, count, rng)
    else:
        # Default to wavy
        return generate_wavy_clusters(center_x, top_y, width, length, count, rng)


def render_cluster(canvas: Canvas, cluster: HairCluster,
                   color_ramp: List[Color],
                   light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """Render a single hair cluster with gradient shading and anti-aliasing."""
    if len(cluster.control_points) < 3:
        return

    ramp_len = len(color_ramp)
    mid_idx = ramp_len // 2

    # Base color from ramp
    color_idx = mid_idx + int(cluster.color_offset * 2)
    color_idx = max(0, min(ramp_len - 1, color_idx))

    # Shadow and highlight indices
    shadow_idx = max(0, color_idx - 2)
    highlight_idx = min(ramp_len - 1, color_idx + 2)
    specular_idx = min(ramp_len - 1, color_idx + 3)

    # Sample points along the bezier curve (more steps for smoother curves)
    steps = 45
    points = cluster.control_points

    for i in range(steps):
        t = i / (steps - 1)

        # Evaluate curve position
        if len(points) == 3:
            pos = bezier_quadratic(points[0], points[1], points[2], t)
        else:
            pos = bezier_cubic(points[0], points[1], points[2], points[3], t)

        # Get width at this position
        width = get_width_at_t(cluster.width_profile, t)

        # Get tangent for perpendicular direction
        if len(points) == 4:
            tangent = bezier_tangent_cubic(points[0], points[1], points[2], points[3], t)
        else:
            if t < 0.99:
                next_pos = bezier_quadratic(points[0], points[1], points[2], min(1.0, t + 0.05))
                tangent = (next_pos[0] - pos[0], next_pos[1] - pos[1])
            else:
                tangent = (0, 1)

        # Normalize and get perpendicular
        mag = math.sqrt(tangent[0]**2 + tangent[1]**2)
        if mag > 0:
            perp = (-tangent[1] / mag, tangent[0] / mag)
        else:
            perp = (1, 0)

        # Light dot product for this segment
        dot_product = perp[0] * light_direction[0] + perp[1] * light_direction[1]

        # Draw thick line with gradient across width
        half_width = width / 2
        x1 = pos[0] - perp[0] * half_width
        y1 = pos[1] - perp[1] * half_width
        x2 = pos[0] + perp[0] * half_width
        y2 = pos[1] + perp[1] * half_width

        dx = x2 - x1
        dy = y2 - y1
        line_length = math.sqrt(dx * dx + dy * dy)
        line_steps = max(int(line_length * 1.5), 1)

        for j in range(line_steps + 1):
            lt = j / line_steps if line_steps > 0 else 0.5
            px_f = x1 + dx * lt
            py_f = y1 + dy * lt
            px = int(px_f)
            py = int(py_f)

            if not (0 <= px < canvas.width and 0 <= py < canvas.height):
                continue

            # Cross-strand gradient: edges darker, center lighter
            edge_dist = abs(lt - 0.5) * 2  # 0 at center, 1 at edges
            center_factor = 1 - edge_dist

            # Combine with light direction
            if cluster.is_highlight and dot_product > 0.2:
                # Specular highlight in center of lit strands
                if center_factor > 0.7 and dot_product > 0.5:
                    color = color_ramp[specular_idx]
                else:
                    color = color_ramp[highlight_idx]
            elif dot_product < -0.2:
                # Shadow side
                color = color_ramp[shadow_idx]
            else:
                # Base color with center brightening
                adj_idx = color_idx + int(center_factor * 1.5)
                adj_idx = min(ramp_len - 1, adj_idx)
                color = color_ramp[adj_idx]

            # Anti-aliasing at strand edges
            alpha = 255
            if edge_dist > 0.7:
                alpha = int(255 * (1.0 - edge_dist) / 0.3)
                alpha = max(0, min(255, alpha))

            if alpha > 0:
                if alpha < 255:
                    color = (*color[:3], alpha)
                canvas.set_pixel(px, py, color)


def render_hair_clusters(canvas: Canvas, clusters: List[HairCluster],
                         color_ramp: List[Color],
                         light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """Render all hair clusters to the canvas."""
    # Clusters should already be sorted by z_depth
    for cluster in clusters:
        render_cluster(canvas, cluster, color_ramp, light_direction)


def generate_bangs_clusters(center_x: float, forehead_y: float,
                            width: float, length: float,
                            count: int = 8,
                            style: HairStyle = HairStyle.WAVY,
                            rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate bangs/fringe clusters that fall over the forehead.

    These are rendered after the face to create the layered look
    of hair falling in front.

    Args:
        center_x: Horizontal center of the bangs
        forehead_y: Y position of the forehead (top of face)
        width: Total width of the bangs area
        length: How far down the bangs extend
        count: Number of bang clusters
        style: Hair style affects curve amount
        rng: Random number generator

    Returns:
        List of HairCluster objects for bangs
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    # Style-specific parameters
    if style == HairStyle.STRAIGHT:
        wave_amount = 0.02
        curve_amount = 0.1
    elif style == HairStyle.CURLY:
        wave_amount = 0.15
        curve_amount = 0.3
    else:  # WAVY and others
        wave_amount = 0.08
        curve_amount = 0.2

    for i in range(count):
        # Distribute across forehead width
        t = (i + 0.5) / count
        start_x = center_x - width / 2 + t * width
        start_x += rng.uniform(-width * 0.03, width * 0.03)

        # Start slightly above forehead
        start_y = forehead_y - length * 0.1

        # Side bias - bangs on edges curve outward slightly
        side_bias = (t - 0.5) * 2  # -1 to 1

        # Wave variation
        wave_offset = rng.uniform(-1, 1) * wave_amount * width
        phase = rng.uniform(0, math.pi)

        # Bangs curve downward and slightly outward
        cluster_length = length * rng.uniform(0.7, 1.0)

        p0 = (start_x, start_y)
        p1 = (
            start_x + side_bias * width * 0.05 + wave_offset,
            start_y + cluster_length * 0.4
        )
        p2 = (
            start_x + side_bias * width * curve_amount + wave_offset * math.cos(phase),
            start_y + cluster_length * 0.7
        )
        p3 = (
            start_x + side_bias * width * curve_amount * 1.2,
            start_y + cluster_length
        )

        # Thinner strands for bangs
        base_width = rng.uniform(1.5, 3.0)
        width_profile = [
            (0.0, base_width * 0.7),
            (0.3, base_width),
            (0.6, base_width * 0.8),
            (0.9, base_width * 0.4),
            (1.0, base_width * 0.15),
        ]

        # Bangs are always in front (high z_depth)
        z_depth = 0.8 + rng.uniform(0, 0.2)

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=z_depth,
            color_offset=rng.uniform(-0.2, 0.2),
            is_highlight=rng.random() > 0.5,  # More highlights on bangs
        )
        clusters.append(cluster)

    # Sort by z_depth
    clusters.sort(key=lambda c: c.z_depth)
    return clusters


def generate_stray_strands(center_x: float, top_y: float,
                           width: float, length: float,
                           count: int = 5,
                           rng: Optional[random.Random] = None) -> List[HairCluster]:
    """
    Generate individual stray strands for added realism.

    These are thin, slightly wild strands that break up the
    uniformity of the main hair mass.

    Args:
        center_x: Horizontal center
        top_y: Top of hair area
        width: Hair width
        length: Hair length
        count: Number of stray strands
        rng: Random number generator

    Returns:
        List of thin HairCluster objects
    """
    if rng is None:
        rng = random.Random()

    clusters = []

    for i in range(count):
        # Random position along hair edge
        side = rng.choice([-1, 1])
        start_x = center_x + side * width * rng.uniform(0.3, 0.5)
        start_y = top_y + length * rng.uniform(0.1, 0.4)

        # Random curve direction
        curve_x = rng.uniform(-width * 0.15, width * 0.15)
        strand_length = length * rng.uniform(0.3, 0.6)

        p0 = (start_x, start_y)
        p1 = (start_x + curve_x * 0.3, start_y + strand_length * 0.33)
        p2 = (start_x + curve_x * 0.7, start_y + strand_length * 0.66)
        p3 = (start_x + curve_x, start_y + strand_length)

        # Very thin strands
        base_width = rng.uniform(0.8, 1.5)
        width_profile = [
            (0.0, base_width),
            (0.5, base_width * 0.7),
            (1.0, base_width * 0.2),
        ]

        cluster = HairCluster(
            control_points=[p0, p1, p2, p3],
            width_profile=width_profile,
            z_depth=rng.uniform(0.3, 0.9),
            color_offset=rng.uniform(-0.3, 0.3),
            is_highlight=rng.random() > 0.7,
        )
        clusters.append(cluster)

    return clusters
