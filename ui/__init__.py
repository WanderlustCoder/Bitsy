"""
Bitsy UI - User interface generation for pixel art games.

This module provides:
- 9-patch/9-slice panels for scalable UI
- Icon generation for common UI elements
- Pixel font text rendering
- Progress bars and status displays

Example usage:

    # Create a panel
    from bitsy.ui import create_panel

    panel = create_panel(200, 150, preset='fantasy_wood')
    panel.save("dialog_box.png")

    # Create icons
    from bitsy.ui import create_icon, create_icon_sheet

    heart = create_icon('heart', size=16)
    icons = create_icon_sheet(['heart', 'star', 'coin'], size=16)

    # Render text
    from bitsy.ui import render_text, Label

    text = render_text("Hello World!", color=(255, 255, 255, 255))
    label = Label("Score: 1000", shadow=True)
"""

# NinePatch panels
from .ninepatch import (
    # Core classes
    NinePatch,
    NinePatchConfig,
    BorderStyle,
    # Presets
    PanelPresets,
    # Frame generation
    FrameGenerator,
    # Progress bars
    ProgressBar,
    HealthBar,
    ManaBar,
    # Convenience
    create_panel,
    list_panel_presets,
)

# Icons
from .icons import (
    # Core classes
    IconGenerator,
    IconStyle,
    IconPalette,
    # Registry
    ICON_GENERATORS,
    # Convenience
    create_icon,
    list_icons,
    create_icon_sheet,
)

# Fonts
from .fonts import (
    # Core classes
    PixelFont,
    FontMetrics,
    TextRenderer,
    # Alignment
    TextAlign,
    VerticalAlign,
    # Font data
    FONT_3X5,
    FONT_4X6,
    # Pre-built fonts
    Fonts,
    # Components
    Label,
    TextBox,
    # Convenience
    render_text,
    measure_text,
)

__all__ = [
    # NinePatch
    'NinePatch',
    'NinePatchConfig',
    'BorderStyle',
    'PanelPresets',
    'FrameGenerator',
    'ProgressBar',
    'HealthBar',
    'ManaBar',
    'create_panel',
    'list_panel_presets',

    # Icons
    'IconGenerator',
    'IconStyle',
    'IconPalette',
    'ICON_GENERATORS',
    'create_icon',
    'list_icons',
    'create_icon_sheet',

    # Fonts
    'PixelFont',
    'FontMetrics',
    'TextRenderer',
    'TextAlign',
    'VerticalAlign',
    'FONT_3X5',
    'FONT_4X6',
    'Fonts',
    'Label',
    'TextBox',
    'render_text',
    'measure_text',
]
