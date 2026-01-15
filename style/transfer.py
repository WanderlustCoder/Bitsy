"""
Style Transfer - Extract and apply artistic styles.

Extract visual characteristics from reference art and apply them
to new sprites for consistent styling across an asset set.

Example usage:
    from style import extract_style, apply_style

    # Extract style from reference
    style = extract_style(reference_sprite)

    # Apply to new sprite
    styled = apply_style(new_sprite, style)
"""

import math
from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Palette
from core.color import rgb_to_hsv, hsv_to_rgb, lerp_color
from editor.palette_tools import (
    extract_palette, extract_palette_kmeans, analyze_palette,
    remap_to_palette, PaletteAnalysis
)


class OutlineType(Enum):
    """Types of outline styles."""
    NONE = 'none'
    FULL = 'full'           # Complete outline
    EXTERNAL = 'external'   # Only outside edges
    SELECTIVE = 'selective' # Darker on bottom/right


class ShadingType(Enum):
    """Types of shading styles."""
    FLAT = 'flat'           # No shading
    CEL = 'cel'             # Hard-edged cel shading
    SOFT = 'soft'           # Soft gradient shading
    DITHER = 'dither'       # Dithered shading


@dataclass
class ShadingStyle:
    """Extracted shading characteristics."""
    type: ShadingType = ShadingType.CEL
    levels: int = 3                    # Number of shading levels
    shadow_hue_shift: float = 0.0      # Hue shift in shadows (degrees)
    highlight_hue_shift: float = 0.0   # Hue shift in highlights
    shadow_saturation: float = 1.0     # Saturation multiplier for shadows
    contrast: float = 0.3              # Shadow/highlight contrast


@dataclass
class OutlineStyle:
    """Extracted outline characteristics."""
    type: OutlineType = OutlineType.FULL
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    thickness: int = 1
    use_darker_shade: bool = False     # Use darker shade of fill instead of solid color
    darken_amount: float = 0.5         # How much darker (if use_darker_shade)


@dataclass
class ExtractedStyle:
    """Complete extracted style from reference art."""
    palette: Palette = field(default_factory=Palette)
    palette_analysis: Optional[PaletteAnalysis] = None
    shading: ShadingStyle = field(default_factory=ShadingStyle)
    outline: OutlineStyle = field(default_factory=OutlineStyle)
    # Additional characteristics
    anti_aliased: bool = False
    pixel_density: float = 0.5         # Ratio of opaque pixels
    color_count: int = 0
    has_transparency: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'palette_colors': [self.palette.get(i) for i in range(len(self.palette))],
            'shading_type': self.shading.type.value,
            'shading_levels': self.shading.levels,
            'shadow_hue_shift': self.shading.shadow_hue_shift,
            'outline_type': self.outline.type.value,
            'outline_color': self.outline.color,
            'outline_thickness': self.outline.thickness,
            'anti_aliased': self.anti_aliased,
            'color_count': self.color_count,
        }


# ==================== Style Extraction ====================

def extract_style(canvas: Canvas, max_palette_colors: int = 32) -> ExtractedStyle:
    """Extract complete style from a reference canvas.

    Args:
        canvas: Reference canvas to analyze
        max_palette_colors: Maximum colors for palette extraction

    Returns:
        ExtractedStyle with all characteristics
    """
    style = ExtractedStyle()

    # Extract palette
    style.palette = extract_palette_kmeans(canvas, num_colors=max_palette_colors)
    style.palette_analysis = analyze_palette(canvas)
    style.color_count = len(style.palette_analysis.colors) if style.palette_analysis else 0

    # Analyze shading
    style.shading = extract_shading_style(canvas)

    # Analyze outlines
    style.outline = extract_outline_style(canvas)

    # Check for anti-aliasing
    style.anti_aliased = _detect_anti_aliasing(canvas)

    # Calculate pixel density
    opaque = sum(1 for y in range(canvas.height) for x in range(canvas.width)
                 if canvas.get_pixel(x, y)[3] > 0)
    style.pixel_density = opaque / (canvas.width * canvas.height)

    # Check transparency
    style.has_transparency = any(
        canvas.get_pixel(x, y)[3] < 255
        for y in range(canvas.height)
        for x in range(canvas.width)
        if canvas.get_pixel(x, y)[3] > 0
    )

    return style


