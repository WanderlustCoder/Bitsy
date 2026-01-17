# Character Spec Format

A spec defines what to draw. The recipe loader reads specs and applies the appropriate recipes.

## Spec Structure

```yaml
# Character specification
size: 128                    # Canvas size (square)
background: [45, 40, 55]     # RGB background color

character:
  # Proportions (optional - defaults provided)
  head_center: [64, 54]      # [x, y] or 'auto'
  head_size: [70, 84]        # [width, height] or 'auto'

  # Skin
  skin:
    tone: fair               # fair, medium, tan, dark, or custom RGB
    # OR custom:
    # base: [235, 200, 175]
    # shadow: [200, 160, 140]
    # light: [245, 220, 200]

  # Hair
  hair:
    style: bun               # bun, long, short, ponytail, etc.
    color: brown             # brown, dark_brown, black, blonde, auburn, or custom
    # OR custom palette:
    # colors: [[50,35,30], [80,55,45], [115,80,60], [150,110,85], [190,150,120]]

  # Eyes
  eyes:
    style: large             # small, medium, large
    color: blue              # brown, blue, green, or custom RGB
    expression: neutral      # neutral, happy, sad, surprised, angry

  # Face details
  face:
    nose: minimal            # minimal, small, none
    mouth: happy             # neutral, happy, sad, surprised, cat_smile
    blush: 0.3               # 0.0-1.0 intensity, or false

  # Accessories (optional)
  accessories:
    glasses:
      style: round           # round, rectangular, cateye
      frame_color: dark      # dark, brown, gold, silver, or custom RGB
      lens: clear            # clear, tinted, or custom RGBA
      glare: true
```

## Minimal Spec

Only required fields:

```yaml
size: 128
character:
  hair:
    style: bun
    color: brown
  eyes:
    color: blue
```

Everything else uses defaults.

## Defaults

```yaml
background: [45, 40, 55]           # dark purple-gray

character:
  head_center: auto                 # calculated from size
  head_size: auto                   # calculated from size

  skin:
    tone: fair

  hair:
    style: long                     # default style
    color: brown                    # default color

  eyes:
    style: large
    color: brown
    expression: neutral

  face:
    nose: minimal
    mouth: neutral
    blush: 0.2

  accessories: {}                   # none by default
```

## Color Presets

### Skin Tones
```python
SKIN_TONES = {
    'fair': {
        'base': (235, 200, 175),
        'shadow': (200, 160, 140),
        'light': (245, 220, 200),
    },
    'medium': {
        'base': (210, 165, 135),
        'shadow': (175, 130, 105),
        'light': (225, 185, 160),
    },
    'tan': {
        'base': (180, 135, 100),
        'shadow': (145, 105, 75),
        'light': (200, 160, 125),
    },
    'dark': {
        'base': (140, 95, 70),
        'shadow': (105, 70, 50),
        'light': (165, 120, 90),
    },
}
```

### Hair Colors
```python
HAIR_COLORS = {
    'brown': [(50,35,30), (80,55,45), (115,80,60), (150,110,85), (190,150,120)],
    'dark_brown': [(35,25,25), (55,40,35), (85,60,50), (120,90,70), (160,125,100)],
    'black': [(20,20,30), (35,35,50), (55,50,65), (80,75,95), (120,110,135)],
    'blonde': [(140,100,50), (180,140,70), (210,175,100), (235,205,140), (250,235,190)],
    'auburn': [(60,25,20), (100,45,35), (145,65,45), (180,95,65), (210,140,100)],
}
```

### Eye Colors
```python
EYE_COLORS = {
    'brown': {'base': (100,65,50), 'dark': (70,45,35), 'light': (140,95,70)},
    'blue': {'base': (70,110,170), 'dark': (50,80,130), 'light': (100,150,200)},
    'green': {'base': (60,120,70), 'dark': (35,80,50), 'light': (90,160,100)},
}
```

### Frame Colors
```python
FRAME_COLORS = {
    'dark': (35, 30, 40),
    'brown': (90, 60, 45),
    'gold': (180, 150, 80),
    'silver': (160, 165, 175),
}
```

## Example Specs

### Simple Character
```yaml
size: 128
character:
  hair: {style: bun, color: brown}
  eyes: {color: blue}
```

### Detailed Character
```yaml
size: 128
background: [30, 35, 45]

character:
  skin:
    tone: fair

  hair:
    style: bun
    color: auburn

  eyes:
    color: green
    expression: happy

  face:
    nose: minimal
    mouth: happy
    blush: 0.4

  accessories:
    glasses:
      style: round
      frame_color: dark
      glare: true
```

### Custom Colors
```yaml
size: 128
character:
  skin:
    base: [255, 220, 200]
    shadow: [220, 180, 160]
    light: [255, 240, 230]

  hair:
    style: long
    colors:
      - [80, 50, 100]      # purple tones
      - [120, 70, 140]
      - [160, 100, 180]
      - [200, 140, 210]
      - [230, 180, 240]

  eyes:
    color: [180, 50, 180]  # custom purple
    expression: neutral
```
