"""HTML templates for the preview server."""

from typing import List, Dict, Any, Optional
import html
import time


# Base CSS styles
BASE_CSS = '''
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #1a1a2e;
    color: #eee;
    min-height: 100vh;
    padding: 20px;
}
a { color: #4da6ff; text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { color: #fff; margin-bottom: 10px; }
h2 { color: #aaa; font-size: 1.2em; margin: 20px 0 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
.container { max-width: 1200px; margin: 0 auto; }
.header { margin-bottom: 30px; }
.header p { color: #888; }

/* Generator cards */
.generators { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.card {
    background: #16213e;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #333;
    transition: border-color 0.2s;
}
.card:hover { border-color: #4da6ff; }
.card h3 { color: #fff; margin-bottom: 10px; text-transform: capitalize; }
.card p { color: #888; font-size: 0.9em; margin-bottom: 15px; }
.card .actions { display: flex; gap: 10px; flex-wrap: wrap; }
.btn {
    display: inline-block;
    padding: 8px 16px;
    background: #4da6ff;
    color: #fff;
    border-radius: 4px;
    font-size: 0.9em;
    transition: background 0.2s;
}
.btn:hover { background: #3a8fd9; text-decoration: none; }
.btn.secondary { background: #333; }
.btn.secondary:hover { background: #444; }

/* Form styles */
.form-section {
    background: #16213e;
    border-radius: 8px;
    padding: 20px;
    margin-top: 15px;
    display: none;
}
.form-section.active { display: block; }
.form-row { margin-bottom: 15px; }
.form-row label { display: block; color: #aaa; font-size: 0.85em; margin-bottom: 5px; }
.form-row select, .form-row input {
    width: 100%;
    padding: 8px 12px;
    background: #0f0f23;
    border: 1px solid #333;
    border-radius: 4px;
    color: #fff;
    font-size: 0.95em;
}
.form-row select:focus, .form-row input:focus {
    outline: none;
    border-color: #4da6ff;
}
.form-actions { display: flex; gap: 10px; margin-top: 20px; }

/* Gallery */
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }
.gallery-item {
    background: #16213e;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
}
.gallery-item img {
    image-rendering: pixelated;
    max-width: 100%;
    height: auto;
}
.gallery-item .info { font-size: 0.8em; color: #888; margin-top: 8px; }

/* Error page */
.error { background: #3e1616; border: 1px solid #ff4d4d; border-radius: 8px; padding: 20px; }
.error h2 { color: #ff4d4d; border: none; }
.error pre { background: #1a1a2e; padding: 15px; border-radius: 4px; margin-top: 15px; overflow-x: auto; }
'''

# JavaScript for interactivity
BASE_JS = '''
function randomSeed() {
    return Math.floor(Math.random() * 1000000);
}

function toggleForm(cardId) {
    const form = document.getElementById(cardId + '-form');
    if (form) {
        form.classList.toggle('active');
    }
}

function setRandomSeed(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = randomSeed();
    }
}

function generateUrl(base, formId) {
    const form = document.getElementById(formId);
    if (!form) return base;

    const params = new URLSearchParams();
    const inputs = form.querySelectorAll('select, input');
    inputs.forEach(input => {
        if (input.value && input.name) {
            params.set(input.name, input.value);
        }
    });

    return base + '?' + params.toString();
}

function submitForm(base, formId) {
    window.location.href = generateUrl(base, formId);
}
'''


