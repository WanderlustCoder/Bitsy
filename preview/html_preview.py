"""
HTML Preview - Generate HTML preview pages for pixel art.

Features:
- Multiple zoom levels (1x, 2x, 4x, 8x)
- Data URI embedding (no external files)
- Responsive layout
- Dark/light background toggle
- Grid overlay option
"""

import sys
import os
import base64
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


@dataclass
class PreviewOptions:
    """Options for HTML preview generation."""
    scales: List[int] = field(default_factory=lambda: [1, 2, 4, 8])
    title: str = "Pixel Art Preview"
    show_grid: bool = False
    dark_background: bool = True
    show_info: bool = True
    include_download: bool = True


def canvas_to_data_uri(canvas: Canvas) -> str:
    """
    Convert a canvas to a data URI for embedding in HTML.

    Args:
        canvas: Canvas to convert

    Returns:
        Data URI string (data:image/png;base64,...)
    """
    png_bytes = canvas.to_bytes()
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return f"data:image/png;base64,{b64}"


def generate_preview_html(canvas: Canvas,
                          options: Optional[PreviewOptions] = None) -> str:
    """
    Generate HTML string for previewing a canvas.

    Args:
        canvas: Canvas to preview
        options: Preview options (None = defaults)

    Returns:
        Complete HTML document as string
    """
    if options is None:
        options = PreviewOptions()

    data_uri = canvas_to_data_uri(canvas)

    # Generate scale images
    scale_sections = []
    for scale in options.scales:
        width = canvas.width * scale
        height = canvas.height * scale
        scale_sections.append(f'''
        <div class="scale-section">
            <h3>{scale}x ({width}x{height})</h3>
            <div class="image-container" style="{'--grid-size: ' + str(scale) + 'px;' if options.show_grid else ''}">
                <img src="{data_uri}"
                     style="width: {width}px; height: {height}px; image-rendering: pixelated;"
                     alt="Preview at {scale}x"
                     class="{'show-grid' if options.show_grid else ''}">
            </div>
        </div>
        ''')

    # Info section
    info_html = ""
    if options.show_info:
        # Count unique colors
        colors = set()
        for row in canvas.pixels:
            for pixel in row:
                if pixel[3] > 0:  # Non-transparent
                    colors.add(tuple(pixel))

        info_html = f'''
        <div class="info-section">
            <h3>Image Info</h3>
            <ul>
                <li><strong>Size:</strong> {canvas.width} x {canvas.height} pixels</li>
                <li><strong>Colors:</strong> {len(colors)} unique colors</li>
            </ul>
        </div>
        '''

    # Download section
    download_html = ""
    if options.include_download:
        download_html = f'''
        <div class="download-section">
            <h3>Download</h3>
            <a href="{data_uri}" download="sprite.png" class="download-btn">
                Download PNG
            </a>
        </div>
        '''

    # Build full HTML
    bg_class = "dark" if options.dark_background else "light"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{options.title}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
            transition: background-color 0.3s, color 0.3s;
        }}

        body.dark {{
            background-color: #1a1a2e;
            color: #eee;
        }}

        body.light {{
            background-color: #f5f5f5;
            color: #333;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #444;
        }}

        h1 {{
            font-size: 24px;
        }}

        .controls {{
            display: flex;
            gap: 10px;
        }}

        button {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }}

        body.dark button {{
            background-color: #333;
            color: #eee;
        }}

        body.light button {{
            background-color: #ddd;
            color: #333;
        }}

        button:hover {{
            opacity: 0.8;
        }}

        button.active {{
            background-color: #4a90d9;
            color: white;
        }}

        .content {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
        }}

        .scale-section {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        h3 {{
            font-size: 14px;
            font-weight: 500;
            opacity: 0.7;
        }}

        .image-container {{
            display: inline-block;
            position: relative;
        }}

        .image-container img {{
            display: block;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }}

        .image-container img.show-grid {{
            background-image:
                linear-gradient(to right, rgba(255,255,255,0.1) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: var(--grid-size, 1px) var(--grid-size, 1px);
        }}

        body.dark .image-container {{
            background-color: #2a2a4a;
            border: 1px solid #444;
        }}

        body.light .image-container {{
            background-color: #fff;
            border: 1px solid #ccc;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .info-section, .download-section {{
            padding: 15px;
            border-radius: 8px;
        }}

        body.dark .info-section, body.dark .download-section {{
            background-color: #2a2a4a;
        }}

        body.light .info-section, body.light .download-section {{
            background-color: #fff;
            border: 1px solid #ddd;
        }}

        .info-section ul {{
            list-style: none;
            margin-top: 10px;
        }}

        .info-section li {{
            margin: 5px 0;
            font-size: 14px;
        }}

        .download-btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #4a90d9;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            transition: background-color 0.2s;
        }}

        .download-btn:hover {{
            background-color: #3a7bc8;
        }}

        .checkerboard {{
            background-image:
                linear-gradient(45deg, #666 25%, transparent 25%),
                linear-gradient(-45deg, #666 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #666 75%),
                linear-gradient(-45deg, transparent 75%, #666 75%);
            background-size: 16px 16px;
            background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
            background-color: #888;
        }}
    </style>
</head>
<body class="{bg_class}">
    <div class="header">
        <h1>{options.title}</h1>
        <div class="controls">
            <button onclick="toggleBackground()" id="bg-toggle">Toggle Background</button>
            <button onclick="toggleGrid()" id="grid-toggle">Toggle Grid</button>
            <button onclick="toggleCheckerboard()" id="checker-toggle">Checkerboard</button>
        </div>
    </div>

    <div class="content">
        {''.join(scale_sections)}
        {info_html}
        {download_html}
    </div>

    <script>
        function toggleBackground() {{
            document.body.classList.toggle('dark');
            document.body.classList.toggle('light');
        }}

        function toggleGrid() {{
            document.querySelectorAll('.image-container img').forEach(img => {{
                img.classList.toggle('show-grid');
            }});
        }}

        function toggleCheckerboard() {{
            document.querySelectorAll('.image-container').forEach(container => {{
                container.classList.toggle('checkerboard');
            }});
        }}
    </script>
</body>
</html>'''

    return html


def generate_preview_page(canvas: Canvas,
                          output_path: str,
                          options: Optional[PreviewOptions] = None) -> str:
    """
    Generate and save an HTML preview page.

    Args:
        canvas: Canvas to preview
        output_path: Path to save HTML file
        options: Preview options (None = defaults)

    Returns:
        Path to saved file
    """
    html = generate_preview_html(canvas, options)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def generate_multi_preview_html(canvases: List[Tuple[str, Canvas]],
                                 options: Optional[PreviewOptions] = None) -> str:
    """
    Generate HTML preview for multiple canvases.

    Args:
        canvases: List of (name, canvas) tuples
        options: Preview options

    Returns:
        Complete HTML document as string
    """
    if options is None:
        options = PreviewOptions()

    # Generate sections for each canvas
    canvas_sections = []
    for name, canvas in canvases:
        data_uri = canvas_to_data_uri(canvas)

        scale_images = []
        for scale in options.scales[:3]:  # Limit scales for multi-preview
            width = canvas.width * scale
            height = canvas.height * scale
            scale_images.append(f'''
                <div class="scale-preview">
                    <span class="scale-label">{scale}x</span>
                    <img src="{data_uri}"
                         style="width: {width}px; height: {height}px;"
                         alt="{name} at {scale}x">
                </div>
            ''')

        canvas_sections.append(f'''
        <div class="canvas-section">
            <h3>{name}</h3>
            <div class="size-info">{canvas.width}x{canvas.height}</div>
            <div class="scale-row">
                {''.join(scale_images)}
            </div>
        </div>
        ''')

    bg_class = "dark" if options.dark_background else "light"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{options.title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }}

        body.dark {{ background-color: #1a1a2e; color: #eee; }}
        body.light {{ background-color: #f5f5f5; color: #333; }}

        h1 {{ font-size: 24px; margin-bottom: 20px; }}

        .canvas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}

        .canvas-section {{
            padding: 15px;
            border-radius: 8px;
        }}

        body.dark .canvas-section {{ background-color: #2a2a4a; }}
        body.light .canvas-section {{ background-color: #fff; border: 1px solid #ddd; }}

        .canvas-section h3 {{
            font-size: 16px;
            margin-bottom: 5px;
        }}

        .size-info {{
            font-size: 12px;
            opacity: 0.6;
            margin-bottom: 10px;
        }}

        .scale-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .scale-preview {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }}

        .scale-label {{
            font-size: 11px;
            opacity: 0.5;
        }}

        .scale-preview img {{
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }}

        body.dark .scale-preview img {{ background-color: #1a1a2e; }}
        body.light .scale-preview img {{ background-color: #f0f0f0; }}
    </style>
</head>
<body class="{bg_class}">
    <h1>{options.title}</h1>
    <div class="canvas-grid">
        {''.join(canvas_sections)}
    </div>
</body>
</html>'''

    return html
