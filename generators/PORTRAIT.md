# Portrait Generation - Current Direction

## Status: Portrait v3 (Procedural Rendering)

**v3 is the current way forward.** The template-based approaches (v1, v2) have been deprecated.

## History

### v1 (Deprecated)
- Basic procedural shapes
- Flat colors, no real shading
- Result: Too simplistic

### v2 (Deprecated)
- Template-based with PNG images
- Placeholder color swapping
- Result: Could not achieve reference quality
  - Flat templates → flat results
  - Color swapping destroys shading detail
  - Double-scaling issues

### v3 (Current)
- Procedural rendering with SDFs
- Proper lighting model
- Mathematical shape definitions
- See: `portrait_v3/DESIGN.md`

## Why Procedural?

The reference image quality requires:
1. **Soft gradients** - not achievable with flat templates
2. **Proper lighting** - 3D-like depth and shading
3. **Smooth edges** - anti-aliased silhouettes
4. **Hue-shifted colors** - shadows cooler, highlights warmer

Template-based approaches cannot provide these because they start from flat art and try to add depth through color swapping - it doesn't work.

Procedural rendering calculates each pixel mathematically, allowing:
- True lighting calculations
- Smooth gradient generation
- Perfect anti-aliasing
- Infinite resolution independence

## Reference Target

The target quality is `output/reference_downsampled.png` - a 64x96 anime pixel art portrait with:
- Soft, cute aesthetic
- Rich shading and highlights
- Detailed hair with rim lighting
- Expressive eyes with catchlights

## Development Phases

1. **Grayscale Face** - Basic face with lighting (IN PROGRESS)
2. **Hair System** - Procedural hair rendering
3. **Color System** - Hue-shift based coloring
4. **Body & Accessories** - Complete portrait
5. **Variation** - Expressions, styles, customization

## Using Portrait v3

```python
from generators.portrait_v3 import ProceduralPortraitRenderer

renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
)
canvas = renderer.render()
canvas.save('portrait.png')
```

## Files

```
generators/
├── PORTRAIT.md              # This document
├── portrait_v2/             # DEPRECATED - template-based
│   ├── composer.py
│   ├── loader.py
│   └── recolor.py
└── portrait_v3/             # CURRENT - procedural
    ├── DESIGN.md            # Detailed design document
    ├── renderer.py          # Main renderer
    └── (more to come)
```
