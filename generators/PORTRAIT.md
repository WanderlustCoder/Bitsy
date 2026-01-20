# Portrait Generation - Current Direction

## Status: Portrait v3 (Procedural Rendering)

**v3 is the current way forward.** The template-based approaches (v1, v2) have been deprecated.

---

## IMPORTANT: Quality Gate

**No new features will be added until the face meets quality standards.**

The grayscale face must be validated against the reference image before proceeding to hair, color, body, or any other features. This prevents wasted effort on features built on a flawed foundation.

**Current focus:** Face only. Iterate until quality is proven.

---

## Quick Links

- **Detailed Design:** `portrait_v3/DESIGN.md`
- **Source Code:** `portrait_v3/renderer.py`
- **Reference Image:** `output/reference_downsampled.png`
- **Current Output:** `output/portrait_v3_test.png`

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
- Hue-shift color system (planned, blocked on quality gate)

---

## Why Procedural Rendering?

The reference image quality requires:

| Requirement | Template Approach | Procedural Approach |
|-------------|-------------------|---------------------|
| Soft gradients | Flat colors only | Calculated per-pixel |
| Proper lighting | Baked in template | Dynamic light model |
| Smooth edges | Pixelated edges | SDF anti-aliasing |
| Hue-shifted shadows | Simple color swap | HSL manipulation |
| Customizable | Need new templates | Change parameters |

**Conclusion:** Template-based approaches cannot produce the desired quality because they start from flat art and try to add depth through color swapping. Procedural rendering calculates each pixel mathematically, enabling true lighting, gradients, and anti-aliasing.

---

## Current Phase: Grayscale Face

**Status:** IN DEVELOPMENT - Quality validation required

**Goal:** Create a grayscale face that demonstrates professional-quality rendering.

**Implemented:**
- [x] SDF utilities (circle, ellipse, rounded rect, smooth union/subtract)
- [x] Face shape (oval with chin taper)
- [x] Lighting model (Lambert diffuse + ambient + rim)
- [x] Eye socket ambient occlusion
- [x] Eyes (sclera, iris with gradient, pupil, dual catchlights)
- [x] Eyebrows (arched shape)
- [x] Nose (subtle detail + shadow)
- [x] Mouth

**Quality validation:**
- [ ] Compare output to reference face (grayscale conversion)
- [ ] Verify lighting creates convincing 3D depth
- [ ] Verify edges are smooth and anti-aliased
- [ ] Verify proportions look "cute" not "outlandish"
- [ ] **User approval required before proceeding**

**Output:** `output/portrait_v3_test.png`

---

## Future Phases (BLOCKED)

The following phases are blocked until the face quality is validated:

### Phase 2: Hair System (BLOCKED)
- Hair silhouette shapes
- Hair strand flow lines
- Highlight bands
- Rim lighting

### Phase 3: Color System (BLOCKED)
- Hue-shift shading
- Palette generation
- Skin subsurface scattering

### Phase 4: Body & Accessories (BLOCKED)
- Neck and shoulders
- Clothing
- Glasses, earrings, props

### Phase 5: Variation & Expression (BLOCKED)
- Face shape variants
- Eye/mouth expressions
- Head angles

**These phases will remain blocked until the grayscale face is approved.**

---

## API (Current)

```python
from generators.portrait_v3 import ProceduralPortraitRenderer

# Grayscale face only
renderer = ProceduralPortraitRenderer(
    width=64,
    height=96,
    light_dir=(-0.5, -0.3, 0.8),  # Light from upper-left-front
    ambient=0.3,                   # Base illumination
)
canvas = renderer.render()
canvas.save('portrait.png')
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
    └── renderer.py              # Main renderer (grayscale face)
```

---

## Quality Targets

To match the reference (`output/reference_downsampled.png`):

| Metric | Target | Current | Validated |
|--------|--------|---------|-----------|
| Canvas size | 64x96 | 64x96 | Pending |
| Smooth gradients | No banding | Implemented | Pending |
| Anti-aliased edges | 1-2px smooth | Implemented | Pending |
| 3D depth | Visible lighting | Implemented | Pending |
| Cute aesthetic | Anime style | Implemented | **Pending user approval** |

---

## Success Criteria (Face Only)

The grayscale face will be considered ready when:

1. [ ] Face has proper 3D depth and lighting
2. [ ] Silhouette edges are smooth (anti-aliased)
3. [ ] Eyes have catchlights and expression
4. [ ] Proportions look natural and appealing
5. [ ] **User confirms quality meets expectations**

Only after these criteria are met will development proceed to Phase 2.

---

## Reference

**Target quality:** `output/reference_downsampled.png`

For face validation, compare the grayscale face structure to the reference:
- Face shape and proportions
- Eye placement and detail
- Lighting direction and depth
- Edge smoothness

---

*Last updated: January 2025*
