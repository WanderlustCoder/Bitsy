"""
Bitsy Test Suite

Comprehensive testing framework for the Bitsy pixel art toolkit.

Test Categories:
- Unit tests: Individual function/class testing
- Integration tests: Cross-module functionality
- Visual regression tests: Image output comparison
- Performance tests: Benchmark critical operations

Usage:
    # Run all tests
    python -m tests.runner

    # Run specific category
    python -m tests.runner --category core

    # Run with verbose output
    python -m tests.runner -v

    # Generate visual baseline
    python -m tests.runner --generate-baseline
"""

__version__ = "1.0.0"
