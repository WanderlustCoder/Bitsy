"""Advanced color quantization algorithms for palette extraction."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set
import math
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.palette import Palette

Color = Tuple[int, int, int, int]


class QuantizeMethod(Enum):
    """Color quantization methods."""
    MEDIAN_CUT = "median_cut"
    OCTREE = "octree"
    KMEANS = "kmeans"
    POPULARITY = "popularity"


@dataclass
class QuantizeConfig:
    """Configuration for color quantization."""
    method: QuantizeMethod = QuantizeMethod.MEDIAN_CUT
    color_count: int = 16
    preserve_exact: List[Color] = field(default_factory=list)
    weight_saturation: float = 1.0
    include_alpha: bool = False
    min_alpha: int = 128


class ColorBox:
    """A box of colors for median cut algorithm."""

    def __init__(self, colors: List[Tuple[Color, int]]):
        """Initialize with list of (color, count) tuples."""
        self.colors = colors
        self._update_bounds()

    def _update_bounds(self):
        """Update min/max bounds for each channel."""
        if not self.colors:
            self.min_r = self.max_r = 0
            self.min_g = self.max_g = 0
            self.min_b = self.max_b = 0
            return

        self.min_r = min(c[0][0] for c in self.colors)
        self.max_r = max(c[0][0] for c in self.colors)
        self.min_g = min(c[0][1] for c in self.colors)
        self.max_g = max(c[0][1] for c in self.colors)
        self.min_b = min(c[0][2] for c in self.colors)
        self.max_b = max(c[0][2] for c in self.colors)

    @property
    def range_r(self) -> int:
        return self.max_r - self.min_r

    @property
    def range_g(self) -> int:
        return self.max_g - self.min_g

    @property
    def range_b(self) -> int:
        return self.max_b - self.min_b

    @property
    def longest_axis(self) -> int:
        """Return index of longest axis (0=R, 1=G, 2=B)."""
        ranges = [self.range_r, self.range_g, self.range_b]
        return ranges.index(max(ranges))

    @property
    def volume(self) -> int:
        """Return volume of the box."""
        return (self.range_r + 1) * (self.range_g + 1) * (self.range_b + 1)

    @property
    def pixel_count(self) -> int:
        """Return total pixel count in box."""
        return sum(c[1] for c in self.colors)

    def average_color(self) -> Color:
        """Return weighted average color of the box."""
        if not self.colors:
            return (0, 0, 0, 255)

        total = sum(c[1] for c in self.colors)
        if total == 0:
            return (0, 0, 0, 255)

        r = sum(c[0][0] * c[1] for c in self.colors) // total
        g = sum(c[0][1] * c[1] for c in self.colors) // total
        b = sum(c[0][2] * c[1] for c in self.colors) // total

        return (r, g, b, 255)

    def split(self) -> Tuple['ColorBox', 'ColorBox']:
        """Split the box along its longest axis."""
        axis = self.longest_axis

        # Sort colors by the splitting axis
        sorted_colors = sorted(self.colors, key=lambda c: c[0][axis])

        # Find median split point by pixel count
        total = self.pixel_count
        running = 0
        split_idx = len(sorted_colors) // 2

        for i, (color, count) in enumerate(sorted_colors):
            running += count
            if running >= total // 2:
                split_idx = max(1, i)
                break

        return (
            ColorBox(sorted_colors[:split_idx]),
            ColorBox(sorted_colors[split_idx:])
        )


class OctreeNode:
    """Node in an octree for color quantization."""

    def __init__(self, level: int):
        self.level = level
        self.children: List[Optional['OctreeNode']] = [None] * 8
        self.pixel_count = 0
        self.red_sum = 0
        self.green_sum = 0
        self.blue_sum = 0
        self.palette_index = -1

    def is_leaf(self) -> bool:
        return self.pixel_count > 0 and all(c is None for c in self.children)

    def get_color(self) -> Color:
        """Get average color of this node."""
        if self.pixel_count == 0:
            return (0, 0, 0, 255)
        return (
            self.red_sum // self.pixel_count,
            self.green_sum // self.pixel_count,
            self.blue_sum // self.pixel_count,
            255
        )

    def add_color(self, color: Color, level: int = 0):
        """Add a color to the tree."""
        if level >= 8:
            self.pixel_count += 1
            self.red_sum += color[0]
            self.green_sum += color[1]
            self.blue_sum += color[2]
            return

        # Calculate child index based on color bits at this level
        idx = 0
        mask = 0x80 >> level
        if color[0] & mask:
            idx |= 4
        if color[1] & mask:
            idx |= 2
        if color[2] & mask:
            idx |= 1

        if self.children[idx] is None:
            self.children[idx] = OctreeNode(level + 1)

        self.children[idx].add_color(color, level + 1)

    def merge(self):
        """Merge children into this node."""
        for child in self.children:
            if child is not None:
                self.pixel_count += child.pixel_count
                self.red_sum += child.red_sum
                self.green_sum += child.green_sum
                self.blue_sum += child.blue_sum

        self.children = [None] * 8

    def get_leaves(self) -> List['OctreeNode']:
        """Get all leaf nodes."""
        leaves = []
        if self.is_leaf():
            leaves.append(self)
        else:
            for child in self.children:
                if child is not None:
                    leaves.extend(child.get_leaves())
        return leaves


class Octree:
    """Octree for color quantization."""

    def __init__(self, max_colors: int = 256):
        self.root = OctreeNode(0)
        self.max_colors = max_colors
        self.levels: List[List[OctreeNode]] = [[] for _ in range(8)]

    def add_color(self, color: Color):
        """Add a color to the octree."""
        self.root.add_color(color)

    def reduce(self):
        """Reduce the tree to max_colors leaves."""
        leaves = self.root.get_leaves()

        while len(leaves) > self.max_colors:
            # Find node with fewest pixels to merge
            # Start from deepest level
            self._collect_levels()

            merged = False
            for level in range(7, -1, -1):
                if not self.levels[level]:
                    continue

                # Find node with smallest pixel count
                min_node = min(self.levels[level], key=lambda n: n.pixel_count)
                min_node.merge()
                merged = True
                break

            if not merged:
                break

            leaves = self.root.get_leaves()

    def _collect_levels(self):
        """Collect nodes by level."""
        self.levels = [[] for _ in range(8)]
        self._collect_node(self.root)

    def _collect_node(self, node: OctreeNode):
        """Recursively collect nodes."""
        if node.is_leaf():
            return

        has_children = False
        for child in node.children:
            if child is not None:
                has_children = True
                self._collect_node(child)

        if has_children:
            self.levels[node.level].append(node)

    def get_palette(self) -> List[Color]:
        """Get the palette from leaf nodes."""
        leaves = self.root.get_leaves()
        return [leaf.get_color() for leaf in leaves]


class ColorQuantizer:
    """Color quantizer with multiple algorithms."""

    def __init__(self, config: Optional[QuantizeConfig] = None):
        self.config = config or QuantizeConfig()

    def quantize(self, canvas: Canvas) -> Tuple[Canvas, Palette]:
        """Quantize canvas colors and return result with palette."""
        # Extract colors with counts
        color_counts = self._count_colors(canvas)

        # Filter transparent pixels if needed
        if not self.config.include_alpha:
            color_counts = {
                c: n for c, n in color_counts.items()
                if c[3] >= self.config.min_alpha
            }

        # Get target color count
        target = self.config.color_count - len(self.config.preserve_exact)
        target = max(1, target)

        # Run quantization
        if self.config.method == QuantizeMethod.MEDIAN_CUT:
            palette_colors = self._median_cut(color_counts, target)
        elif self.config.method == QuantizeMethod.OCTREE:
            palette_colors = self._octree(color_counts, target)
        elif self.config.method == QuantizeMethod.KMEANS:
            palette_colors = self._kmeans(color_counts, target)
        else:  # POPULARITY
            palette_colors = self._popularity(color_counts, target)

        # Add preserved colors
        palette_colors = list(self.config.preserve_exact) + palette_colors

        # Create palette
        palette = Palette(palette_colors[:self.config.color_count], "Quantized")

        # Remap canvas
        result = self._remap_canvas(canvas, palette)

        return result, palette

    def extract_palette(self, canvas: Canvas) -> Palette:
        """Extract palette without remapping."""
        _, palette = self.quantize(canvas)
        return palette

    def _count_colors(self, canvas: Canvas) -> Dict[Color, int]:
        """Count occurrences of each color."""
        counts: Dict[Color, int] = {}
        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)
                counts[color] = counts.get(color, 0) + 1
        return counts

    def _median_cut(self, color_counts: Dict[Color, int], n: int) -> List[Color]:
        """Median cut algorithm."""
        if not color_counts:
            return [(0, 0, 0, 255)]

        # Create initial box
        colors = [(c, count) for c, count in color_counts.items()]
        boxes = [ColorBox(colors)]

        # Split boxes until we have enough
        while len(boxes) < n:
            # Find box with largest volume * pixel_count
            boxes.sort(key=lambda b: b.volume * b.pixel_count, reverse=True)

            # Split the largest splittable box
            split_done = False
            for i, box in enumerate(boxes):
                if len(box.colors) > 1 and box.volume > 0:
                    box1, box2 = box.split()
                    boxes[i] = box1
                    boxes.append(box2)
                    split_done = True
                    break

            if not split_done:
                break

        return [box.average_color() for box in boxes]

    def _octree(self, color_counts: Dict[Color, int], n: int) -> List[Color]:
        """Octree quantization."""
        tree = Octree(n)

        for color, count in color_counts.items():
            for _ in range(min(count, 100)):  # Limit iterations
                tree.add_color(color)

        tree.reduce()
        return tree.get_palette()

    def _kmeans(self, color_counts: Dict[Color, int], n: int,
                max_iterations: int = 20) -> List[Color]:
        """K-means clustering."""
        colors = list(color_counts.keys())
        if len(colors) <= n:
            return colors

        # Initialize centroids randomly
        random.seed(42)  # Deterministic
        centroids = random.sample(colors, n)
        centroids = [list(c) for c in centroids]

        for _ in range(max_iterations):
            # Assign colors to nearest centroid
            clusters: List[List[Tuple[Color, int]]] = [[] for _ in range(n)]

            for color, count in color_counts.items():
                min_dist = float('inf')
                min_idx = 0

                for i, centroid in enumerate(centroids):
                    dist = self._color_distance_sq(color, tuple(centroid))
                    if dist < min_dist:
                        min_dist = dist
                        min_idx = i

                clusters[min_idx].append((color, count))

            # Update centroids
            new_centroids = []
            for cluster in clusters:
                if cluster:
                    total = sum(c[1] for c in cluster)
                    r = sum(c[0][0] * c[1] for c in cluster) // total
                    g = sum(c[0][1] * c[1] for c in cluster) // total
                    b = sum(c[0][2] * c[1] for c in cluster) // total
                    new_centroids.append([r, g, b, 255])
                else:
                    # Keep old centroid for empty clusters
                    new_centroids.append(centroids[len(new_centroids)])

            # Check convergence
            if centroids == new_centroids:
                break
            centroids = new_centroids

        return [tuple(c) for c in centroids]

    def _popularity(self, color_counts: Dict[Color, int], n: int) -> List[Color]:
        """Simple popularity-based selection."""
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_colors[:n]]

    def _color_distance_sq(self, c1: Color, c2: Color) -> int:
        """Squared Euclidean distance between colors."""
        dr = c1[0] - c2[0]
        dg = c1[1] - c2[1]
        db = c1[2] - c2[2]
        # Weight green more (human perception)
        return dr * dr + dg * dg * 2 + db * db

    def _remap_canvas(self, canvas: Canvas, palette: Palette) -> Canvas:
        """Remap canvas colors to palette."""
        result = Canvas(canvas.width, canvas.height)
        palette_colors = palette.colors

        # Build cache for color mapping
        cache: Dict[Color, Color] = {}

        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)

                # Keep transparent pixels
                if color[3] < self.config.min_alpha:
                    result.set_pixel(x, y, color)
                    continue

                # Check cache
                if color in cache:
                    result.set_pixel(x, y, cache[color])
                    continue

                # Find nearest palette color
                min_dist = float('inf')
                nearest = palette_colors[0]

                for pc in palette_colors:
                    dist = self._color_distance_sq(color, pc)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = pc

                cache[color] = nearest
                result.set_pixel(x, y, nearest)

        return result


# Convenience functions

def median_cut(colors: List[Color], n: int) -> List[Color]:
    """Apply median cut to a list of colors."""
    counts = {c: 1 for c in colors}
    quantizer = ColorQuantizer(QuantizeConfig(
        method=QuantizeMethod.MEDIAN_CUT,
        color_count=n
    ))
    return quantizer._median_cut(counts, n)


def octree_quantize(colors: List[Color], n: int) -> List[Color]:
    """Apply octree quantization to a list of colors."""
    counts = {c: 1 for c in colors}
    quantizer = ColorQuantizer(QuantizeConfig(
        method=QuantizeMethod.OCTREE,
        color_count=n
    ))
    return quantizer._octree(counts, n)


def quantize_image(canvas: Canvas, colors: int = 16,
                   method: str = "median_cut") -> Tuple[Canvas, Palette]:
    """Quantize image colors.

    Args:
        canvas: Source canvas
        colors: Target color count
        method: Quantization method ("median_cut", "octree", "kmeans", "popularity")

    Returns:
        Tuple of (quantized canvas, palette)
    """
    method_map = {
        "median_cut": QuantizeMethod.MEDIAN_CUT,
        "octree": QuantizeMethod.OCTREE,
        "kmeans": QuantizeMethod.KMEANS,
        "popularity": QuantizeMethod.POPULARITY,
    }

    quantizer = ColorQuantizer(QuantizeConfig(
        method=method_map.get(method, QuantizeMethod.MEDIAN_CUT),
        color_count=colors
    ))

    return quantizer.quantize(canvas)


def extract_palette(canvas: Canvas, colors: int = 16,
                    method: str = "median_cut") -> Palette:
    """Extract palette from image.

    Args:
        canvas: Source canvas
        colors: Target color count
        method: Quantization method

    Returns:
        Extracted palette
    """
    _, palette = quantize_image(canvas, colors, method)
    return palette
