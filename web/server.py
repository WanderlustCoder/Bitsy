"""HTTP server for Bitsy preview."""

from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import random
import traceback
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.routes import parse_route, get_generator_info, GENERATORS, EFFECTS
from web.templates import (
    render_index,
    render_gallery,
    render_error,
    render_generation_page,
)

from core import Canvas
from preview.html_preview import generate_preview_html


@dataclass
class GalleryEntry:
    """A gallery entry."""
    generator: str
    params: Dict[str, Any]
    thumbnail: str
    url: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = 'localhost'
    port: int = 8080
    debug: bool = False
    gallery_size: int = 20


class Gallery:
    """In-memory gallery storage."""

    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.entries: List[GalleryEntry] = []

    def add(self, entry: GalleryEntry):
        """Add an entry to the gallery."""
        self.entries.append(entry)
        if len(self.entries) > self.max_size:
            self.entries.pop(0)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all entries as dictionaries."""
        return [
            {
                'generator': e.generator,
                'params': e.params,
                'thumbnail': e.thumbnail,
                'url': e.url,
                'timestamp': e.timestamp,
            }
            for e in self.entries
        ]

    def clear(self):
        """Clear all entries."""
        self.entries.clear()


# Global gallery instance
_gallery = Gallery()
_config = ServerConfig()


def generate_sprite(generator: str, params: Dict[str, Any]) -> Canvas:
    """Generate a sprite using the specified generator.

    Args:
        generator: Generator name
        params: Generation parameters

    Returns:
        Generated Canvas
    """
    seed = params.get('seed', random.randint(0, 999999))

    if generator == 'structure':
        from generators import StructureGenerator
        structure_type = params.get('structure_type', 'castle')
        gen = StructureGenerator(seed=seed)
        # Map structure type to method
        if structure_type in ('house', 'cottage', 'cabin', 'villa'):
            return gen.generate_house(style=structure_type if structure_type != 'house' else 'cottage')
        elif structure_type == 'tower':
            return gen.generate_castle_tower()
        elif structure_type == 'wall':
            return gen.generate_castle_wall()
        else:
            # Default to house
            return gen.generate_house()

    elif generator == 'character':
        from generators import CharacterGenerator
        style = params.get('style', 'chibi')
        gen = CharacterGenerator(seed=seed)
        gen.set_style(style)
        gen.randomize()
        return gen.render()

    elif generator == 'creature':
        from generators import CreatureGenerator
        import random as rand_module
        rand_module.seed(seed)
        creature_types = ['slime', 'ghost', 'skeleton', 'zombie', 'wolf', 'bat', 'spider']
        creature_type = params.get('creature_type', rand_module.choice(creature_types))
        gen = CreatureGenerator(seed=seed)
        return gen.generate(creature_type)

    elif generator == 'item':
        from generators.item import generate_item, ITEM_GENERATORS
        import random as rand_module
        rand_module.seed(seed)
        item_type = params.get('item_type', rand_module.choice(list(ITEM_GENERATORS.keys())))
        return generate_item(item_type, seed=seed)

    elif generator == 'prop':
        from generators.prop import generate_prop, list_prop_types
        import random as rand_module
        rand_module.seed(seed)
        prop_types = list_prop_types()
        prop_type = params.get('prop_type', rand_module.choice(prop_types))
        return generate_prop(prop_type, seed=seed)

    elif generator == 'particle':
        from effects import create_effect
        effect_type = params.get('effect_type', 'spark')
        emitter = create_effect(effect_type)
        # Create a frame
        canvas = Canvas(64, 64)
        emitter.burst()
        for _ in range(10):
            emitter.update(0.05)
        emitter.render(canvas)
        return canvas

    elif generator == 'weather':
        from effects import create_rain_overlay, create_snow_overlay, create_fog_overlay
        weather_type = params.get('weather_type', 'rain')
        if weather_type == 'rain':
            return create_rain_overlay(64, 64, seed=seed)
        elif weather_type == 'snow':
            return create_snow_overlay(64, 64, seed=seed)
        else:
            return create_fog_overlay(64, 64, seed=seed)

    else:
        # Fallback: create a placeholder
        canvas = Canvas(32, 32)
        for y in range(32):
            for x in range(32):
                if (x + y) % 2 == 0:
                    canvas.set_pixel(x, y, (100, 100, 100, 255))
                else:
                    canvas.set_pixel(x, y, (50, 50, 50, 255))
        return canvas


def create_thumbnail(canvas: Canvas, max_size: int = 64) -> str:
    """Create a thumbnail data URI from a canvas."""
    from core.png_writer import create_png
    import base64

    # Scale down if needed
    scale = min(max_size / canvas.width, max_size / canvas.height, 1.0)
    if scale < 1.0:
        new_w = int(canvas.width * scale)
        new_h = int(canvas.height * scale)
        thumb = Canvas(new_w, new_h)
        for y in range(new_h):
            for x in range(new_w):
                src_x = int(x / scale)
                src_y = int(y / scale)
                thumb.set_pixel(x, y, canvas.get_pixel(src_x, src_y))
    else:
        thumb = canvas

    png_bytes = create_png(thumb.width, thumb.height, thumb.pixels)
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return f'data:image/png;base64,{b64}'


class PreviewHandler(BaseHTTPRequestHandler):
    """HTTP request handler for preview server."""

    def log_message(self, format, *args):
        """Custom log formatting."""
        if _config.debug:
            print(f"[{self.log_date_time_string()}] {format % args}")

    def send_html(self, html: str, status: int = 200):
        """Send an HTML response."""
        content = html.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        """Handle GET requests."""
        try:
            route = parse_route(self.path)

            if route.type == 'index':
                self.handle_index()
            elif route.type == 'generate':
                self.handle_generate(route)
            elif route.type == 'animate':
                self.handle_animate(route)
            elif route.type == 'gallery':
                self.handle_gallery()
            elif route.type == 'static':
                self.handle_static(route)
            elif route.type == 'error':
                self.send_html(render_error('Invalid Request', route.error or 'Unknown error'), 400)
            else:
                self.send_html(render_error('Not Found', f'Unknown route type: {route.type}'), 404)

        except Exception as e:
            if _config.debug:
                details = traceback.format_exc()
                self.send_html(render_error('Server Error', str(e), details), 500)
            else:
                self.send_html(render_error('Server Error', 'An error occurred'), 500)

    def handle_index(self):
        """Handle index page request."""
        generators = get_generator_info()
        html = render_index(generators)
        self.send_html(html)

    def handle_generate(self, route):
        """Handle generation request."""
        generator = route.generator
        params = route.params
        options = route.options

        # Generate the sprite
        canvas = generate_sprite(generator, params)

        # Generate preview HTML
        zoom = options.get('zoom', 4)
        show_grid = options.get('grid', False)
        dark_mode = options.get('dark', True)

        preview_html = generate_preview_html(
            canvas,
            title=f"{generator.title()} Preview",
            zoom=zoom,
            show_grid=show_grid,
            dark_mode=dark_mode,
        )

        # Build regenerate URL
        param_parts = [f"{k}={v}" for k, v in params.items()]
        param_parts.extend([f"{k}={v}" for k, v in options.items()])
        regen_url = f"/generate/{generator}?{'&'.join(param_parts)}" if param_parts else f"/generate/{generator}"

        # Wrap with navigation
        html = render_generation_page(generator, params, preview_html, regen_url)

        # Add to gallery
        thumbnail = create_thumbnail(canvas)
        _gallery.add(GalleryEntry(
            generator=generator,
            params=params,
            thumbnail=thumbnail,
            url=regen_url,
        ))

        self.send_html(html)

    def handle_animate(self, route):
        """Handle animation request."""
        # For now, generate a single frame and show it
        # Full animation support would require generating multiple frames
        generator = route.generator
        params = route.params

        # Generate a placeholder for now
        canvas = Canvas(32, 32)
        canvas.clear((50, 50, 80, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                canvas.set_pixel(x, y, (100, 150, 200, 255))

        preview_html = generate_preview_html(
            canvas,
            title=f"{generator.title()} Animation",
            zoom=4,
        )

        html = render_generation_page(generator, params, preview_html, f"/animate/{generator}")
        self.send_html(html)

    def handle_gallery(self):
        """Handle gallery page request."""
        entries = _gallery.get_all()
        html = render_gallery(entries)
        self.send_html(html)

    def handle_static(self, route):
        """Handle static file request."""
        filename = route.params.get('file', '')

        if filename == 'favicon.ico':
            # Return a simple 1x1 transparent PNG
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            # Minimal ICO file
            self.wfile.write(bytes([
                0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 24, 0,
                30, 0, 0, 0, 22, 0, 0, 0, 40, 0, 0, 0, 1, 0,
                0, 0, 2, 0, 0, 0, 1, 0, 24, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]))
        else:
            self.send_html(render_error('Not Found', f'Static file not found: {filename}'), 404)


def serve(
    port: int = 8080,
    host: str = 'localhost',
    debug: bool = False,
    gallery_size: int = 20,
):
    """Start the preview server.

    Args:
        port: Port to listen on
        host: Host to bind to
        debug: Enable debug mode (show errors)
        gallery_size: Maximum gallery entries to keep
    """
    global _config, _gallery

    _config = ServerConfig(
        host=host,
        port=port,
        debug=debug,
        gallery_size=gallery_size,
    )
    _gallery = Gallery(max_size=gallery_size)

    server_address = (host, port)
    httpd = HTTPServer(server_address, PreviewHandler)

    print(f"Bitsy Preview Server")
    print(f"====================")
    print(f"Running at: http://{host}:{port}/")
    print(f"Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"Press Ctrl+C to stop")
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Bitsy Preview Server')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Port (default: 8080)')
    parser.add_argument('--host', '-H', type=str, default='localhost', help='Host (default: localhost)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--gallery-size', '-g', type=int, default=20, help='Gallery size (default: 20)')

    args = parser.parse_args()

    serve(
        port=args.port,
        host=args.host,
        debug=args.debug,
        gallery_size=args.gallery_size,
    )


if __name__ == '__main__':
    main()
