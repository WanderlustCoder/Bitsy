#!/usr/bin/env python3
"""
Generate Anime-Style Portrait Test

Tests the anime portrait system by generating a character portrait
and comparing it against the quality standard.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait import (
    PortraitConfig, PortraitGenerator, RenderMode, CompositionMode,
    HairStyle, EyeShape, get_canvas_size, generate_portrait
)
from core.canvas import Canvas


def generate_anime_portrait(
    character_type: str = "female_young",
    seed: int = None
) -> Canvas:
    """
    Generate an anime-style portrait.

    Args:
        character_type: Type of character to generate
        seed: Random seed for reproducibility

    Returns:
        Canvas with rendered portrait
    """
    # Get canvas size for upper body composition
    width, height = get_canvas_size(CompositionMode.UPPER_BODY)

    # Create config for anime mode
    config = PortraitConfig(
        width=width,
        height=height,
        seed=seed,

        # Enable anime mode
        render_mode=RenderMode.ANIME,
        anime_eye_scale=2.5,
        anime_palette_size=6,
        use_hue_shifting=True,

        # Enable rim lighting
        rim_light_enabled=True,
        rim_light_color=(180, 200, 255),
        rim_light_intensity=0.4,

        # Composition
        composition_mode="upper_body",
    )

    return config, generate_portrait(config)


def generate_cleric_portrait(seed: int = 42) -> Canvas:
    """
    Generate a male, older cleric character.

    Returns:
        Canvas with rendered portrait
    """
    width, height = get_canvas_size(CompositionMode.UPPER_BODY)

    config = PortraitConfig(
        width=width,
        height=height,
        seed=seed,

        # Anime mode
        render_mode=RenderMode.ANIME,
        anime_eye_scale=3.5,  # Very large anime eyes
        anime_palette_size=6,
        use_hue_shifting=True,

        # Rim lighting - strong like reference
        rim_light_enabled=True,
        rim_light_color=(180, 200, 255),  # Cool blue rim
        rim_light_intensity=0.8,  # Strong rim lighting

        # Composition
        composition_mode="upper_body",
        body_pose="holding",  # Show book prop

        # Skin - medium tone for older character
        skin_tone="medium",
        skin_undertone="warm",

        # Hair - gray/white, wavy for more volume
        hair_style=HairStyle.WAVY,
        hair_color="gray",
        hair_volume=2.0,  # Large volume like reference

        # Eyes - amber/brown, wise look
        eye_shape=EyeShape.DROOPY,  # Slight droop for age
        eye_color="amber",

        # Face features for older male
        face_shape="oval",
        face_width=1.05,  # Slightly broader
        jaw_angle=0.4,  # More defined jaw

        # Wrinkles and age features
        crows_feet=0.5,  # Eye wrinkles
        forehead_lines=0.4,  # Forehead wrinkles
        smile_lines=0.3,  # Nasolabial folds

        # Post-processing
        outline_mode="thin",
        selective_aa=True,
    )

    return config, generate_portrait(config)


def main():
    """Generate test portraits and save them."""
    print("=" * 60)
    print("ANIME PORTRAIT GENERATION TEST")
    print("=" * 60)
    print()

    # Generate cleric portrait
    print("Generating: Male older cleric character...")
    print("  - Hair: Gray, wavy style, large volume")
    print("  - Eyes: Amber, droopy shape, 3.5x anime scale")
    print("  - Skin: Medium tone, warm undertone")
    print("  - Style: Anime with rim lighting")
    print()

    config, canvas = generate_cleric_portrait(seed=42)

    # Save the portrait
    output_path = "output/test_anime_cleric.png"
    canvas.save(output_path)
    print(f"Saved to: {output_path}")
    print(f"Canvas size: {canvas.width}x{canvas.height}")

    # Debug: print key config values
    print(f"\nConfig Debug:")
    print(f"  anime_eye_scale: {config.anime_eye_scale}")
    print(f"  face_width config: {config.face_width}")
    print(f"  hair_style: {config.hair_style}")
    print(f"  render_mode: {config.render_mode}")
    print()

    # Count colors
    from generators.portrait_parts.post_processing import count_colors
    color_count = count_colors(canvas)
    print(f"Total colors: {color_count}")
    print()

    # Quality check summary
    print("-" * 60)
    print("QUALITY CHECK (compare to UserExamples/HighRes.png)")
    print("-" * 60)
    print("[ ] Hair forms volumetric masses with rim lighting")
    print("[ ] Eyes are large and expressive with catchlights")
    print("[ ] Skin has warm base with cool hue-shifted shadows")
    print("[ ] Clothing has form shadows and rim lighting")
    print("[ ] Limited color palette per element (5-6 colors)")
    print("[ ] Clean pixel work with strategic anti-aliasing")
    print()
    print("View the output and compare against the reference!")


if __name__ == "__main__":
    main()
