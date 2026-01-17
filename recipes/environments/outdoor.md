# Outdoor Environments Recipe

How to draw exterior backgrounds in pixel art.

## General Principles

1. **Atmospheric perspective**: Distant objects are lighter/hazier
2. **Ground plane**: Establish clear horizon line
3. **Sky gradient**: Adds depth and mood
4. **Natural variation**: Avoid perfect symmetry in nature

## Sky Palettes

```python
SKY_PALETTES = {
    'day_clear': {
        'top': (100, 160, 220),
        'mid': (140, 190, 235),
        'low': (180, 215, 245),
        'horizon': (220, 235, 250),
    },
    'sunset': {
        'top': (60, 80, 140),
        'mid': (180, 120, 100),
        'low': (255, 180, 100),
        'horizon': (255, 220, 160),
    },
    'sunrise': {
        'top': (80, 100, 160),
        'mid': (180, 160, 180),
        'low': (255, 200, 150),
        'horizon': (255, 230, 200),
    },
    'night': {
        'top': (15, 20, 40),
        'mid': (25, 35, 60),
        'low': (40, 50, 80),
        'horizon': (60, 70, 100),
    },
    'overcast': {
        'top': (140, 145, 155),
        'mid': (160, 165, 175),
        'low': (180, 185, 195),
        'horizon': (200, 205, 215),
    },
    'stormy': {
        'top': (50, 55, 70),
        'mid': (70, 75, 90),
        'low': (90, 95, 110),
        'horizon': (120, 125, 140),
    },
}

GROUND_PALETTES = {
    'grass': {
        'dark': (45, 80, 35),
        'mid': (70, 120, 50),
        'light': (100, 160, 70),
    },
    'dirt': {
        'dark': (70, 50, 35),
        'mid': (110, 85, 60),
        'light': (150, 120, 90),
    },
    'sand': {
        'dark': (180, 160, 120),
        'mid': (210, 195, 160),
        'light': (235, 225, 200),
    },
    'snow': {
        'dark': (200, 210, 220),
        'mid': (225, 235, 245),
        'light': (245, 250, 255),
    },
    'stone': {
        'dark': (80, 80, 90),
        'mid': (120, 120, 130),
        'light': (160, 160, 170),
    },
}
```

## Sky Drawing

```python
def draw_sky(canvas, width, height, sky_height, palette_name='day_clear'):
    """
    Draw sky with gradient.

    Args:
        sky_height: Where sky ends (horizon line)
    """
    palette = SKY_PALETTES.get(palette_name, SKY_PALETTES['day_clear'])

    for y in range(min(sky_height, height)):
        t = y / sky_height

        # 4-stop gradient
        if t < 0.25:
            color = _lerp_color(palette['top'], palette['mid'], t * 4)
        elif t < 0.5:
            color = _lerp_color(palette['mid'], palette['low'], (t - 0.25) * 4)
        elif t < 0.75:
            color = _lerp_color(palette['low'], palette['horizon'], (t - 0.5) * 4)
        else:
            color = palette['horizon']

        canvas.draw_line(0, y, width - 1, y, color)


def _lerp_color(c1, c2, t):
    """Linear interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_stars(canvas, width, height, density=0.002):
    """Add stars to night sky."""
    import random

    star_count = int(width * height * density)
    for _ in range(star_count):
        x = random.randint(0, width - 1)
        y = random.randint(0, height // 2)  # Upper half

        # Vary brightness
        brightness = random.randint(150, 255)
        # Slight color variation
        tint = random.choice([(0, 0, 0), (10, 10, -10), (-10, 0, 10)])
        color = tuple(max(0, min(255, brightness + t)) for t in tint)

        canvas.set_pixel(x, y, color)

        # Occasional larger star
        if random.random() < 0.1:
            canvas.set_pixel(x + 1, y, (brightness // 2,) * 3)
            canvas.set_pixel(x - 1, y, (brightness // 2,) * 3)


def draw_moon(canvas, x, y, size, phase='full'):
    """Draw moon."""
    # Base moon
    moon_color = (240, 235, 220)
    moon_shadow = (180, 175, 165)
    moon_highlight = (255, 252, 245)

    canvas.fill_ellipse(x, y, size, size, moon_color)

    # Craters (subtle)
    if size >= 6:
        canvas.set_pixel(x - size // 3, y - size // 4, moon_shadow)
        canvas.set_pixel(x + size // 4, y + size // 3, moon_shadow)
        canvas.set_pixel(x - 1, y + size // 4, moon_shadow)

    # Highlight
    canvas.set_pixel(x - size // 2 + 1, y - size // 2 + 1, moon_highlight)

    # Phase shadow
    if phase == 'crescent':
        # Shadow covers right side
        for sy in range(-size, size + 1):
            shadow_x = size // 2
            canvas.draw_line(x + shadow_x, y + sy, x + size, y + sy, (20, 25, 40))
    elif phase == 'half':
        for sy in range(-size, size + 1):
            canvas.draw_line(x, y + sy, x + size, y + sy, (30, 35, 50))
```