def extract_shading_style(canvas: Canvas) -> ShadingStyle:
    """Extract shading characteristics from canvas.

    Args:
        canvas: Reference canvas

    Returns:
        ShadingStyle describing the shading approach
    """
    style = ShadingStyle()

    # Collect colors and their HSV values
    colors_hsv = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel[3] > 128:
                h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])
                colors_hsv.append((h, s, v, pixel))

    if len(colors_hsv) < 2:
        return style

    # Group colors by base hue
    hue_groups: Dict[int, List] = {}
    for h, s, v, pixel in colors_hsv:
        hue_bucket = int(h * 12) % 12  # 30 degree buckets
        if hue_bucket not in hue_groups:
            hue_groups[hue_bucket] = []
        hue_groups[hue_bucket].append((h, s, v, pixel))

    # Analyze the largest hue group for shading
    if hue_groups:
        largest_group = max(hue_groups.values(), key=len)

        # Count distinct value levels
        values = sorted(set(int(v * 10) for h, s, v, _ in largest_group))
        style.levels = len(values)

        # Detect shading type
        if style.levels <= 2:
            style.type = ShadingType.FLAT
        elif style.levels <= 4:
            style.type = ShadingType.CEL
        else:
            style.type = ShadingType.SOFT

        # Analyze hue shift in shadows vs highlights
        if len(largest_group) >= 4:
            sorted_by_value = sorted(largest_group, key=lambda x: x[2])
            dark_hue = sorted_by_value[0][0]
            light_hue = sorted_by_value[-1][0]

            # Calculate hue difference (handling wrap-around)
            hue_diff = light_hue - dark_hue
            if hue_diff > 0.5:
                hue_diff -= 1.0
            elif hue_diff < -0.5:
                hue_diff += 1.0

            style.shadow_hue_shift = -hue_diff * 360 / 2
            style.highlight_hue_shift = hue_diff * 360 / 2

            # Analyze saturation difference
            dark_sat = sorted_by_value[0][1]
            light_sat = sorted_by_value[-1][1]
            if light_sat > 0:
                style.shadow_saturation = dark_sat / light_sat

    return style


def extract_outline_style(canvas: Canvas) -> OutlineStyle:
    """Extract outline characteristics from canvas.

    Args:
        canvas: Reference canvas

    Returns:
        OutlineStyle describing the outline approach
    """
    style = OutlineStyle()

    # Find edge pixels
    edge_colors: Dict[Tuple[int, int, int, int], int] = {}
    interior_colors: Dict[Tuple[int, int, int, int], int] = {}

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel[3] < 128:
                continue

            pixel_tuple = tuple(pixel)

            # Check if this is an edge pixel
            is_edge = False
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                        if canvas.get_pixel(nx, ny)[3] < 128:
                            is_edge = True
                            break
                    else:
                        is_edge = True
                        break
                if is_edge:
                    break

            if is_edge:
                edge_colors[pixel_tuple] = edge_colors.get(pixel_tuple, 0) + 1
            else:
                interior_colors[pixel_tuple] = interior_colors.get(pixel_tuple, 0) + 1

    if not edge_colors:
        style.type = OutlineType.NONE
        return style

    # Find most common edge color
    most_common_edge = max(edge_colors.items(), key=lambda x: x[1])[0]

    # Check if edges use a consistent dark color
    edge_luminances = []
    for color, count in edge_colors.items():
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        edge_luminances.append((lum, count))

    avg_edge_lum = sum(l * c for l, c in edge_luminances) / sum(c for _, c in edge_luminances)

    interior_luminances = []
    for color, count in interior_colors.items():
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        interior_luminances.append((lum, count))

    if interior_luminances:
        avg_interior_lum = sum(l * c for l, c in interior_luminances) / sum(c for _, c in interior_luminances)

        # Edges significantly darker = outline style
        if avg_edge_lum < avg_interior_lum * 0.7:
            style.type = OutlineType.FULL
            style.color = most_common_edge

            # Check if it's a darker shade vs solid color
            if most_common_edge[0] > 10 or most_common_edge[1] > 10 or most_common_edge[2] > 10:
                style.use_darker_shade = True
                style.darken_amount = 1 - avg_edge_lum / max(1, avg_interior_lum)
        else:
            style.type = OutlineType.NONE
    else:
        style.type = OutlineType.EXTERNAL
        style.color = most_common_edge

    return style


