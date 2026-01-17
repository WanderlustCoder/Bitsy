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

### Core Foundation
- [x] Core PNG writer (no dependencies)
- [x] Basic canvas with drawing primitives
- [x] Color palette system with HSV operations
- [x] Color operations (blend modes, dithering, interpolation)

### Animation System
- [x] Animation keyframes and timing
- [x] 23 easing functions
- [x] Track-based timeline system
- [x] Procedural animations (breathing, bobbing, blinking)
- [x] Pre-built cycles (walk, run, attack, jump)
- [x] Animation blending and state machines

### Rigging & Parts
- [x] Skeleton/rig system with bone hierarchies
- [x] Pose library with interpolation
- [x] Body part templates (heads, bodies, hair, eyes)
- [ ] Equipment/armor parts system

### Generation
- [x] Character generator
- [x] Creature generator (slime, beast, undead, elemental)
- [x] Item generator (weapons, potions, keys)
- [x] Prop generator (furniture, vegetation, chests)
- [x] Environment generator (sky, terrain, weather)
- [x] Structure generator (houses, castles, dungeons)
- [ ] Character assembly from parts

### Effects & Visual
- [x] Particle system with presets
- [x] Weather effects (rain, snow)
- [x] Motion trails and smear frames
- [x] Screen effects

### Export
- [x] Sprite sheet export with metadata
- [x] GIF export with optimization
- [x] APNG export
- [x] Sprite atlas with bin packing

### Tools & Quality
- [x] Style presets (chibi, retro, modern)
- [x] UI components (fonts, icons, 9-patch)
- [x] Tile system with autotiling
- [x] Quality validators and analyzers
- [x] Auto-shading and color harmony
- [ ] Style transfer between sprites
- [ ] Full editor toolchain

See [ROADMAP.md](ROADMAP.md) for detailed development plan.

See [DEVELOPMENT.md](DEVELOPMENT.md) for the dual-agent development workflow.

## License

MIT License - See LICENSE file

## Credits

Developed by AI agents under human direction:
- **Claude** (Anthropic) - Orchestration and development
- **Codex** (OpenAI) - Parallel development via delegation
