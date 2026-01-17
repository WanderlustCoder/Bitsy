# Pixel Art Principles

Core principles that apply to ALL pixel art drawing in this toolkit.

## Light Direction

**Standard light source: Top-left (315 degrees)**

This means:
- Highlights appear on top-left edges of forms
- Shadows fall on bottom-right
- Cast shadows extend toward bottom-right

When drawing ANY shape:
```
Highlight: offset (-1, -1) from main shape, lighter color
Shadow: offset (+1, +1) from main shape, darker color
```

## Color Relationships

### Creating a Color Ramp (5 colors minimum for quality)

For any base color, generate:
1. **Darkest shadow** - darken 35%, shift hue toward cool (blue/purple)
2. **Shadow** - darken 20%, slight cool shift
3. **Base** - the main color
4. **Light** - lighten 15%, shift hue toward warm (yellow/orange)
5. **Highlight** - lighten 30%, strong warm shift

Example for brown hair (base: 110, 75, 60):
```python
colors = [
    (50, 35, 35),    # darkest - cool shadow
    (75, 50, 45),    # shadow
    (110, 75, 60),   # base
    (140, 100, 75),  # light
    (180, 140, 110), # highlight - warm
]
```

### Hue Shifting

Never just lighten/darken. Always shift hue:
- Shadows → cooler (toward blue/purple)
- Highlights → warmer (toward yellow/orange)

This creates life and depth. Pure value changes look flat.

## Shape Layering Order

Always draw back-to-front:
1. Shadows/background elements
2. Main forms (back layer)
3. Main forms (front layer)
4. Highlights
5. Details/outlines

## Anti-Aliasing Rules

Use AA (`_aa` methods) for:
- Curves and diagonals
- Anything that would look jagged at display size

Skip AA for:
- Horizontal/vertical lines
- Very small details (under 4px)
- Intentionally crisp edges

## Size-Appropriate Detail

### 32x32 and smaller
- Minimal detail, focus on readable silhouette
- 2-3 colors per region max
- No strand-level hair detail
- Eyes: 2-4 pixels, simple highlight

### 64x64
- Moderate detail
- 3-4 colors per region
- Hair: suggest strands with a few lines, not individual strands
- Eyes: can show iris/pupil separation, 1-2 highlights

### 128x128 and larger
- Full detail
- 5+ colors per region
- Hair: visible strand groupings
- Eyes: full iris detail, multiple highlights, lash hints

## Outline Techniques

### Selout (Selective Outline)
- Outline color matches adjacent region but darker
- Creates softer, more integrated look
- Use for interior edges between parts

### Hard Outline
- Single dark color (near-black)
- Use for character silhouette/exterior only
- Creates clear separation from background

### No Outline
- Shapes defined purely by color contrast
- Softest look, requires careful color planning
- Good for organic forms (hair, clouds)

## Common Mistakes to Avoid

1. **Pillow shading** - Don't shade from edges inward. Shade based on light direction.
2. **Banding** - Don't create parallel lines of color. Vary transitions.
3. **Too many colors** - Constrain palette. More colors ≠ better.
4. **Ignoring hue shift** - Pure value ramps look dead.
5. **Over-rendering small areas** - Detail should be size-appropriate.

## Canvas Primitive Selection

| Want to draw | Use this | Notes |
|--------------|----------|-------|
| Solid circle/oval | `fill_ellipse` | Basic shapes |
| Smooth circle edge | `fill_ellipse_aa` | When jaggies visible |
| Shaded sphere | `fill_ellipse_radial_gradient` | 3D form |
| Directional shading | `fill_ellipse_gradient` | Hair mass, clothing |
| Smooth color blend | `fill_ellipse_dithered` | Subtle transitions |
| Hair strand | `draw_bezier_tapered` | Thick→thin curves |
| Smooth line | `draw_line_aa` | Diagonals |
| Sharp line | `draw_line` | H/V lines |
