"""
Bitsy Benchmarks - Performance testing for all modules.

This module provides comprehensive benchmarks for:
- Canvas operations
- Drawing primitives
- Color operations
- Generator functions
- Export operations

Usage:
    python -m tests.benchmarks
    python -m tests.runner --benchmark
"""

import sys
import os
import time
from typing import Dict, List, Callable, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import blend, rgb_to_hsv, hsv_to_rgb
from core.palette import Palette


# =============================================================================
# Benchmark Framework
# =============================================================================

class BenchmarkResult:
    """Result of a single benchmark."""

    def __init__(self, name: str, iterations: int, times: List[float]):
        self.name = name
        self.iterations = iterations
        self.times = times

    @property
    def total(self) -> float:
        return sum(self.times)

    @property
    def avg(self) -> float:
        return self.total / len(self.times) if self.times else 0

    @property
    def min(self) -> float:
        return min(self.times) if self.times else 0

    @property
    def max(self) -> float:
        return max(self.times) if self.times else 0

    @property
    def std(self) -> float:
        if not self.times:
            return 0
        avg = self.avg
        return (sum((t - avg) ** 2 for t in self.times) / len(self.times)) ** 0.5

    def __str__(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total:      {self.total*1000:.2f}ms\n"
            f"  Avg:        {self.avg*1000:.4f}ms\n"
            f"  Min:        {self.min*1000:.4f}ms\n"
            f"  Max:        {self.max*1000:.4f}ms\n"
            f"  Std:        {self.std*1000:.4f}ms"
        )


def benchmark(func: Callable, iterations: int = 100, warmup: int = 10,
              name: str = None) -> BenchmarkResult:
    """
    Run a benchmark on a function.

    Args:
        func: Function to benchmark (no arguments)
        iterations: Number of timed runs
        warmup: Number of warmup runs
        name: Name for the benchmark

    Returns:
        BenchmarkResult with timing data
    """
    benchmark_name = name or func.__name__

    # Warmup
    for _ in range(warmup):
        func()

    # Timed runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)

    return BenchmarkResult(benchmark_name, iterations, times)


# =============================================================================
# Canvas Benchmarks
# =============================================================================

def bench_canvas_creation():
    """Benchmark canvas creation at various sizes."""
    results = []

    for size in [16, 32, 64, 128, 256]:
        result = benchmark(
            lambda s=size: Canvas(s, s),
            iterations=100,
            name=f"Canvas({size}x{size})"
        )
        results.append(result)

    return results


def bench_canvas_fill():
    """Benchmark canvas fill operations."""
    results = []

    for size in [32, 64, 128]:
        canvas = Canvas(size, size)
        result = benchmark(
            lambda c=canvas: c.fill_rect(0, 0, c.width, c.height, (255, 0, 0, 255)),
            iterations=100,
            name=f"fill_rect({size}x{size})"
        )
        results.append(result)

    return results


def bench_canvas_shapes():
    """Benchmark shape drawing operations."""
    canvas = Canvas(64, 64)
    results = []

    # Rectangle
    result = benchmark(
        lambda: canvas.fill_rect(10, 10, 44, 44, (255, 0, 0, 255)),
        iterations=500,
        name="fill_rect"
    )
    results.append(result)

    # Circle
    result = benchmark(
        lambda: canvas.fill_circle(32, 32, 20, (0, 255, 0, 255)),
        iterations=500,
        name="fill_circle"
    )
    results.append(result)

    # Ellipse
    result = benchmark(
        lambda: canvas.fill_ellipse(32, 32, 25, 15, (0, 0, 255, 255)),
        iterations=500,
        name="fill_ellipse"
    )
    results.append(result)

    # Line
    result = benchmark(
        lambda: canvas.draw_line(0, 0, 63, 63, (255, 255, 255, 255)),
        iterations=500,
        name="draw_line"
    )
    results.append(result)

    return results


