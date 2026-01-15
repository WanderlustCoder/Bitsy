#!/usr/bin/env python3
"""
Bitsy Test Runner - Discovers and runs all tests with reporting.

Usage:
    # Run all tests
    python -m tests.runner

    # Run specific category
    python -m tests.runner --category core
    python -m tests.runner --category generators

    # Run with verbose output
    python -m tests.runner -v

    # Run specific test pattern
    python -m tests.runner --filter test_canvas

    # Generate visual baseline
    python -m tests.runner --generate-baseline

    # Run performance benchmarks
    python -m tests.runner --benchmark

    # Save results to file
    python -m tests.runner --output results.txt
"""

import sys
import os
import argparse
import time
import importlib
import pkgutil
from typing import List, Dict, Any, Optional, Type
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.framework import (
    TestCase, TestResult, TestSuiteResult,
    discover_tests, run_test_class
)


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def disable():
        Colors.GREEN = ''
        Colors.RED = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.BOLD = ''
        Colors.RESET = ''


def colorize(text: str, color: str) -> str:
    """Add color to text."""
    return f"{color}{text}{Colors.RESET}"


# ==================== Test Discovery ====================

def find_test_modules(category: str = None) -> List[str]:
    """Find all test modules.

    Args:
        category: Optional category to filter (core, generators, etc.)

    Returns:
        List of module paths like 'tests.core.test_canvas'
    """
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    modules = []

    # Categories to search
    if category:
        categories = [category]
    else:
        categories = [
            'core', 'generators', 'effects', 'ui',
            'editor', 'export', 'integration', 'visual', 'quality', 'preview'
        ]

    for cat in categories:
        cat_dir = os.path.join(tests_dir, cat)
        if not os.path.isdir(cat_dir):
            continue

        for filename in os.listdir(cat_dir):
            if filename.startswith('test_') and filename.endswith('.py'):
                module_name = filename[:-3]
                modules.append(f"tests.{cat}.{module_name}")

    return sorted(modules)


