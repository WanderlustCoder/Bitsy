#!/usr/bin/env python3
"""
HD Features Demo - Demonstrates Bitsy's high-quality pixel art capabilities.

Shows off the professional-quality features:
- Professional HD style preset with selout and anti-aliasing
- HD hair styles with multi-layer highlights
- Face accessories (glasses)
- Held items (books, etc.)
- Anti-aliased drawing methods
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style, Palette, hex_to_rgba
from core.style import PROFESSIONAL_HD, MODERN_HD
from quality.selout import apply_selout, derive_selout_color
from parts.hair_hd import BunHairHD, LongHairHD, PonytailHairHD, ShortHairHD
from parts.face_accessories import Glasses, SquareGlasses, Goggles, GlassesConfig
from parts.held_items import Book, OpenBook, Scroll, Flower
from parts.base import PartConfig


def create_aa_comparison(size: int = 64) -> Canvas:
    """Create comparison of regular vs anti-aliased shapes."""
    canvas = Canvas(size * 2 + 16, size + 8, (40, 40, 50, 255))

    color = hex_to_rgba('#60a0e0')

    # Regular circle (left)
    canvas.fill_circle(size // 2, size // 2 + 4, size // 3, color)

    # Anti-aliased circle (right)
    canvas.fill_circle_aa(size + 8 + size // 2, size // 2 + 4, size // 3, color)

    return canvas


def create_selout_demo(size: int = 64) -> Canvas:
    """Create demonstration of selective outline."""
    canvas = Canvas(size * 2 + 16, size + 8, (40, 40, 50, 255))

    # Draw a multi-colored shape without selout (left)
    left_canvas = Canvas(size, size)
    # Purple hair area
    left_canvas.fill_ellipse(size // 2, size // 3, size // 3, size // 4,
                             hex_to_rgba('#c090d0'))
    # Skin area below
    left_canvas.fill_ellipse(size // 2, size // 2 + 5, size // 4, size // 4,
                             hex_to_rgba('#f0c090'))
    # Red clothing
    left_canvas.fill_rect(size // 3, size // 2 + 15, size // 3, size // 4,
                          hex_to_rgba('#c05050'))

    canvas.blit(left_canvas, 4, 4)

    # Same shape with selout applied (right)
    right_canvas = apply_selout(left_canvas.copy())
    canvas.blit(right_canvas, size + 12, 4)

    return canvas


def create_hd_hair_showcase(size: int = 64) -> Canvas:
    """Showcase HD hair styles."""
    padding = 8
    canvas_width = (size + padding) * 4 + padding
    canvas = Canvas(canvas_width, size + padding * 2, (40, 40, 50, 255))

    # Lavender color for hair
    hair_color = hex_to_rgba('#c0a0d0')

    hair_styles = [
        ('Bun HD', BunHairHD),
        ('Long HD', LongHairHD),
        ('Ponytail HD', PonytailHairHD),
        ('Short HD', ShortHairHD),
    ]

    for i, (name, hair_class) in enumerate(hair_styles):
        x = padding + i * (size + padding) + size // 2
        y = padding + size // 2

        config = PartConfig(base_color=hair_color)
        hair = hair_class(config)

        # Draw hair
        hair.draw(canvas, x, y, size - 8, size - 16)

    return canvas


def create_glasses_showcase(size: int = 48) -> Canvas:
    """Showcase face accessories."""
    padding = 8
    canvas_width = (size + padding) * 4 + padding
    canvas = Canvas(canvas_width, size + padding * 2, (40, 40, 50, 255))

    # Draw a simple face shape first, then glasses on top
    face_color = hex_to_rgba('#f0c090')

    accessories = [
        ('Round', Glasses, None),
        ('Square', SquareGlasses, None),
        ('Goggles', Goggles, None),
        ('Tinted', Glasses, GlassesConfig(lens_color=(100, 150, 200, 120))),
    ]

    for i, (name, acc_class, config) in enumerate(accessories):
        x = padding + i * (size + padding) + size // 2
        y = padding + size // 2

        # Draw face background
        canvas.fill_ellipse(x, y, size // 3, size // 2 - 4, face_color)

        # Draw accessory
        if config:
            accessory = acc_class(config)
        else:
            accessory = acc_class()

        accessory.draw(canvas, x, y - 2, size - 8, size - 16)

    return canvas


def create_held_items_showcase(size: int = 48) -> Canvas:
    """Showcase held items."""
    padding = 8
    canvas_width = (size + padding) * 4 + padding
    canvas = Canvas(canvas_width, size + padding * 2, (40, 40, 50, 255))

    items = [
        ('Book', Book, {}),
        ('Open Book', OpenBook, {}),
        ('Scroll', Scroll, {}),
        ('Flower', Flower, {'petal_color': (255, 150, 180, 255)}),
    ]

    for i, (name, item_class, kwargs) in enumerate(items):
        x = padding + i * (size + padding) + size // 2
        y = padding + size // 2

        item = item_class(**kwargs) if kwargs else item_class()
        item.draw(canvas, x, y, size - 8, size - 8)

    return canvas


def create_style_comparison() -> Canvas:
    """Compare modern_hd vs professional_hd styles."""
    size = 64
    canvas = Canvas(size * 2 + 24, size + 16, (40, 40, 50, 255))

    # Create a test shape
    base_color = hex_to_rgba('#a080c0')

    # Modern HD (left)
    modern = MODERN_HD
    modern_colors = modern.get_shading_colors(base_color)
    for i, color in enumerate(reversed(modern_colors)):
        r = (size // 3) - i * 2
        canvas.fill_circle(size // 2 + 4, size // 2 + 8, r, color)

    # Professional HD (right) with AA
    pro = PROFESSIONAL_HD
    pro_colors = pro.get_shading_colors(base_color)
    for i, color in enumerate(reversed(pro_colors)):
        r = (size // 3) - i * 2
        canvas.fill_circle_aa(size + 16 + size // 2, size // 2 + 8, r, color)

    return canvas


def print_style_info():
    """Print information about HD style presets."""
    print("\nProfessional HD Style Features:")
    print(f"  - Shading levels: {PROFESSIONAL_HD.shading.levels}")
    print(f"  - Selout enabled: {PROFESSIONAL_HD.outline.selout_enabled}")
    print(f"  - Anti-aliasing: {PROFESSIONAL_HD.anti_alias}")
    print(f"  - Highlight hue shift: +{PROFESSIONAL_HD.shading.highlight_hue_shift}°")
    print(f"  - Shadow hue shift: {PROFESSIONAL_HD.shading.shadow_hue_shift}°")

    print("\nComparison with Modern HD:")
    print(f"  Modern HD levels: {MODERN_HD.shading.levels}")
    print(f"  Professional HD levels: {PROFESSIONAL_HD.shading.levels}")
    print(f"  Modern HD selout: {MODERN_HD.outline.selout_enabled}")
    print(f"  Professional HD selout: {PROFESSIONAL_HD.outline.selout_enabled}")


def main():
    print("Bitsy - HD Features Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # AA comparison
    print("\n1. Creating anti-aliasing comparison...")
    aa_demo = create_aa_comparison()
    aa_demo.save(os.path.join(output_dir, "hd_aa_comparison.png"))
    print("   Saved: output/hd_aa_comparison.png")
    print("   (Left: regular, Right: anti-aliased)")

    # Selout demo
    print("\n2. Creating selout demonstration...")
    selout_demo = create_selout_demo()
    selout_demo.save(os.path.join(output_dir, "hd_selout_demo.png"))
    print("   Saved: output/hd_selout_demo.png")
    print("   (Left: no selout, Right: with selout)")

    # HD Hair showcase
    print("\n3. Creating HD hair showcase...")
    hair_demo = create_hd_hair_showcase()
    hair_demo.save(os.path.join(output_dir, "hd_hair_showcase.png"))
    print("   Saved: output/hd_hair_showcase.png")
    print("   (Bun, Long, Ponytail, Short - all HD versions)")

    # Glasses showcase
    print("\n4. Creating glasses showcase...")
    glasses_demo = create_glasses_showcase()
    glasses_demo.save(os.path.join(output_dir, "hd_glasses_showcase.png"))
    print("   Saved: output/hd_glasses_showcase.png")
    print("   (Round, Square, Goggles, Tinted)")

    # Held items showcase
    print("\n5. Creating held items showcase...")
    items_demo = create_held_items_showcase()
    items_demo.save(os.path.join(output_dir, "hd_items_showcase.png"))
    print("   Saved: output/hd_items_showcase.png")
    print("   (Book, Open Book, Scroll, Flower)")

    # Style comparison
    print("\n6. Creating style comparison...")
    style_demo = create_style_comparison()
    style_demo.save(os.path.join(output_dir, "hd_style_comparison.png"))
    print("   Saved: output/hd_style_comparison.png")
    print("   (Left: Modern HD, Right: Professional HD)")

    # Print style info
    print_style_info()

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory for results.")
    print("\nNew HD Features Summary:")
    print("  - Selective Outline (Selout): Color-aware outlines")
    print("  - Anti-aliased drawing: Smooth edges on curves")
    print("  - HD Hair Styles: Multi-layer highlights")
    print("  - Face Accessories: Glasses, goggles, eye patches")
    print("  - Held Items: Books, scrolls, flowers, cups, bags")
    print("  - Professional HD Style: 6-level shading with selout & AA")


if __name__ == "__main__":
    main()