def bench_canvas_pixel_ops():
    """Benchmark individual pixel operations."""
    canvas = Canvas(64, 64)
    results = []

    # Set pixel (solid)
    result = benchmark(
        lambda: canvas.set_pixel_solid(32, 32, (255, 0, 0, 255)),
        iterations=1000,
        name="set_pixel_solid"
    )
    results.append(result)

    # Set pixel with blending
    canvas2 = Canvas(64, 64, (100, 100, 100, 255))
    result = benchmark(
        lambda: canvas2.set_pixel(32, 32, (255, 0, 0, 128)),
        iterations=1000,
        name="set_pixel (blended)"
    )
    results.append(result)

    # Get pixel
    result = benchmark(
        lambda: canvas.pixels[32][32],
        iterations=1000,
        name="get_pixel"
    )
    results.append(result)

    return results


def bench_canvas_transforms():
    """Benchmark canvas transformation operations."""
    canvas = Canvas(64, 64, (255, 0, 0, 255))
    canvas.fill_circle(32, 32, 20, (0, 255, 0, 255))

    results = []

    # Copy
    result = benchmark(
        lambda: canvas.copy(),
        iterations=100,
        name="copy"
    )
    results.append(result)

    # Flip horizontal
    result = benchmark(
        lambda: canvas.flip_horizontal(),
        iterations=100,
        name="flip_horizontal"
    )
    results.append(result)

    # Flip vertical
    result = benchmark(
        lambda: canvas.flip_vertical(),
        iterations=100,
        name="flip_vertical"
    )
    results.append(result)

    # Scale up
    result = benchmark(
        lambda: canvas.scale(2),
        iterations=50,
        name="scale(2x)"
    )
    results.append(result)

    return results


def bench_canvas_blit():
    """Benchmark canvas compositing."""
    base = Canvas(64, 64, (100, 100, 100, 255))
    overlay = Canvas(32, 32, (255, 0, 0, 128))

    result = benchmark(
        lambda: base.blit(overlay, 16, 16),
        iterations=500,
        name="blit(32x32 onto 64x64)"
    )

    return [result]


# =============================================================================
# Color Benchmarks
# =============================================================================

def bench_color_blend():
    """Benchmark color blending operations."""
    results = []

    color1 = (255, 0, 0, 128)
    color2 = (0, 255, 0, 255)

    result = benchmark(
        lambda: blend(color1, color2),
        iterations=1000,
        name="blend"
    )
    results.append(result)

    return results


def bench_color_conversion():
    """Benchmark color space conversions."""
    results = []

    rgb = (255, 128, 64)

    result = benchmark(
        lambda: rgb_to_hsv(*rgb),
        iterations=1000,
        name="rgb_to_hsv"
    )
    results.append(result)

    hsv = rgb_to_hsv(*rgb)
    result = benchmark(
        lambda: hsv_to_rgb(*hsv),
        iterations=1000,
        name="hsv_to_rgb"
    )
    results.append(result)

    return results


# =============================================================================
# Palette Benchmarks
# =============================================================================

def bench_palette_ops():
    """Benchmark palette operations."""
    results = []

    # Create palette
    result = benchmark(
        lambda: Palette([
            (0, 0, 0, 255),
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255),
            (255, 255, 0, 255),
            (255, 0, 255, 255),
            (0, 255, 255, 255),
            (255, 255, 255, 255),
        ]),
        iterations=500,
        name="Palette creation"
    )
    results.append(result)

    # Nearest color
    palette = Palette([
        (0, 0, 0, 255),
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 255, 255),
    ])

    result = benchmark(
        lambda: palette.find_nearest((128, 64, 192, 255)),
        iterations=1000,
        name="find_nearest"
    )
    results.append(result)

    return results


# =============================================================================
# Generator Benchmarks
# =============================================================================

def bench_generators():
    """Benchmark generator operations."""
    results = []

    try:
        from generators import generate_item, ItemGenerator

        # Simple item
        result = benchmark(
            lambda: generate_item('sword', seed=42),
            iterations=50,
            name="generate_item('sword')"
        )
        results.append(result)

        # Generator class
        gen = ItemGenerator(16, 24, seed=42)
        result = benchmark(
            lambda: gen.generate_sword(),
            iterations=50,
            name="ItemGenerator.generate_sword()"
        )
        results.append(result)

    except ImportError:
        print("  Generators not available, skipping")

    return results


