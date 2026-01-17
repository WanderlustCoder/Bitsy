"""
Bitsy Web - Browser-based preview server.

This module provides a simple HTTP server for previewing Bitsy generations
in a web browser. No external dependencies required.

Example usage:

    # Start server programmatically
    from web import serve

    serve(port=8080)

    # Or with options
    serve(
        port=8080,
        host='0.0.0.0',  # Allow external connections
        debug=True,       # Show errors in browser
        gallery_size=50   # Keep more history
    )

Command line usage:

    python -m web --port 8080
    python -m web --port 8080 --debug

Then open http://localhost:8080/ in your browser.
"""

from .server import serve, ServerConfig, Gallery, GalleryEntry
from .routes import Route, parse_route, get_generator_info, GENERATORS, EFFECTS

__all__ = [
    'serve',
    'ServerConfig',
    'Gallery',
    'GalleryEntry',
    'Route',
    'parse_route',
    'get_generator_info',
    'GENERATORS',
    'EFFECTS',
]
