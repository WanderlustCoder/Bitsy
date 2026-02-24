# Bitsy

Shared art asset repository. Art is generated via [PixelLab](https://www.pixellab.ai/) and stored here for use across multiple projects.

## Projects

- `headwaters/` - Headwaters game assets
- `keyboard-defense/` - Keyboard Defense game assets

Each project has subdirectories: `characters/`, `animations/`, `tilesets/`, `map-objects/`.

## Python Client

```python
from pixellab import PixelLabClient

client = PixelLabClient()  # reads PIXELLAB_API_KEY from env or .env

# Generate a character with 4 directions
img, meta = client.create_character(
    "a knight in silver armor",
    width=64, height=64,
    save_to="headwaters/characters/knight.png",
)

# Generate a tileset
img, meta = client.create_tileset(
    lower_description="grass field",
    upper_description="dirt path",
    save_to="headwaters/tilesets/grass-dirt.png",
)

# Check balance
print(client.get_balance())
```

## Setup

1. Copy `.env.example` to `.env` and add your PixelLab API key
2. Or set `PIXELLAB_API_KEY` environment variable
