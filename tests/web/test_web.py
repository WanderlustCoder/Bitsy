"""Tests for web preview server."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from web.routes import (
    Route,
    parse_route,
    get_generator_info,
    validate_generator_params,
    GENERATORS,
    EFFECTS,
)
from web.templates import (
    render_index,
    render_gallery,
    render_error,
    render_base,
    render_generator_card,
)
from web.server import (
    generate_sprite,
    create_thumbnail,
    Gallery,
    GalleryEntry,
)


class TestRoutes:
    """Tests for URL routing."""

    def test_parse_index(self):
        """Test parsing index route."""
        route = parse_route('/')
        assert route.type == 'index'

    def test_parse_index_empty(self):
        """Test parsing empty path."""
        route = parse_route('')
        assert route.type == 'index'

    def test_parse_gallery(self):
        """Test parsing gallery route."""
        route = parse_route('/gallery')
        assert route.type == 'gallery'

    def test_parse_generate(self):
        """Test parsing generate route."""
        route = parse_route('/generate/structure')
        assert route.type == 'generate'
        assert route.generator == 'structure'

    def test_parse_generate_with_params(self):
        """Test parsing generate with parameters."""
        route = parse_route('/generate/structure?type=castle&seed=42')
        assert route.type == 'generate'
        assert route.generator == 'structure'
        assert 'structure_type' in route.params
        assert route.params['structure_type'] == 'castle'

    def test_parse_generate_with_display_options(self):
        """Test parsing display options."""
        route = parse_route('/generate/structure?zoom=8&grid=true')
        assert route.options['zoom'] == 8
        assert route.options['grid'] is True

    def test_parse_invalid_generator(self):
        """Test parsing invalid generator."""
        route = parse_route('/generate/invalid')
        assert route.type == 'error'
        assert 'Unknown generator' in route.error

    def test_parse_animate(self):
        """Test parsing animate route."""
        route = parse_route('/animate/walk')
        assert route.type == 'animate'
        assert route.generator == 'walk'

    def test_parse_unknown_path(self):
        """Test parsing unknown path."""
        route = parse_route('/unknown/path')
        assert route.type == 'error'

    def test_get_generator_info(self):
        """Test getting generator info."""
        info = get_generator_info()
        assert len(info) > 0

        # Check structure
        names = [g['name'] for g in info]
        assert 'structure' in names
        assert 'character' in names

    def test_validate_generator_params(self):
        """Test parameter validation."""
        params = {'seed': '123', 'type': 'castle'}
        validated = validate_generator_params('structure', params)
        assert validated['seed'] == 123
        assert validated['structure_type'] == 'castle'

    def test_validate_invalid_seed(self):
        """Test invalid seed handling."""
        params = {'seed': 'not_a_number'}
        validated = validate_generator_params('structure', params)
        assert 'seed' not in validated


class TestTemplates:
    """Tests for HTML templates."""

    def test_render_base(self):
        """Test base template rendering."""
        html = render_base('Test Title', '<p>Content</p>')
        assert '<!DOCTYPE html>' in html
        assert 'Test Title' in html
        assert '<p>Content</p>' in html

    def test_render_index(self):
        """Test index page rendering."""
        generators = get_generator_info()
        html = render_index(generators)
        assert 'Bitsy Preview' in html
        assert 'structure' in html.lower()
        assert 'character' in html.lower()

    def test_render_gallery_empty(self):
        """Test empty gallery rendering."""
        html = render_gallery([])
        assert 'Gallery' in html
        assert 'No generations' in html

    def test_render_gallery_with_entries(self):
        """Test gallery with entries."""
        entries = [
            {
                'generator': 'structure',
                'params': {'seed': 42},
                'thumbnail': 'data:image/png;base64,test',
                'url': '/generate/structure?seed=42',
            }
        ]
        html = render_gallery(entries)
        assert 'Gallery' in html
        assert 'structure' in html

    def test_render_error(self):
        """Test error page rendering."""
        html = render_error('Not Found', 'Page not found')
        assert 'Not Found' in html
        assert 'Page not found' in html

    def test_render_error_with_details(self):
        """Test error page with details."""
        html = render_error('Error', 'Something went wrong', 'Stack trace here')
        assert 'Stack trace here' in html

    def test_render_generator_card(self):
        """Test generator card rendering."""
        gen = {
            'name': 'test',
            'type': 'generator',
            'description': 'Test generator',
            'params': ['seed'],
            'styles': ['default'],
            'types': [],
        }
        html = render_generator_card(gen)
        assert 'test' in html
        assert 'Generate' in html


class TestServer:
    """Tests for server functionality."""

    def test_generate_structure(self):
        """Test structure generation."""
        canvas = generate_sprite('structure', {'structure_type': 'house', 'seed': 42})
        assert canvas is not None
        assert canvas.width > 0
        assert canvas.height > 0

    def test_generate_character(self):
        """Test character generation."""
        canvas = generate_sprite('character', {'style': 'chibi', 'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_creature(self):
        """Test creature generation."""
        canvas = generate_sprite('creature', {'creature_type': 'slime', 'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_item(self):
        """Test item generation."""
        canvas = generate_sprite('item', {'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_prop(self):
        """Test prop generation."""
        canvas = generate_sprite('prop', {'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_particle(self):
        """Test particle generation."""
        canvas = generate_sprite('particle', {'effect_type': 'spark', 'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_weather(self):
        """Test weather generation."""
        canvas = generate_sprite('weather', {'weather_type': 'rain', 'seed': 42})
        assert canvas is not None
        assert canvas.width > 0

    def test_generate_unknown(self):
        """Test unknown generator fallback."""
        canvas = generate_sprite('unknown', {'seed': 42})
        assert canvas is not None
        assert canvas.width == 32  # Placeholder size

    def test_generate_deterministic(self):
        """Test that same seed produces same result."""
        canvas1 = generate_sprite('structure', {'structure_type': 'house', 'seed': 12345})
        canvas2 = generate_sprite('structure', {'structure_type': 'house', 'seed': 12345})
        # Check a few pixels
        assert canvas1.get_pixel(0, 0) == canvas2.get_pixel(0, 0)
        assert canvas1.get_pixel(10, 10) == canvas2.get_pixel(10, 10)

    def test_create_thumbnail(self):
        """Test thumbnail creation."""
        from core import Canvas
        canvas = Canvas(32, 32)
        for y in range(32):
            for x in range(32):
                canvas.set_pixel(x, y, (255, 0, 0, 255))

        thumbnail = create_thumbnail(canvas)
        assert thumbnail.startswith('data:image/png;base64,')

    def test_create_thumbnail_large(self):
        """Test thumbnail scaling for large images."""
        from core import Canvas
        canvas = Canvas(256, 256)
        for y in range(256):
            for x in range(256):
                canvas.set_pixel(x, y, (0, 255, 0, 255))

        thumbnail = create_thumbnail(canvas, max_size=64)
        assert thumbnail.startswith('data:image/png;base64,')


class TestGallery:
    """Tests for gallery functionality."""

    def test_gallery_init(self):
        """Test gallery initialization."""
        gallery = Gallery(max_size=10)
        assert gallery.max_size == 10
        assert len(gallery.entries) == 0

    def test_gallery_add(self):
        """Test adding to gallery."""
        gallery = Gallery(max_size=10)
        entry = GalleryEntry(
            generator='test',
            params={'seed': 42},
            thumbnail='data:test',
            url='/test',
        )
        gallery.add(entry)
        assert len(gallery.entries) == 1

    def test_gallery_max_size(self):
        """Test gallery max size limit."""
        gallery = Gallery(max_size=3)

        for i in range(5):
            gallery.add(GalleryEntry(
                generator=f'test{i}',
                params={},
                thumbnail='',
                url='',
            ))

        assert len(gallery.entries) == 3
        # First entries should be removed
        assert gallery.entries[0].generator == 'test2'

    def test_gallery_get_all(self):
        """Test getting all entries."""
        gallery = Gallery()
        gallery.add(GalleryEntry(
            generator='test',
            params={'seed': 42},
            thumbnail='data:test',
            url='/test',
        ))

        entries = gallery.get_all()
        assert len(entries) == 1
        assert entries[0]['generator'] == 'test'
        assert entries[0]['params'] == {'seed': 42}

    def test_gallery_clear(self):
        """Test clearing gallery."""
        gallery = Gallery()
        gallery.add(GalleryEntry(
            generator='test',
            params={},
            thumbnail='',
            url='',
        ))
        gallery.clear()
        assert len(gallery.entries) == 0


class TestDisplayOptions:
    """Tests for display option parsing."""

    def test_zoom_option(self):
        """Test zoom option parsing."""
        route = parse_route('/generate/structure?zoom=8')
        assert route.options['zoom'] == 8

    def test_grid_option_true(self):
        """Test grid option true."""
        route = parse_route('/generate/structure?grid=true')
        assert route.options['grid'] is True

    def test_grid_option_false(self):
        """Test grid option false."""
        route = parse_route('/generate/structure?grid=false')
        assert route.options['grid'] is False

    def test_dark_option(self):
        """Test dark mode option."""
        route = parse_route('/generate/structure?dark=false')
        assert route.options['dark'] is False

    def test_default_options(self):
        """Test default option values."""
        route = parse_route('/generate/structure')
        assert route.options['zoom'] == 4
        assert route.options['grid'] is False
        assert route.options['dark'] is True
