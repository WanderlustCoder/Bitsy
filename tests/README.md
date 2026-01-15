# Bitsy Test Suite

## AI-Driven Development Project

**This project is developed entirely by AI agents under human direction.**

You (the AI reading this) are the developer, not just a helper. The human provides requirements and feedback; you implement everything including tests.

---

## MANDATORY: Test Requirements for AI Developers

Since you are the sole developer of this codebase, **you must write tests for all code you create**.

### Your Workflow (Every Task)

```
1. Implement the feature in source files
2. Create/update tests in tests/<category>/test_<module>.py
3. Run: python -m tests.runner
4. If tests fail → fix code or tests → run again
5. Only report "done" when ALL tests pass
```

### Why This Matters

- There is no human developer to catch your mistakes
- Tests are the only safety net for code quality
- The human relies on passing tests to trust your work
- Untested code WILL break eventually

### What Happens If You Skip Tests

- The human will ask you to add them
- You'll have to revisit the code later
- Context may be lost, making it harder
- **Just write the tests the first time**

---

This test suite ensures:
- API stability across changes
- Deterministic output (same seed = same result)
- No regressions in existing functionality
- Performance doesn't degrade

## Quick Start

```bash
# Run all tests
python -m tests.runner

# Run specific category
python -m tests.runner --category core

# Run with verbose output
python -m tests.runner -v

# Run with debug session
python -m tests.runner --debug

# Run benchmarks
python -m tests.runner --benchmark
```

## Test Structure

```
tests/
├── framework.py          # TestCase base class, assertions, fixtures
├── runner.py             # Test discovery and execution
├── debug.py              # Debugging and inspection utilities
├── benchmarks.py         # Performance benchmarks
│
├── core/                 # Core module tests
│   ├── test_canvas.py    # Canvas operations
│   ├── test_color.py     # Color operations
│   └── test_palette.py   # Palette operations
│
├── generators/           # Generator tests
│   └── test_item.py      # Item generation
│
├── effects/              # Effects tests
│   └── test_particles.py # Particle system
│
├── ui/                   # UI tests
│   └── test_icons.py     # Icon generation
│
├── editor/               # Editor tests
│   └── test_transforms.py # Image transforms
│
├── export/               # Export tests
│   ├── test_spritesheet.py
│   └── test_gif.py
│
├── integration/          # Cross-module tests
│   └── test_workflow.py
│
└── visual/               # Visual regression tests
    └── test_regression.py
```

## Development Workflow

### When Adding a New Feature

1. **Create test file** in appropriate category:
   ```
   tests/<category>/test_<module>.py
   ```

2. **Write tests BEFORE or WHILE implementing**:
   ```python
   from tests.framework import TestCase
   from your_module import YourClass

   class TestYourClass(TestCase):
       def test_creation(self):
           """YourClass can be created."""
           obj = YourClass()
           self.assertIsNotNone(obj)

       def test_main_functionality(self):
           """YourClass does what it should."""
           obj = YourClass()
           result = obj.do_thing()
           self.assertEqual(result, expected)

       def test_determinism(self):
           """Same seed produces same output."""
           obj1 = YourClass(seed=42)
           obj2 = YourClass(seed=42)
           self.assertEqual(obj1.generate(), obj2.generate())
   ```

3. **Run tests** to verify:
   ```bash
   python -m tests.runner --filter your_module
   ```

### When Modifying Existing Code

1. **Run existing tests FIRST**:
   ```bash
   python -m tests.runner
   ```

2. **Make your changes**

3. **Update tests** if API changed:
   - Fix broken assertions
   - Add tests for new behavior
   - Remove tests for removed functionality

4. **Run tests again** - all must pass:
   ```bash
   python -m tests.runner
   ```

### Before Committing

```bash
# All tests must pass
python -m tests.runner

# Check performance if relevant
python -m tests.runner --benchmark
```

## Required Test Coverage

Each class/function should have tests for:

| Area | What to Test |
|------|--------------|
| **Creation** | Constructor parameters, defaults, invalid inputs |
| **Core Methods** | All public methods with valid inputs |
| **Edge Cases** | Empty inputs, boundaries, None values |
| **Determinism** | Same seed → identical output |
| **Integration** | Works with other modules |

## Test Framework Features

### Assertions

```python
# Standard assertions
self.assertEqual(a, b)
self.assertNotEqual(a, b)
self.assertTrue(condition)
self.assertFalse(condition)
self.assertIsNone(obj)
self.assertIsNotNone(obj)
self.assertIn(item, container)
self.assertIsInstance(obj, cls)
self.assertAlmostEqual(a, b, places=7, delta=None)
self.assertGreater(a, b)
self.assertLess(a, b)

# Canvas-specific assertions
self.assertCanvasSize(canvas, width, height)
self.assertPixelColor(canvas, x, y, (r, g, b, a))
self.assertCanvasEqual(canvas1, canvas2)
self.assertCanvasClose(canvas1, canvas2, tolerance=5)
self.assertCanvasNotEmpty(canvas)
self.assertCanvasHasColor(canvas, color)

# Color assertions
self.assertColorEqual(color1, color2)
self.assertColorClose(color1, color2, tolerance=5)
```

### Fixtures

```python
from tests.framework import CanvasFixtures

# Pre-built test canvases
canvas = CanvasFixtures.blank(16, 16)
canvas = CanvasFixtures.solid((255, 0, 0, 255))
canvas = CanvasFixtures.checkerboard()
canvas = CanvasFixtures.gradient_h(color1, color2)
canvas = CanvasFixtures.gradient_v(color1, color2)
```

### Skip Tests

```python
def test_optional_feature(self):
    self.skipUnless(FEATURE_AVAILABLE, "Feature not implemented")
    # ... test code
```

## Debug Utilities

```python
from tests.debug import (
    quick_inspect,      # One-line canvas stats
    quick_view,         # ASCII preview in terminal
    quick_diff,         # Compare two canvases
    inspect_canvas,     # Detailed inspection dict
    canvas_to_ascii,    # Convert to ASCII art
    canvas_to_ansi,     # Convert to colored terminal output
    canvas_diff,        # Visual diff canvas
    extract_palette,    # Get colors from canvas
    Profiler,           # Time code blocks
    benchmark,          # Benchmark a function
    DebugSession,       # Full debug session with snapshots
)

# Quick debugging
quick_inspect(canvas)  # Canvas 16x16: 256 opaque, 5 colors
quick_view(canvas)     # ASCII art preview

# Detailed inspection
info = inspect_canvas(canvas)
print(info['unique_color_count'])
print(info['bounding_box'])

# Performance profiling
profiler = Profiler()
with profiler.time('my_operation'):
    do_something()
print(profiler.report())
```

## Adding Tests for New Modules

When a new module is added to Bitsy:

1. Create `tests/<category>/test_<module>.py`
2. Import the module and TestCase
3. Create test classes following naming: `Test<ClassName>`
4. Create test methods following naming: `test_<what_it_tests>`
5. Run to verify: `python -m tests.runner --filter <module>`
6. Update this README if adding a new category

## Current Test Count

- **Total**: 249 tests
- **Core**: 128 tests
- **Generators**: 31 tests
- **UI**: 22 tests
- **Editor**: 22 tests
- **Export**: 28 tests
- **Effects**: 2 tests
- **Integration**: 11 tests
- **Visual**: 5 tests
