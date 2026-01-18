# Phase 3: Portrait Quality Overhaul

## Overview

This design addresses the quality gap between current Bitsy output and professional pixel art portraits like `UserExamples/HighRes.png`. The target is creating detailed, expressive portraits with realistic hair clusters, nuanced facial features, and sophisticated color work.

## Reference Analysis

The reference portrait (`UserExamples/HighRes.png`) demonstrates:
- **Hair**: Individual strand clusters with varied shapes, 5-6 color gradient
- **Face**: Subtle nose shading, defined lips, detailed eyes with catchlights
- **Eyes**: Multi-layer (white, iris gradient, pupil, catchlight, lashes)
- **Accessories**: Glasses with reflections, book with visible pages
- **Shading**: Smooth transitions with hue-shifting (warm highlights, cool shadows)

## Architecture

### New PortraitGenerator Class

```
generators/
├── portrait.py              # Main PortraitGenerator class
└── portrait_parts/
    ├── __init__.py
    ├── hair.py              # Hair cluster rendering
    ├── face.py              # Facial features (nose, lips, eyes)
    ├── accessories.py       # Glasses, jewelry, etc.
    └── clothing.py          # Neckline, collars, folds
```

### Canvas Specifications
- **Default size**: 128x160 pixels (portrait orientation)
- **Minimum for full detail**: 64x80 pixels
- **Shading levels**: 7 (base + 3 shadow + 3 highlight)

### Color System
- **create_portrait_ramp(base_color, levels=7)**: Generates hue-shifted ramp
  - Highlights: +18° hue shift (warmer)
  - Shadows: -25° hue shift (cooler)
  - Saturation: Increases in midtones, decreases at extremes
  - Lightness: Controlled steps with smooth falloff

## Component Designs

### 1. Hair Cluster Rendering

**Approach**: Bezier-based strand clusters instead of solid shapes

```python
class HairCluster:
    control_points: List[Tuple[int, int]]  # Bezier control points
    width_profile: List[float]              # Width along path (0.0-1.0)
    color_ramp: List[Color]                 # 5-6 colors from dark to light
```

**Rendering Pipeline**:
1. Generate cluster paths based on hair style template
2. Vary control points with Perlin noise for natural look
3. Draw clusters back-to-front for proper overlap
4. Apply highlight strips along light-facing curves
5. Add stray strands for realism

**Hair Styles**:
- `wavy`: Sinusoidal control point offsets
- `straight`: Minimal deviation, parallel clusters
- `curly`: Tight spiral paths
- `short`: Truncated clusters with more variation

### 2. Facial Features

**Nose**:
- Triangular highlight on bridge
- Soft shadow on one side (based on light direction)
- Nostril hints at larger sizes (64px+)

**Lips**:
- Upper lip slightly darker (shadow from nose)
- Lower lip with highlight strip
- Subtle color gradient (center lighter than edges)
- Lip line 1px darker than surrounding

**Eyes** (multi-layer):
```
Layer 1: Eye white (slight gray, not pure white)
Layer 2: Iris - radial gradient, darker at edge
Layer 3: Pupil - black with slight blue tint
Layer 4: Catchlight - 2-3px white/near-white dots
Layer 5: Eyelid shadow - 1px darker strip at top
Layer 6: Lashes - individual strokes at edges
```

**Eye Expression Parameters**:
- `openness`: 0.0-1.0 (affects visible iris/white ratio)
- `gaze_direction`: (x, y) offset for pupil position
- `eyebrow_arch`: Controls eyebrow curve intensity

### 3. Advanced Shading System

**Hue-Shifting Ramps**:
```python
def create_portrait_ramp(base_color: Color, levels: int = 7) -> List[Color]:
    """
    Generate a hue-shifted color ramp for portrait shading.

    Highlights: Shift toward yellow/warm (+15-20° hue)
    Shadows: Shift toward blue/cool (-20-25° hue)
    """
```

**Shading Application**:
- Ambient occlusion in crevices (eye sockets, under nose, neck)
- Rim lighting on light-opposite edge
- Subsurface scattering approximation on ears/thin areas (slight red shift)

### 4. Clothing & Accessories

**Clothing**:
- Fabric fold patterns based on garment type
- Material-appropriate shading (matte vs shiny)
- Collar/neckline detail templates

**Glasses**:
- Frame with 3-color shading
- Lens with subtle reflection (diagonal highlight strip)
- Shadow cast on face beneath frame

**Other Accessories**:
- Earrings with metallic shading
- Necklaces with proper depth
- Hair accessories integrated with clusters

## Implementation Plan

### Milestone 1: Foundation
1. Create `generators/portrait.py` with `PortraitGenerator` skeleton
2. Create `generators/portrait_parts/` directory and `__init__.py`
3. Implement `create_portrait_ramp()` with hue shifting in LCh space
4. Add basic face outline and skin base

### Milestone 2: Hair System
1. Implement `HairCluster` class with bezier paths
2. Create hair style templates (wavy, straight, curly, short)
3. Add cluster variation with Perlin noise
4. Implement highlight/shadow application on clusters

### Milestone 3: Facial Features
1. Implement nose rendering with directional shading
2. Add lip rendering with gradient and highlight
3. Create multi-layer eye system
4. Add eyebrow rendering with expression control

### Milestone 4: Accessories & Clothing
1. Implement glasses with reflections
2. Add basic clothing/neckline templates
3. Create fabric fold patterns
4. Add earring and necklace support

### Milestone 5: Integration & Polish
1. Integrate all parts into cohesive render pipeline
2. Add configuration for style variations
3. Create showcase/comparison images
4. Update documentation

## Success Criteria

- Generated portraits visually comparable to `UserExamples/HighRes.png`
- Hair shows individual cluster definition, not solid masses
- Eyes have visible catchlights and layered depth
- Shading uses hue-shifting, not just lightness changes
- Minimum 64x80 resolution produces recognizable features

## Technical Notes

- All color operations use LCh color space for perceptual uniformity
- Bezier rendering uses adaptive subdivision for smooth curves
- Anti-aliasing applied to all curved edges
- Configuration-driven for reproducible results with seed
