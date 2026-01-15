"""
Test Visual Regression - Visual regression tests with baseline comparison.

Tests:
- Generated output matches known-good baselines
- Hash-based comparison for quick verification
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from generators import generate_item
from ui import create_icon
from core import Canvas


# Known-good hashes for baseline comparison
# These should be regenerated when intentional changes are made
BASELINE_HASHES = {
    'sword_default': None,  # To be generated
    'axe_default': None,
    'heart_icon': None,
    'star_icon': None,
}


class TestVisualBaselines(TestCase):
    """Tests comparing output against visual baselines."""

    def test_sword_visual_stability(self):
        """Sword generation is visually stable."""
        result = generate_item('sword', seed=42, width=16, height=24)

        # Generate hash for comparison
        hash_val = self.getCanvasHash(result)

        # If baseline exists, compare
        if BASELINE_HASHES.get('sword_default'):
            self.assertEqual(hash_val, BASELINE_HASHES['sword_default'],
                           f"Sword visual changed! New hash: {hash_val}")
        else:
            # Record baseline for future tests
            print(f"  Sword baseline hash: {hash_val}")
            self.assertCanvasNotEmpty(result)

    def test_icon_visual_stability(self):
        """Icon generation is visually stable."""
        for name in ['heart', 'star']:
            result = create_icon(name, size=16)
            hash_val = self.getCanvasHash(result)

            baseline_key = f'{name}_icon'
            if BASELINE_HASHES.get(baseline_key):
                self.assertEqual(hash_val, BASELINE_HASHES[baseline_key],
                               f"Icon '{name}' changed! New hash: {hash_val}")
            else:
                print(f"  {name} icon baseline hash: {hash_val}")
                self.assertCanvasNotEmpty(result)


class TestCanvasHashing(TestCase):
    """Tests for canvas hash functionality."""

    def test_hash_consistent(self):
        """Same canvas produces same hash."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))

        hash1 = self.getCanvasHash(canvas)
        hash2 = self.getCanvasHash(canvas)

        self.assertEqual(hash1, hash2)

    def test_hash_different_for_different_content(self):
        """Different canvases produce different hashes."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        hash1 = self.getCanvasHash(canvas1)
        hash2 = self.getCanvasHash(canvas2)

        self.assertNotEqual(hash1, hash2)

    def test_hash_detects_small_changes(self):
        """Hash changes for single pixel change."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = canvas1.copy()
        canvas2.set_pixel_solid(0, 0, (254, 0, 0, 255))  # Tiny change

        hash1 = self.getCanvasHash(canvas1)
        hash2 = self.getCanvasHash(canvas2)

        self.assertNotEqual(hash1, hash2)
