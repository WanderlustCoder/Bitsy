"""
Bitsy Test Framework - Core testing utilities and base classes.

Provides:
- TestCase base class with rich assertions
- Canvas comparison utilities
- Visual regression testing helpers
- Performance benchmarking
- Test fixtures and factories
"""

import sys
import os
import time
import hashlib
import traceback
from typing import Optional, List, Tuple, Callable, Any, Dict
from dataclasses import dataclass, field
from io import BytesIO
from contextlib import contextmanager

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Palette


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    duration: float = 0.0
    error: Optional[str] = None
    traceback: Optional[str] = None
    assertions: int = 0
    category: str = "unit"


@dataclass
class TestSuiteResult:
    """Result of a test suite run."""
    name: str
    results: List[TestResult] = field(default_factory=list)
    setup_error: Optional[str] = None
    teardown_error: Optional[str] = None

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def total_duration(self) -> float:
        return sum(r.duration for r in self.results)


class AssertionError(Exception):
    """Custom assertion error with detailed message."""
    pass


class SkipTest(Exception):
    """Exception to skip a test."""
    pass


class TestCase:
    """Base class for all Bitsy tests.

    Provides rich assertions for testing pixel art generation:
    - Basic value assertions
    - Canvas pixel comparison
    - Color matching with tolerance
    - Visual regression testing
    - Performance benchmarking
    """

    def __init__(self):
        self.assertions = 0
        self._skip_reason: Optional[str] = None

    # ==================== Setup/Teardown ====================

    def setUp(self) -> None:
        """Called before each test method."""
        pass

    def tearDown(self) -> None:
        """Called after each test method."""
        pass

    @classmethod
    def setUpClass(cls) -> None:
        """Called once before all tests in the class."""
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        """Called once after all tests in the class."""
        pass

    # ==================== Skip Helpers ====================

    def skip(self, reason: str = ""):
        """Skip this test with optional reason."""
        raise SkipTest(reason)

    def skipIf(self, condition: bool, reason: str = ""):
        """Skip test if condition is true."""
        if condition:
            raise SkipTest(reason)

    def skipUnless(self, condition: bool, reason: str = ""):
        """Skip test unless condition is true."""
        if not condition:
            raise SkipTest(reason)

    # ==================== Basic Assertions ====================

    def assertTrue(self, value: Any, msg: str = "") -> None:
        """Assert value is truthy."""
        self.assertions += 1
        if not value:
            raise AssertionError(msg or f"Expected truthy value, got {value!r}")

    def assertFalse(self, value: Any, msg: str = "") -> None:
        """Assert value is falsy."""
        self.assertions += 1
        if value:
            raise AssertionError(msg or f"Expected falsy value, got {value!r}")

    def assertEqual(self, actual: Any, expected: Any, msg: str = "") -> None:
        """Assert two values are equal."""
        self.assertions += 1
        if actual != expected:
            raise AssertionError(msg or f"Expected {expected!r}, got {actual!r}")

    def assertNotEqual(self, actual: Any, expected: Any, msg: str = "") -> None:
        """Assert two values are not equal."""
        self.assertions += 1
        if actual == expected:
            raise AssertionError(msg or f"Values should not be equal: {actual!r}")

    def assertIs(self, actual: Any, expected: Any, msg: str = "") -> None:
        """Assert two objects are the same."""
        self.assertions += 1
        if actual is not expected:
            raise AssertionError(msg or f"Expected {expected!r} (same object), got {actual!r}")

    def assertIsNot(self, actual: Any, expected: Any, msg: str = "") -> None:
        """Assert two objects are not the same."""
        self.assertions += 1
        if actual is expected:
            raise AssertionError(msg or f"Objects should not be the same: {actual!r}")

    def assertIsNone(self, value: Any, msg: str = "") -> None:
        """Assert value is None."""
        self.assertions += 1
        if value is not None:
            raise AssertionError(msg or f"Expected None, got {value!r}")

    def assertIsNotNone(self, value: Any, msg: str = "") -> None:
        """Assert value is not None."""
        self.assertions += 1
        if value is None:
            raise AssertionError(msg or "Expected non-None value, got None")

    def assertIn(self, item: Any, container: Any, msg: str = "") -> None:
        """Assert item is in container."""
        self.assertions += 1
        if item not in container:
            raise AssertionError(msg or f"{item!r} not found in {container!r}")

    def assertNotIn(self, item: Any, container: Any, msg: str = "") -> None:
        """Assert item is not in container."""
        self.assertions += 1
        if item in container:
            raise AssertionError(msg or f"{item!r} unexpectedly found in {container!r}")

    def assertIsInstance(self, obj: Any, cls: type, msg: str = "") -> None:
        """Assert object is instance of class."""
        self.assertions += 1
        if not isinstance(obj, cls):
            raise AssertionError(msg or f"Expected instance of {cls.__name__}, got {type(obj).__name__}")

    def assertGreater(self, a: Any, b: Any, msg: str = "") -> None:
        """Assert a > b."""
        self.assertions += 1
        if not (a > b):
            raise AssertionError(msg or f"Expected {a!r} > {b!r}")

    def assertGreaterEqual(self, a: Any, b: Any, msg: str = "") -> None:
        """Assert a >= b."""
        self.assertions += 1
        if not (a >= b):
            raise AssertionError(msg or f"Expected {a!r} >= {b!r}")

    def assertLess(self, a: Any, b: Any, msg: str = "") -> None:
        """Assert a < b."""
        self.assertions += 1
        if not (a < b):
            raise AssertionError(msg or f"Expected {a!r} < {b!r}")

    def assertLessEqual(self, a: Any, b: Any, msg: str = "") -> None:
        """Assert a <= b."""
        self.assertions += 1
        if not (a <= b):
            raise AssertionError(msg or f"Expected {a!r} <= {b!r}")

    def assertAlmostEqual(self, a: float, b: float, places: int = 7,
                          msg: str = "", delta: float = None) -> None:
        """Assert floats are almost equal.

        Args:
            a: First value
            b: Second value
            places: Decimal places for comparison (ignored if delta set)
            msg: Custom error message
            delta: Absolute tolerance (overrides places if set)
        """
        self.assertions += 1
        if delta is not None:
            if abs(a - b) > delta:
                raise AssertionError(msg or f"Expected {a} ~= {b} (within delta {delta})")
        else:
            if round(abs(a - b), places) != 0:
                raise AssertionError(msg or f"Expected {a} ~= {b} (to {places} places)")

    def assertRaises(self, exception: type, callable_obj: Callable = None, *args, **kwargs):
        """Assert that an exception is raised.

        Can be used as context manager:
            with self.assertRaises(ValueError):
                do_something()

        Or with callable:
            self.assertRaises(ValueError, int, 'not a number')
        """
        if callable_obj is None:
            return _AssertRaisesContext(self, exception)

        self.assertions += 1
        try:
            callable_obj(*args, **kwargs)
        except exception:
            return
        except Exception as e:
            raise AssertionError(f"Expected {exception.__name__}, got {type(e).__name__}: {e}")
        raise AssertionError(f"Expected {exception.__name__} but no exception was raised")

    # ==================== Canvas Assertions ====================

    def assertCanvasSize(self, canvas: Canvas, width: int, height: int, msg: str = "") -> None:
        """Assert canvas has expected dimensions."""
        self.assertions += 1
        if canvas.width != width or canvas.height != height:
            raise AssertionError(
                msg or f"Expected canvas size {width}x{height}, got {canvas.width}x{canvas.height}"
            )

    def assertPixelColor(self, canvas: Canvas, x: int, y: int,
                         expected: Tuple[int, int, int, int], msg: str = "") -> None:
        """Assert pixel at (x, y) has expected RGBA color."""
        self.assertions += 1
        actual = canvas.pixels[y][x]
        if tuple(actual) != tuple(expected):
            raise AssertionError(
                msg or f"Pixel at ({x}, {y}): expected {expected}, got {tuple(actual)}"
            )

    def assertPixelColorClose(self, canvas: Canvas, x: int, y: int,
                              expected: Tuple[int, int, int, int],
                              tolerance: int = 5, msg: str = "") -> None:
        """Assert pixel color is within tolerance of expected."""
        self.assertions += 1
        actual = canvas.pixels[y][x]
        for i, (a, e) in enumerate(zip(actual, expected)):
            if abs(a - e) > tolerance:
                channel = ['R', 'G', 'B', 'A'][i]
                raise AssertionError(
                    msg or f"Pixel at ({x}, {y}): {channel} channel {a} not within "
                    f"{tolerance} of {e} (full color: {tuple(actual)} vs {expected})"
                )

    def assertCanvasEqual(self, canvas1: Canvas, canvas2: Canvas, msg: str = "") -> None:
        """Assert two canvases are pixel-identical."""
        self.assertions += 1

        if canvas1.width != canvas2.width or canvas1.height != canvas2.height:
            raise AssertionError(
                msg or f"Canvas sizes differ: {canvas1.width}x{canvas1.height} vs "
                f"{canvas2.width}x{canvas2.height}"
            )

        for y in range(canvas1.height):
            for x in range(canvas1.width):
                p1 = canvas1.pixels[y][x]
                p2 = canvas2.pixels[y][x]
                if tuple(p1) != tuple(p2):
                    raise AssertionError(
                        msg or f"Canvases differ at ({x}, {y}): {tuple(p1)} vs {tuple(p2)}"
                    )

    def assertCanvasClose(self, canvas1: Canvas, canvas2: Canvas,
                          tolerance: int = 5, max_diff_pixels: int = 0,
                          msg: str = "") -> None:
        """Assert two canvases are similar within tolerance.

        Args:
            canvas1: First canvas
            canvas2: Second canvas
            tolerance: Max difference per color channel
            max_diff_pixels: Max number of differing pixels allowed
            msg: Custom error message
        """
        self.assertions += 1

        if canvas1.width != canvas2.width or canvas1.height != canvas2.height:
            raise AssertionError(
                msg or f"Canvas sizes differ: {canvas1.width}x{canvas1.height} vs "
                f"{canvas2.width}x{canvas2.height}"
            )

        diff_count = 0
        first_diff = None

        for y in range(canvas1.height):
            for x in range(canvas1.width):
                p1 = canvas1.pixels[y][x]
                p2 = canvas2.pixels[y][x]

                for i in range(4):
                    if abs(p1[i] - p2[i]) > tolerance:
                        diff_count += 1
                        if first_diff is None:
                            first_diff = (x, y, tuple(p1), tuple(p2))
                        break

        if diff_count > max_diff_pixels:
            x, y, p1, p2 = first_diff
            raise AssertionError(
                msg or f"Canvases have {diff_count} differing pixels (max {max_diff_pixels}). "
                f"First diff at ({x}, {y}): {p1} vs {p2}"
            )

    def assertCanvasNotEmpty(self, canvas: Canvas, msg: str = "") -> None:
        """Assert canvas has at least one non-transparent pixel."""
        self.assertions += 1

        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.pixels[y][x][3] > 0:
                    return

        raise AssertionError(msg or "Canvas is empty (all pixels are transparent)")

    def assertCanvasHasColor(self, canvas: Canvas,
                             color: Tuple[int, int, int, int], msg: str = "") -> None:
        """Assert canvas contains at least one pixel of the specified color."""
        self.assertions += 1

        for y in range(canvas.height):
            for x in range(canvas.width):
                if tuple(canvas.pixels[y][x]) == tuple(color):
                    return

        raise AssertionError(msg or f"Color {color} not found in canvas")

    def assertCanvasColorCount(self, canvas: Canvas,
                               expected_count: int, msg: str = "") -> None:
        """Assert canvas has expected number of unique colors."""
        self.assertions += 1

        colors = set()
        for y in range(canvas.height):
            for x in range(canvas.width):
                colors.add(tuple(canvas.pixels[y][x]))

        if len(colors) != expected_count:
            raise AssertionError(
                msg or f"Expected {expected_count} unique colors, found {len(colors)}"
            )

    def assertCanvasHash(self, canvas: Canvas, expected_hash: str, msg: str = "") -> None:
        """Assert canvas produces expected pixel hash.

        Useful for regression testing - generate hash once, then verify.
        """
        self.assertions += 1
        actual_hash = self.getCanvasHash(canvas)

        if actual_hash != expected_hash:
            raise AssertionError(
                msg or f"Canvas hash mismatch: expected {expected_hash}, got {actual_hash}"
            )

    def getCanvasHash(self, canvas: Canvas) -> str:
        """Generate a hash of canvas pixels for comparison."""
        hasher = hashlib.md5()

        for row in canvas.pixels:
            for pixel in row:
                hasher.update(bytes(pixel))

        return hasher.hexdigest()[:16]

    # ==================== Color Assertions ====================

    def assertColorEqual(self, color1: Tuple, color2: Tuple, msg: str = "") -> None:
        """Assert two colors are equal."""
        self.assertions += 1

        # Normalize to RGBA
        c1 = tuple(color1) + (255,) * (4 - len(color1)) if len(color1) < 4 else tuple(color1)
        c2 = tuple(color2) + (255,) * (4 - len(color2)) if len(color2) < 4 else tuple(color2)

        if c1 != c2:
            raise AssertionError(msg or f"Colors differ: {c1} vs {c2}")

    def assertColorClose(self, color1: Tuple, color2: Tuple,
                         tolerance: int = 5, msg: str = "") -> None:
        """Assert two colors are within tolerance."""
        self.assertions += 1

        c1 = tuple(color1) + (255,) * (4 - len(color1)) if len(color1) < 4 else tuple(color1)
        c2 = tuple(color2) + (255,) * (4 - len(color2)) if len(color2) < 4 else tuple(color2)

        for i, (a, b) in enumerate(zip(c1, c2)):
            if abs(a - b) > tolerance:
                channel = ['R', 'G', 'B', 'A'][i]
                raise AssertionError(
                    msg or f"Colors differ in {channel}: {c1} vs {c2} (tolerance {tolerance})"
                )

    # ==================== Performance Assertions ====================

    def assertRunsWithin(self, seconds: float, callable_obj: Callable,
                         *args, msg: str = "", **kwargs) -> Any:
        """Assert callable completes within time limit."""
        self.assertions += 1

        start = time.perf_counter()
        result = callable_obj(*args, **kwargs)
        elapsed = time.perf_counter() - start

        if elapsed > seconds:
            raise AssertionError(
                msg or f"Took {elapsed:.3f}s, expected under {seconds:.3f}s"
            )

        return result

    @contextmanager
    def assertMaxDuration(self, seconds: float, msg: str = ""):
        """Context manager to assert code block completes within time limit."""
        start = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start

        self.assertions += 1
        if elapsed > seconds:
            raise AssertionError(
                msg or f"Block took {elapsed:.3f}s, expected under {seconds:.3f}s"
            )


