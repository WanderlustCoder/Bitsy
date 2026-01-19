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


@dataclass
class FlowField:
    """
    Grid of direction vectors for coherent hair flow.

    Uses 8x8 grid with bilinear interpolation to create smooth,
    natural-looking directional flow for hair strands.
    """
    # Grid dimensions (8x8 by default)
    grid_size: int = 8

    # Direction vectors for each grid cell: [(dx, dy), ...]
    # Stored as flat list, index = y * grid_size + x
    directions: List[Tuple[float, float]] = field(default_factory=list)

    # Bounds of the flow field in world coordinates
    min_x: float = 0.0
    max_x: float = 100.0
    min_y: float = 0.0
    max_y: float = 100.0

    def sample(self, x: float, y: float) -> Tuple[float, float]:
        """Sample the flow direction at a world coordinate using bilinear interpolation."""
        if not self.directions:
            return (0.0, 1.0)  # Default: flow downward

        # Normalize to grid coordinates
        gx = (x - self.min_x) / max(0.001, self.max_x - self.min_x) * (self.grid_size - 1)
        gy = (y - self.min_y) / max(0.001, self.max_y - self.min_y) * (self.grid_size - 1)

        # Clamp to grid bounds
        gx = max(0, min(self.grid_size - 1.001, gx))
        gy = max(0, min(self.grid_size - 1.001, gy))

        # Get integer grid cell and fractional part
        ix = int(gx)
        iy = int(gy)
        fx = gx - ix
        fy = gy - iy

        # Bilinear interpolation
        def get_dir(gx: int, gy: int) -> Tuple[float, float]:
            idx = min(len(self.directions) - 1, gy * self.grid_size + gx)
            return self.directions[max(0, idx)]

        d00 = get_dir(ix, iy)
        d10 = get_dir(min(ix + 1, self.grid_size - 1), iy)
        d01 = get_dir(ix, min(iy + 1, self.grid_size - 1))
        d11 = get_dir(min(ix + 1, self.grid_size - 1), min(iy + 1, self.grid_size - 1))

        # Interpolate
        dx = (d00[0] * (1 - fx) + d10[0] * fx) * (1 - fy) + (d01[0] * (1 - fx) + d11[0] * fx) * fy
        dy = (d00[1] * (1 - fx) + d10[1] * fx) * (1 - fy) + (d01[1] * (1 - fx) + d11[1] * fx) * fy

        # Normalize
        mag = math.sqrt(dx * dx + dy * dy)
        if mag > 0:
            return (dx / mag, dy / mag)
        return (0.0, 1.0)


@dataclass
class StrandBundle:
    """
    A group of strands that flow together, creating more coherent hair appearance.

    Contains a master spine curve with 8-15 tightly-grouped sub-strands that share
    similar direction and color variation.
    """
    # Master spine curve control points
    spine_points: List[Tuple[float, float]]

    # Number of sub-strands in this bundle
    strand_count: int = 10

    # How tightly grouped the strands are (0.0 = on spine, 1.0 = spread out)
    spread: float = 0.3

    # Shared color offset for the bundle
    color_offset: float = 0.0

    # Z-depth for rendering order
    z_depth: float = 0.0

    # Is this bundle on the light-facing side?
    is_highlight: bool = False


def create_flow_field(center_x: float, top_y: float, width: float, height: float,
                      style: 'HairStyle', rng: random.Random) -> FlowField:
    """
    Create a flow field for a given hair style.

    Different styles have different flow patterns:
    - STRAIGHT: Mostly downward flow
    - WAVY: Gentle side-to-side variation
    - CURLY: More chaotic but still coherent
    """
    grid_size = 8
    directions = []

    for gy in range(grid_size):
        for gx in range(grid_size):
            # Normalize grid position
            nx = gx / (grid_size - 1)  # 0 to 1
            ny = gy / (grid_size - 1)  # 0 to 1

            # Side position: -1 (left) to 1 (right)
            side = (nx - 0.5) * 2

            # Base direction: flow outward and down
            base_dx = side * 0.3  # Outward spread
            base_dy = 0.8 + ny * 0.2  # Downward, slightly faster at bottom

            # Style-specific modifications
            if style == HairStyle.STRAIGHT:
                # Very little variation
                dx = base_dx * 0.5
                dy = base_dy
            elif style == HairStyle.CURLY:
                # More variation with some noise
                noise = simple_noise(gx * 0.5, gy * 0.5, rng.randint(0, 1000))
                dx = base_dx + noise * 0.3
                dy = base_dy + simple_noise(gx * 0.3, gy * 0.7, rng.randint(0, 1000)) * 0.2
            else:  # WAVY and others
                # Gentle wave pattern
                wave = math.sin(ny * math.pi * 1.5 + side * 0.5) * 0.15
                dx = base_dx + wave
                dy = base_dy

            # Normalize
            mag = math.sqrt(dx * dx + dy * dy)
            if mag > 0:
                dx, dy = dx / mag, dy / mag
            else:
                dx, dy = 0, 1

            directions.append((dx, dy))

    return FlowField(
        grid_size=grid_size,
        directions=directions,
        min_x=center_x - width / 2,
        max_x=center_x + width / 2,
        min_y=top_y,
        max_y=top_y + height,
    )


