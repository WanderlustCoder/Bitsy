"""
Fonts - Pixel font rendering for UI text.

Provides:
- Built-in pixel fonts (3x5, 4x6, 5x7)
- Text rendering with alignment
- Text effects (shadow, outline)
- Custom font loading
"""

import sys
import os
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class TextAlign(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    """Vertical alignment options."""
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


@dataclass
class FontMetrics:
    """Font dimension metrics."""
    char_width: int
    char_height: int
    spacing: int = 1
    line_spacing: int = 2


# Built-in 3x5 pixel font (minimal, uppercase + numbers + common symbols)
FONT_3X5: Dict[str, List[int]] = {
    # Each character is 3 wide, 5 tall
    # Represented as 5 rows of 3-bit values (LSB = left pixel)
    'A': [0b010, 0b101, 0b111, 0b101, 0b101],
    'B': [0b110, 0b101, 0b110, 0b101, 0b110],
    'C': [0b011, 0b100, 0b100, 0b100, 0b011],
    'D': [0b110, 0b101, 0b101, 0b101, 0b110],
    'E': [0b111, 0b100, 0b110, 0b100, 0b111],
    'F': [0b111, 0b100, 0b110, 0b100, 0b100],
    'G': [0b011, 0b100, 0b101, 0b101, 0b011],
    'H': [0b101, 0b101, 0b111, 0b101, 0b101],
    'I': [0b111, 0b010, 0b010, 0b010, 0b111],
    'J': [0b001, 0b001, 0b001, 0b101, 0b010],
    'K': [0b101, 0b110, 0b100, 0b110, 0b101],
    'L': [0b100, 0b100, 0b100, 0b100, 0b111],
    'M': [0b101, 0b111, 0b101, 0b101, 0b101],
    'N': [0b101, 0b111, 0b111, 0b101, 0b101],
    'O': [0b010, 0b101, 0b101, 0b101, 0b010],
    'P': [0b110, 0b101, 0b110, 0b100, 0b100],
    'Q': [0b010, 0b101, 0b101, 0b111, 0b011],
    'R': [0b110, 0b101, 0b110, 0b101, 0b101],
    'S': [0b011, 0b100, 0b010, 0b001, 0b110],
    'T': [0b111, 0b010, 0b010, 0b010, 0b010],
    'U': [0b101, 0b101, 0b101, 0b101, 0b010],
    'V': [0b101, 0b101, 0b101, 0b010, 0b010],
    'W': [0b101, 0b101, 0b101, 0b111, 0b101],
    'X': [0b101, 0b101, 0b010, 0b101, 0b101],
    'Y': [0b101, 0b101, 0b010, 0b010, 0b010],
    'Z': [0b111, 0b001, 0b010, 0b100, 0b111],
    '0': [0b010, 0b101, 0b101, 0b101, 0b010],
    '1': [0b010, 0b110, 0b010, 0b010, 0b111],
    '2': [0b110, 0b001, 0b010, 0b100, 0b111],
    '3': [0b110, 0b001, 0b010, 0b001, 0b110],
    '4': [0b101, 0b101, 0b111, 0b001, 0b001],
    '5': [0b111, 0b100, 0b110, 0b001, 0b110],
    '6': [0b011, 0b100, 0b110, 0b101, 0b010],
    '7': [0b111, 0b001, 0b010, 0b010, 0b010],
    '8': [0b010, 0b101, 0b010, 0b101, 0b010],
    '9': [0b010, 0b101, 0b011, 0b001, 0b110],
    ' ': [0b000, 0b000, 0b000, 0b000, 0b000],
    '.': [0b000, 0b000, 0b000, 0b000, 0b010],
    ',': [0b000, 0b000, 0b000, 0b010, 0b100],
    ':': [0b000, 0b010, 0b000, 0b010, 0b000],
    ';': [0b000, 0b010, 0b000, 0b010, 0b100],
    '!': [0b010, 0b010, 0b010, 0b000, 0b010],
    '?': [0b110, 0b001, 0b010, 0b000, 0b010],
    '-': [0b000, 0b000, 0b111, 0b000, 0b000],
    '+': [0b000, 0b010, 0b111, 0b010, 0b000],
    '*': [0b000, 0b101, 0b010, 0b101, 0b000],
    '/': [0b001, 0b001, 0b010, 0b100, 0b100],
    '(': [0b001, 0b010, 0b010, 0b010, 0b001],
    ')': [0b100, 0b010, 0b010, 0b010, 0b100],
    '[': [0b011, 0b010, 0b010, 0b010, 0b011],
    ']': [0b110, 0b010, 0b010, 0b010, 0b110],
    '<': [0b001, 0b010, 0b100, 0b010, 0b001],
    '>': [0b100, 0b010, 0b001, 0b010, 0b100],
    '=': [0b000, 0b111, 0b000, 0b111, 0b000],
    '#': [0b101, 0b111, 0b101, 0b111, 0b101],
    '%': [0b101, 0b001, 0b010, 0b100, 0b101],
    '&': [0b010, 0b101, 0b010, 0b101, 0b011],
    '@': [0b010, 0b101, 0b111, 0b100, 0b011],
    "'": [0b010, 0b010, 0b000, 0b000, 0b000],
    '"': [0b101, 0b101, 0b000, 0b000, 0b000],
    '_': [0b000, 0b000, 0b000, 0b000, 0b111],
    '^': [0b010, 0b101, 0b000, 0b000, 0b000],
}

# Built-in 4x6 pixel font (includes lowercase)
FONT_4X6: Dict[str, List[int]] = {
    # Each character is 4 wide, 6 tall
    'A': [0b0110, 0b1001, 0b1001, 0b1111, 0b1001, 0b1001],
    'B': [0b1110, 0b1001, 0b1110, 0b1001, 0b1001, 0b1110],
    'C': [0b0111, 0b1000, 0b1000, 0b1000, 0b1000, 0b0111],
    'D': [0b1110, 0b1001, 0b1001, 0b1001, 0b1001, 0b1110],
    'E': [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b1111],
    'F': [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b1000],
    'G': [0b0111, 0b1000, 0b1011, 0b1001, 0b1001, 0b0111],
    'H': [0b1001, 0b1001, 0b1111, 0b1001, 0b1001, 0b1001],
    'I': [0b1110, 0b0100, 0b0100, 0b0100, 0b0100, 0b1110],
    'J': [0b0011, 0b0001, 0b0001, 0b0001, 0b1001, 0b0110],
    'K': [0b1001, 0b1010, 0b1100, 0b1010, 0b1001, 0b1001],
    'L': [0b1000, 0b1000, 0b1000, 0b1000, 0b1000, 0b1111],
    'M': [0b1001, 0b1111, 0b1111, 0b1001, 0b1001, 0b1001],
    'N': [0b1001, 0b1101, 0b1111, 0b1011, 0b1001, 0b1001],
    'O': [0b0110, 0b1001, 0b1001, 0b1001, 0b1001, 0b0110],
    'P': [0b1110, 0b1001, 0b1110, 0b1000, 0b1000, 0b1000],
    'Q': [0b0110, 0b1001, 0b1001, 0b1001, 0b1011, 0b0111],
    'R': [0b1110, 0b1001, 0b1110, 0b1010, 0b1001, 0b1001],
    'S': [0b0111, 0b1000, 0b0110, 0b0001, 0b0001, 0b1110],
    'T': [0b1111, 0b0100, 0b0100, 0b0100, 0b0100, 0b0100],
    'U': [0b1001, 0b1001, 0b1001, 0b1001, 0b1001, 0b0110],
    'V': [0b1001, 0b1001, 0b1001, 0b1001, 0b0110, 0b0110],
    'W': [0b1001, 0b1001, 0b1001, 0b1111, 0b1111, 0b1001],
    'X': [0b1001, 0b1001, 0b0110, 0b0110, 0b1001, 0b1001],
    'Y': [0b1001, 0b1001, 0b0110, 0b0100, 0b0100, 0b0100],
    'Z': [0b1111, 0b0001, 0b0010, 0b0100, 0b1000, 0b1111],
    'a': [0b0000, 0b0000, 0b0110, 0b1001, 0b1011, 0b0101],
    'b': [0b1000, 0b1000, 0b1110, 0b1001, 0b1001, 0b1110],
    'c': [0b0000, 0b0000, 0b0111, 0b1000, 0b1000, 0b0111],
    'd': [0b0001, 0b0001, 0b0111, 0b1001, 0b1001, 0b0111],
    'e': [0b0000, 0b0110, 0b1001, 0b1111, 0b1000, 0b0111],
    'f': [0b0011, 0b0100, 0b1110, 0b0100, 0b0100, 0b0100],
    'g': [0b0000, 0b0111, 0b1001, 0b0111, 0b0001, 0b0110],
    'h': [0b1000, 0b1000, 0b1110, 0b1001, 0b1001, 0b1001],
    'i': [0b0100, 0b0000, 0b1100, 0b0100, 0b0100, 0b1110],
    'j': [0b0010, 0b0000, 0b0110, 0b0010, 0b1010, 0b0100],
    'k': [0b1000, 0b1001, 0b1010, 0b1100, 0b1010, 0b1001],
    'l': [0b1100, 0b0100, 0b0100, 0b0100, 0b0100, 0b1110],
    'm': [0b0000, 0b0000, 0b1001, 0b1111, 0b1001, 0b1001],
    'n': [0b0000, 0b0000, 0b1110, 0b1001, 0b1001, 0b1001],
    'o': [0b0000, 0b0000, 0b0110, 0b1001, 0b1001, 0b0110],
    'p': [0b0000, 0b1110, 0b1001, 0b1110, 0b1000, 0b1000],
    'q': [0b0000, 0b0111, 0b1001, 0b0111, 0b0001, 0b0001],
    'r': [0b0000, 0b0000, 0b1011, 0b1100, 0b1000, 0b1000],
    's': [0b0000, 0b0111, 0b1000, 0b0110, 0b0001, 0b1110],
    't': [0b0100, 0b1110, 0b0100, 0b0100, 0b0100, 0b0011],
    'u': [0b0000, 0b0000, 0b1001, 0b1001, 0b1001, 0b0111],
    'v': [0b0000, 0b0000, 0b1001, 0b1001, 0b0110, 0b0110],
    'w': [0b0000, 0b0000, 0b1001, 0b1001, 0b1111, 0b0110],
    'x': [0b0000, 0b0000, 0b1001, 0b0110, 0b0110, 0b1001],
    'y': [0b0000, 0b1001, 0b1001, 0b0111, 0b0001, 0b0110],
    'z': [0b0000, 0b0000, 0b1111, 0b0010, 0b0100, 0b1111],
    '0': [0b0110, 0b1001, 0b1011, 0b1101, 0b1001, 0b0110],
    '1': [0b0100, 0b1100, 0b0100, 0b0100, 0b0100, 0b1110],
    '2': [0b0110, 0b1001, 0b0010, 0b0100, 0b1000, 0b1111],
    '3': [0b0110, 0b1001, 0b0010, 0b0001, 0b1001, 0b0110],
    '4': [0b0010, 0b0110, 0b1010, 0b1111, 0b0010, 0b0010],
    '5': [0b1111, 0b1000, 0b1110, 0b0001, 0b1001, 0b0110],
    '6': [0b0011, 0b0100, 0b1110, 0b1001, 0b1001, 0b0110],
    '7': [0b1111, 0b0001, 0b0010, 0b0100, 0b0100, 0b0100],
    '8': [0b0110, 0b1001, 0b0110, 0b1001, 0b1001, 0b0110],
    '9': [0b0110, 0b1001, 0b0111, 0b0001, 0b0010, 0b1100],
    ' ': [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
    '.': [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0100],
    ',': [0b0000, 0b0000, 0b0000, 0b0000, 0b0100, 0b1000],
    ':': [0b0000, 0b0100, 0b0000, 0b0000, 0b0100, 0b0000],
    ';': [0b0000, 0b0100, 0b0000, 0b0000, 0b0100, 0b1000],
    '!': [0b0100, 0b0100, 0b0100, 0b0100, 0b0000, 0b0100],
    '?': [0b0110, 0b1001, 0b0010, 0b0100, 0b0000, 0b0100],
    '-': [0b0000, 0b0000, 0b0000, 0b1111, 0b0000, 0b0000],
    '+': [0b0000, 0b0100, 0b0100, 0b1111, 0b0100, 0b0100],
    '*': [0b0000, 0b1001, 0b0110, 0b1111, 0b0110, 0b1001],
    '/': [0b0001, 0b0001, 0b0010, 0b0100, 0b1000, 0b1000],
    '(': [0b0010, 0b0100, 0b0100, 0b0100, 0b0100, 0b0010],
    ')': [0b0100, 0b0010, 0b0010, 0b0010, 0b0010, 0b0100],
    '[': [0b0110, 0b0100, 0b0100, 0b0100, 0b0100, 0b0110],
    ']': [0b0110, 0b0010, 0b0010, 0b0010, 0b0010, 0b0110],
    '<': [0b0001, 0b0010, 0b0100, 0b0100, 0b0010, 0b0001],
    '>': [0b1000, 0b0100, 0b0010, 0b0010, 0b0100, 0b1000],
    '=': [0b0000, 0b1111, 0b0000, 0b0000, 0b1111, 0b0000],
    '#': [0b0101, 0b1111, 0b0101, 0b0101, 0b1111, 0b0101],
    '%': [0b1001, 0b0001, 0b0010, 0b0100, 0b1000, 0b1001],
    '&': [0b0100, 0b1010, 0b0100, 0b1010, 0b1001, 0b0111],
    '@': [0b0110, 0b1001, 0b1011, 0b1011, 0b1000, 0b0111],
    "'": [0b0100, 0b0100, 0b0000, 0b0000, 0b0000, 0b0000],
    '"': [0b1010, 0b1010, 0b0000, 0b0000, 0b0000, 0b0000],
    '_': [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b1111],
    '^': [0b0100, 0b1010, 0b0000, 0b0000, 0b0000, 0b0000],
    '~': [0b0000, 0b0101, 0b1010, 0b0000, 0b0000, 0b0000],
    '`': [0b1000, 0b0100, 0b0000, 0b0000, 0b0000, 0b0000],
    '\\': [0b1000, 0b1000, 0b0100, 0b0010, 0b0001, 0b0001],
    '|': [0b0100, 0b0100, 0b0100, 0b0100, 0b0100, 0b0100],
    '{': [0b0011, 0b0100, 0b1100, 0b0100, 0b0100, 0b0011],
    '}': [0b1100, 0b0010, 0b0011, 0b0010, 0b0010, 0b1100],
}


class PixelFont:
    """Pixel font for text rendering."""

    def __init__(self, font_data: Dict[str, List[int]],
                 char_width: int, char_height: int,
                 spacing: int = 1, line_spacing: int = 2):
        """Initialize pixel font.

        Args:
            font_data: Character bitmap data
            char_width: Character width in pixels
            char_height: Character height in pixels
            spacing: Space between characters
            line_spacing: Space between lines
        """
        self.font_data = font_data
        self.metrics = FontMetrics(char_width, char_height, spacing, line_spacing)

    def measure_text(self, text: str) -> Tuple[int, int]:
        """Measure the size of rendered text.

        Args:
            text: Text to measure

        Returns:
            (width, height) tuple
        """
        lines = text.split('\n')
        max_width = 0

        for line in lines:
            line_width = len(line) * (self.metrics.char_width + self.metrics.spacing)
            if line_width > 0:
                line_width -= self.metrics.spacing  # Remove trailing spacing
            max_width = max(max_width, line_width)

        height = len(lines) * (self.metrics.char_height + self.metrics.line_spacing)
        if height > 0:
            height -= self.metrics.line_spacing  # Remove trailing spacing

        return (max_width, height)

    def render_char(self, char: str, color: Tuple[int, int, int, int]) -> Canvas:
        """Render a single character.

        Args:
            char: Character to render
            color: Text color

        Returns:
            Canvas with rendered character
        """
        canvas = Canvas(self.metrics.char_width, self.metrics.char_height, (0, 0, 0, 0))

        if char not in self.font_data:
            # Unknown character - render placeholder
            char = '?'
            if char not in self.font_data:
                return canvas

        rows = self.font_data[char]

        for y, row in enumerate(rows):
            for x in range(self.metrics.char_width):
                if row & (1 << (self.metrics.char_width - 1 - x)):
                    canvas.set_pixel(x, y, color)

        return canvas

    def render_text(self, text: str,
                    color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                    shadow_color: Optional[Tuple[int, int, int, int]] = None,
                    shadow_offset: Tuple[int, int] = (1, 1),
                    outline_color: Optional[Tuple[int, int, int, int]] = None,
                    ) -> Canvas:
        """Render text string.

        Args:
            text: Text to render
            color: Text color
            shadow_color: Optional shadow color
            shadow_offset: Shadow offset (x, y)
            outline_color: Optional outline color

        Returns:
            Canvas with rendered text
        """
        width, height = self.measure_text(text)

        # Account for effects
        extra_x = 0
        extra_y = 0
        if shadow_color:
            extra_x = max(extra_x, shadow_offset[0])
            extra_y = max(extra_y, shadow_offset[1])
        if outline_color:
            extra_x = max(extra_x, 1)
            extra_y = max(extra_y, 1)

        canvas = Canvas(width + extra_x, height + extra_y, (0, 0, 0, 0))

        lines = text.split('\n')

        for line_idx, line in enumerate(lines):
            y = line_idx * (self.metrics.char_height + self.metrics.line_spacing)

            for char_idx, char in enumerate(line):
                x = char_idx * (self.metrics.char_width + self.metrics.spacing)

                # Draw outline first
                if outline_color:
                    for ox in range(-1, 2):
                        for oy in range(-1, 2):
                            if ox == 0 and oy == 0:
                                continue
                            char_canvas = self.render_char(char, outline_color)
                            canvas.blit(char_canvas, x + ox, y + oy)

                # Draw shadow
                if shadow_color:
                    char_canvas = self.render_char(char, shadow_color)
                    canvas.blit(char_canvas, x + shadow_offset[0], y + shadow_offset[1])

                # Draw main character
                char_canvas = self.render_char(char, color)
                canvas.blit(char_canvas, x, y)

        return canvas


class TextRenderer:
    """High-level text rendering with fonts."""

    def __init__(self, font: Optional[PixelFont] = None):
        """Initialize text renderer.

        Args:
            font: Font to use (defaults to 4x6)
        """
        self.font = font or PixelFont(FONT_4X6, 4, 6)

    def render(self, text: str,
               color: Tuple[int, int, int, int] = (255, 255, 255, 255),
               shadow: bool = False,
               outline: bool = False) -> Canvas:
        """Render text with optional effects.

        Args:
            text: Text to render
            color: Text color
            shadow: Add drop shadow
            outline: Add outline

        Returns:
            Canvas with rendered text
        """
        shadow_color = (0, 0, 0, 180) if shadow else None
        outline_color = (0, 0, 0, 255) if outline else None

        return self.font.render_text(text, color, shadow_color, (1, 1), outline_color)

    def render_in_rect(self, text: str, width: int, height: int,
                       color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                       align: TextAlign = TextAlign.LEFT,
                       valign: VerticalAlign = VerticalAlign.TOP,
                       shadow: bool = False,
                       outline: bool = False,
                       wrap: bool = False) -> Canvas:
        """Render text within a rectangle.

        Args:
            text: Text to render
            width: Rectangle width
            height: Rectangle height
            color: Text color
            align: Horizontal alignment
            valign: Vertical alignment
            shadow: Add drop shadow
            outline: Add outline
            wrap: Word wrap text

        Returns:
            Canvas with rendered text
        """
        canvas = Canvas(width, height, (0, 0, 0, 0))

        if wrap:
            text = self._word_wrap(text, width)

        # Render the text
        text_canvas = self.render(text, color, shadow, outline)

        # Calculate position
        text_width = text_canvas.width
        text_height = text_canvas.height

        if align == TextAlign.LEFT:
            x = 0
        elif align == TextAlign.CENTER:
            x = (width - text_width) // 2
        else:  # RIGHT
            x = width - text_width

        if valign == VerticalAlign.TOP:
            y = 0
        elif valign == VerticalAlign.MIDDLE:
            y = (height - text_height) // 2
        else:  # BOTTOM
            y = height - text_height

        canvas.blit(text_canvas, x, y)
        return canvas

    def _word_wrap(self, text: str, max_width: int) -> str:
        """Wrap text to fit within width.

        Args:
            text: Text to wrap
            max_width: Maximum width in pixels

        Returns:
            Wrapped text with newlines
        """
        char_width = self.font.metrics.char_width + self.font.metrics.spacing
        max_chars = max(1, max_width // char_width)

        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= max_chars:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    # Handle words longer than max_chars
                    while len(word) > max_chars:
                        lines.append(word[:max_chars])
                        word = word[max_chars:]
                    current_line = word

            if current_line:
                lines.append(current_line)

        return '\n'.join(lines)


# Pre-built fonts
class Fonts:
    """Collection of pre-built fonts."""

    @staticmethod
    def tiny() -> PixelFont:
        """3x5 minimal font."""
        return PixelFont(FONT_3X5, 3, 5, spacing=1, line_spacing=2)

    @staticmethod
    def small() -> PixelFont:
        """4x6 small font with lowercase."""
        return PixelFont(FONT_4X6, 4, 6, spacing=1, line_spacing=2)

    @staticmethod
    def default() -> PixelFont:
        """Default font (4x6)."""
        return Fonts.small()


# Convenience functions
def render_text(text: str,
                color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                font: str = 'small',
                shadow: bool = False,
                outline: bool = False) -> Canvas:
    """Render text with specified font.

    Args:
        text: Text to render
        color: Text color
        font: Font name ('tiny', 'small')
        shadow: Add drop shadow
        outline: Add outline

    Returns:
        Canvas with rendered text
    """
    fonts = {
        'tiny': Fonts.tiny,
        'small': Fonts.small,
    }

    font_fn = fonts.get(font, Fonts.small)
    pixel_font = font_fn()

    renderer = TextRenderer(pixel_font)
    return renderer.render(text, color, shadow, outline)


def measure_text(text: str, font: str = 'small') -> Tuple[int, int]:
    """Measure text dimensions.

    Args:
        text: Text to measure
        font: Font name

    Returns:
        (width, height) tuple
    """
    fonts = {
        'tiny': Fonts.tiny,
        'small': Fonts.small,
    }

    font_fn = fonts.get(font, Fonts.small)
    pixel_font = font_fn()

    return pixel_font.measure_text(text)


class Label:
    """UI label component."""

    def __init__(self, text: str,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 font: Optional[PixelFont] = None,
                 shadow: bool = False,
                 outline: bool = False):
        """Initialize label.

        Args:
            text: Label text
            color: Text color
            font: Font to use
            shadow: Add drop shadow
            outline: Add outline
        """
        self.text = text
        self.color = color
        self.font = font or Fonts.default()
        self.shadow = shadow
        self.outline = outline

    def render(self) -> Canvas:
        """Render the label."""
        renderer = TextRenderer(self.font)
        return renderer.render(self.text, self.color, self.shadow, self.outline)


class TextBox:
    """Multi-line text box component."""

    def __init__(self, width: int, height: int,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 font: Optional[PixelFont] = None,
                 align: TextAlign = TextAlign.LEFT,
                 valign: VerticalAlign = VerticalAlign.TOP,
                 wrap: bool = True):
        """Initialize text box.

        Args:
            width: Box width
            height: Box height
            color: Text color
            font: Font to use
            align: Horizontal alignment
            valign: Vertical alignment
            wrap: Word wrap text
        """
        self.width = width
        self.height = height
        self.color = color
        self.font = font or Fonts.default()
        self.align = align
        self.valign = valign
        self.wrap = wrap
        self.text = ""

    def set_text(self, text: str) -> None:
        """Set the text content."""
        self.text = text

    def render(self) -> Canvas:
        """Render the text box."""
        renderer = TextRenderer(self.font)
        return renderer.render_in_rect(
            self.text, self.width, self.height,
            self.color, self.align, self.valign,
            shadow=False, outline=False, wrap=self.wrap
        )