def _detect_anti_aliasing(canvas: Canvas) -> bool:
    """Detect if canvas uses anti-aliasing."""
    # Count semi-transparent pixels at edges
    semi_transparent = 0
    edge_pixels = 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)

            if pixel[3] == 0:
                continue

            # Check if edge
            is_edge = False
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                        if canvas.get_pixel(nx, ny)[3] == 0:
                            is_edge = True
                            break
                if is_edge:
                    break

            if is_edge:
                edge_pixels += 1
                if 0 < pixel[3] < 255:
                    semi_transparent += 1

    if edge_pixels == 0:
        return False

    # If more than 10% of edge pixels are semi-transparent, likely AA
    return semi_transparent / edge_pixels > 0.1


# ==================== Style Application ====================

def apply_style(canvas: Canvas, style: ExtractedStyle,
               apply_palette: bool = True,
               apply_shading: bool = True,
               apply_outline: bool = True) -> Canvas:
    """Apply an extracted style to a canvas.

    Args:
        canvas: Canvas to style
        style: Style to apply
        apply_palette: Apply palette remapping
        apply_shading: Apply shading adjustments
        apply_outline: Apply outline style

    Returns:
        New Canvas with style applied
    """
    result = canvas.copy()

    if apply_shading:
        result = apply_shading_style(result, style.shading)

    if apply_palette and len(style.palette) > 0:
        result = apply_palette_style(result, style.palette)

    if apply_outline and style.outline.type != OutlineType.NONE:
        result = apply_outline_style(result, style.outline)

    return result


def apply_palette_style(canvas: Canvas, palette: Palette) -> Canvas:
    """Apply palette to canvas by remapping colors.

    Args:
        canvas: Source canvas
        palette: Target palette

    Returns:
        Canvas with remapped colors
    """
    return remap_to_palette(canvas, palette, preserve_transparency=True)


def apply_shading_style(canvas: Canvas, shading: ShadingStyle) -> Canvas:
    """Apply shading style to canvas.

    Args:
        canvas: Source canvas
        shading: Shading style to apply

    Returns:
        Canvas with adjusted shading
    """
    result = canvas.copy()

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel[3] == 0:
                continue

            h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

            # Apply hue shift based on value (darker = shadow shift, lighter = highlight shift)
            if v < 0.5:
                # Shadow region
                hue_shift = shading.shadow_hue_shift * (0.5 - v) * 2
                s *= shading.shadow_saturation
            else:
                # Highlight region
                hue_shift = shading.highlight_hue_shift * (v - 0.5) * 2

            h = (h + hue_shift / 360) % 1.0
            s = max(0, min(1, s))

            # Quantize value for cel shading
            if shading.type == ShadingType.CEL and shading.levels > 1:
                v = round(v * (shading.levels - 1)) / (shading.levels - 1)

            r, g, b = hsv_to_rgb(h, s, v)
            result.set_pixel_solid(x, y, (r, g, b, pixel[3]))

    return result


def apply_outline_style(canvas: Canvas, outline: OutlineStyle) -> Canvas:
    """Apply outline style to canvas.

    Args:
        canvas: Source canvas
        outline: Outline style to apply

    Returns:
        Canvas with outline applied
    """
    if outline.type == OutlineType.NONE:
        return canvas.copy()

    result = Canvas(canvas.width, canvas.height)

    # First pass: add outline pixels
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)

            if pixel[3] > 128:
                # Check if this should be an outline pixel
                is_edge = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                            if canvas.get_pixel(nx, ny)[3] < 128:
                                is_edge = True
                                break
                        else:
                            is_edge = True
                            break
                    if is_edge:
                        break

                if is_edge:
                    if outline.use_darker_shade:
                        # Darken the pixel color
                        factor = 1 - outline.darken_amount
                        color = (
                            int(pixel[0] * factor),
                            int(pixel[1] * factor),
                            int(pixel[2] * factor),
                            pixel[3]
                        )
                    else:
                        color = outline.color
                    result.set_pixel_solid(x, y, color)
                else:
                    result.set_pixel_solid(x, y, pixel)

    return result


