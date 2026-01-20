# Portrait Generator v3 - Procedural Rendering

## Overview

A complete rewrite of the portrait generation system using procedural rendering with proper lighting, replacing the template-based approach (v2) which could not achieve the desired quality.

## Why v3?

The template-based approach (v2) failed because:
- Flat placeholder colors → flat results
- Color swapping cannot preserve shading detail
- Templates designed for one size don't scale well
- No real lighting or depth

The reference portrait quality requires:
- Soft gradients throughout
- Proper 3D-like lighting and shading
- Smooth anti-aliased edges
- Rich color with hue-shifted shadows/highlights

## Architecture

### Core Concept: SDF-Based Rendering

Use Signed Distance Fields (SDFs) to define shapes mathematically:
- Smooth, anti-aliased edges automatically
- Easy to combine shapes (union, subtract, intersect)
- Can estimate surface normals for lighting
- Resolution-independent definitions

### Lighting Model

1. **Directional Light** - Main illumination from configurable angle
2. **Ambient Light** - Base illumination to prevent pure black
3. **Rim Light** - Anime-style edge glow on opposite side of main light
4. **Ambient Occlusion** - Darkening in crevices (eye sockets, under chin)

### Rendering Pipeline

```
1. Define shapes (face, eyes, nose, mouth, hair, body)
        ↓
2. For each pixel:
   a. Calculate SDF distance to determine if inside shape
   b. Calculate alpha for anti-aliased edges
   c. Estimate surface normal from SDF gradient
   d. Apply lighting model
   e. Apply local modifiers (AO, shadows)
        ↓
3. Output final pixel color
```

## Quality Gate

**IMPORTANT:** No features beyond the face will be implemented until the face quality is validated by the user. This prevents building on a flawed foundation.

Current status: **Face implemented, awaiting quality validation.**

---

## Implementation Phases

### Phase 1: Grayscale Face (IN PROGRESS - Awaiting Validation)
- [x] SDF utilities (circle, ellipse, rounded rect, smooth operations)
- [x] Basic face shape (oval with chin taper)
- [x] Lighting model (Lambert diffuse + ambient + rim)
- [x] Eye socket shadows (ambient occlusion)
- [x] Nose shadow
- [x] Eye rendering (sclera, iris, pupil, dual catchlights)
- [x] Eyebrow shapes (arched)
- [x] Mouth rendering
- [x] Nose detail
- [ ] **Quality validation by user**

### Phase 2: Hair System (BLOCKED - Requires Phase 1 Validation)
- [ ] Hair silhouette shapes (various styles)
- [ ] Hair strand flow lines
- [ ] Highlight bands
- [ ] Rim lighting on hair edges

### Phase 3: Color System (BLOCKED)
- [ ] Base color input (skin, hair, eyes)
- [ ] Hue-shift shading (shadows cooler, highlights warmer)
- [ ] Automatic palette generation
- [ ] Color blending and gradients

### Phase 4: Body & Accessories (BLOCKED)
- [ ] Neck and shoulders
- [ ] Clothing with folds
- [ ] Glasses, earrings, etc.
- [ ] Props (books, cups, etc.)

### Phase 5: Variation & Expression (BLOCKED)
- [ ] Face shape variants (round, oval, square, heart)
- [ ] Eye expressions (normal, happy, sad, angry)
- [ ] Mouth expressions
- [ ] Head angle/tilt

## File Structure

```
generators/portrait_v3/
├── __init__.py          # Public API
├── DESIGN.md            # This document
├── renderer.py          # Main renderer class
├── sdf.py               # SDF shape utilities
├── lighting.py          # Lighting calculations
├── features/
│   ├── face.py          # Face shape rendering
│   ├── eyes.py          # Eye rendering
│   ├── hair.py          # Hair system
│   ├── mouth.py         # Mouth/lips
│   └── body.py          # Body/clothing
└── color.py             # Color system with hue-shifting
```

## API Design

```python
from generators.portrait_v3 import ProceduralPortraitRenderer

# Phase 1: Grayscale
renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
    light_dir=(-0.5, -0.3, 0.8),
    ambient=0.3,
)
canvas = renderer.render()

# Future phases:
renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
    skin_color=(253, 181, 115),
    hair_color=(123, 84, 155),
    eye_color=(100, 80, 60),
    hair_style="wavy",
    face_shape="oval",
    expression="neutral",
)
```

## Quality Targets

To match the reference image quality:
- Smooth gradients (no banding)
- Soft silhouette edges (1-2px anti-aliasing)
- Visible depth in face features
- Natural-looking lighting
- Cohesive color palette (when color added)
- "Cute" anime aesthetic

## Success Criteria

1. Grayscale face looks 3D with proper depth
2. Silhouette edges are smooth, not jagged
3. Eye sockets have subtle shadow depth
4. Overall impression is "hand-drawn quality"
5. Easily extensible to add features

## References

- Signed Distance Fields: https://iquilezles.org/articles/distfunctions2d/
- Pixel art lighting: Study of professional anime pixel art
- Target reference: `output/reference_downsampled.png`
