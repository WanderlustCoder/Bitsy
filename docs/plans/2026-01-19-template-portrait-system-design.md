# Template-Based Portrait System Design

## Problem Statement

The current procedural portrait generator produces output that doesn't look human. Face proportions are wrong, features are misplaced, and hair renders as abstract shapes rather than recognizable masses. The system needs a fundamental redesign to produce quality anime-style portraits.

## Chosen Approach: Template-Based Rendering

Instead of procedurally calculating every pixel, define "templates" - pre-designed face shapes, eye styles, and hair patterns that are known to look good. The system composites and colors these templates based on parameters.

**Why this approach:**
- Guaranteed quality output - templates are designed to look correct
- Easy to add new styles - just add new template folders
- Predictable results - same config always produces similar quality
- Flexible - supports multiple art styles via profiles

---

## Architecture Overview

### Three Layers

1. **Template Library** - Pre-designed pixel art stencils (PNG files)
2. **Template Composer** - Combines templates with correct layering/positioning
3. **Style Profiles** - JSON configs defining how templates combine

---

## Template Format

### File Structure
```
templates/
  anime_standard/
    profile.json
    faces/
      oval.png, oval.json
      round.png, round.json
    eyes/
      large.png, large.json
    noses/
      dot.png, dot.json
    mouths/
      neutral.png, neutral.json
    hair/
      wavy_back.png, wavy_front.png
    bodies/
      neutral.png, holding.png
```

### Standardized Palette for Recoloring

| Index | Purpose | Placeholder Color |
|-------|---------|-------------------|
| 0 | Transparent | (0,0,0,0) |
| 1 | Base color | (255,0,0) |
| 2 | Shadow 1 | (200,0,0) |
| 3 | Shadow 2 (deep) | (150,0,0) |
| 4 | Highlight 1 | (255,100,100) |
| 5 | Highlight 2 (bright) | (255,180,180) |
| 6 | Outline | (100,0,0) |
| 7 | Secondary color | (0,255,0) |

### Template Metadata (JSON)
```json
{
  "name": "anime_large_eyes",
  "anchor": [16, 20],
  "size": [32, 24],
  "symmetric": true,
  "flip_for_right": true
}
```

---

## Composition Pipeline

Render order (back to front):

1. **Background** (optional)
2. **Back Hair Layer** - hair behind head
3. **Body/Clothing** - shoulders, clothing
4. **Face Base** - face shape template with skin colors
5. **Facial Features** - eyes, nose, mouth, eyebrows (positioned relative to face)
6. **Front Hair Layer** - bangs, hair overlapping face
7. **Accessories** - glasses, earrings
8. **Post-processing** - rim lighting, outline

### Feature Positioning

Features are placed relative to face bounds using ratios from the style profile:

```python
def place_feature(canvas, template, face_bounds, y_ratio, x_offset=0):
    face_x, face_y, face_w, face_h = face_bounds
    x = face_x + (face_w // 2) - (template.width // 2) + x_offset
    y = face_y + int(face_h * y_ratio) - template.anchor_y
    canvas.composite(template, x, y)
```

---

## Style Profiles

Each style has a `profile.json` defining proportions and settings:

```json
{
  "name": "anime_standard",
  "description": "Standard anime style matching HighRes.png reference",

  "canvas_size": [80, 128],

  "proportions": {
    "head_ratio": 0.35,
    "eye_y": 0.42,
    "nose_y": 0.58,
    "mouth_y": 0.68,
    "eye_spacing": 0.24
  },

  "templates": {
    "face": ["oval", "round", "soft_square"],
    "eyes": ["anime_large", "anime_round"],
    "nose": ["dot", "minimal"],
    "mouth": ["small_neutral", "small_smile"],
    "hair": ["wavy", "straight", "curly"]
  },

  "coloring": {
    "skin_ramp_size": 5,
    "hair_ramp_size": 6,
    "use_hue_shift": true,
    "shadow_hue_shift": -15,
    "rim_light_color": [180, 210, 255],
    "rim_light_intensity": 0.7
  },

  "post_processing": {
    "outline": "thin",
    "outline_color": [40, 30, 50],
    "selective_aa": true
  }
}
```

---

## Code Structure

### New Module
```
generators/
  portrait_v2/
    __init__.py
    composer.py      # Template composition logic
    recolor.py       # Palette swapping
    loader.py        # Template loading/caching
```

### Integration
```python
# Old system (preserved)
from generators.portrait import PortraitGenerator

# New system
from generators.portrait_v2 import TemplatePortraitGenerator

# Same config works with both
config = PortraitConfig(hair_color="purple", eye_color="blue", ...)
canvas = TemplatePortraitGenerator(config, style="anime_standard").render()
```

---

## Implementation Phases

### Phase 1: Foundation
- Create `generators/portrait_v2/` module structure
- Implement `loader.py` - load PNG templates, parse JSON metadata
- Implement `recolor.py` - palette swapping with hue-shift support
- Create `templates/anime_standard/profile.json`

### Phase 2: Core Templates
- Design face templates (oval, round) - 32x32px
- Design eye templates (anime_large) - 16x12px
- Design minimal nose/mouth templates
- Test: render face with eyes

### Phase 3: Composer
- Implement `composer.py` with render pipeline
- Layer ordering and positioning logic
- Feature placement relative to face bounds
- Test: full face renders correctly

### Phase 4: Hair & Body
- Create hair templates (back layer, front layer)
- Create body/pose templates (neutral, holding)
- Integrate into composer pipeline
- Test: full upper-body portrait

### Phase 5: Polish & Parity
- Add rim lighting post-processing
- Add outline support
- Match output quality to reference image
- Create additional template variants

### Phase 6: Migration
- Update `PortraitConfig` to support both systems
- Add style selection parameter
- Deprecate old renderer (optional)

---

## Success Criteria

### Minimum Viable Output
- [ ] Generated portrait immediately recognizable as human/anime character
- [ ] Face proportions look natural
- [ ] Hair reads as hair, not abstract shapes
- [ ] Body pose is clear and readable

### Quality Targets
- [ ] Output comparable to `UserExamples/HighRes.png`
- [ ] Clean pixel art with no artifacts
- [ ] Color palette: 30-45 colors
- [ ] Consistent style across configs

### Flexibility Targets
- [ ] Can change hair/eye color without breaking proportions
- [ ] Can add new templates without code changes
- [ ] Can create new style profiles by adding template folders

---

## Reference

Target quality: `UserExamples/HighRes.png`