def load_test_classes(module_path: str) -> List[Type[TestCase]]:
    """Load test classes from a module.

    Args:
        module_path: Module path like 'tests.core.test_canvas'

    Returns:
        List of TestCase subclasses
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"  {colorize('ERROR', Colors.RED)}: Could not import {module_path}: {e}")
        return []

    classes = []
    for name in dir(module):
        obj = getattr(module, name)
        if (isinstance(obj, type) and
            issubclass(obj, TestCase) and
            obj is not TestCase and
            not name.startswith('_')):
            classes.append(obj)

    return classes


# ==================== Result Formatting ====================

def format_result_line(result: TestResult, verbose: bool = False) -> str:
    """Format a single test result."""
    if result.passed:
        if result.error and "SKIPPED" in result.error:
            status = colorize("SKIP", Colors.YELLOW)
            reason = result.error.replace("SKIPPED: ", "").replace("SKIPPED", "")
            extra = f" ({reason})" if reason else ""
        else:
            status = colorize("PASS", Colors.GREEN)
            extra = f" ({result.assertions} assertions, {result.duration:.3f}s)"
    else:
        status = colorize("FAIL", Colors.RED)
        extra = ""

    line = f"  {status} {result.name}{extra if verbose else ''}"

    if not result.passed and result.error:
        line += f"\n       {result.error}"

    return line


def format_suite_summary(suite: TestSuiteResult) -> str:
    """Format summary for a test suite."""
    if suite.total == 0:
        return f"  (no tests)"

    passed = colorize(str(suite.passed), Colors.GREEN) if suite.passed else "0"
    failed = colorize(str(suite.failed), Colors.RED) if suite.failed else "0"

    return f"  {passed} passed, {failed} failed ({suite.total_duration:.3f}s)"


def print_summary(results: List[TestSuiteResult], duration: float) -> None:
    """Print overall test summary."""
    total_passed = sum(s.passed for s in results)
    total_failed = sum(s.failed for s in results)
    total_tests = sum(s.total for s in results)

    print("\n" + "=" * 60)
    print(colorize("TEST SUMMARY", Colors.BOLD))
    print("=" * 60)

    # Category breakdown
    print(f"\nSuites run: {len(results)}")
    for suite in results:
        status = colorize("✓", Colors.GREEN) if suite.failed == 0 else colorize("✗", Colors.RED)
        print(f"  {status} {suite.name}: {suite.passed}/{suite.total} passed")

    # Overall stats
    print(f"\nTotal: {total_tests} tests")
    print(f"  {colorize(str(total_passed), Colors.GREEN)} passed")
    if total_failed > 0:
        print(f"  {colorize(str(total_failed), Colors.RED)} failed")

    print(f"\nDuration: {duration:.2f}s")

    # Final status
    if total_failed == 0:
        print(f"\n{colorize('ALL TESTS PASSED', Colors.GREEN + Colors.BOLD)}")
    else:
        print(f"\n{colorize('SOME TESTS FAILED', Colors.RED + Colors.BOLD)}")


def print_failures(results: List[TestSuiteResult]) -> None:
    """Print detailed failure information."""
    failures = []

    for suite in results:
        for result in suite.results:
            if not result.passed and "SKIPPED" not in (result.error or ""):
                failures.append((suite.name, result))

    if not failures:
        return

    print("\n" + "=" * 60)
    print(colorize("FAILURES", Colors.RED + Colors.BOLD))
    print("=" * 60)

    for suite_name, result in failures:
        print(f"\n{colorize('FAIL', Colors.RED)}: {suite_name}.{result.name}")
        print(f"  Error: {result.error}")
        if result.traceback:
            print(f"\n  Traceback:")
            for line in result.traceback.split('\n'):
                if line.strip():
                    print(f"    {line}")


# ==================== Main Runner ====================

def run_tests(category: str = None,
              filter_pattern: str = None,
              verbose: bool = False,
              fail_fast: bool = False,
              no_color: bool = False,
              output_file: str = None,
              debug: bool = False) -> int:
    """Run tests and return exit code.

    Args:
        category: Test category to run (None = all)
        filter_pattern: Pattern to filter test names
        verbose: Print detailed output
        fail_fast: Stop on first failure
        no_color: Disable colored output
        output_file: File to write results to
        debug: Enable enhanced debugging output

    Returns:
        0 if all tests pass, 1 otherwise
    """
    if no_color or not sys.stdout.isatty():
        Colors.disable()

    # Initialize debug session if requested
    debug_session = None
    if debug:
        from tests.debug import DebugSession, Profiler
        debug_session = DebugSession("test_run")
        debug_session.log("test_run_started", {"category": category, "filter": filter_pattern})

    # Capture output if writing to file
    output_buffer = StringIO() if output_file else None

    def log(msg: str = ""):
        print(msg)
        if output_buffer:
            output_buffer.write(msg + "\n")

    # Header
    log("=" * 60)
    log(colorize("BITSY TEST SUITE", Colors.BOLD + Colors.CYAN))
    log("=" * 60)
    log()

    if category:
        log(f"Category: {category}")
    if filter_pattern:
        log(f"Filter: {filter_pattern}")
    log()

    # Discover tests
    modules = find_test_modules(category)

    if not modules:
        log(colorize("No test modules found!", Colors.YELLOW))
        return 1

    log(f"Found {len(modules)} test module(s)")
    log()

    # Run tests
    start_time = time.perf_counter()
    all_results: List[TestSuiteResult] = []

    for module_path in modules:
        log(f"{colorize('Module:', Colors.BLUE)} {module_path}")

        classes = load_test_classes(module_path)

        if not classes:
            log(f"  (no test classes found)")
            continue

        for test_class in classes:
            log(f"\n  {colorize('Class:', Colors.CYAN)} {test_class.__name__}")

            result = run_test_class(
                test_class,
                verbose=verbose,
                filter_pattern=filter_pattern
            )
            all_results.append(result)

            # Print results
            for test_result in result.results:
                log(format_result_line(test_result, verbose))

            log(format_suite_summary(result))

            # Fail fast
            if fail_fast and result.failed > 0:
                log(colorize("\nStopping due to --fail-fast", Colors.YELLOW))
                break

        if fail_fast and any(r.failed > 0 for r in all_results):
            break

        log()

    duration = time.perf_counter() - start_time

    # Print summary
    print_summary(all_results, duration)

    # Print failures
    print_failures(all_results)

    # Debug output
    if debug and debug_session:
        debug_session.log("test_run_completed", {
            "duration": duration,
            "total_passed": sum(s.passed for s in all_results),
            "total_failed": sum(s.failed for s in all_results),
        })
        print("\n" + "=" * 60)
        print(colorize("DEBUG SESSION REPORT", Colors.BOLD + Colors.CYAN))
        print("=" * 60)
        print(debug_session.report())
        debug_session.save()
        print(f"\nDebug output saved to: debug_output/test_run/")

    # Save output
    if output_file and output_buffer:
        with open(output_file, 'w') as f:
            f.write(output_buffer.getvalue())
        print(f"\nResults saved to: {output_file}")

    # Return exit code
    total_failed = sum(s.failed for s in all_results)
    return 0 if total_failed == 0 else 1


def generate_baseline() -> int:
    """Generate visual regression baselines."""
    print("=" * 60)
    print(colorize("GENERATING VISUAL BASELINES", Colors.BOLD + Colors.CYAN))
    print("=" * 60)
    print()

    # Import visual tests
    try:
        from tests.visual import baseline_generator
        baseline_generator.generate_all()
        print(colorize("\nBaselines generated successfully!", Colors.GREEN))
        return 0
    except ImportError:
        print(colorize("Visual baseline generator not found.", Colors.YELLOW))
        print("Create tests/visual/baseline_generator.py to use this feature.")
        return 1
    except Exception as e:
        print(colorize(f"Error generating baselines: {e}", Colors.RED))
        return 1


def run_benchmarks() -> int:
    """Run performance benchmarks."""
    print("=" * 60)
    print(colorize("PERFORMANCE BENCHMARKS", Colors.BOLD + Colors.CYAN))
    print("=" * 60)
    print()

    # Import benchmark module
    try:
        from tests import benchmarks
        benchmarks.run_all()
        return 0
    except ImportError:
        print(colorize("Benchmark module not found.", Colors.YELLOW))
        print("Create tests/benchmarks.py to use this feature.")
        return 1
    except Exception as e:
        print(colorize(f"Error running benchmarks: {e}", Colors.RED))
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bitsy Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Categories:
  core        - Core module tests (Canvas, Palette, Animation)
  generators  - Generator tests (Character, Item, Effect)
  effects     - Effects tests (Particles, Trails)
  ui          - UI tests (NinePatch, Icons, Fonts)
  editor      - Editor tests (Loader, Layers, Transforms)
  export      - Export tests (GIF, APNG, Spritesheet)
  integration - Integration tests (cross-module)
  visual      - Visual regression tests
  quality     - Quality analysis tests (Analyzer, Validators, Color Harmony)
  preview     - Preview tools tests (HTML Preview, Comparison, Contact Sheets)

Examples:
  python -m tests.runner                    # Run all tests
  python -m tests.runner -v                 # Verbose output
  python -m tests.runner --category core    # Run only core tests
  python -m tests.runner --filter canvas    # Run tests matching 'canvas'
  python -m tests.runner --fail-fast        # Stop on first failure
"""
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output with timing and assertions'
    )

    parser.add_argument(
        '-c', '--category',
        choices=['core', 'generators', 'effects', 'ui', 'editor', 'export', 'integration', 'visual', 'quality', 'preview'],
        help='Run tests from specific category'
    )

    parser.add_argument(
        '-f', '--filter',
        dest='filter_pattern',
        help='Run only tests matching pattern'
    )

    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop on first test failure'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Write results to file'
    )

    parser.add_argument(
        '--generate-baseline',
        action='store_true',
        help='Generate visual regression baselines'
    )

    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmarks'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable enhanced debugging output and save session data'
    )

    args = parser.parse_args()

    if args.generate_baseline:
        sys.exit(generate_baseline())

    if args.benchmark:
        sys.exit(run_benchmarks())

    sys.exit(run_tests(
        category=args.category,
        filter_pattern=args.filter_pattern,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        no_color=args.no_color,
        output_file=args.output_file,
        debug=args.debug
    ))


if __name__ == '__main__':
    main()