def generate_strand_bundles(center_x: float, top_y: float, width: float, length: float,
                            flow_field: FlowField, bundle_count: int,
                            light_direction: Tuple[float, float],
                            rng: random.Random) -> List[StrandBundle]:
    """
    Generate strand bundles that follow the flow field.

    Each bundle has a master spine curve that follows the flow field,
    with sub-strands tightly grouped around it.
    """
    bundles = []

    for i in range(bundle_count):
        # Distribute starting points across the head width
        t = (i + 0.5) / bundle_count
        start_x = center_x - width / 2 + t * width
        start_x += rng.uniform(-width * 0.02, width * 0.02)  # Tight variation (was ±5%, now ±2%)
        start_y = top_y + rng.uniform(0, length * 0.08)

        # Side bias for outward flow
        side_bias = (t - 0.5) * 2

        # Build spine curve by following flow field
        spine_points = [(start_x, start_y)]
        current_x, current_y = start_x, start_y

        # Length varies by position (shorter at edges)
        edge_factor = 1.0 - abs(side_bias) * 0.3
        segment_length = length * edge_factor / 3

        for seg in range(3):  # 4 control points (cubic bezier)
            # Sample flow at current position
            flow_dx, flow_dy = flow_field.sample(current_x, current_y)

            # Add slight phase variation (±0.1 rad instead of 0 to 2π)
            phase_var = rng.uniform(-0.1, 0.1)
            cos_var = math.cos(phase_var)
            sin_var = math.sin(phase_var)
            varied_dx = flow_dx * cos_var - flow_dy * sin_var
            varied_dy = flow_dx * sin_var + flow_dy * cos_var

            # Move along flow
            current_x += varied_dx * segment_length * 0.3
            current_y += varied_dy * segment_length

            spine_points.append((current_x, current_y))

        # Determine if this bundle catches highlights
        # Use curve normal at middle point
        if len(spine_points) >= 2:
            mid_dx = spine_points[2][0] - spine_points[1][0]
            mid_dy = spine_points[2][1] - spine_points[1][1]
            # Normal is perpendicular to tangent
            normal_x = -mid_dy
            normal_y = mid_dx
            norm_len = math.sqrt(normal_x * normal_x + normal_y * normal_y)
            if norm_len > 0:
                normal_x, normal_y = normal_x / norm_len, normal_y / norm_len
            # Dot with light direction
            light_dot = normal_x * light_direction[0] + normal_y * light_direction[1]
            is_highlight = light_dot > 0.2
        else:
            is_highlight = side_bias > 0.3

        bundle = StrandBundle(
            spine_points=spine_points,
            strand_count=rng.randint(8, 15),  # 8-15 sub-strands per bundle
            spread=rng.uniform(0.2, 0.4),
            color_offset=rng.uniform(-0.2, 0.2),
            z_depth=1.0 - abs(side_bias) + rng.uniform(-0.1, 0.1),
            is_highlight=is_highlight,
        )
        bundles.append(bundle)

    # Sort by z-depth
    bundles.sort(key=lambda b: b.z_depth)
    return bundles