# ==================== Style Consistency ====================

class StyleEnforcer:
    """Enforces style consistency across multiple assets."""

    def __init__(self, reference_style: ExtractedStyle = None,
                 reference_canvases: List[Canvas] = None):
        """Initialize enforcer with reference style or canvases.

        Args:
            reference_style: Pre-extracted style to enforce
            reference_canvases: Canvases to extract reference style from
        """
        if reference_style:
            self.style = reference_style
        elif reference_canvases:
            # Extract combined style from all references
            self.style = self._extract_combined_style(reference_canvases)
        else:
            self.style = ExtractedStyle()

    def _extract_combined_style(self, canvases: List[Canvas]) -> ExtractedStyle:
        """Extract combined style from multiple canvases."""
        if not canvases:
            return ExtractedStyle()

        # Start with first canvas style
        combined = extract_style(canvases[0])

        # Merge palettes from all canvases
        all_colors: Dict[Tuple, int] = {}
        for canvas in canvases:
            analysis = analyze_palette(canvas)
            for info in analysis.color_info:
                all_colors[info.color] = all_colors.get(info.color, 0) + info.count

        # Create combined palette from most common colors
        sorted_colors = sorted(all_colors.items(), key=lambda x: x[1], reverse=True)
        combined.palette = Palette()
        for color, _ in sorted_colors[:32]:
            combined.palette.add(color)

        return combined

    def check(self, canvas: Canvas) -> Dict[str, Any]:
        """Check how well a canvas matches the reference style.

        Args:
            canvas: Canvas to check

        Returns:
            Dict with consistency scores and issues
        """
        return check_style_consistency(canvas, self.style)

    def enforce(self, canvas: Canvas) -> Canvas:
        """Apply reference style to canvas.

        Args:
            canvas: Canvas to enforce style on

        Returns:
            Canvas with enforced style
        """
        return apply_style(canvas, self.style)

    def fix(self, canvas: Canvas) -> Canvas:
        """Fix style inconsistencies in canvas.

        Args:
            canvas: Canvas to fix

        Returns:
            Canvas with inconsistencies fixed
        """
        return fix_style_inconsistencies(canvas, self.style)


def check_style_consistency(canvas: Canvas, reference: ExtractedStyle) -> Dict[str, Any]:
    """Check how well a canvas matches a reference style.

    Args:
        canvas: Canvas to check
        reference: Reference style

    Returns:
        Dict with consistency scores and issues
    """
    result = {
        'overall_score': 0.0,
        'palette_score': 0.0,
        'shading_score': 0.0,
        'outline_score': 0.0,
        'issues': []
    }

    # Extract style from canvas
    canvas_style = extract_style(canvas)

    # Check palette consistency
    if len(reference.palette) > 0:
        matching_colors = 0
        for i in range(len(canvas_style.palette)):
            color = canvas_style.palette.get(i)
            # Check if similar color exists in reference
            for j in range(len(reference.palette)):
                ref_color = reference.palette.get(j)
                dist = sum(abs(color[k] - ref_color[k]) for k in range(3))
                if dist < 50:
                    matching_colors += 1
                    break

        if len(canvas_style.palette) > 0:
            result['palette_score'] = matching_colors / len(canvas_style.palette)
        else:
            result['palette_score'] = 1.0

        if result['palette_score'] < 0.5:
            result['issues'].append('Palette differs significantly from reference')

    # Check shading consistency
    shading_match = 1.0
    if canvas_style.shading.type != reference.shading.type:
        shading_match -= 0.3
        result['issues'].append(f'Shading type differs: {canvas_style.shading.type.value} vs {reference.shading.type.value}')

    if abs(canvas_style.shading.levels - reference.shading.levels) > 1:
        shading_match -= 0.2
        result['issues'].append(f'Shading levels differ: {canvas_style.shading.levels} vs {reference.shading.levels}')

    result['shading_score'] = max(0, shading_match)

    # Check outline consistency
    outline_match = 1.0
    if canvas_style.outline.type != reference.outline.type:
        outline_match -= 0.5
        result['issues'].append(f'Outline type differs: {canvas_style.outline.type.value} vs {reference.outline.type.value}')

    result['outline_score'] = max(0, outline_match)

    # Overall score
    result['overall_score'] = (
        result['palette_score'] * 0.4 +
        result['shading_score'] * 0.3 +
        result['outline_score'] * 0.3
    )

    return result