class _AssertRaisesContext:
    """Context manager for assertRaises."""

    def __init__(self, test_case: TestCase, expected_exception: type):
        self.test_case = test_case
        self.expected = expected_exception
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.test_case.assertions += 1

        if exc_type is None:
            raise AssertionError(f"Expected {self.expected.__name__} but no exception was raised")

        if not issubclass(exc_type, self.expected):
            raise AssertionError(
                f"Expected {self.expected.__name__}, got {exc_type.__name__}: {exc_val}"
            )

        self.exception = exc_val
        return True  # Suppress the exception


# ==================== Test Discovery ====================

def discover_tests(test_class: type) -> List[str]:
    """Discover test methods in a test class.

    Test methods must start with 'test_'.
    """
    methods = []
    for name in dir(test_class):
        if name.startswith('test_') and callable(getattr(test_class, name)):
            methods.append(name)
    return sorted(methods)


def run_test_class(test_class: type,
                   verbose: bool = False,
                   filter_pattern: str = None) -> TestSuiteResult:
    """Run all tests in a test class.

    Args:
        test_class: TestCase subclass
        verbose: Print progress
        filter_pattern: Only run tests matching pattern

    Returns:
        TestSuiteResult with all test results
    """
    suite_result = TestSuiteResult(name=test_class.__name__)

    # Class setup
    try:
        test_class.setUpClass()
    except Exception as e:
        suite_result.setup_error = f"{type(e).__name__}: {e}"
        return suite_result

    # Discover and run tests
    test_methods = discover_tests(test_class)

    if filter_pattern:
        test_methods = [m for m in test_methods if filter_pattern in m]

    for method_name in test_methods:
        if verbose:
            print(f"  {method_name}...", end=" ", flush=True)

        # Create fresh instance
        instance = test_class()
        result = TestResult(name=method_name, passed=True)

        start = time.perf_counter()

        try:
            # Setup
            instance.setUp()

            # Run test
            method = getattr(instance, method_name)
            method()

            result.assertions = instance.assertions

        except SkipTest as e:
            result.passed = True
            result.error = f"SKIPPED: {e}" if str(e) else "SKIPPED"

        except AssertionError as e:
            result.passed = False
            result.error = str(e)
            result.traceback = traceback.format_exc()
            result.assertions = instance.assertions

        except Exception as e:
            result.passed = False
            result.error = f"{type(e).__name__}: {e}"
            result.traceback = traceback.format_exc()
            result.assertions = instance.assertions

        finally:
            try:
                instance.tearDown()
            except Exception as e:
                if result.passed:
                    result.passed = False
                    result.error = f"tearDown error: {type(e).__name__}: {e}"

        result.duration = time.perf_counter() - start
        suite_result.results.append(result)

        if verbose:
            if result.passed:
                if result.error and "SKIPPED" in result.error:
                    print(f"SKIP ({result.error})")
                else:
                    print(f"OK ({result.duration:.3f}s)")
            else:
                print(f"FAIL")
                if result.error:
                    print(f"    {result.error}")

    # Class teardown
    try:
        test_class.tearDownClass()
    except Exception as e:
        suite_result.teardown_error = f"{type(e).__name__}: {e}"

    return suite_result


