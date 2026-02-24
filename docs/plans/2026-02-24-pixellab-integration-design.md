# PixelLab Integration Design

## Overview

Bitsy is a shared art asset repository for multiple game projects. Art is generated via PixelLab's API v2 and stored here. A thin Python client wraps the API for scripting.

## Directory Structure

```
bitsy/
├── headwaters/
│   ├── characters/
│   ├── animations/
│   ├── tilesets/
│   └── map-objects/
├── keyboard-defense/
│   ├── characters/
│   ├── animations/
│   ├── tilesets/
│   └── map-objects/
├── pixellab/
│   ├── __init__.py          # PixelLabClient class
│   └── config.py            # API key loading (env var + .env fallback)
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

Each asset gets a PNG + JSON sidecar for reproducibility:
```
headwaters/characters/hero.png
headwaters/characters/hero.json    # {prompt, seed, endpoint, timestamp, image_size, ...}
```

Sub-batches use nested folders: `headwaters/characters/town-npcs/blacksmith.png`

## Python Client

Single `PixelLabClient` class wrapping PixelLab API v2 (`https://api.pixellab.ai/v2`).

### Methods

- `generate_image(description, size, **opts)` - `/generate-image-v2`
- `create_character(description, size, directions=4, **opts)` - 4 or 8 direction characters
- `animate_character(character_id, animation, **opts)` - animate existing character
- `create_tileset(lower, upper, tile_size=32, **opts)` - Wang tileset (async, polls until done)
- `create_isometric_tile(description, size, **opts)` - single isometric tile (async)
- `create_map_object(description, size, **opts)` - map objects with transparency
- `edit_image(image_path, description, **opts)` - edit existing asset
- `get_balance()` - check remaining credits

### Behavior

- All generation methods return `(image_bytes, metadata_dict)`
- Optional `save_to` parameter writes PNG + JSON sidecar
- `seed` parameter for reproducibility (defaults to random)
- Async endpoints polled internally, return when complete

### Config

API key resolution priority: explicit arg > `PIXELLAB_API_KEY` env var > `.env` file.

## Out of Scope

- No CLI tool
- No asset pipeline or auto-sync
- No image processing or post-processing
