# Bitsy

A pure Python pixel art and sprite generation toolkit with animation support.

## Features

- **Zero Dependencies** - Core functionality uses only Python standard library
- **Procedural Generation** - Create characters, sprites, and effects from templates
- **Animation System** - Keyframe-based animation with sprite sheet export
- **Style Presets** - Chibi, retro 8-bit, 16-bit, modern HD pixel art
- **Palette Management** - Custom palettes with hue shifting and dithering

## Installation

```bash
git clone https://github.com/yourusername/bitsy.git
cd bitsy
python -m bitsy.examples.hello_sprite
```

No pip install required - just clone and run!

## Quick Start

```python
from bitsy.core import Canvas, Palette
from bitsy.parts import Body, Head
from bitsy.export import save_spritesheet

# Create a character
char = Character(
    style="chibi",
    body=Body.MEDIUM,
    head=Head.ROUND,
    palette=Palette.FANTASY_HERO
)

# Generate idle animation
idle = char.animate("idle", frames=4)

# Export
save_spritesheet(idle, "hero_idle.png")
```

## Project Structure

```
bitsy/
├── core/           # PNG encoding, canvas, palettes, animation timing
├── rig/            # Skeleton system, poses, interpolation
├── parts/          # Body parts, heads, limbs, equipment
├── styles/         # Art style presets (chibi, retro, modern)
├── export/         # Sprite sheet and GIF/APNG export
├── characters/     # Character templates and presets
└── examples/       # Usage examples
```

## Core Concepts

### Canvas
The drawing surface with primitives (pixels, lines, shapes, fills).

### Palette
Color management with support for hue shifting, limited palettes, and dithering.

### Rig
A skeleton/joint system that allows posing characters and interpolating between poses.

### Parts
Modular body parts (heads, torsos, limbs) that can be combined to create characters.

### Styles
Proportion and rendering presets that define the art style.

## Examples

See the `examples/` directory for:
- Basic sprite generation
- Character creation
- Walk cycle animation
- Sprite sheet export
- Custom palettes

## Roadmap

- [x] Core PNG writer (no dependencies)
- [x] Basic canvas with drawing primitives
- [ ] Color palette system
- [ ] Character body templates
- [ ] Skeleton/rig system
- [ ] Pose library
- [ ] Animation keyframes
- [ ] Walk cycle generator
- [ ] Sprite sheet export
- [ ] GIF/APNG export
- [ ] Style presets (chibi, retro, modern)
- [ ] Equipment/clothing system
- [ ] Effects (projectiles, impacts)

## License

MIT License - See LICENSE file

## Credits

Created with assistance from Claude (Anthropic).