# ==================== Fixtures ====================

class CanvasFixtures:
    """Pre-built canvas fixtures for testing."""

    @staticmethod
    def blank(width: int = 16, height: int = 16) -> Canvas:
        """Create blank transparent canvas."""
        return Canvas(width, height, (0, 0, 0, 0))

    @staticmethod
    def solid(color: Tuple[int, int, int, int] = (255, 0, 0, 255),
              width: int = 16, height: int = 16) -> Canvas:
        """Create solid color canvas."""
        return Canvas(width, height, color)

    @staticmethod
    def checkerboard(color1: Tuple[int, int, int, int] = (255, 255, 255, 255),
                     color2: Tuple[int, int, int, int] = (0, 0, 0, 255),
                     width: int = 16, height: int = 16,
                     cell_size: int = 1) -> Canvas:
        """Create checkerboard pattern."""
        canvas = Canvas(width, height, color1)
        for y in range(height):
            for x in range(width):
                if ((x // cell_size) + (y // cell_size)) % 2 == 1:
                    canvas.pixels[y][x] = list(color2)
        return canvas

    @staticmethod
    def gradient_h(color1: Tuple[int, int, int, int],
                   color2: Tuple[int, int, int, int],
                   width: int = 16, height: int = 16) -> Canvas:
        """Create horizontal gradient."""
        canvas = Canvas(width, height, (0, 0, 0, 0))
        for x in range(width):
            t = x / max(1, width - 1)
            color = [
                int(color1[i] + (color2[i] - color1[i]) * t)
                for i in range(4)
            ]
            for y in range(height):
                canvas.pixels[y][x] = color
        return canvas

    @staticmethod
    def gradient_v(color1: Tuple[int, int, int, int],
                   color2: Tuple[int, int, int, int],
                   width: int = 16, height: int = 16) -> Canvas:
        """Create vertical gradient."""
        canvas = Canvas(width, height, (0, 0, 0, 0))
        for y in range(height):
            t = y / max(1, height - 1)
            color = [
                int(color1[i] + (color2[i] - color1[i]) * t)
                for i in range(4)
            ]
            for x in range(width):
                canvas.pixels[y][x] = color
        return canvas

    @staticmethod
    def border(border_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
               fill_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
               width: int = 16, height: int = 16,
               border_width: int = 1) -> Canvas:
        """Create canvas with border."""
        canvas = Canvas(width, height, fill_color)

        # Top and bottom
        for x in range(width):
            for b in range(border_width):
                if b < height:
                    canvas.pixels[b][x] = list(border_color)
                    canvas.pixels[height - 1 - b][x] = list(border_color)

        # Left and right
        for y in range(height):
            for b in range(border_width):
                if b < width:
                    canvas.pixels[y][b] = list(border_color)
                    canvas.pixels[y][width - 1 - b] = list(border_color)

        return canvas

    @staticmethod
    def circle(color: Tuple[int, int, int, int] = (255, 255, 255, 255),
               background: Tuple[int, int, int, int] = (0, 0, 0, 0),
               size: int = 16) -> Canvas:
        """Create canvas with filled circle."""
        canvas = Canvas(size, size, background)
        cx, cy = size // 2, size // 2
        radius = size // 2 - 1

        for y in range(size):
            for x in range(size):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= radius * radius:
                    canvas.pixels[y][x] = list(color)

        return canvas


class PaletteFixtures:
    """Pre-built palette fixtures for testing."""

    @staticmethod
    def monochrome() -> List[Tuple[int, int, int, int]]:
        """Black and white palette."""
        return [
            (0, 0, 0, 255),
            (255, 255, 255, 255)
        ]

    @staticmethod
    def grayscale(steps: int = 4) -> List[Tuple[int, int, int, int]]:
        """Grayscale palette with n steps."""
        return [
            (v, v, v, 255)
            for v in range(0, 256, 255 // (steps - 1))
        ][:steps]

    @staticmethod
    def primary() -> List[Tuple[int, int, int, int]]:
        """Primary colors palette."""
        return [
            (255, 0, 0, 255),     # Red
            (0, 255, 0, 255),     # Green
            (0, 0, 255, 255),     # Blue
            (255, 255, 0, 255),   # Yellow
            (255, 0, 255, 255),   # Magenta
            (0, 255, 255, 255),   # Cyan
        ]

    @staticmethod
    def gameboy() -> List[Tuple[int, int, int, int]]:
        """Classic Game Boy 4-color palette."""
        return [
            (15, 56, 15, 255),     # Darkest
            (48, 98, 48, 255),     # Dark
            (139, 172, 15, 255),   # Light
            (155, 188, 15, 255),   # Lightest
        ]

    @staticmethod
    def nes() -> List[Tuple[int, int, int, int]]:
        """NES-style limited palette (subset)."""
        return [
            (0, 0, 0, 255),        # Black
            (252, 252, 252, 255),  # White
            (248, 56, 0, 255),     # Red
            (0, 120, 248, 255),    # Blue
            (0, 168, 0, 255),      # Green
            (248, 184, 0, 255),    # Yellow
        ]


# ==================== Debug Utilities ====================

def canvas_to_ascii(canvas: Canvas,
                    chars: str = " ░▒▓█",
                    width: int = None) -> str:
    """Convert canvas to ASCII art representation.

    Args:
        canvas: Canvas to convert
        chars: Characters from transparent to opaque
        width: Max width (None = original size)

    Returns:
        ASCII art string
    """
    # Calculate scale if width specified
    scale = 1
    if width and canvas.width > width:
        scale = canvas.width // width

    lines = []
    for y in range(0, canvas.height, scale):
        line = ""
        for x in range(0, canvas.width, scale):
            pixel = canvas.pixels[y][x]

            # Use alpha for transparency, or average RGB for brightness
            if pixel[3] == 0:
                idx = 0
            else:
                brightness = (pixel[0] + pixel[1] + pixel[2]) // 3
                # Combine with alpha
                brightness = (brightness * pixel[3]) // 255
                idx = min(len(chars) - 1, brightness * len(chars) // 256)

            line += chars[idx]
        lines.append(line)

    return "\n".join(lines)


def canvas_diff(canvas1: Canvas, canvas2: Canvas) -> Canvas:
    """Create visual diff between two canvases.

    Returns canvas showing:
    - Green: pixels only in canvas1
    - Red: pixels only in canvas2
    - White: matching pixels
    - Gray: both have pixels but different
    """
    width = max(canvas1.width, canvas2.width)
    height = max(canvas1.height, canvas2.height)
    diff = Canvas(width, height, (0, 0, 0, 255))

    for y in range(height):
        for x in range(width):
            # Get pixels (or transparent if out of bounds)
            p1 = canvas1.pixels[y][x] if y < canvas1.height and x < canvas1.width else [0, 0, 0, 0]
            p2 = canvas2.pixels[y][x] if y < canvas2.height and x < canvas2.width else [0, 0, 0, 0]

            has1 = p1[3] > 0
            has2 = p2[3] > 0
            same = tuple(p1) == tuple(p2)

            if same:
                diff.pixels[y][x] = [255, 255, 255, 255]  # White - match
            elif has1 and not has2:
                diff.pixels[y][x] = [0, 255, 0, 255]  # Green - only in canvas1
            elif has2 and not has1:
                diff.pixels[y][x] = [255, 0, 0, 255]  # Red - only in canvas2
            else:
                diff.pixels[y][x] = [128, 128, 128, 255]  # Gray - different

    return diff


def print_canvas_info(canvas: Canvas, name: str = "Canvas") -> None:
    """Print detailed canvas information for debugging."""
    colors = set()
    opaque_count = 0

    for row in canvas.pixels:
        for pixel in row:
            colors.add(tuple(pixel))
            if pixel[3] > 0:
                opaque_count += 1

    total_pixels = canvas.width * canvas.height

    print(f"\n{name}:")
    print(f"  Size: {canvas.width}x{canvas.height} ({total_pixels} pixels)")
    print(f"  Opaque pixels: {opaque_count} ({100*opaque_count/total_pixels:.1f}%)")
    print(f"  Unique colors: {len(colors)}")

    if len(colors) <= 10:
        print(f"  Colors: {sorted(colors)}")


def benchmark(func: Callable, iterations: int = 100,
              warmup: int = 5, *args, **kwargs) -> Dict[str, float]:
    """Benchmark a function.

    Args:
        func: Function to benchmark
        iterations: Number of iterations
        warmup: Warmup iterations (not counted)
        *args, **kwargs: Arguments to pass to function

    Returns:
        Dict with min, max, mean, median times
    """
    # Warmup
    for _ in range(warmup):
        func(*args, **kwargs)

    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        times.append(time.perf_counter() - start)

    times.sort()

    return {
        'min': times[0],
        'max': times[-1],
        'mean': sum(times) / len(times),
        'median': times[len(times) // 2],
        'iterations': iterations,
    }
