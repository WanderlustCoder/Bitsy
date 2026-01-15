"""
Animation Preview - Generate animation previews with playback controls.

Features:
- HTML preview with play/pause controls
- Speed adjustment (0.5x, 1x, 2x)
- Frame-by-frame stepping
- Frame strip visualization
"""

import sys
import os
import base64
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.animation import Animation


@dataclass
class AnimationPreviewOptions:
    """Options for animation preview generation."""
    scales: List[int] = field(default_factory=lambda: [1, 2, 4])
    speeds: List[float] = field(default_factory=lambda: [0.5, 1.0, 2.0])
    show_frame_strip: bool = True
    dark_background: bool = True
    title: str = "Animation Preview"
    loop: bool = True


def canvas_to_data_uri(canvas: Canvas) -> str:
    """Convert canvas to data URI."""
    png_bytes = canvas.to_bytes()
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return f"data:image/png;base64,{b64}"


def create_frame_strip(frames: List[Canvas],
                       padding: int = 2,
                       max_frames: int = 16,
                       background: Tuple[int, int, int, int] = (40, 40, 60, 255)) -> Canvas:
    """
    Create a horizontal strip showing all animation frames.

    Args:
        frames: List of frame canvases
        padding: Padding between frames
        max_frames: Maximum frames to show (truncate if more)
        background: Background color

    Returns:
        Canvas with frame strip
    """
    if not frames:
        return Canvas(1, 1, background)

    # Limit frames
    display_frames = frames[:max_frames]
    truncated = len(frames) > max_frames

    # Calculate dimensions
    max_height = max(f.height for f in display_frames)
    total_width = (sum(f.width for f in display_frames) +
                   padding * (len(display_frames) - 1))

    # Add indicator if truncated
    if truncated:
        total_width += 10  # Space for "..." indicator

    result = Canvas(total_width, max_height, background)

    # Place frames
    x = 0
    for i, frame in enumerate(display_frames):
        y = (max_height - frame.height) // 2
        result.blit(frame, x, y)

        # Draw frame number indicator (small dot at top)
        indicator_color = (100, 150, 255, 200)
        result.set_pixel_solid(x + frame.width // 2, 0, indicator_color)

        x += frame.width + padding

    # Draw truncation indicator
    if truncated:
        for i in range(3):
            result.set_pixel_solid(x + i * 3, max_height // 2, (150, 150, 150, 255))

    return result


def generate_animation_preview(animation: Animation,
                               options: Optional[AnimationPreviewOptions] = None) -> str:
    """
    Generate HTML preview for an animation.

    Args:
        animation: Animation to preview
        options: Preview options

    Returns:
        HTML string with interactive animation player
    """
    if options is None:
        options = AnimationPreviewOptions()

    # Get frames from animation
    frames = animation.frames if hasattr(animation, 'frames') else []

    if not frames:
        return "<html><body><p>No frames in animation</p></body></html>"

    # Convert all frames to data URIs
    frame_uris = [canvas_to_data_uri(f) for f in frames]

    # Get frame dimensions
    width = frames[0].width
    height = frames[0].height

    # Calculate frame duration in ms
    fps = animation.fps if hasattr(animation, 'fps') else 8
    frame_duration = 1000 / fps

    # Generate frame strip if enabled
    frame_strip_html = ""
    if options.show_frame_strip:
        strip = create_frame_strip(frames)
        strip_uri = canvas_to_data_uri(strip)
        frame_strip_html = f'''
        <div class="frame-strip-container">
            <h3>Frames ({len(frames)} total, {fps} FPS)</h3>
            <img src="{strip_uri}" class="frame-strip" alt="Frame strip">
        </div>
        '''

    # Generate scale preview sections
    scale_sections = []
    for scale in options.scales:
        w = width * scale
        h = height * scale
        scale_sections.append(f'''
        <div class="scale-section">
            <h3>{scale}x ({w}x{h})</h3>
            <div class="animation-container">
                <img class="animation-frame"
                     data-scale="{scale}"
                     style="width: {w}px; height: {h}px;"
                     alt="Animation at {scale}x">
            </div>
        </div>
        ''')

    # Speed button HTML
    speed_buttons = []
    for speed in options.speeds:
        active = "active" if speed == 1.0 else ""
        label = f"{speed}x"
        speed_buttons.append(
            f'<button class="speed-btn {active}" data-speed="{speed}">{label}</button>'
        )

    bg_class = "dark" if options.dark_background else "light"

    # Build complete HTML
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

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        h1 {{ font-size: 24px; }}
        h3 {{ font-size: 14px; font-weight: 500; opacity: 0.7; margin-bottom: 8px; }}

        .controls {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        button {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}

        body.dark button {{ background-color: #333; color: #eee; }}
        body.light button {{ background-color: #ddd; color: #333; }}

        button:hover {{ opacity: 0.8; }}
        button.active {{ background-color: #4a90d9; color: white; }}

        .playback-controls {{
            display: flex;
            gap: 5px;
            margin-right: 15px;
        }}

        .speed-controls {{
            display: flex;
            gap: 5px;
        }}

        .content {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
        }}

        .scale-section {{
            display: flex;
            flex-direction: column;
        }}

        .animation-container {{
            display: inline-block;
            padding: 10px;
            border-radius: 4px;
        }}

        body.dark .animation-container {{ background-color: #2a2a4a; }}
        body.light .animation-container {{ background-color: #fff; border: 1px solid #ddd; }}

        .animation-frame {{
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            display: block;
        }}

        .frame-strip-container {{
            width: 100%;
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
        }}

        body.dark .frame-strip-container {{ background-color: #2a2a4a; }}
        body.light .frame-strip-container {{ background-color: #fff; border: 1px solid #ddd; }}

        .frame-strip {{
            image-rendering: pixelated;
            max-width: 100%;
            height: auto;
        }}

        .frame-info {{
            margin-top: 10px;
            font-size: 14px;
            opacity: 0.7;
        }}

        .frame-counter {{
            font-family: monospace;
            padding: 4px 8px;
            border-radius: 4px;
        }}

        body.dark .frame-counter {{ background-color: #333; }}
        body.light .frame-counter {{ background-color: #eee; }}
    </style>
</head>
<body class="{bg_class}">
    <div class="header">
        <h1>{options.title}</h1>
        <div class="controls">
            <div class="playback-controls">
                <button id="prev-frame" title="Previous frame">&lt;</button>
                <button id="play-pause" class="active">Pause</button>
                <button id="next-frame" title="Next frame">&gt;</button>
            </div>
            <div class="speed-controls">
                {''.join(speed_buttons)}
            </div>
            <span class="frame-counter" id="frame-counter">1 / {len(frames)}</span>
        </div>
    </div>

    <div class="content">
        {''.join(scale_sections)}
    </div>

    {frame_strip_html}

    <script>
        const frames = {frame_uris};
        const frameCount = frames.length;
        const baseFrameDuration = {frame_duration};

        let currentFrame = 0;
        let isPlaying = true;
        let speed = 1.0;
        let animationTimer = null;

        const frameImages = document.querySelectorAll('.animation-frame');
        const playPauseBtn = document.getElementById('play-pause');
        const frameCounter = document.getElementById('frame-counter');
        const speedBtns = document.querySelectorAll('.speed-btn');

        function updateFrame() {{
            frameImages.forEach(img => {{
                img.src = frames[currentFrame];
            }});
            frameCounter.textContent = (currentFrame + 1) + ' / ' + frameCount;
        }}

        function nextFrame() {{
            currentFrame = (currentFrame + 1) % frameCount;
            updateFrame();
        }}

        function prevFrame() {{
            currentFrame = (currentFrame - 1 + frameCount) % frameCount;
            updateFrame();
        }}

        function startAnimation() {{
            if (animationTimer) clearInterval(animationTimer);
            animationTimer = setInterval(nextFrame, baseFrameDuration / speed);
        }}

        function stopAnimation() {{
            if (animationTimer) {{
                clearInterval(animationTimer);
                animationTimer = null;
            }}
        }}

        function togglePlayPause() {{
            isPlaying = !isPlaying;
            playPauseBtn.textContent = isPlaying ? 'Pause' : 'Play';
            playPauseBtn.classList.toggle('active', isPlaying);

            if (isPlaying) {{
                startAnimation();
            }} else {{
                stopAnimation();
            }}
        }}

        function setSpeed(newSpeed) {{
            speed = newSpeed;
            speedBtns.forEach(btn => {{
                btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
            }});
            if (isPlaying) {{
                startAnimation();
            }}
        }}

        // Event listeners
        playPauseBtn.addEventListener('click', togglePlayPause);
        document.getElementById('prev-frame').addEventListener('click', () => {{
            if (isPlaying) togglePlayPause();
            prevFrame();
        }});
        document.getElementById('next-frame').addEventListener('click', () => {{
            if (isPlaying) togglePlayPause();
            nextFrame();
        }});

        speedBtns.forEach(btn => {{
            btn.addEventListener('click', () => setSpeed(parseFloat(btn.dataset.speed)));
        }});

        // Keyboard controls
        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                togglePlayPause();
            }} else if (e.code === 'ArrowLeft') {{
                if (isPlaying) togglePlayPause();
                prevFrame();
            }} else if (e.code === 'ArrowRight') {{
                if (isPlaying) togglePlayPause();
                nextFrame();
            }}
        }});

        // Initialize
        updateFrame();
        startAnimation();
    </script>
</body>
</html>'''

    return html


def create_animation_html(frames: List[Canvas],
                          fps: int = 8,
                          output_path: Optional[str] = None,
                          options: Optional[AnimationPreviewOptions] = None) -> str:
    """
    Create HTML animation preview from a list of frames.

    Args:
        frames: List of frame canvases
        fps: Frames per second
        output_path: Optional path to save HTML file
        options: Preview options

    Returns:
        HTML string (also saves to file if output_path provided)
    """
    # Create a simple animation object
    class SimpleAnimation:
        def __init__(self, frames, fps):
            self.frames = frames
            self.fps = fps

    animation = SimpleAnimation(frames, fps)
    html = generate_animation_preview(animation, options)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    return html


def create_animation_comparison_html(animations: List[Tuple[str, Animation]],
                                      options: Optional[AnimationPreviewOptions] = None) -> str:
    """
    Create HTML comparing multiple animations side by side.

    Args:
        animations: List of (name, animation) tuples
        options: Preview options

    Returns:
        HTML string with multiple animations
    """
    if options is None:
        options = AnimationPreviewOptions()

    if not animations:
        return "<html><body><p>No animations to compare</p></body></html>"

    # Collect all frame data
    animation_data = []
    for name, animation in animations:
        frames = animation.frames if hasattr(animation, 'frames') else []
        fps = animation.fps if hasattr(animation, 'fps') else 8

        if frames:
            frame_uris = [canvas_to_data_uri(f) for f in frames]
            width = frames[0].width
            height = frames[0].height
            animation_data.append({
                'name': name,
                'frames': frame_uris,
                'fps': fps,
                'width': width,
                'height': height
            })

    if not animation_data:
        return "<html><body><p>No valid animations</p></body></html>"

    # Generate animation sections
    anim_sections = []
    for i, data in enumerate(animation_data):
        scale = 4  # Default scale for comparison
        w = data['width'] * scale
        h = data['height'] * scale

        anim_sections.append(f'''
        <div class="animation-section">
            <h3>{data['name']} ({data['fps']} FPS)</h3>
            <div class="animation-container">
                <img class="animation-frame"
                     data-index="{i}"
                     style="width: {w}px; height: {h}px;"
                     alt="{data['name']}">
            </div>
        </div>
        ''')

    bg_class = "dark" if options.dark_background else "light"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Animation Comparison</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 20px;
        }}
        body.dark {{ background-color: #1a1a2e; color: #eee; }}
        body.light {{ background-color: #f5f5f5; color: #333; }}

        h1 {{ margin-bottom: 20px; }}
        h3 {{ font-size: 14px; margin-bottom: 8px; opacity: 0.7; }}

        .animations {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
        }}

        .animation-section {{ display: flex; flex-direction: column; }}

        .animation-container {{
            padding: 10px;
            border-radius: 4px;
        }}
        body.dark .animation-container {{ background-color: #2a2a4a; }}
        body.light .animation-container {{ background-color: #fff; border: 1px solid #ddd; }}

        .animation-frame {{
            image-rendering: pixelated;
            display: block;
        }}
    </style>
</head>
<body class="{bg_class}">
    <h1>Animation Comparison</h1>
    <div class="animations">
        {''.join(anim_sections)}
    </div>

    <script>
        const animations = {[d for d in animation_data]};

        let timers = [];

        animations.forEach((anim, index) => {{
            let currentFrame = 0;
            const img = document.querySelector(`.animation-frame[data-index="${{index}}"]`);

            function updateFrame() {{
                img.src = anim.frames[currentFrame];
                currentFrame = (currentFrame + 1) % anim.frames.length;
            }}

            updateFrame();
            timers.push(setInterval(updateFrame, 1000 / anim.fps));
        }});
    </script>
</body>
</html>'''

    return html
