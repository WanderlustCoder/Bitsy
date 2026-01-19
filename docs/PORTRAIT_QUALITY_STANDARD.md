# Portrait Quality Standard

## Reference Image: `UserExamples/HighRes.png`

This document defines the quality standard for anime-style portraits based on the reference image. All generated portraits should be compared against this standard.

---

## 1. Overall Composition

| Aspect | Reference Standard |
|--------|-------------------|
| **Canvas Size** | ~80x128 pixels (upper body composition) |
| **Framing** | Head + shoulders + upper arms + hands visible |
| **Background** | Solid dark color (navy #1a1a2e or similar) |
| **Subject Position** | Centered, slight asymmetry acceptable |
| **Negative Space** | Clean edges, character doesn't touch canvas borders |

---

## 2. Hair Quality Standard

### 2.1 Structure
- **Form**: Large volumetric masses, NOT individual strands
- **Silhouette**: Clean, readable shape with interesting contour
- **Depth**: Multiple overlapping layers (back hair, side hair, bangs, accessories)
- **Movement**: Suggests natural flow and volume

### 2.2 Color Palette (5-6 colors)
| Level | Description | Example (Purple) |
|-------|-------------|------------------|
| 1 | Deep shadow | #3c2850 |
| 2 | Shadow | #5a3c6e |
| 3 | Base shadow | #826496 |
| 4 | Base | #a08cb4 |
| 5 | Highlight | #c4b4d2 |
| 6 | Rim/Peak | #e8daf0 (near white) |

### 2.3 Lighting
- **Rim Light**: Strong cool blue-white on back edges
- **Form Shadows**: Follow hair mass curvature
- **Highlights**: Concentrated on top curves facing light

### 2.4 Quality Checklist
- [ ] Hair reads as cohesive volumetric shape
- [ ] Rim lighting creates depth separation from background
- [ ] Color transitions are deliberate, not gradient-like
- [ ] Silhouette is interesting and readable at small sizes

---

## 3. Face Quality Standard

### 3.1 Proportions (Anime Style)
- **Eyes**: Large, ~30-35% of face width
- **Eye Position**: Lower on face (larger forehead)
- **Nose**: Minimal, dot or small triangle shadow
- **Mouth**: Small, 1-3 pixels wide
- **Chin**: Soft point, not harsh angles

### 3.2 Skin Color Palette (6 colors)
| Level | Description | RGB Approximate |
|-------|-------------|-----------------|
| 1 | Deep shadow (cool) | #8b5a4a |
| 2 | Shadow | #a67563 |
| 3 | Base shadow | #d4a088 |
| 4 | Base | #e8c4a8 |
| 5 | Highlight | #f5dcc8 |
| 6 | Peak | #fff0e0 |

### 3.3 Shading Principles
- **Shadow Hue**: Shifts toward cool (purple/blue undertone)
- **Highlight Hue**: Shifts toward warm (yellow/peach)
- **Form**: Shadows define cheekbones, jaw, nose bridge
- **Rim Light**: Cool blue on edge facing away from light

### 3.4 Quality Checklist
- [ ] Face shape is clear and appealing
- [ ] Skin has warm base with cool shadows
- [ ] Features are simplified but expressive
- [ ] No muddy colors or over-blending

---

## 4. Eye Quality Standard

### 4.1 Structure (8 layers, back to front)
1. **Sclera**: Warm white/cream tint
2. **Iris Base**: Mid-tone of eye color
3. **Iris Gradient**: Dark at top, lighter at bottom
4. **Pupil**: Black, centered or slightly up
5. **Detail Ring**: Optional, adds depth
6. **Upper Shadow**: From eyelid, creates depth
7. **Primary Catchlight**: Large, white, upper area
8. **Secondary Catchlight**: Small, opposite side

### 4.2 Proportions
- **Width**: 12-16 pixels for 80px canvas
- **Height**: 70-80% of width (tall ellipse)
- **Iris**: 70-80% of eye opening
- **Pupil**: 30-40% of iris

### 4.3 Quality Checklist
- [ ] Eyes are expressive and alive
- [ ] Catchlights create sparkle effect
- [ ] Iris has gradient depth
- [ ] Both eyes consistent but not perfectly identical

---

## 5. Clothing Quality Standard

### 5.1 Structure
- **Form**: Suggests body shape underneath
- **Folds**: Simple, strategic fold lines only
- **Details**: Collars, buttons, trim where appropriate

### 5.2 Color Palette (4-5 colors)
- Deep shadow, shadow, base, highlight, rim

### 5.3 Lighting
- **Same rim light** as hair and skin
- **Form shadows** follow body contour
- **Consistent light direction** with rest of portrait

### 5.4 Quality Checklist
- [ ] Clothing reads as fabric, not flat color
- [ ] Rim lighting consistent with other elements
- [ ] Details are clear but not overwhelming

---

## 6. Accessories Quality Standard

### 6.1 Glasses (if present)
- **Frames**: 2-3 colors (shadow, base, highlight)
- **Lenses**: Semi-transparent or tinted
- **Fit**: Natural position on face

### 6.2 Props (books, items)
- **Clarity**: Immediately recognizable
- **Integration**: Hands naturally hold them
- **Palette**: Limited colors, cohesive with portrait

---

## 7. Technical Quality Standard

### 7.1 Pixel Art Rules
| Rule | Standard |
|------|----------|
| **Jaggies** | No unintentional jagged lines |
| **Orphan Pixels** | No single floating pixels |
| **Banding** | No unintentional color banding |
| **Pillow Shading** | Avoided - use directional light |
| **Anti-aliasing** | Selective, silhouette edges only |

### 7.2 Color Count
- **Total Portrait**: 25-40 unique colors
- **Per Element**: 4-6 colors maximum
- **No Gradients**: Distinct color steps only

### 7.3 Readability
- **Small Size**: Portrait should read clearly at 50% scale
- **Silhouette**: Recognizable as character with hair visible

---

## 8. Lighting Consistency

### 8.1 Light Sources
| Source | Direction | Color | Intensity |
|--------|-----------|-------|-----------|
| Key Light | Front-left | Warm white | Primary |
| Rim Light | Back-right | Cool blue #b4c8ff | Strong |
| Ambient | All | Neutral | Subtle |

### 8.2 Shadow Direction
- All shadows fall consistently opposite key light
- Rim light appears on edges facing away from viewer

---

## 9. Comparison Checklist

When comparing generated portrait to reference:

### Must Match
- [ ] Professional anime pixel art style
- [ ] Volumetric hair with rim lighting
- [ ] Large expressive eyes with catchlights
- [ ] Warm skin with cool shadows (hue shifting)
- [ ] Limited color palette per element
- [ ] Clean pixel work, strategic AA
- [ ] Upper body composition with hands visible
- [ ] Consistent lighting direction

### Acceptable Variation
- Character gender, age, features
- Hair style, color, length
- Eye color, expression
- Clothing style, color
- Accessories present/absent
- Exact proportions (within anime style)

### Not Acceptable
- Realistic/gradient shading
- Individual hair strands instead of masses
- Small realistic-proportion eyes
- Muddy or over-blended colors
- Inconsistent lighting direction
- Unprofessional pixel artifacts

---

## 10. Quality Scoring

Rate each aspect 1-5:

| Aspect | Weight | Score | Notes |
|--------|--------|-------|-------|
| Hair Quality | 20% | /5 | |
| Face/Skin | 20% | /5 | |
| Eye Quality | 15% | /5 | |
| Clothing | 10% | /5 | |
| Lighting Consistency | 15% | /5 | |
| Technical Quality | 10% | /5 | |
| Overall Appeal | 10% | /5 | |

**Minimum Passing Score**: 3.5/5 weighted average

---

## Version History
- v1.0 - Initial quality standard based on HighRes.png reference