## Forest

```python
def draw_forest_bg(canvas, width, height, density='medium', time='day'):
    """Draw a forest background."""

    # Sky
    sky_height = height // 2
    sky_palette = 'day_clear' if time == 'day' else 'night' if time == 'night' else 'sunset'
    draw_sky(canvas, width, height, sky_height, sky_palette)

    ground = GROUND_PALETTES['grass']

    # Ground
    for y in range(sky_height, height):
        t = (y - sky_height) / (height - sky_height)
        idx = min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, ground[['light', 'mid', 'dark'][idx]])

    # Tree colors
    if time == 'night':
        trunk = [(20, 18, 22), (35, 32, 38), (50, 45, 55)]
        leaves = [(25, 40, 35), (35, 55, 45), (45, 70, 55)]
    else:
        trunk = [(50, 35, 25), (80, 60, 45), (110, 90, 70)]
        leaves = [(35, 70, 40), (50, 95, 55), (70, 120, 75)]

    # Background trees (distant, simple)
    tree_density = {'light': 3, 'medium': 5, 'heavy': 8}[density]
    import random
    random.seed(42)  # Consistent trees

    # Far trees
    for i in range(tree_density):
        tx = random.randint(0, width - 1)
        tree_height = random.randint(height // 4, height // 3)
        base_y = sky_height + random.randint(-5, 10)

        # Simple triangle tree
        _draw_simple_tree(canvas, tx, base_y, tree_height, leaves[0], trunk[0])

    # Mid trees
    for i in range(tree_density // 2):
        tx = random.randint(0, width - 1)
        tree_height = random.randint(height // 3, height // 2)
        base_y = sky_height + height // 4

        _draw_simple_tree(canvas, tx, base_y, tree_height, leaves[1], trunk[1])

    # Add some grass tufts
    for gx in range(0, width, 4):
        gy = height - random.randint(2, 5)
        canvas.set_pixel(gx, gy, ground['dark'])
        if random.random() > 0.5:
            canvas.set_pixel(gx + 1, gy - 1, ground['mid'])


def _draw_simple_tree(canvas, x, base_y, height, leaf_color, trunk_color):
    """Draw a simple triangular tree."""
    trunk_height = height // 4
    foliage_height = height - trunk_height

    # Trunk
    trunk_width = max(2, height // 10)
    canvas.fill_rect(x - trunk_width // 2, base_y, trunk_width, trunk_height, trunk_color)

    # Foliage (triangle)
    foliage_start = base_y - foliage_height
    for fy in range(foliage_height):
        t = fy / foliage_height
        row_width = int((1 - t) * foliage_height // 2) * 2 + 1
        row_x = x - row_width // 2
        canvas.draw_line(row_x, foliage_start + fy, row_x + row_width - 1, foliage_start + fy, leaf_color)
```

## Beach / Coast

