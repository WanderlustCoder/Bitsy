"""
Hair Comparison Demo - Basic vs Professional Hair Rendering

This demo shows the quality difference between:
- Basic shape-based hair (ellipses)
- Professional strand-based hair (bezier curves, gradients)

Run with: python examples/hair_comparison.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from parts.hair import LongHair
from parts.hair_pro import ProfessionalLongHair, ProfessionalBunHair, ProHairConfig


def create_comparison():
    """Generate side-by-side comparison of hair rendering methods."""

    # Hair color palette (dark brown)
    hair_colors = [
        (45, 30, 25, 255),    # Darkest shadow
        (85, 55, 45, 255),    # Shadow
        (110, 75, 60, 255),   # Base
        (65, 40, 35, 255),    # Mid shadow
        (35, 22, 18, 255),    # Deep shadow
    ]

    # Create output directory
    os.makedirs('output/hair_comparison', exist_ok=True)

    # --- Individual renders at 128x128 ---

    # Basic Long Hair
    canvas_basic = Canvas(128, 128)
    canvas_basic.fill_rect(0, 0, 128, 128, (30, 25, 35, 255))
    basic_long = LongHair()
    basic_long._colors = hair_colors
    basic_long.draw(canvas_basic, 64, 70, 100, 80)
    canvas_basic.save('output/hair_comparison/basic_long_128.png')
    print('Saved: basic_long_128.png')

    # Professional Long Hair
    canvas_pro_long = Canvas(128, 128)
    canvas_pro_long.fill_rect(0, 0, 128, 128, (30, 25, 35, 255))
    pro_long = ProfessionalLongHair(ProHairConfig())
    pro_long._colors = hair_colors
    pro_long.draw(canvas_pro_long, 64, 70, 100, 80)
    canvas_pro_long.save('output/hair_comparison/pro_long_128.png')
    print('Saved: pro_long_128.png')

    # Professional Bun Hair
    canvas_pro_bun = Canvas(128, 128)
    canvas_pro_bun.fill_rect(0, 0, 128, 128, (30, 25, 35, 255))
    pro_bun = ProfessionalBunHair(ProHairConfig())
    pro_bun._colors = hair_colors
    pro_bun.draw(canvas_pro_bun, 64, 70, 100, 80)
    canvas_pro_bun.save('output/hair_comparison/pro_bun_128.png')
    print('Saved: pro_bun_128.png')

    # --- Comparison strip ---

    comparison = Canvas(384, 160)
    comparison.fill_rect(0, 0, 384, 160, (30, 25, 35, 255))

    # Panel 1: Basic Long Hair
    basic = LongHair()
    basic._colors = hair_colors
    basic.draw(comparison, 64, 90, 100, 80)

    # Panel 2: Professional Long Hair
    pro_l = ProfessionalLongHair(ProHairConfig())
    pro_l._colors = hair_colors
    pro_l.draw(comparison, 192, 90, 100, 80)

    # Panel 3: Professional Bun Hair
    pro_b = ProfessionalBunHair(ProHairConfig())
    pro_b._colors = hair_colors
    pro_b.draw(comparison, 320, 90, 100, 80)

    comparison.save('output/hair_comparison/comparison_strip.png')
    print('Saved: comparison_strip.png (Basic Long | Pro Long | Pro Bun)')

    # --- Large render for detail visibility ---

    large = Canvas(256, 256)
    large.fill_rect(0, 0, 256, 256, (30, 25, 35, 255))
    pro_bun_large = ProfessionalBunHair(ProHairConfig())
    pro_bun_large._colors = hair_colors
    pro_bun_large.draw(large, 128, 140, 200, 160)
    large.save('output/hair_comparison/pro_bun_large.png')
    print('Saved: pro_bun_large.png (256x256)')

    print('\nComparison complete!')
    print('Key differences:')
    print('- Basic: Smooth ellipse shapes, no strand detail')
    print('- Professional: Individual bezier strands, gradient shading, highlights')


if __name__ == '__main__':
    create_comparison()
