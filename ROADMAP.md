# Bitsy Development Roadmap

This document outlines the development plan for Bitsy, a pure Python pixel art toolkit.

## Current Status

**Version:** 0.2.0 (Post-foundation expansion)

The toolkit has a solid foundation with comprehensive systems for:
- Core rendering (PNG, canvas, palettes, colors)
- Animation (keyframes, easing, timelines, procedural, cycles)
- Rigging (skeletons, poses, interpolation)
- Generation (characters, creatures, items, props, environments, structures)
- Effects (particles, weather, trails)
- Export (PNG, GIF, APNG, spritesheets)
- Quality tools (validators, analyzers, auto-shade)

**Test Coverage:** 537 tests passing

---

## Phase 1: Polish & Complete (Next)

Focus on finishing partially-implemented features and improving usability.

### 1.1 Character Assembly System
**Priority: HIGH**

Create a unified system to assemble characters from parts.

- [ ] `CharacterBuilder` class for composing parts
- [ ] Part attachment points and layering
- [ ] Palette application across all parts
- [ ] Style-aware scaling and proportions
- [ ] Preset character templates (hero, villager, monster)

### 1.2 Equipment & Clothing
**Priority: HIGH**

Extend parts system with equipment.

- [ ] Armor parts (helmet, chest, legs, boots)
- [ ] Weapon holding and attachment
- [ ] Clothing layers (cape, robe, accessories)
- [ ] Color customization per equipment piece
- [ ] Equipment sets/presets

### 1.3 Style Transfer
**Priority: MEDIUM**

Complete the style transfer system.

- [ ] Extract style from reference sprite
- [ ] Apply extracted style to new sprites
- [ ] Palette extraction and mapping
- [ ] Outline/shading style matching
- [ ] Batch style application

### 1.4 Editor Toolchain
**Priority: MEDIUM**

Verify and complete editor tools.

- [ ] Layer compositing and blending
- [ ] Transform operations (rotate, scale, skew)
- [ ] Selection and masking
- [ ] Undo/redo stack
- [ ] Image import/conversion

---

## Phase 2: Advanced Generation

Expand procedural generation capabilities.

### 2.1 Smarter Character Generation
- [ ] Body type variations (thin, muscular, stocky)
- [ ] Age variations (child, adult, elderly)
- [ ] Species/race templates (human, elf, orc, etc.)
- [ ] Clothing style generation
- [ ] Accessory randomization

### 2.2 Animation Generation
- [ ] Generate walk cycles from skeleton
- [ ] Auto-generate idle animations
- [ ] Attack animation templates
- [ ] Hurt/death animation generation
- [ ] Transition animations between states

### 2.3 Tileset Generation
- [ ] Complete terrain tileset generation
- [ ] Interior tileset generation (floors, walls, furniture)
- [ ] Dungeon tileset variations
- [ ] Seamless texture generation
- [ ] Tile variation systems (randomized details)

### 2.4 Scene Composition
- [ ] Layer-based scene building
- [ ] Parallax background generation
- [ ] Lighting and shadow casting
- [ ] Time-of-day variations
- [ ] Weather overlay integration

---

## Phase 3: Game-Ready Features

Features for direct game integration.

### 3.1 Sprite Atlasing
- [ ] Automatic atlas optimization
- [ ] Multi-resolution atlas generation
- [ ] Atlas update/patching (add sprites without rebuild)
- [ ] Engine-specific export (Unity, Godot, GameMaker)
- [ ] Texture compression options

### 3.2 Animation Export
- [ ] Aseprite format export
- [ ] Spine JSON export
- [ ] Custom animation format with events
- [ ] Animation preview player
- [ ] Frame timing optimization

### 3.3 Asset Pipeline
- [ ] Watch mode for auto-regeneration
- [ ] Asset manifest generation
- [ ] Dependency tracking
- [ ] Incremental builds
- [ ] CLI tool for batch processing

### 3.4 Documentation & Examples
- [ ] API reference documentation
- [ ] Tutorial series (beginner to advanced)
- [ ] Gallery of generated examples
- [ ] Recipe book (common patterns)
- [ ] Video/GIF demos

---

## Phase 4: Extended Capabilities

Nice-to-have features for completeness.

### 4.1 Advanced Effects
- [ ] Shader-like post-processing
- [ ] Glow and bloom effects
- [ ] Color grading and LUTs
- [ ] Displacement effects
- [ ] Palette cycling animations

### 4.2 Import Capabilities
- [ ] Import existing sprites for editing
- [ ] Aseprite file reading
- [ ] Palette extraction from images
- [ ] Sprite splitting and detection
- [ ] Reference image tracing

### 4.3 AI Integration Hooks
- [ ] Prompt-to-sprite generation interface
- [ ] Style description parsing
- [ ] Variation generation from examples
- [ ] Quality scoring and selection
- [ ] Iterative refinement loops

### 4.4 Web/Interactive
- [ ] Browser-based preview server
- [ ] Interactive parameter tuning
- [ ] Real-time generation preview
- [ ] Shareable generation configs
- [ ] Gallery/showcase system

---

## Stretch Goals

Ideas for future consideration.

- **3D to 2D**: Generate pixel art from 3D models
- **Animation Retargeting**: Apply animations across different skeletons
- **Procedural Sound**: Generate 8-bit sound effects to match sprites
- **Mod Support**: Plugin system for custom generators
- **Collaborative**: Multi-user generation sessions
- **Machine Learning**: Train on generated sprites for style learning

---

## Development Principles

### Code Quality
- All features must have tests
- Tests run before any commit
- Deterministic output (same seed = same result)
- No external dependencies for core functionality

### Design Philosophy
- Simple API over flexible API
- Sensible defaults, optional customization
- Composition over inheritance
- Pure functions where possible

### AI Development
- Human provides requirements and feedback
- AI implements all code including tests
- AI maintains documentation
- AI ensures backwards compatibility

---

## Version History

| Version | Status | Highlights |
|---------|--------|------------|
| 0.1.0 | Complete | Core foundation (PNG, canvas, palette) |
| 0.2.0 | Complete | Generation, effects, animation, export |
| 0.3.0 | Planned | Character assembly, equipment, style transfer |
| 0.4.0 | Planned | Advanced generation, scene composition |
| 0.5.0 | Planned | Game-ready export, asset pipeline |
| 1.0.0 | Future | Full-featured release |

---

## Contributing

This project is developed by AI agents under human direction. To contribute:

1. Open an issue describing the feature/fix
2. The AI will implement based on requirements
3. All code changes include tests
4. Human reviews and approves changes

---

*Last updated: January 2025*
