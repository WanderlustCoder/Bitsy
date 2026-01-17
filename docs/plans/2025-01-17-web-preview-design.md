# Web Preview Server Design

## Overview

A simple, pure-Python HTTP server that provides browser-based previews of Bitsy's generators. Uses Python's built-in `http.server` module with no external dependencies.

## Architecture

### URL Structure

```
/                           → Landing page with generator links
/generate/<type>?params     → Generate and preview a sprite
/animate/<type>?params      → Generate and preview an animation
/gallery                    → Show recent generations (in-memory)
```

### Generator Types

**Sprites:**
- `character` - Character generation
- `creature` - Creature generation
- `item` - Item generation
- `prop` - Prop generation
- `structure` - Structure generation (castle, house, tower, etc.)

**Effects:**
- `particle` - Particle effects (spark, explosion, magic, etc.)
- `weather` - Weather overlays (rain, snow, fog)

**Animations:**
- `walk` - Walk cycle animation
- `idle` - Idle animation
- `attack` - Attack animation

### Common Parameters

All generators accept:
- `seed` (int) - Random seed for reproducibility
- `style` (string) - Visual style (chibi, tiny, standard)
- `palette` (string) - Color palette name
- `zoom` (int) - Preview zoom level (1, 2, 4, 8)
- `grid` (bool) - Show pixel grid overlay

## Components

### web/server.py (~300 lines)

Main HTTP server using `http.server.HTTPServer` and custom `BaseHTTPRequestHandler`.

```python
class PreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = parse_route(self.path)
        if route.type == 'index':
            self.send_html(render_index())
        elif route.type == 'generate':
            canvas = generate(route.generator, route.params)
            html = generate_preview_html(canvas, **route.options)
            self.send_html(html)
        # ...
```

### web/templates.py (~150 lines)

HTML templates as Python f-strings. No template engine required.

```python
def render_index(generators: List[GeneratorInfo]) -> str:
    return f'''<!DOCTYPE html>
    <html>
    <head><title>Bitsy Preview</title></head>
    <body>
        <h1>Bitsy Preview Server</h1>
        {render_generator_list(generators)}
    </body>
    </html>'''
```

### web/routes.py (~100 lines)

URL parsing and parameter validation.

```python
@dataclass
class Route:
    type: str  # 'index', 'generate', 'animate', 'gallery'
    generator: Optional[str]
    params: Dict[str, Any]
    options: Dict[str, Any]

def parse_route(path: str) -> Route:
    # Parse URL and query string
    # Validate parameters
    # Return typed Route object
```

## Integration

### Generator Mapping

```python
GENERATORS = {
    'character': ('generators', 'generate_character'),
    'creature': ('generators', 'generate_creature'),
    'item': ('generators', 'generate_item'),
    'prop': ('generators', 'generate_prop'),
    'structure': ('generators', 'generate_structure'),
}

EFFECTS = {
    'particle': ('effects', 'create_effect'),
    'weather': ('effects', 'create_rain_overlay'),
}
```

### Preview Integration

Uses existing preview module:
- `preview.html_preview.generate_preview_html()` for static images
- `preview.animation_preview.generate_animation_preview()` for animations

## Gallery

In-memory storage of recent generations:

```python
@dataclass
class GalleryEntry:
    generator: str
    params: Dict[str, Any]
    timestamp: float
    thumbnail: str  # Base64 data URI

class Gallery:
    def __init__(self, max_size: int = 20):
        self.entries: List[GalleryEntry] = []

    def add(self, entry: GalleryEntry):
        self.entries.append(entry)
        if len(self.entries) > self.max_size:
            self.entries.pop(0)
```

## Usage

### Python API

```python
from web import serve

# Start server
serve(port=8080)

# With options
serve(
    port=8080,
    host='0.0.0.0',  # Allow external connections
    debug=True,       # Show errors in browser
    gallery_size=50   # Keep more history
)
```

### Command Line

```bash
python -m web --port 8080
python -m web --port 8080 --debug
```

## Error Handling

- **404**: Unknown generator type → list valid types
- **400**: Invalid parameter → show parameter documentation
- **500**: Generation error → show error (debug mode) or generic message

## Security Considerations

- Server binds to localhost by default
- No file system writes (except optional temp files)
- No user input executed as code
- Query parameters are validated and typed

## Testing

- Unit tests for route parsing
- Unit tests for parameter validation
- Integration tests for each generator endpoint
- Test error handling for invalid inputs
