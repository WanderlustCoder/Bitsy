# Bitsy Development Roadmap

This document outlines the development plan for Bitsy, a pure Python pixel art toolkit.

## Current Status

**Version:** 1.0.0 (Full-featured release)

The toolkit is complete with all planned features:
- Core rendering (PNG, canvas, palettes, colors)
- Animation (keyframes, easing, timelines, procedural, cycles)
- Rigging (skeletons, poses, interpolation)
- Generation (characters, creatures, items, props, environments, structures, scenes)
- Effects (particles, weather, trails, post-processing)
- Export (PNG, GIF, APNG, spritesheets, atlases, Aseprite, Spine)
- Quality tools (validators, analyzers, auto-shade)
- Character assembly (builder, parts, equipment, presets)
- Style transfer (extract, apply, batch processing)
- Editor tools (layers, transforms, selection, undo/redo)
- Asset pipeline (CLI, watch mode, incremental builds)
- Web preview server (browser-based generation)
- AI integration hooks (prompt interface, variation generation)

**All Phases Complete:** 1 ✓, 2 ✓, 3 ✓, 4 ✓

---

## Phase 1: Polish & Complete ✓

Focus on finishing partially-implemented features and improving usability.

### 1.1 Character Assembly System ✓
**Priority: HIGH**

Create a unified system to assemble characters from parts.

- [x] `CharacterBuilder` class for composing parts
- [x] Part attachment points and layering
- [x] Palette application across all parts
- [x] Style-aware scaling and proportions
- [x] Preset character templates (hero, villager, monster)

### 1.2 Equipment & Clothing ✓
**Priority: HIGH**

Extend parts system with equipment.

- [x] Armor parts (helmet, chest, legs, boots)
- [x] Weapon holding and attachment
- [x] Clothing layers (cape, robe, accessories)
- [x] Color customization per equipment piece
- [x] Equipment sets/presets

### 1.3 Style Transfer ✓
**Priority: MEDIUM**

Complete the style transfer system.

- [x] Extract style from reference sprite
- [x] Apply extracted style to new sprites
- [x] Palette extraction and mapping
- [x] Outline/shading style matching
- [x] Batch style application

### 1.4 Editor Toolchain ✓
**Priority: MEDIUM**

Verify and complete editor tools.

- [x] Layer compositing and blending
- [x] Transform operations (rotate, scale, skew)
- [x] Selection and masking
- [x] Undo/redo stack
- [x] Image import/conversion

---

## Phase 2: Advanced Generation ✓

Expand procedural generation capabilities.

### 2.1 Smarter Character Generation ✓
- [x] Body type variations (thin, muscular, stocky)
- [x] Age variations (child, adult, elderly)
- [x] Species/race templates (human, elf, orc, etc.)
- [x] Clothing style generation
- [x] Accessory randomization

### 2.2 Animation Generation ✓
- [x] Generate walk cycles from skeleton
- [x] Auto-generate idle animations
- [x] Attack animation templates
- [x] Hurt/death animation generation
- [x] Transition animations between states

### 2.3 Tileset Generation ✓
- [x] Complete terrain tileset generation
- [x] Interior tileset generation (floors, walls, furniture)
- [x] Dungeon tileset variations
- [x] Seamless texture generation
- [x] Tile variation systems (randomized details)

### 2.4 Scene Composition ✓
- [x] Layer-based scene building
- [x] Parallax background generation
- [x] Lighting and shadow casting
- [x] Time-of-day variations
- [x] Weather overlay integration

---

## Phase 3: Game-Ready Features ✓

Features for direct game integration.

### 3.1 Sprite Atlasing ✓
- [x] Automatic atlas optimization
- [x] Multi-resolution atlas generation
- [x] Atlas update/patching (add sprites without rebuild)
- [x] Engine-specific export (Unity, Godot, GameMaker)
- [x] Texture compression options

### 3.2 Animation Export ✓
- [x] Aseprite format export
- [x] Spine JSON export
- [x] Custom animation format with events
- [x] Animation preview player
- [x] Frame timing optimization

### 3.3 Asset Pipeline ✓
- [x] Watch mode for auto-regeneration
- [x] Asset manifest generation
- [x] Dependency tracking
- [x] Incremental builds
- [x] CLI tool for batch processing

### 3.4 Documentation & Examples ✓
- [x] API reference documentation
- [x] Tutorial series (beginner to advanced)
- [x] Gallery of generated examples
- [x] Recipe book (common patterns)
- [x] Video/GIF demos

---

## Phase 4: Extended Capabilities

Nice-to-have features for completeness.

### 4.1 Advanced Effects ✓
- [x] Shader-like post-processing
- [x] Glow and bloom effects
- [x] Color grading and LUTs
- [x] Displacement effects
- [x] Palette cycling animations

### 4.2 Import Capabilities ✓
- [x] Import existing sprites for editing
- [x] Aseprite file reading
- [x] Palette extraction from images
- [x] Sprite splitting and detection
- [x] Reference image tracing

### 4.3 AI Integration Hooks ✓
- [x] Prompt-to-sprite generation interface
- [x] Style description parsing
- [x] Variation generation from examples
- [x] Quality scoring and selection
- [x] Iterative refinement loops

### 4.4 Web/Interactive ✓
- [x] Browser-based preview server
- [x] Interactive parameter tuning
- [x] Real-time generation preview
- [x] Shareable generation configs
- [x] Gallery/showcase system

---

## Stretch Goals

Ideas for future consideration.

- **3D to 2D**: Generate pixel art from 3D models
- **Animation Retargeting** ✓: Apply animations across different skeletons
- **Procedural Sound** ✓: Generate 8-bit sound effects to match sprites
- **Mod Support** ✓: Plugin system for custom generators
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
| 0.3.0 | Complete | Character assembly, equipment, style transfer |
| 0.4.0 | Complete | Advanced generation, scene composition |
| 0.5.0 | Complete | Game-ready export, asset pipeline |
| 0.6.0 | Complete | Extended capabilities, web preview, AI hooks |
| 1.0.0 | Current | Full-featured release |

---

## Contributing

This project is developed by AI agents under human direction. To contribute:

1. Open an issue describing the feature/fix
2. The AI will implement based on requirements
3. All code changes include tests
4. Human reviews and approves changes

---

*Last updated: January 2025*
