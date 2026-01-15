"""
Contact Sheet - Create sheets showing multiple variations.

Features:
- Grid layout contact sheets
- Labeled variation sheets
- Variation preview generation
- Configurable layout options
"""

import sys
import os
from typing import List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


@dataclass
class ContactSheetOptions:
    """Options for contact sheet generation."""
    columns: int = 4
    padding: int = 4
    background: Tuple[int, int, int, int] = field(default_factory=lambda: (40, 40, 60, 255))
    cell_background: Optional[Tuple[int, int, int, int]] = None
    show_index: bool = False
    scale: int = 1
    title_height: int = 0


def create_contact_sheet(canvases: List[Canvas],
                         options: Optional[ContactSheetOptions] = None) -> Canvas:
    """
    Create a contact sheet from multiple canvases.

    Args:
        canvases: List of canvases to include
        options: Layout options (None = defaults)

    Returns:
        Single canvas containing all images in a grid
    """
    if options is None:
        options = ContactSheetOptions()

    if not canvases:
        return Canvas(1, 1, options.background)

    # Scale canvases if needed
    if options.scale > 1:
        canvases = [c.scale(options.scale) for c in canvases]

    # Find max cell dimensions
    max_width = max(c.width for c in canvases)
    max_height = max(c.height for c in canvases)

    # Add space for index labels if enabled
    index_height = 8 if options.show_index else 0
    cell_height = max_height + index_height

    # Calculate grid dimensions
    columns = min(options.columns, len(canvases))
    rows = (len(canvases) + columns - 1) // columns

    # Calculate total size
    total_width = columns * max_width + (columns - 1) * options.padding
    total_height = (rows * cell_height + (rows - 1) * options.padding +
                    options.title_height)

    # Create result canvas
    result = Canvas(total_width, total_height, options.background)

    # Place each canvas in grid
    for i, canvas in enumerate(canvases):
        col = i % columns
        row = i // columns

        # Calculate cell position
        cell_x = col * (max_width + options.padding)
        cell_y = options.title_height + row * (cell_height + options.padding)

        # Draw cell background if specified
        if options.cell_background:
            result.fill_rect(cell_x, cell_y, max_width, cell_height,
                           options.cell_background)

        # Center canvas in cell
        x = cell_x + (max_width - canvas.width) // 2
        y = cell_y + index_height + (max_height - canvas.height) // 2

        result.blit(canvas, x, y)

        # Draw index number if enabled
        if options.show_index:
            _draw_index(result, i, cell_x, cell_y, max_width)

    return result