def expand_bundle_to_clusters(bundle: StrandBundle, width: float,
                               rng: random.Random) -> List[HairCluster]:
    """
    Expand a strand bundle into individual HairCluster objects.

    Creates tightly-grouped strands around the master spine.
    """
    clusters = []

    for strand_idx in range(bundle.strand_count):
        # Offset from spine center
        strand_t = strand_idx / max(1, bundle.strand_count - 1)
        offset_angle = strand_t * 2 * math.pi  # Distribute around spine
        offset_dist = bundle.spread * width * 0.05 * (0.5 + 0.5 * math.sin(strand_t * 3))

        offset_x = math.cos(offset_angle) * offset_dist
        offset_y = math.sin(offset_angle) * offset_dist * 0.3  # Flatter in y

        # Create offset control points
        control_points = []
        for px, py in bundle.spine_points:
            # Vary offset slightly along length
            varied_offset_x = offset_x + rng.uniform(-1, 1)
            varied_offset_y = offset_y + rng.uniform(-0.5, 0.5)
            control_points.append((px + varied_offset_x, py + varied_offset_y))

        # Width profile
        base_width = rng.uniform(2.0, 3.5)
        width_profile = [
            (0.0, base_width * 0.8),
            (0.25, base_width),
            (0.5, base_width * 0.85),
            (0.75, base_width * 0.5),
            (1.0, base_width * 0.15),
        ]

        # Color variation within bundle (tighter than random)
        strand_color_offset = bundle.color_offset + rng.uniform(-0.1, 0.1)

        cluster = HairCluster(
            control_points=control_points,
            width_profile=width_profile,
            z_depth=bundle.z_depth + strand_idx * 0.001,  # Slight z variation
            color_offset=strand_color_offset,
            is_highlight=bundle.is_highlight,
        )
        clusters.append(cluster)

    return clusters


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

    # Sample points along the bezier curve (more steps for smoother, professional curves)
    steps = 90  # Increased from 45 for smoother rendering
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


def _pick_curl_color(color_ramp: List[Color], base_idx: int,
                     light_factor: float, t: float,
                     rng: random.Random) -> Color:
    ramp_len = len(color_ramp)
    idx = base_idx

    if light_factor > 0.55 and t < 0.35:
        idx = min(ramp_len - 1, base_idx + 3)
    elif light_factor > 0.25:
        idx = min(ramp_len - 1, base_idx + 2)
    elif light_factor < -0.45:
        idx = max(0, base_idx - 2)
    elif light_factor < -0.2:
        idx = max(0, base_idx - 1)

    if t > 0.65:
        idx = max(0, idx - 1)

    idx = max(0, min(ramp_len - 1, idx + rng.choice([-1, 0, 0, 1])))
    return color_ramp[idx]


def _draw_spiral_curl(canvas: Canvas, cx: float, cy: float,
                      curl_radius: float, color_ramp: List[Color],
                      base_idx: int, light_factor: float,
                      rng: random.Random) -> None:
    turns = rng.uniform(1.4, 2.4)
    steps = max(12, int(turns * 14))
    direction = rng.choice([-1, 1])
    phase = rng.uniform(0.0, math.tau)

    for i in range(steps):
        t = i / (steps - 1)
        angle = phase + direction * t * turns * math.tau
        radius = curl_radius * (1.0 - 0.55 * t)
        radius += math.sin(t * math.tau) * curl_radius * 0.08

        px = cx + math.cos(angle) * radius
        py = cy + math.sin(angle) * radius

        dot_radius = max(1, int(curl_radius * (0.25 - 0.1 * t)))
        color = _pick_curl_color(color_ramp, base_idx, light_factor, t, rng)
        canvas.fill_circle_aa(int(px), int(py), dot_radius, color)


