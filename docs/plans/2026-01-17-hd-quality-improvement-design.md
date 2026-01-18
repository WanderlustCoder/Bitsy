# HD Quality Improvement Design

**Date:** 2026-01-17
**Status:** Approved
**Goal:** Make Bitsy produce professional-quality pixel art by default

## Problem Statement

Current demo output looks amateurish ("like a kid made these in MS Paint") because:

1. **Defaults are weak** - 32x32, chibi style, no selout, no anti-aliasing
2. **Geometric shapes** - Hair uses circles/ellipses instead of organic strands
3. **Flat band shading** - Concentric shapes create "mushroom" effect
4. **Professional features exist but aren't enabled** - selout, strand hair, color harmony

## Solution Overview

Two-phase approach:

- **Phase 1:** Quick wins - Wire up existing quality features as defaults
- **Phase 2:** Advanced techniques - Add missing pixel art rendering algorithms

---

## Phase 1: Quick Wins (Wire Up Existing Features)

### 1.1 Change Default Style

**Current:** 32x32 chibi with no selout
**Target:** 48x48 modern_hd with selout enabled

Files:
- `generators/character.py`
- `generators/creature.py`
- `generators/item.py`
- `generators/prop.py`

### 1.2 Enable Selout by Default

Enable selective outline in all styles except retro presets.

File: `core/style.py`

```python
# Before (chibi)
outline=OutlineConfig(enabled=True, mode='external', color_mode='soft')

# After (chibi)
outline=OutlineConfig(enabled=True, mode='selout', selout_enabled=True)
```

### 1.3 Use Professional Hair Rendering

Switch from geometric circles/ellipses to bezier strand-based rendering.

Files:
- `parts/hair.py` - Import and delegate to `hair_pro.py`
- Add strand count scaling for smaller sizes

### 1.4 Apply Color Harmony

Use `quality/color_harmony.py` to ensure pleasing color combinations in generated palettes.

File: `generators/character.py`

### 1.5 Enable Gradient Shading (5-level minimum)

**Current:** 3-level cel shading (flat bands)
**Target:** 5-level gradient shading with hue shifting

File: `core/style.py`

```python
shading=ShadingConfig(
    mode='gradient',
    levels=5,
    highlight_hue_shift=15.0,
    shadow_hue_shift=-20.0
)
```

**Estimated impact:** 60-70% quality improvement with minimal new code.

---

## Phase 2: Advanced Techniques (New Rendering Features)

### 2.1 Floyd-Steinberg Dithering

**Problem:** Current Bayer matrix creates visible diagonal patterns
**Solution:** Error-diffusion dithering for smoother gradients

File: `core/canvas.py`

```python
def dither_floyd_steinberg(self, palette: List[RGBA]) -> Canvas:
    """Apply Floyd-Steinberg error-diffusion dithering."""
    # Distribute quantization error to neighboring pixels
    # Right: 7/16, Bottom-left: 3/16, Bottom: 5/16, Bottom-right: 1/16
```

### 2.2 Lab/LCh Color Space

**Problem:** RGB Euclidean distance picks visually wrong colors
**Solution:** Lab distance matches human perception

File: `core/palette.py`

```python
def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to CIE Lab color space."""

def color_distance_lab(c1: RGBA, c2: RGBA) -> float:
    """Perceptually uniform color distance."""
```

### 2.3 Contact Shadows Between Parts

**Problem:** Parts float on top of each other with no depth
**Solution:** Subtle darkening where parts meet

File: `generators/character.py`

```python
def apply_contact_shadow(canvas: Canvas, top_layer: Canvas, offset: int = 1):
    """Add shadow where top layer overlaps bottom."""
```

### 2.4 Automatic Highlight Placement

**Problem:** Highlights are geometrically centered (unnatural)
**Solution:** Calculate surface normals, place highlights based on light direction

File: `quality/auto_shade.py`

```python
def calculate_highlight_position(shape_mask: Canvas, light_dir: Tuple[float, float]) -> Tuple[int, int]:
    """Find optimal highlight position based on shape and lighting."""
```

### 2.5 Sub-pixel Anti-aliasing for Curves

**Problem:** Current AA works but could be sharper
**Solution:** Coverage-based anti-aliasing for cleaner edges

File: `core/canvas.py`

**Estimated impact:** Additional 20-30% quality improvement.

---

## Implementation Order

### Phase 1 (Dependencies matter)

```
1. Update core/style.py defaults
   └── Enable selout, bump shading levels

2. Update generators to use new defaults
   └── character.py, creature.py, item.py, prop.py

3. Wire professional hair to standard rendering
   └── parts/hair.py imports from hair_pro.py

4. Integrate color harmony into palette generation
   └── generators/character.py uses color_harmony.py

5. Regenerate demo assets & verify quality
```

### Phase 2 (Dependencies matter)

```
1. Floyd-Steinberg dithering (core/canvas.py)
   └── Standalone, no dependencies

2. Lab color space (core/palette.py)
   └── Affects color harmony, needs tests

3. Contact shadows (generators/character.py)
   └── Depends on working render pipeline

4. Auto highlight placement (quality/auto_shade.py)
   └── Depends on Lab colors for natural results

5. Sub-pixel AA (core/canvas.py)
   └── Final polish, lowest priority
```

---

## Testing Approach

1. **Visual regression tests:** Generate reference images, compare after changes
2. **A/B comparison page:** HTML page showing old vs new output side-by-side
3. **Metrics:** Use existing `quality/analyzer.py` to measure orphan pixels, jaggies, banding

## Success Criteria

- Demo output no longer looks "MS Paint"
- Professional_hd quality becomes the baseline for all output
- Measurable reduction in quality analyzer warnings

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance regression from professional hair | Medium | Strand count scaling based on sprite size |
| Lab color space breaks existing palettes | High | Keep RGB fallback; convert at boundaries only |
| Contact shadows look wrong at small sizes | Low | Disable below 32x32; use 1px shadow max |
| Breaking changes for existing users | Medium | Version bump; keep `chibi` style unchanged |

## Backwards Compatibility

- Keep all existing styles available (`chibi`, `retro_nes`, etc.)
- Add new `modern` style as the new default
- Existing code using explicit `style=Style.chibi()` continues working
- Only default behavior changes

---

## Deliverables

1. Updated `core/style.py` with better defaults
2. Updated generators with quality features enabled
3. New dithering algorithms in `core/canvas.py`
4. Lab color space in `core/palette.py`
5. Contact shadow system in render pipeline
6. Updated demo with before/after comparison
7. Documentation of new quality features
