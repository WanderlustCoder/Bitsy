# Portrait Generation - Current Direction

## Status: Portrait v3 (Procedural Rendering)

**v3 is the current way forward.** The template-based approaches (v1, v2) have been deprecated.

---

## Quick Links

- **Detailed Design:** `portrait_v3/DESIGN.md`
- **Source Code:** `portrait_v3/renderer.py`
- **Reference Image:** `output/reference_downsampled.png`

---

## History

### v1 (Deprecated)
- Basic procedural shapes
- Flat colors, no real shading
- **Result:** Too simplistic

### v2 (Deprecated)
- Template-based with PNG images
- Placeholder color swapping
- **Result:** Could not achieve reference quality
  - Flat templates → flat results
  - Color swapping destroys shading detail
  - Scaling issues

### v3 (Current) ← **This is the way forward**
- Procedural rendering with SDFs
- Proper lighting model (Lambert + ambient + rim)
- Mathematical shape definitions
- Hue-shift color system (planned)

---

## Why Procedural Rendering?

The reference image quality requires:

| Requirement | Template Approach | Procedural Approach |
|-------------|-------------------|---------------------|
| Soft gradients | ❌ Flat colors only | ✅ Calculated per-pixel |
| Proper lighting | ❌ Baked in template | ✅ Dynamic light model |
| Smooth edges | ❌ Pixelated edges | ✅ SDF anti-aliasing |
| Hue-shifted shadows | ❌ Simple color swap | ✅ HSL manipulation |
| Customizable | ❌ Need new templates | ✅ Change parameters |

**Conclusion:** Template-based approaches cannot produce the desired quality because they start from flat art and try to add depth through color swapping. Procedural rendering calculates each pixel mathematically, enabling true lighting, gradients, and anti-aliasing.

---

## Development Phases

### Phase 1: Grayscale Face ✅ COMPLETE

**Goal:** Establish the rendering foundation with proper 3D-like shading.

**Completed:**
- [x] SDF utilities (circle, ellipse, rounded rect, smooth union/subtract)
- [x] Face shape (oval with chin taper)
- [x] Lighting model (Lambert diffuse + ambient + rim)
- [x] Eye socket ambient occlusion
- [x] Eyes (sclera, iris with gradient, pupil, dual catchlights)
- [x] Eyebrows (arched shape)
- [x] Nose (subtle detail + shadow)
- [x] Mouth

**Output:** `output/portrait_v3_test.png`

---

### Phase 2: Hair System 🔜 NEXT

**Goal:** Add procedural hair with proper flow, highlights, and rim lighting.

**Planned:**
- [ ] Hair silhouette shapes (define multiple styles)
- [ ] Hair strand flow lines (using curves/noise)
- [ ] Highlight bands (anime-style)
- [ ] Rim lighting on hair edges
- [ ] Back hair layer (behind face)
- [ ] Front hair layer (bangs over face)

**Styles to implement:**
- Wavy, Straight, Short, Ponytail, Bun, Braided

**Technical approach:**
```
1. Define hair silhouette with SDFs
2. Generate flow field for strand direction
3. Render highlight bands following flow
4. Apply rim light on silhouette edges
5. Layer: back hair → face → front hair
```

---

### Phase 3: Color System

**Goal:** Add hue-shift based coloring for natural-looking shading.

**Planned:**
- [ ] Base color input (skin, hair, eyes, clothing)
- [ ] Hue-shift shading:
  - Shadows → shift toward cooler hues
  - Highlights → shift toward warmer hues
- [ ] Automatic palette generation from base colors
- [ ] Color blending and smooth gradients
- [ ] Subsurface scattering for skin (warm shadows)

**Color theory:**
```
Base skin: (253, 181, 115)
Shadow:    hue - 10°, saturation + 5%, lightness - 15%
Highlight: hue + 5°, saturation - 5%, lightness + 10%
```

---

### Phase 4: Body & Accessories

**Goal:** Complete the portrait with body and customization options.

**Planned:**
- [ ] Neck and shoulders
- [ ] Basic clothing shapes
- [ ] Clothing folds and shading
- [ ] Glasses (multiple styles)
- [ ] Earrings
- [ ] Props (books, cups, flowers)

---

### Phase 5: Variation & Expression

**Goal:** Support different face shapes, expressions, and styles.

**Planned:**
- [ ] Face shape variants: round, oval, square, heart, diamond
- [ ] Eye expressions: normal, happy, sad, surprised, angry, wink
- [ ] Mouth expressions: neutral, smile, open, frown, pout
- [ ] Eyebrow expressions: normal, raised, furrowed, worried
- [ ] Head angle/tilt variations

---

## API (Current)

```python
from generators.portrait_v3 import ProceduralPortraitRenderer

# Phase 1: Grayscale rendering
renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
    light_dir=(-0.5, -0.3, 0.8),  # Light from upper-left-front
    ambient=0.3,                   # Base illumination
)
canvas = renderer.render()
canvas.save('portrait.png')
```

## API (Planned - Future Phases)

```python
renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
    # Colors
    skin_color=(253, 181, 115),
    hair_color=(123, 84, 155),
    eye_color=(100, 80, 60),
    clothing_color=(80, 60, 120),
    # Style
    hair_style="wavy",
    face_shape="oval",
    # Expression
    eye_expression="happy",
    mouth_expression="smile",
    # Accessories
    has_glasses=True,
    glasses_style="round",
    has_earrings=True,
)
canvas = renderer.render()
```

---

## Files

```
generators/
├── PORTRAIT.md                  # This document (direction & roadmap)
│
├── portrait_v2/                 # DEPRECATED - template-based
│   ├── composer.py              # (do not use)
│   ├── loader.py
│   └── recolor.py
│
└── portrait_v3/                 # CURRENT - procedural
    ├── __init__.py              # Public API
    ├── DESIGN.md                # Technical design document
    ├── renderer.py              # Main renderer (current: grayscale face)
    │
    └── (planned structure)
        ├── sdf.py               # SDF utilities (extract from renderer)
        ├── lighting.py          # Lighting calculations
        ├── color.py             # Hue-shift color system
        └── features/
            ├── face.py
            ├── eyes.py
            ├── hair.py
            ├── mouth.py
            └── body.py
```

---

## Quality Targets

To match the reference (`output/reference_downsampled.png`):

| Metric | Target | Current |
|--------|--------|---------|
| Canvas size | 64x96 | ✅ 64x96 |
| Smooth gradients | No banding | ✅ Achieved |
| Anti-aliased edges | 1-2px smooth | ✅ Achieved |
| 3D depth | Visible lighting | ✅ Achieved |
| Cute aesthetic | Anime style | 🔜 Needs hair/color |

---

## Success Criteria

The portrait generator will be considered complete when:

1. ✅ Grayscale face has proper 3D depth and lighting
2. ✅ Silhouette edges are smooth (anti-aliased)
3. ✅ Eyes have catchlights and expression
4. ⬜ Hair has flow, highlights, and rim lighting
5. ⬜ Colors use hue-shift shading (not flat)
6. ⬜ Multiple face shapes and expressions work
7. ⬜ Output visually comparable to reference image

---

## Reference

**Target quality:** `output/reference_downsampled.png`

This 64x96 anime pixel art portrait demonstrates:
- Soft, cute aesthetic
- Rich shading with smooth gradients
- Detailed hair with highlights and rim lighting
- Expressive eyes with catchlights
- Cohesive, limited color palette

---

*Last updated: January 2025*