def fix_style_inconsistencies(canvas: Canvas, reference: ExtractedStyle) -> Canvas:
    """Fix style inconsistencies to match reference.

    Args:
        canvas: Canvas to fix
        reference: Reference style to match

    Returns:
        Fixed Canvas
    """
    # Apply full style transfer
    return apply_style(canvas, reference)


# ==================== Utility Functions ====================

def compare_styles(style1: ExtractedStyle, style2: ExtractedStyle) -> Dict[str, Any]:
    """Compare two extracted styles.

    Args:
        style1: First style
        style2: Second style

    Returns:
        Dict with comparison results
    """
    result = {
        'similarity': 0.0,
        'palette_match': 0.0,
        'shading_match': 0.0,
        'outline_match': 0.0,
        'differences': []
    }

    # Compare palettes
    if len(style1.palette) > 0 and len(style2.palette) > 0:
        matching = 0
        for i in range(min(len(style1.palette), len(style2.palette))):
            c1 = style1.palette.get(i)
            c2 = style2.palette.get(i)
            dist = sum(abs(c1[k] - c2[k]) for k in range(3))
            if dist < 50:
                matching += 1
        result['palette_match'] = matching / max(len(style1.palette), len(style2.palette))
    else:
        result['palette_match'] = 1.0 if len(style1.palette) == len(style2.palette) else 0.0

    # Compare shading
    if style1.shading.type == style2.shading.type:
        result['shading_match'] = 1.0
    else:
        result['shading_match'] = 0.5
        result['differences'].append('Different shading types')

    # Compare outlines
    if style1.outline.type == style2.outline.type:
        result['outline_match'] = 1.0
    else:
        result['outline_match'] = 0.5
        result['differences'].append('Different outline types')

    result['similarity'] = (
        result['palette_match'] * 0.4 +
        result['shading_match'] * 0.3 +
        result['outline_match'] * 0.3
    )

    return result


def blend_styles(style1: ExtractedStyle, style2: ExtractedStyle,
                blend_factor: float = 0.5) -> ExtractedStyle:
    """Blend two styles together.

    Args:
        style1: First style
        style2: Second style
        blend_factor: 0.0 = all style1, 1.0 = all style2

    Returns:
        Blended ExtractedStyle
    """
    result = ExtractedStyle()

    # Blend palettes
    max_colors = max(len(style1.palette), len(style2.palette))
    for i in range(max_colors):
        if i < len(style1.palette) and i < len(style2.palette):
            c1 = style1.palette.get(i)
            c2 = style2.palette.get(i)
            blended = lerp_color(c1, c2, blend_factor)
            result.palette.add(blended)
        elif i < len(style1.palette):
            result.palette.add(style1.palette.get(i))
        else:
            result.palette.add(style2.palette.get(i))

    # Use dominant shading style
    if blend_factor < 0.5:
        result.shading = style1.shading
    else:
        result.shading = style2.shading

    # Blend shading parameters
    result.shading.shadow_hue_shift = (
        style1.shading.shadow_hue_shift * (1 - blend_factor) +
        style2.shading.shadow_hue_shift * blend_factor
    )
    result.shading.highlight_hue_shift = (
        style1.shading.highlight_hue_shift * (1 - blend_factor) +
        style2.shading.highlight_hue_shift * blend_factor
    )

    # Use dominant outline style
    if blend_factor < 0.5:
        result.outline = style1.outline
    else:
        result.outline = style2.outline

    return result


def list_style_attributes() -> List[str]:
    """List all extractable style attributes."""
    return [
        'palette',
        'shading_type',
        'shading_levels',
        'shadow_hue_shift',
        'highlight_hue_shift',
        'outline_type',
        'outline_color',
        'outline_thickness',
        'anti_aliased',
        'pixel_density',
        'color_count',
    ]
