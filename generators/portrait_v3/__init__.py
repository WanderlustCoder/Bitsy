"""
Portrait Generator v3 - Procedural rendering with proper lighting.

Generates anime-style pixel art portraits using:
- Signed Distance Fields (SDFs) for smooth shapes
- Physically-inspired lighting model
- Hue-shift color system
"""

from generators.portrait_v3.renderer import ProceduralPortraitRenderer

__all__ = ['ProceduralPortraitRenderer']
