"""
Bitsy Debug Utilities - Comprehensive inspection and debugging tools.

This module provides utilities for:
- Visual inspection of canvases
- Color analysis and palette extraction
- Performance profiling
- State inspection and comparison
- Error diagnosis
"""

import sys
import os
import time
import traceback
from collections import Counter
from typing import Optional, List, Dict, Any, Tuple, Callable

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


# =============================================================================
# Canvas Inspection
# =============================================================================

def inspect_canvas(canvas: Canvas, name: str = "Canvas") -> Dict[str, Any]:
    """
    Comprehensive canvas inspection returning detailed statistics.

    Args:
        canvas: Canvas to inspect
        name: Display name for the canvas

    Returns:
        Dictionary with inspection results
    """
    info = {
        "name": name,
        "dimensions": (canvas.width, canvas.height),
        "total_pixels": canvas.width * canvas.height,
        "opaque_pixels": 0,
        "transparent_pixels": 0,
        "semi_transparent_pixels": 0,
        "unique_colors": set(),
        "color_histogram": Counter(),
        "bounding_box": None,
        "center_of_mass": None,
    }

    min_x, min_y = canvas.width, canvas.height
    max_x, max_y = 0, 0
    sum_x, sum_y = 0, 0
    opaque_count = 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.pixels[y][x])
            alpha = pixel[3]

            info["unique_colors"].add(pixel)
            info["color_histogram"][pixel] += 1

            if alpha == 255:
                info["opaque_pixels"] += 1
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)
                sum_x += x
                sum_y += y
                opaque_count += 1
            elif alpha == 0:
                info["transparent_pixels"] += 1
            else:
                info["semi_transparent_pixels"] += 1
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)

    info["unique_color_count"] = len(info["unique_colors"])

    if opaque_count > 0:
        info["bounding_box"] = (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        info["center_of_mass"] = (sum_x / opaque_count, sum_y / opaque_count)

    # Convert set to list for JSON serialization
    info["unique_colors"] = list(info["unique_colors"])

    return info


def print_canvas_stats(canvas: Canvas, name: str = "Canvas"):
    """Print formatted canvas statistics to stdout."""
    info = inspect_canvas(canvas, name)

    print(f"\n{'='*60}")
    print(f"Canvas: {info['name']}")
    print(f"{'='*60}")
    print(f"Dimensions: {info['dimensions'][0]}x{info['dimensions'][1]}")
    print(f"Total pixels: {info['total_pixels']}")
    print(f"Opaque pixels: {info['opaque_pixels']} ({100*info['opaque_pixels']/info['total_pixels']:.1f}%)")
    print(f"Transparent pixels: {info['transparent_pixels']} ({100*info['transparent_pixels']/info['total_pixels']:.1f}%)")
    print(f"Semi-transparent: {info['semi_transparent_pixels']}")
    print(f"Unique colors: {info['unique_color_count']}")

    if info['bounding_box']:
        bb = info['bounding_box']
        print(f"Bounding box: x={bb[0]}, y={bb[1]}, w={bb[2]}, h={bb[3]}")

    if info['center_of_mass']:
        com = info['center_of_mass']
        print(f"Center of mass: ({com[0]:.1f}, {com[1]:.1f})")

    # Top colors
    print(f"\nTop 5 colors:")
    for color, count in info['color_histogram'].most_common(5):
        r, g, b, a = color
        pct = 100 * count / info['total_pixels']
        print(f"  rgba({r},{g},{b},{a}): {count} pixels ({pct:.1f}%)")


def canvas_to_ascii(canvas: Canvas, width: int = 40) -> str:
    """
    Convert canvas to ASCII art representation.

    Args:
        canvas: Canvas to convert
        width: Target width in characters

    Returns:
        ASCII art string
    """
    # ASCII gradient from dark to light
    chars = " .:-=+*#%@"

    # Calculate scaling
    scale = max(1, canvas.width // width)
    out_width = canvas.width // scale
    out_height = canvas.height // scale

    lines = []
    for y in range(out_height):
        line = ""
        for x in range(out_width):
            # Sample the canvas
            px = min(x * scale, canvas.width - 1)
            py = min(y * scale, canvas.height - 1)
            pixel = canvas.pixels[py][px]

            # Calculate brightness
            if pixel[3] == 0:
                char = " "
            else:
                brightness = (pixel[0] + pixel[1] + pixel[2]) / 3 / 255
                alpha_factor = pixel[3] / 255
                adjusted = brightness * alpha_factor
                char_idx = int(adjusted * (len(chars) - 1))
                char = chars[char_idx]

            line += char
        lines.append(line)

    return "\n".join(lines)


def canvas_to_ansi(canvas: Canvas, width: int = 40) -> str:
    """
    Convert canvas to ANSI colored terminal output.
    Uses block characters with true color.

    Args:
        canvas: Canvas to convert
        width: Target width in characters

    Returns:
        ANSI colored string
    """
    scale = max(1, canvas.width // width)
    out_width = canvas.width // scale
    out_height = canvas.height // scale

    lines = []
    for y in range(out_height):
        line = ""
        for x in range(out_width):
            px = min(x * scale, canvas.width - 1)
            py = min(y * scale, canvas.height - 1)
            pixel = canvas.pixels[py][px]

            if pixel[3] == 0:
                line += " "
            else:
                r, g, b = pixel[0], pixel[1], pixel[2]
                # True color ANSI escape
                line += f"\033[48;2;{r};{g};{b}m \033[0m"

        lines.append(line)

    return "\n".join(lines)


def canvas_diff(canvas1: Canvas, canvas2: Canvas) -> Tuple[Canvas, int]:
    """
    Create a visual diff between two canvases.

    Returns:
        Tuple of (diff_canvas, difference_count)
        - Matching pixels shown in grayscale
        - Different pixels shown in red
    """
    w = max(canvas1.width, canvas2.width)
    h = max(canvas1.height, canvas2.height)
    diff = Canvas(w, h)
    diff_count = 0

    for y in range(h):
        for x in range(w):
            # Get pixels (transparent if out of bounds)
            p1 = canvas1.pixels[y][x] if y < canvas1.height and x < canvas1.width else [0, 0, 0, 0]
            p2 = canvas2.pixels[y][x] if y < canvas2.height and x < canvas2.width else [0, 0, 0, 0]

            if list(p1) == list(p2):
                # Same - show in grayscale
                gray = (p1[0] + p1[1] + p1[2]) // 3
                diff.pixels[y][x] = [gray, gray, gray, p1[3]]
            else:
                # Different - show in red
                diff.pixels[y][x] = [255, 0, 0, 255]
                diff_count += 1

    return diff, diff_count


# =============================================================================
# Color Analysis
# =============================================================================

def extract_palette(canvas: Canvas, max_colors: int = 16) -> List[Tuple[int, int, int, int]]:
    """
    Extract the most common colors from a canvas.

    Args:
        canvas: Source canvas
        max_colors: Maximum colors to return

    Returns:
        List of RGBA tuples sorted by frequency
    """
    counter = Counter()

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.pixels[y][x])
            if pixel[3] > 0:  # Skip transparent
                counter[pixel] += 1

    return [color for color, _ in counter.most_common(max_colors)]


def analyze_color_distribution(canvas: Canvas) -> Dict[str, Any]:
    """
    Analyze the color distribution in a canvas.

    Returns:
        Dictionary with color analysis results
    """
    analysis = {
        "total_opaque_pixels": 0,
        "avg_brightness": 0,
        "avg_saturation": 0,
        "dominant_hue": None,
        "color_spread": 0,
        "is_grayscale": True,
        "has_alpha_gradient": False,
    }

    brightness_sum = 0
    saturation_sum = 0
    hue_counts = Counter()
    alpha_values = set()

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]
            r, g, b, a = pixel[0], pixel[1], pixel[2], pixel[3]

            if a > 0:
                analysis["total_opaque_pixels"] += 1
                alpha_values.add(a)

                # Check grayscale
                if not (r == g == b):
                    analysis["is_grayscale"] = False

                # Brightness (0-1)
                brightness = (r + g + b) / 3 / 255
                brightness_sum += brightness

                # Simple saturation approximation
                max_c = max(r, g, b)
                min_c = min(r, g, b)
                if max_c > 0:
                    sat = (max_c - min_c) / max_c
                    saturation_sum += sat

                # Hue bucket (simplified)
                if max_c - min_c > 10:  # Has color
                    if r > g and r > b:
                        hue_counts["red"] += 1
                    elif g > r and g > b:
                        hue_counts["green"] += 1
                    elif b > r and b > g:
                        hue_counts["blue"] += 1
                    elif r > b and g > b:
                        hue_counts["yellow"] += 1
                    elif r > g and b > g:
                        hue_counts["magenta"] += 1
                    else:
                        hue_counts["cyan"] += 1

    if analysis["total_opaque_pixels"] > 0:
        analysis["avg_brightness"] = brightness_sum / analysis["total_opaque_pixels"]
        analysis["avg_saturation"] = saturation_sum / analysis["total_opaque_pixels"]

        if hue_counts:
            analysis["dominant_hue"] = hue_counts.most_common(1)[0][0]

    # Check for alpha gradient (more than just 0 and 255)
    analysis["has_alpha_gradient"] = len(alpha_values - {0, 255}) > 0

    return analysis


# =============================================================================
# Performance Profiling
# =============================================================================

class Profiler:
    """Simple profiler for timing code blocks."""

    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
        self.active_timers: Dict[str, float] = {}

    def start(self, name: str):
        """Start timing a named block."""
        self.active_timers[name] = time.perf_counter()

    def stop(self, name: str) -> float:
        """Stop timing a named block and return elapsed time."""
        if name not in self.active_timers:
            return 0.0

        elapsed = time.perf_counter() - self.active_timers[name]
        del self.active_timers[name]

        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(elapsed)

        return elapsed

    def time(self, name: str):
        """Context manager for timing a block."""
        class Timer:
            def __init__(self, profiler, name):
                self.profiler = profiler
                self.name = name

            def __enter__(self):
                self.profiler.start(self.name)
                return self

            def __exit__(self, *args):
                self.profiler.stop(self.name)

        return Timer(self, name)

    def report(self) -> str:
        """Generate a timing report."""
        lines = ["\nProfiling Report", "=" * 50]

        for name, times in sorted(self.timings.items()):
            total = sum(times)
            avg = total / len(times)
            min_t = min(times)
            max_t = max(times)

            lines.append(f"\n{name}:")
            lines.append(f"  Calls: {len(times)}")
            lines.append(f"  Total: {total*1000:.2f}ms")
            lines.append(f"  Avg:   {avg*1000:.2f}ms")
            lines.append(f"  Min:   {min_t*1000:.2f}ms")
            lines.append(f"  Max:   {max_t*1000:.2f}ms")

        return "\n".join(lines)

    def clear(self):
        """Clear all timings."""
        self.timings.clear()
        self.active_timers.clear()


def benchmark(func: Callable, iterations: int = 100, warmup: int = 10) -> Dict[str, float]:
    """
    Benchmark a function.

    Args:
        func: Function to benchmark (takes no arguments)
        iterations: Number of timed iterations
        warmup: Number of warmup iterations

    Returns:
        Dictionary with timing statistics
    """
    # Warmup
    for _ in range(warmup):
        func()

    # Timed runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)

    return {
        "iterations": iterations,
        "total_ms": sum(times) * 1000,
        "avg_ms": (sum(times) / len(times)) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "std_ms": (sum((t - sum(times)/len(times))**2 for t in times) / len(times)) ** 0.5 * 1000,
    }


def memory_size_estimate(canvas: Canvas) -> int:
    """
    Estimate memory usage of a canvas in bytes.

    Note: This is an estimate based on the pixel array structure.
    """
    # Each pixel is 4 integers (RGBA)
    # Python integers are 28 bytes each (on 64-bit)
    # Lists have overhead
    pixel_count = canvas.width * canvas.height

    # Rough estimate
    pixel_size = 4 * 28  # 4 ints per pixel
    list_overhead = 56  # Per list object
    row_overhead = list_overhead * canvas.height

    return pixel_count * pixel_size + row_overhead + list_overhead


# =============================================================================
# Error Diagnosis
# =============================================================================

def diagnose_canvas_error(canvas: Canvas, operation: str) -> Dict[str, Any]:
    """
    Diagnose potential issues with a canvas after an operation.

    Args:
        canvas: Canvas to diagnose
        operation: Name of the operation performed

    Returns:
        Dictionary with diagnosis results
    """
    issues = []
    warnings = []

    # Check dimensions
    if canvas.width <= 0 or canvas.height <= 0:
        issues.append(f"Invalid dimensions: {canvas.width}x{canvas.height}")

    if canvas.width > 4096 or canvas.height > 4096:
        warnings.append(f"Large canvas: {canvas.width}x{canvas.height} may cause performance issues")

    # Check pixel validity
    sample_count = min(100, canvas.width * canvas.height)
    invalid_pixels = 0

    import random
    rng = random.Random(42)

    for _ in range(sample_count):
        x = rng.randint(0, canvas.width - 1)
        y = rng.randint(0, canvas.height - 1)
        pixel = canvas.pixels[y][x]

        # Check pixel structure
        if len(pixel) != 4:
            invalid_pixels += 1
            continue

        # Check value ranges
        for i, val in enumerate(pixel):
            if not isinstance(val, (int, float)) or val < 0 or val > 255:
                invalid_pixels += 1
                break

    if invalid_pixels > 0:
        issues.append(f"Found {invalid_pixels}/{sample_count} invalid pixels in sample")

    # Check for common issues
    info = inspect_canvas(canvas)

    if info["opaque_pixels"] == 0:
        warnings.append("Canvas is completely transparent")

    if info["unique_color_count"] == 1 and info["opaque_pixels"] > 0:
        warnings.append("Canvas has only one color (may be unintended)")

    return {
        "operation": operation,
        "issues": issues,
        "warnings": warnings,
        "has_issues": len(issues) > 0,
        "canvas_info": info,
    }


def trace_operation(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Execute a function with full tracing.

    Returns:
        Dictionary with execution results and trace information
    """
    result = {
        "success": False,
        "return_value": None,
        "error": None,
        "traceback": None,
        "execution_time_ms": 0,
    }

    start = time.perf_counter()

    try:
        result["return_value"] = func(*args, **kwargs)
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()

    result["execution_time_ms"] = (time.perf_counter() - start) * 1000

    return result


# =============================================================================
# Comparison Utilities
# =============================================================================

def compare_canvases(canvas1: Canvas, canvas2: Canvas,
                     name1: str = "Canvas 1", name2: str = "Canvas 2") -> Dict[str, Any]:
    """
    Detailed comparison between two canvases.

    Returns:
        Dictionary with comparison results
    """
    info1 = inspect_canvas(canvas1, name1)
    info2 = inspect_canvas(canvas2, name2)

    comparison = {
        "same_dimensions": info1["dimensions"] == info2["dimensions"],
        "dimension_diff": (
            info2["dimensions"][0] - info1["dimensions"][0],
            info2["dimensions"][1] - info1["dimensions"][1]
        ),
        "same_content": False,
        "pixel_differences": 0,
        "color_count_diff": info2["unique_color_count"] - info1["unique_color_count"],
        "opacity_diff": info2["opaque_pixels"] - info1["opaque_pixels"],
        "shared_colors": 0,
    }

    # Check content equality if same dimensions
    if comparison["same_dimensions"]:
        diff_count = 0
        for y in range(canvas1.height):
            for x in range(canvas1.width):
                if list(canvas1.pixels[y][x]) != list(canvas2.pixels[y][x]):
                    diff_count += 1

        comparison["pixel_differences"] = diff_count
        comparison["same_content"] = diff_count == 0

    # Count shared colors
    colors1 = set(tuple(c) for c in info1["unique_colors"])
    colors2 = set(tuple(c) for c in info2["unique_colors"])
    comparison["shared_colors"] = len(colors1 & colors2)

    return comparison


def assert_canvas_valid(canvas: Canvas, context: str = ""):
    """
    Assert that a canvas is valid, raising detailed errors if not.

    Args:
        canvas: Canvas to validate
        context: Context string for error messages
    """
    prefix = f"[{context}] " if context else ""

    # Check type
    if not isinstance(canvas, Canvas):
        raise AssertionError(f"{prefix}Expected Canvas, got {type(canvas).__name__}")

    # Check dimensions
    if canvas.width <= 0:
        raise AssertionError(f"{prefix}Invalid width: {canvas.width}")
    if canvas.height <= 0:
        raise AssertionError(f"{prefix}Invalid height: {canvas.height}")

    # Check pixel array structure
    if len(canvas.pixels) != canvas.height:
        raise AssertionError(
            f"{prefix}Pixel array height mismatch: {len(canvas.pixels)} != {canvas.height}"
        )

    for y, row in enumerate(canvas.pixels):
        if len(row) != canvas.width:
            raise AssertionError(
                f"{prefix}Row {y} width mismatch: {len(row)} != {canvas.width}"
            )

        for x, pixel in enumerate(row):
            if len(pixel) != 4:
                raise AssertionError(
                    f"{prefix}Pixel ({x},{y}) has {len(pixel)} components, expected 4"
                )


# =============================================================================
# Debug Output
# =============================================================================

def save_debug_snapshot(canvas: Canvas, name: str, output_dir: str = "debug_output"):
    """
    Save a debug snapshot of a canvas.

    Creates:
    - PNG image
    - Text file with statistics
    - ASCII preview
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    base_path = os.path.join(output_dir, name)

    # Save PNG
    canvas.save(f"{base_path}.png")

    # Save stats
    info = inspect_canvas(canvas, name)
    with open(f"{base_path}_stats.txt", "w") as f:
        f.write(f"Canvas: {name}\n")
        f.write(f"Dimensions: {info['dimensions']}\n")
        f.write(f"Opaque pixels: {info['opaque_pixels']}\n")
        f.write(f"Unique colors: {info['unique_color_count']}\n")
        if info['bounding_box']:
            f.write(f"Bounding box: {info['bounding_box']}\n")
        f.write(f"\nASCII Preview:\n")
        f.write(canvas_to_ascii(canvas))

    # Save ASCII
    with open(f"{base_path}_ascii.txt", "w") as f:
        f.write(canvas_to_ascii(canvas, width=80))


class DebugSession:
    """
    Debugging session that captures operations and their results.
    """

    def __init__(self, name: str = "debug_session"):
        self.name = name
        self.operations: List[Dict[str, Any]] = []
        self.profiler = Profiler()
        self.snapshots: Dict[str, Canvas] = {}

    def log(self, operation: str, details: Dict[str, Any] = None):
        """Log an operation."""
        entry = {
            "timestamp": time.time(),
            "operation": operation,
            "details": details or {},
        }
        self.operations.append(entry)

    def snapshot(self, name: str, canvas: Canvas):
        """Save a canvas snapshot."""
        self.snapshots[name] = canvas.copy()
        self.log("snapshot", {"name": name, "dimensions": (canvas.width, canvas.height)})

    def compare_snapshots(self, name1: str, name2: str) -> Dict[str, Any]:
        """Compare two saved snapshots."""
        if name1 not in self.snapshots:
            raise KeyError(f"Snapshot '{name1}' not found")
        if name2 not in self.snapshots:
            raise KeyError(f"Snapshot '{name2}' not found")

        return compare_canvases(
            self.snapshots[name1], self.snapshots[name2],
            name1, name2
        )

    def report(self) -> str:
        """Generate a session report."""
        lines = [
            f"\nDebug Session: {self.name}",
            "=" * 60,
            f"\nOperations logged: {len(self.operations)}",
            f"Snapshots saved: {len(self.snapshots)}",
        ]

        if self.operations:
            lines.append("\nOperation Log:")
            for i, op in enumerate(self.operations[-10:]):  # Last 10
                lines.append(f"  {i+1}. {op['operation']}: {op['details']}")

        lines.append(self.profiler.report())

        return "\n".join(lines)

    def save(self, output_dir: str = "debug_output"):
        """Save session data to disk."""
        import os
        import json

        session_dir = os.path.join(output_dir, self.name)
        os.makedirs(session_dir, exist_ok=True)

        # Save operations log
        with open(os.path.join(session_dir, "operations.json"), "w") as f:
            json.dump(self.operations, f, indent=2, default=str)

        # Save snapshots
        for name, canvas in self.snapshots.items():
            save_debug_snapshot(canvas, name, session_dir)

        # Save report
        with open(os.path.join(session_dir, "report.txt"), "w") as f:
            f.write(self.report())


# =============================================================================
# Quick Debug Functions
# =============================================================================

def quick_inspect(canvas: Canvas):
    """Quick one-liner canvas inspection."""
    info = inspect_canvas(canvas)
    print(f"Canvas {info['dimensions'][0]}x{info['dimensions'][1]}: "
          f"{info['opaque_pixels']} opaque, {info['unique_color_count']} colors")


def quick_view(canvas: Canvas):
    """Quick ASCII view of a canvas."""
    print(canvas_to_ascii(canvas, width=40))


def quick_diff(canvas1: Canvas, canvas2: Canvas):
    """Quick visual diff between canvases."""
    _, diff_count = canvas_diff(canvas1, canvas2)
    same_dims = canvas1.width == canvas2.width and canvas1.height == canvas2.height

    print(f"Dimensions match: {same_dims}")
    print(f"Pixel differences: {diff_count}")

    if diff_count > 0:
        print(f"Difference rate: {100*diff_count/(canvas1.width*canvas1.height):.2f}%")


if __name__ == "__main__":
    # Demo the debug utilities
    print("Bitsy Debug Utilities")
    print("=" * 40)

    # Create a test canvas
    canvas = Canvas(16, 16, (100, 150, 200, 255))
    canvas.fill_circle(8, 8, 5, (255, 100, 100, 255))

    print("\n1. Quick Inspect:")
    quick_inspect(canvas)

    print("\n2. ASCII View:")
    quick_view(canvas)

    print("\n3. Full Stats:")
    print_canvas_stats(canvas, "Test Canvas")

    print("\n4. Color Analysis:")
    analysis = analyze_color_distribution(canvas)
    for key, value in analysis.items():
        print(f"  {key}: {value}")

    print("\n5. Benchmark Example:")
    result = benchmark(lambda: Canvas(32, 32, (255, 0, 0, 255)), iterations=100)
    print(f"  Canvas creation: {result['avg_ms']:.3f}ms avg")

    print("\nDebug utilities loaded successfully!")