def bench_icons():
    """Benchmark icon generation."""
    results = []

    try:
        from ui import create_icon, IconGenerator

        result = benchmark(
            lambda: create_icon('heart', size=16),
            iterations=100,
            name="create_icon('heart')"
        )
        results.append(result)

        gen = IconGenerator(size=16)
        result = benchmark(
            lambda: gen.star(),
            iterations=100,
            name="IconGenerator.star()"
        )
        results.append(result)

    except ImportError:
        print("  Icons not available, skipping")

    return results


# =============================================================================
# Export Benchmarks
# =============================================================================

def bench_png_export():
    """Benchmark PNG export."""
    canvas = Canvas(64, 64, (100, 100, 100, 255))
    canvas.fill_circle(32, 32, 20, (255, 0, 0, 255))

    results = []

    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = f.name

    result = benchmark(
        lambda: canvas.save(temp_path),
        iterations=50,
        name="save PNG (64x64)"
    )
    results.append(result)

    # Cleanup
    import os
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return results


def bench_spritesheet():
    """Benchmark spritesheet operations."""
    results = []

    try:
        from export import create_grid_sheet

        frames = [Canvas(16, 16, (i * 30, 0, 0, 255)) for i in range(8)]

        result = benchmark(
            lambda: create_grid_sheet(frames, columns=4),
            iterations=100,
            name="create_grid_sheet(8 frames)"
        )
        results.append(result)

    except ImportError:
        print("  Spritesheet export not available, skipping")

    return results


# =============================================================================
# Main Runner
# =============================================================================

def run_all():
    """Run all benchmarks and print results."""
    print("=" * 70)
    print("BITSY PERFORMANCE BENCHMARKS")
    print("=" * 70)

    all_results = []

    # Canvas benchmarks
    print("\n" + "-" * 70)
    print("CANVAS OPERATIONS")
    print("-" * 70)

    print("\nCanvas Creation:")
    for result in bench_canvas_creation():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nCanvas Fill:")
    for result in bench_canvas_fill():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nShape Drawing (64x64 canvas):")
    for result in bench_canvas_shapes():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nPixel Operations:")
    for result in bench_canvas_pixel_ops():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nTransforms:")
    for result in bench_canvas_transforms():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nCompositing:")
    for result in bench_canvas_blit():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    # Color benchmarks
    print("\n" + "-" * 70)
    print("COLOR OPERATIONS")
    print("-" * 70)

    print("\nBlending:")
    for result in bench_color_blend():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    print("\nConversions:")
    for result in bench_color_conversion():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    # Palette benchmarks
    print("\n" + "-" * 70)
    print("PALETTE OPERATIONS")
    print("-" * 70)

    for result in bench_palette_ops():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    # Generator benchmarks
    print("\n" + "-" * 70)
    print("GENERATORS")
    print("-" * 70)

    for result in bench_generators():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    for result in bench_icons():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    # Export benchmarks
    print("\n" + "-" * 70)
    print("EXPORT OPERATIONS")
    print("-" * 70)

    for result in bench_png_export():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    for result in bench_spritesheet():
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")
        all_results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_time = sum(r.total for r in all_results)
    print(f"\nTotal benchmarks: {len(all_results)}")
    print(f"Total time: {total_time:.2f}s")

    # Find slowest operations
    print("\nSlowest operations:")
    sorted_results = sorted(all_results, key=lambda r: r.avg, reverse=True)[:5]
    for result in sorted_results:
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")

    # Find fastest operations
    print("\nFastest operations:")
    sorted_results = sorted(all_results, key=lambda r: r.avg)[:5]
    for result in sorted_results:
        print(f"  {result.name}: {result.avg*1000:.4f}ms avg")


if __name__ == "__main__":
    run_all()