def render_base(title: str, content: str, extra_css: str = '', extra_js: str = '') -> str:
    """Render base HTML template."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>{BASE_CSS}{extra_css}</style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <script>{BASE_JS}{extra_js}</script>
</body>
</html>'''


def render_index(generators: List[Dict[str, Any]]) -> str:
    """Render the index page with all generators."""
    # Group by type
    sprite_gens = [g for g in generators if g['type'] == 'generator']
    effect_gens = [g for g in generators if g['type'] == 'effect']
    anim_gens = [g for g in generators if g['type'] == 'animation']

    content = '''
    <div class="header">
        <h1>Bitsy Preview Server</h1>
        <p>Generate and preview pixel art sprites in your browser</p>
    </div>
    '''

    # Sprite generators
    content += '<h2>Sprite Generators</h2><div class="generators">'
    for gen in sprite_gens:
        content += render_generator_card(gen)
    content += '</div>'

    # Effect generators
    if effect_gens:
        content += '<h2>Effects</h2><div class="generators">'
        for gen in effect_gens:
            content += render_generator_card(gen)
        content += '</div>'

    # Animations
    if anim_gens:
        content += '<h2>Animations</h2><div class="generators">'
        for gen in anim_gens:
            content += render_generator_card(gen, animate=True)
        content += '</div>'

    # Gallery link
    content += '''
    <h2>Recent</h2>
    <p><a href="/gallery">View Gallery</a> - See your recent generations</p>
    '''

    return render_base('Bitsy Preview', content)


def render_generator_card(gen: Dict[str, Any], animate: bool = False) -> str:
    """Render a generator card."""
    name = gen['name']
    desc = html.escape(gen['description'])
    base_url = f"/{'animate' if animate else 'generate'}/{name}"
    card_id = f"{name}-card"
    form_id = f"{name}-form"

    # Quick generate URL with random seed
    quick_url = f"{base_url}?seed={int(time.time() * 1000) % 1000000}"

    card = f'''
    <div class="card" id="{card_id}">
        <h3>{name}</h3>
        <p>{desc}</p>
        <div class="actions">
            <a href="{quick_url}" class="btn">Generate</a>
            <button class="btn secondary" onclick="toggleForm('{name}')">Options</button>
        </div>
        {render_generator_form(gen, form_id, base_url)}
    </div>
    '''
    return card


def render_generator_form(gen: Dict[str, Any], form_id: str, base_url: str) -> str:
    """Render the options form for a generator."""
    name = gen['name']

    form = f'<div class="form-section" id="{form_id}">'

    # Seed input
    form += f'''
    <div class="form-row">
        <label>Seed</label>
        <div style="display: flex; gap: 10px;">
            <input type="number" name="seed" id="{name}-seed" placeholder="Random" style="flex: 1;">
            <button type="button" class="btn secondary" onclick="setRandomSeed('{name}-seed')">Random</button>
        </div>
    </div>
    '''

    # Style dropdown (if applicable)
    if gen.get('styles'):
        options = ''.join(f'<option value="{s}">{s}</option>' for s in gen['styles'])
        form += f'''
        <div class="form-row">
            <label>Style</label>
            <select name="style">{options}</select>
        </div>
        '''

    # Type dropdown (for structures, effects)
    if gen.get('types'):
        options = ''.join(f'<option value="{t}">{t}</option>' for t in gen['types'])
        form += f'''
        <div class="form-row">
            <label>Type</label>
            <select name="type">{options}</select>
        </div>
        '''

    # Display options
    form += '''
    <div class="form-row">
        <label>Zoom</label>
        <select name="zoom">
            <option value="1">1x</option>
            <option value="2">2x</option>
            <option value="4" selected>4x</option>
            <option value="8">8x</option>
        </select>
    </div>
    '''

    # Submit button
    form += f'''
    <div class="form-actions">
        <button type="button" class="btn" onclick="submitForm('{base_url}', '{form_id}')">Generate</button>
    </div>
    '''

    form += '</div>'
    return form


def render_gallery(entries: List[Dict[str, Any]]) -> str:
    """Render the gallery page."""
    if not entries:
        content = '''
        <div class="header">
            <h1>Gallery</h1>
            <p>No generations yet. <a href="/">Start generating!</a></p>
        </div>
        '''
    else:
        items = ''
        for entry in reversed(entries):  # Most recent first
            gen = html.escape(entry.get('generator', 'unknown'))
            thumb = entry.get('thumbnail', '')
            url = entry.get('url', '/')
            items += f'''
            <div class="gallery-item">
                <a href="{html.escape(url)}"><img src="{thumb}" alt="{gen}"></a>
                <div class="info">{gen}</div>
            </div>
            '''

        content = f'''
        <div class="header">
            <h1>Gallery</h1>
            <p><a href="/">&larr; Back to generators</a></p>
        </div>
        <div class="gallery">{items}</div>
        '''

    return render_base('Gallery - Bitsy Preview', content)


def render_error(title: str, message: str, details: Optional[str] = None) -> str:
    """Render an error page."""
    content = f'''
    <div class="header">
        <h1>Bitsy Preview</h1>
        <p><a href="/">&larr; Back to generators</a></p>
    </div>
    <div class="error">
        <h2>{html.escape(title)}</h2>
        <p>{html.escape(message)}</p>
        {f'<pre>{html.escape(details)}</pre>' if details else ''}
    </div>
    '''
    return render_base(f'Error - {title}', content)


def render_generation_page(
    generator: str,
    params: Dict[str, Any],
    preview_html: str,
    regenerate_url: str
) -> str:
    """Render a page showing generated content with navigation."""
    param_str = ', '.join(f'{k}={v}' for k, v in params.items()) if params else 'defaults'

    # Add navigation header to the preview HTML
    nav_css = '''
    .nav-bar {
        background: #16213e;
        padding: 15px 20px;
        margin: -20px -20px 20px -20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
    }
    .nav-bar a { margin-right: 15px; }
    .nav-bar .info { color: #888; font-size: 0.9em; }
    '''

    nav_html = f'''
    <div class="nav-bar">
        <div>
            <a href="/">&larr; Back</a>
            <a href="{html.escape(regenerate_url)}">Regenerate</a>
            <a href="{html.escape(regenerate_url)}&seed={int(time.time() * 1000) % 1000000}">New Seed</a>
        </div>
        <div class="info">{html.escape(generator)}: {html.escape(param_str)}</div>
    </div>
    '''

    # Inject navigation into the preview HTML
    if '<body>' in preview_html:
        preview_html = preview_html.replace(
            '<body>',
            f'<body><style>{nav_css}</style>{nav_html}'
        )

    return preview_html