def _draw_index(canvas: Canvas, index: int, x: int, y: int, width: int) -> None:
    """Draw a small index number at the top of a cell."""
    # Simple pixel font for single digits (0-9)
    # Each digit is 3x5 pixels
    digits = {
        0: [(1,0), (0,1), (2,1), (0,2), (2,2), (0,3), (2,3), (1,4)],
        1: [(1,0), (0,1), (1,1), (1,2), (1,3), (0,4), (1,4), (2,4)],
        2: [(0,0), (1,0), (2,0), (2,1), (1,2), (0,3), (0,4), (1,4), (2,4)],
        3: [(0,0), (1,0), (2,1), (1,2), (2,3), (0,4), (1,4)],
        4: [(0,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (2,3), (2,4)],
        5: [(0,0), (1,0), (2,0), (0,1), (0,2), (1,2), (2,3), (0,4), (1,4)],
        6: [(1,0), (0,1), (0,2), (1,2), (0,3), (2,3), (1,4)],
        7: [(0,0), (1,0), (2,0), (2,1), (1,2), (1,3), (1,4)],
        8: [(1,0), (0,1), (2,1), (1,2), (0,3), (2,3), (1,4)],
        9: [(1,0), (0,1), (2,1), (1,2), (2,2), (2,3), (1,4)],
    }

    # Convert index to string and draw each digit
    index_str = str(index)
    digit_width = 4  # 3px digit + 1px spacing
    total_digit_width = len(index_str) * digit_width - 1

    # Center the number
    start_x = x + (width - total_digit_width) // 2

    color = (200, 200, 200, 255)  # Light gray

    for i, char in enumerate(index_str):
        digit = int(char)
        dx = start_x + i * digit_width

        if digit in digits:
            for px, py in digits[digit]:
                canvas.set_pixel_solid(dx + px, y + py + 1, color)


def create_labeled_sheet(items: List[Tuple[str, Canvas]],
                         options: Optional[ContactSheetOptions] = None) -> Canvas:
    """
    Create a contact sheet with labels for each item.

    Args:
        items: List of (label, canvas) tuples
        options: Layout options

    Returns:
        Canvas with labeled grid
    """
    if options is None:
        options = ContactSheetOptions()

    if not items:
        return Canvas(1, 1, options.background)

    # Extract canvases
    canvases = [canvas for _, canvas in items]

    # Scale if needed
    if options.scale > 1:
        canvases = [c.scale(options.scale) for c in canvases]

    # Find max dimensions
    max_width = max(c.width for c in canvases)
    max_height = max(c.height for c in canvases)

    # Label height (simplified - just a color bar)
    label_height = 3
    cell_height = max_height + label_height + 2

    # Calculate grid
    columns = min(options.columns, len(items))
    rows = (len(items) + columns - 1) // columns

    total_width = columns * max_width + (columns - 1) * options.padding
    total_height = rows * cell_height + (rows - 1) * options.padding

    result = Canvas(total_width, total_height, options.background)

    # Color palette for labels
    label_colors = [
        (100, 150, 255, 255),  # Blue
        (150, 255, 100, 255),  # Green
        (255, 150, 100, 255),  # Orange
        (255, 100, 150, 255),  # Pink
        (150, 100, 255, 255),  # Purple
        (255, 255, 100, 255),  # Yellow
        (100, 255, 255, 255),  # Cyan
        (255, 100, 255, 255),  # Magenta
    ]

    for i, (label, original_canvas) in enumerate(items):
        canvas = canvases[i]  # Use potentially scaled version
        col = i % columns
        row = i // columns

        cell_x = col * (max_width + options.padding)
        cell_y = row * (cell_height + options.padding)

        # Draw label bar with cycling colors
        color = label_colors[i % len(label_colors)]
        result.fill_rect(cell_x, cell_y, max_width, label_height, color)

        # Center canvas in cell
        x = cell_x + (max_width - canvas.width) // 2
        y = cell_y + label_height + 2

        result.blit(canvas, x, y)

    return result


def generate_variations_preview(generator_func: Callable[..., Canvas],
                                 count: int = 9,
                                 seed_start: int = 0,
                                 columns: int = 3,
                                 **generator_kwargs: Any) -> Canvas:
    """
    Generate multiple variations using a generator function and create preview.

    Args:
        generator_func: Function that takes seed as first argument and returns Canvas
        count: Number of variations to generate
        seed_start: Starting seed value
        columns: Columns in output grid
        **generator_kwargs: Additional arguments to pass to generator

    Returns:
        Contact sheet with all variations
    """
    canvases = []

    for i in range(count):
        seed = seed_start + i
        try:
            canvas = generator_func(seed=seed, **generator_kwargs)
            canvases.append(canvas)
        except TypeError:
            # If generator doesn't accept seed, try without it
            canvas = generator_func(**generator_kwargs)
            canvases.append(canvas)

    options = ContactSheetOptions(
        columns=columns,
        show_index=True,
        padding=4
    )

    return create_contact_sheet(canvases, options)


def create_parameter_sweep(generator_func: Callable[..., Canvas],
                            param_name: str,
                            param_values: List[Any],
                            columns: int = 4,
                            **fixed_kwargs: Any) -> Canvas:
    """
    Create a contact sheet showing variations of a single parameter.

    Args:
        generator_func: Generator function
        param_name: Name of parameter to vary
        param_values: List of values to try
        columns: Columns in output grid
        **fixed_kwargs: Fixed arguments to pass to generator

    Returns:
        Contact sheet showing parameter sweep
    """
    items = []

    for value in param_values:
        kwargs = {**fixed_kwargs, param_name: value}
        try:
            canvas = generator_func(**kwargs)
            label = f"{param_name}={value}"
            items.append((label, canvas))
        except Exception:
            # Skip failed generations
            pass

    return create_labeled_sheet(items, ContactSheetOptions(columns=columns))


def create_comparison_strip(canvases: List[Canvas],
                            labels: Optional[List[str]] = None,
                            horizontal: bool = True,
                            padding: int = 4) -> Canvas:
    """
    Create a single row/column strip of canvases for comparison.

    Args:
        canvases: List of canvases
        labels: Optional list of labels
        horizontal: True for row, False for column
        padding: Padding between items

    Returns:
        Strip canvas
    """
    if not canvases:
        return Canvas(1, 1)

    # Calculate dimensions
    if horizontal:
        total_width = sum(c.width for c in canvases) + padding * (len(canvases) - 1)
        max_height = max(c.height for c in canvases)
        result = Canvas(total_width, max_height, (40, 40, 60, 255))

        x = 0
        for canvas in canvases:
            y = (max_height - canvas.height) // 2
            result.blit(canvas, x, y)
            x += canvas.width + padding
    else:
        max_width = max(c.width for c in canvases)
        total_height = sum(c.height for c in canvases) + padding * (len(canvases) - 1)
        result = Canvas(max_width, total_height, (40, 40, 60, 255))

        y = 0
        for canvas in canvases:
            x = (max_width - canvas.width) // 2
            result.blit(canvas, x, y)
            y += canvas.height + padding

    return result