def _render_curly_hair(canvas: Canvas, center_x: float, top_y: float,
                       width: float, length: float,
                       color_ramp: List[Color],
                       light_direction: Tuple[float, float] = (1.0, -1.0),
                       seed: Optional[int] = None) -> None:
    rng = random.Random(seed) if seed is not None else random.Random()

    ramp_len = len(color_ramp)
    base_idx = ramp_len // 2
    shadow_idx = max(0, base_idx - 2)
    highlight_idx = min(ramp_len - 1, base_idx + 3)

    hair_height = length * 0.9
    mass_cx = center_x
    mass_cy = top_y + hair_height * 0.45
    rx = width * 0.55
    ry = hair_height * 0.6

    ld_x, ld_y = light_direction
    ld_mag = math.sqrt(ld_x * ld_x + ld_y * ld_y)
    if ld_mag > 0:
        ld_x /= ld_mag
        ld_y /= ld_mag
    else:
        ld_x, ld_y = (1.0, -1.0)

    def random_point_in_mass() -> Tuple[float, float]:
        for _ in range(24):
            x = rng.uniform(mass_cx - rx, mass_cx + rx)
            y = rng.uniform(top_y, top_y + hair_height)
            nx = (x - mass_cx) / rx
            ny = (y - mass_cy) / ry
            if nx * nx + ny * ny <= 1.05:
                return x, y
        return (
            rng.uniform(mass_cx - rx, mass_cx + rx),
            rng.uniform(top_y, top_y + hair_height),
        )

    curl_count = max(80, int(width * 1.5))
    base_count = int(curl_count * 0.35)
    mid_count = int(curl_count * 0.45)
    top_count = max(1, curl_count - base_count - mid_count)

    base_min = max(2.0, width * 0.045)
    base_max = width * 0.09
    mid_min = max(2.0, width * 0.035)
    mid_max = width * 0.075
    top_min = max(2.0, width * 0.03)
    top_max = width * 0.06

    base_color = color_ramp[shadow_idx]
    for _ in range(base_count):
        cx, cy = random_point_in_mass()
        radius = rng.uniform(base_min, base_max)
        canvas.fill_circle_aa(int(cx), int(cy), int(radius), base_color)

    for _ in range(mid_count):
        cx, cy = random_point_in_mass()
        radius = rng.uniform(mid_min, mid_max)
        nx = (cx - mass_cx) / rx
        ny = (cy - mass_cy) / ry
        light_factor = nx * ld_x + ny * ld_y + (mass_cy - cy) / max(ry, 1.0) * 0.2
        _draw_spiral_curl(canvas, cx, cy, radius, color_ramp, base_idx, light_factor, rng)

    for _ in range(top_count):
        cx, cy = random_point_in_mass()
        radius = rng.uniform(top_min, top_max)
        nx = (cx - mass_cx) / rx
        ny = (cy - mass_cy) / ry
        light_factor = nx * ld_x + ny * ld_y + (mass_cy - cy) / max(ry, 1.0) * 0.25
        _draw_spiral_curl(canvas, cx, cy, radius, color_ramp, base_idx, light_factor, rng)

        if light_factor > 0.35 and rng.random() > 0.6:
            hx = cx + radius * 0.3
            hy = cy - radius * 0.25
            canvas.fill_circle_aa(int(hx), int(hy), max(1, int(radius * 0.2)), color_ramp[highlight_idx])


def render_hair(canvas: Canvas, style: HairStyle, center_x: float, top_y: float,
                width: float, length: float, color_ramp: List[Color],
                light_direction: Tuple[float, float] = (1.0, -1.0),
                count: int = 70,
                seed: Optional[int] = None,
                include_strays: bool = True,
                highlight_ramp: Optional[List[Color]] = None,
                highlight_intensity: float = 0.0,
                use_bundles: bool = True) -> None:
    """
    Render hair for a given style.

    Args:
        count: Number of hair bundles (60-100 recommended for quality)
        highlight_ramp: Optional color ramp for highlighted strands
        highlight_intensity: 0.0-1.0, proportion of clusters to highlight
        use_bundles: If True, use the FlowField/StrandBundle system for coherent flow
    """
    if style == HairStyle.CURLY:
        _render_curly_hair(
            canvas=canvas,
            center_x=center_x,
            top_y=top_y,
            width=width,
            length=length,
            color_ramp=color_ramp,
            light_direction=light_direction,
            seed=seed,
        )
        return

    rng = random.Random(seed) if seed is not None else random.Random()

    # Use bundle system for styles that benefit from coherent flow
    if use_bundles and style in (HairStyle.WAVY, HairStyle.STRAIGHT, HairStyle.LONG):
        # Create flow field
        flow_field = create_flow_field(center_x, top_y, width, length, style, rng)

        # Generate bundles
        bundle_count = max(60, min(100, count))  # Clamp to 60-100 range
        bundles = generate_strand_bundles(
            center_x, top_y, width, length,
            flow_field, bundle_count, light_direction, rng
        )

        # Expand bundles to clusters
        clusters = []
        for bundle in bundles:
            bundle_clusters = expand_bundle_to_clusters(bundle, width, rng)
            clusters.extend(bundle_clusters)
    else:
        # Use legacy cluster generation for other styles
        clusters = generate_hair_clusters(style, center_x, top_y, width, length, count, seed)

    if include_strays:
        strays = generate_stray_strands(center_x, top_y, width, length, max(3, count // 6), rng)
        clusters.extend(strays)

    clusters.sort(key=lambda c: c.z_depth)

    # Render with highlights if enabled
    if highlight_ramp is not None and highlight_intensity > 0:
        highlight_rng = random.Random(seed + 500 if seed else None)
        for cluster in clusters:
            # Randomly select clusters to highlight based on intensity
            use_highlight = highlight_rng.random() < highlight_intensity
            ramp = highlight_ramp if use_highlight else color_ramp
            render_cluster(canvas, cluster, ramp, light_direction)
    else:
        render_hair_clusters(canvas, clusters, color_ramp, light_direction)


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