```python
def draw_beach_bg(canvas, width, height, time='day'):
    """Draw a beach scene."""

    # Sky (upper third)
    sky_height = height // 3
    sky_palette = 'day_clear' if time == 'day' else 'sunset'
    draw_sky(canvas, width, height, sky_height, sky_palette)

    # Ocean (middle third)
    ocean_start = sky_height
    ocean_end = height * 2 // 3

    ocean_colors = {
        'day': [(40, 80, 140), (60, 110, 170), (80, 140, 195)],
        'sunset': [(60, 70, 100), (90, 100, 130), (120, 130, 160)],
    }[time]

    for y in range(ocean_start, ocean_end):
        t = (y - ocean_start) / (ocean_end - ocean_start)
        idx = min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, ocean_colors[idx])

    # Waves (white lines)
    wave_y = ocean_end - 3
    for wx in range(0, width, 8):
        canvas.draw_line(wx, wave_y, wx + 4, wave_y, (220, 235, 250))

    # Sand (lower third)
    sand = GROUND_PALETTES['sand']
    for y in range(ocean_end, height):
        t = (y - ocean_end) / (height - ocean_end)
        idx = min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, sand[['light', 'mid', 'dark'][idx]])

    # Beach foam line
    canvas.draw_line(0, ocean_end, width - 1, ocean_end, (250, 250, 255))
```

## Mountains

```python
def draw_mountain_bg(canvas, width, height, snow_level=0.3, time='day'):
    """Draw mountain background."""

    # Sky
    sky_height = height // 3
    draw_sky(canvas, width, height, sky_height, 'day_clear' if time == 'day' else 'sunset')

    # Ground
    ground = GROUND_PALETTES['grass']
    for y in range(height * 2 // 3, height):
        canvas.draw_line(0, y, width - 1, y, ground['mid'])

    # Mountain colors
    mountain_colors = [
        (100, 105, 120),  # Far/dark
        (130, 135, 150),  # Mid
        (160, 165, 180),  # Near/light
    ]
    snow = GROUND_PALETTES['snow']

    # Draw mountains (back to front)
    import random
    random.seed(123)

    # Far mountain
    _draw_mountain(canvas, width // 4, sky_height, width // 2, height // 2,
                  mountain_colors[0], snow['dark'], snow_level + 0.1)

    # Near mountain
    _draw_mountain(canvas, width * 3 // 4, sky_height + height // 6, width // 2, height * 2 // 5,
                  mountain_colors[2], snow['light'], snow_level)


def _draw_mountain(canvas, peak_x, peak_y, base_width, height, rock_color, snow_color, snow_ratio):
    """Draw a single mountain."""
    base_y = peak_y + height

    for y in range(peak_y, base_y):
        t = (y - peak_y) / height
        row_width = int(t * base_width)
        row_x = peak_x - row_width // 2

        # Snow above snow line
        if t < snow_ratio:
            color = snow_color
        else:
            color = rock_color

        canvas.draw_line(row_x, y, row_x + row_width, y, color)
```

## Simple Backgrounds

For quick backgrounds without complex scenes:

```python
def draw_gradient_bg(canvas, width, height, color_top, color_bottom):
    """Simple vertical gradient background."""
    for y in range(height):
        t = y / height
        color = _lerp_color(color_top, color_bottom, t)
        canvas.draw_line(0, y, width - 1, y, color)


def draw_solid_with_floor(canvas, width, height, wall_color, floor_color, floor_ratio=0.35):
    """Solid color wall with floor."""
    floor_y = int(height * (1 - floor_ratio))

    # Wall
    canvas.fill_rect(0, 0, width, floor_y, wall_color)

    # Floor
    canvas.fill_rect(0, floor_y, width, height - floor_y, floor_color)


# Preset simple backgrounds
SIMPLE_BACKGROUNDS = {
    'pink_sunset': {
        'top': (80, 60, 100),
        'bottom': (255, 180, 150),
    },
    'forest_green': {
        'top': (60, 80, 60),
        'bottom': (30, 50, 35),
    },
    'ocean_blue': {
        'top': (40, 60, 120),
        'bottom': (20, 100, 140),
    },
    'warm_interior': {
        'top': (120, 100, 85),
        'bottom': (80, 65, 55),
    },
    'cool_night': {
        'top': (20, 25, 45),
        'bottom': (40, 50, 70),
    },
}
```
