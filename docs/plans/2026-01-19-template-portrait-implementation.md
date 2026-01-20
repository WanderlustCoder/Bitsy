# Template-Based Portrait System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a template-based portrait rendering system that composites pre-designed PNG templates to produce human-recognizable anime portraits.

**Architecture:** Templates (small PNGs with placeholder colors) are loaded, recolored with character palettes, and composited in layer order. Style profiles (JSON) define proportions and available templates.

**Tech Stack:** Python, PNG loading via existing core/png_writer.py, JSON for metadata/profiles

---

## Phase 1: Foundation

### Task 1: Create Module Structure

**Files:**
- Create: `generators/portrait_v2/__init__.py`
- Create: `generators/portrait_v2/loader.py`
- Create: `generators/portrait_v2/recolor.py`
- Create: `generators/portrait_v2/composer.py`

**Step 1: Create the module directory and files**

```bash
mkdir -p generators/portrait_v2
touch generators/portrait_v2/__init__.py
touch generators/portrait_v2/loader.py
touch generators/portrait_v2/recolor.py
touch generators/portrait_v2/composer.py
```

**Step 2: Add module exports to __init__.py**

```python
"""
Template-Based Portrait Generator v2

A flexible portrait system using pre-designed templates
instead of pure procedural generation.
"""

from .composer import TemplatePortraitGenerator
from .loader import TemplateLoader
from .recolor import recolor_template

__all__ = [
    "TemplatePortraitGenerator",
    "TemplateLoader",
    "recolor_template",
]
```

**Step 3: Commit**

```bash
git add generators/portrait_v2/
git commit -m "feat: create portrait_v2 module structure"
```

---

### Task 2: Implement Template Loader

**Files:**
- Modify: `generators/portrait_v2/loader.py`
- Create: `tests/test_portrait_v2/test_loader.py`

**Step 1: Write the failing test**

```python
"""Tests for template loader."""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.loader import TemplateLoader, Template


class TestTemplateLoader:
    def test_load_template_returns_template_object(self, tmp_path):
        """Loader returns a Template with pixel data."""
        # Create a minimal 2x2 PNG for testing
        from core.canvas import Canvas
        canvas = Canvas(2, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))  # Red
        canvas.set_pixel_solid(1, 0, (0, 255, 0, 255))  # Green
        canvas.set_pixel_solid(0, 1, (0, 0, 255, 255))  # Blue
        canvas.set_pixel_solid(1, 1, (255, 255, 0, 255))  # Yellow

        png_path = tmp_path / "test.png"
        canvas.save(str(png_path))

        # Create metadata
        meta_path = tmp_path / "test.json"
        meta_path.write_text('{"name": "test", "anchor": [1, 1]}')

        loader = TemplateLoader(str(tmp_path))
        template = loader.load("test")

        assert template is not None
        assert template.name == "test"
        assert template.width == 2
        assert template.height == 2
        assert template.anchor == (1, 1)

    def test_load_template_without_metadata_uses_defaults(self, tmp_path):
        """Template without .json uses default anchor at center."""
        from core.canvas import Canvas
        canvas = Canvas(4, 4)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))

        png_path = tmp_path / "nodata.png"
        canvas.save(str(png_path))

        loader = TemplateLoader(str(tmp_path))
        template = loader.load("nodata")

        assert template.anchor == (2, 2)  # Center of 4x4
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_portrait_v2/test_loader.py -v
```

Expected: FAIL with import error

**Step 3: Create tests directory**

```bash
mkdir -p tests/test_portrait_v2
touch tests/test_portrait_v2/__init__.py
```

**Step 4: Implement the loader**

```python
"""Template loading and caching."""
import os
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from core.png_writer import load_png


@dataclass
class Template:
    """A loaded template with pixel data and metadata."""
    name: str
    pixels: List[List[Tuple[int, int, int, int]]]  # [y][x] -> RGBA
    width: int
    height: int
    anchor: Tuple[int, int]  # Attachment point
    symmetric: bool = False
    flip_for_right: bool = False

    def get_pixel(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        """Get pixel at position, or None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None


class TemplateLoader:
    """Loads and caches templates from a directory."""

    def __init__(self, base_path: str):
        """
        Initialize loader with base template directory.

        Args:
            base_path: Path to template directory
        """
        self.base_path = base_path
        self._cache: Dict[str, Template] = {}

    def load(self, name: str, subdir: str = "") -> Template:
        """
        Load a template by name.

        Args:
            name: Template name (without extension)
            subdir: Optional subdirectory (e.g., "faces", "eyes")

        Returns:
            Template object with pixel data
        """
        cache_key = f"{subdir}/{name}" if subdir else name

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Build paths
        if subdir:
            dir_path = os.path.join(self.base_path, subdir)
        else:
            dir_path = self.base_path

        png_path = os.path.join(dir_path, f"{name}.png")
        json_path = os.path.join(dir_path, f"{name}.json")

        # Load PNG
        if not os.path.exists(png_path):
            raise FileNotFoundError(f"Template not found: {png_path}")

        pixels = load_png(png_path)
        height = len(pixels)
        width = len(pixels[0]) if height > 0 else 0

        # Load metadata or use defaults
        metadata = self._load_metadata(json_path, width, height)

        template = Template(
            name=name,
            pixels=pixels,
            width=width,
            height=height,
            anchor=tuple(metadata.get("anchor", [width // 2, height // 2])),
            symmetric=metadata.get("symmetric", False),
            flip_for_right=metadata.get("flip_for_right", False),
        )

        self._cache[cache_key] = template
        return template

    def _load_metadata(self, json_path: str, width: int, height: int) -> dict:
        """Load metadata from JSON or return defaults."""
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        return {
            "anchor": [width // 2, height // 2],
            "symmetric": False,
            "flip_for_right": False,
        }

    def clear_cache(self):
        """Clear the template cache."""
        self._cache.clear()
```

**Step 5: Add load_png to core/png_writer.py if not exists**

Check if `load_png` exists:
```bash
grep "def load_png" core/png_writer.py
```

If not found, add this function to `core/png_writer.py`:

```python
def load_png(filepath: str) -> List[List[Tuple[int, int, int, int]]]:
    """
    Load a PNG file and return pixel data.

    Args:
        filepath: Path to PNG file

    Returns:
        2D list of RGBA tuples [y][x]
    """
    import zlib
    import struct

    with open(filepath, 'rb') as f:
        # Verify PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")

        width = height = 0
        bit_depth = color_type = 0
        compressed_data = b''

        while True:
            chunk_len = struct.unpack('>I', f.read(4))[0]
            chunk_type = f.read(4)
            chunk_data = f.read(chunk_len)
            f.read(4)  # CRC

            if chunk_type == b'IHDR':
                width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
            elif chunk_type == b'IDAT':
                compressed_data += chunk_data
            elif chunk_type == b'IEND':
                break

        # Decompress
        raw_data = zlib.decompress(compressed_data)

        # Parse pixel data (assumes RGBA, 8-bit)
        pixels = []
        bytes_per_pixel = 4 if color_type == 6 else 3
        row_size = 1 + width * bytes_per_pixel  # +1 for filter byte

        for y in range(height):
            row_start = y * row_size + 1  # Skip filter byte
            row = []
            for x in range(width):
                px_start = row_start + x * bytes_per_pixel
                r = raw_data[px_start]
                g = raw_data[px_start + 1]
                b = raw_data[px_start + 2]
                a = raw_data[px_start + 3] if bytes_per_pixel == 4 else 255
                row.append((r, g, b, a))
            pixels.append(row)

        return pixels
```

**Step 6: Run test to verify it passes**

```bash
pytest tests/test_portrait_v2/test_loader.py -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add generators/portrait_v2/loader.py tests/test_portrait_v2/ core/png_writer.py
git commit -m "feat: implement template loader with PNG and metadata support"
```

---

### Task 3: Implement Recolor System

**Files:**
- Modify: `generators/portrait_v2/recolor.py`
- Create: `tests/test_portrait_v2/test_recolor.py`

**Step 1: Write the failing test**

```python
"""Tests for template recoloring."""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.recolor import recolor_template, PLACEHOLDER_PALETTE


class TestRecolor:
    def test_recolor_swaps_placeholder_colors(self):
        """Recolor replaces placeholder red with target color."""
        # Simple 2x2 template with placeholder colors
        pixels = [
            [(255, 0, 0, 255), (200, 0, 0, 255)],  # Base red, shadow red
            [(150, 0, 0, 255), (0, 0, 0, 0)],      # Deep shadow, transparent
        ]

        # Target skin palette
        target_palette = [
            (232, 190, 160, 255),  # Base skin
            (200, 150, 130, 255),  # Shadow 1
            (170, 120, 100, 255),  # Shadow 2
        ]

        result = recolor_template(pixels, target_palette)

        assert result[0][0] == (232, 190, 160, 255)  # Base replaced
        assert result[0][1] == (200, 150, 130, 255)  # Shadow 1 replaced
        assert result[1][0] == (170, 120, 100, 255)  # Shadow 2 replaced
        assert result[1][1] == (0, 0, 0, 0)          # Transparent unchanged

    def test_recolor_preserves_unknown_colors(self):
        """Colors not in placeholder palette are preserved."""
        pixels = [
            [(128, 128, 128, 255)],  # Gray - not a placeholder
        ]

        target_palette = [(255, 200, 150, 255)]
        result = recolor_template(pixels, target_palette)

        assert result[0][0] == (128, 128, 128, 255)  # Unchanged
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_portrait_v2/test_recolor.py -v
```

Expected: FAIL with import error

**Step 3: Implement the recolor system**

```python
"""Template recoloring with palette swapping."""
from typing import List, Tuple, Dict, Optional

# Placeholder palette used in templates
# Templates are drawn with these colors, then swapped at runtime
PLACEHOLDER_PALETTE = {
    "base":       (255, 0, 0, 255),      # Index 1 - Base color
    "shadow1":    (200, 0, 0, 255),      # Index 2 - Shadow 1
    "shadow2":    (150, 0, 0, 255),      # Index 3 - Shadow 2 (deep)
    "highlight1": (255, 100, 100, 255),  # Index 4 - Highlight 1
    "highlight2": (255, 180, 180, 255),  # Index 5 - Highlight 2 (bright)
    "outline":    (100, 0, 0, 255),      # Index 6 - Outline
    "secondary":  (0, 255, 0, 255),      # Index 7 - Secondary color
}

# Ordered list for index-based access
PLACEHOLDER_LIST = [
    (255, 0, 0, 255),      # 0 - Base
    (200, 0, 0, 255),      # 1 - Shadow 1
    (150, 0, 0, 255),      # 2 - Shadow 2
    (255, 100, 100, 255),  # 3 - Highlight 1
    (255, 180, 180, 255),  # 4 - Highlight 2
    (100, 0, 0, 255),      # 5 - Outline
    (0, 255, 0, 255),      # 6 - Secondary
]


def color_distance(c1: Tuple[int, ...], c2: Tuple[int, ...]) -> int:
    """Calculate squared RGB distance between colors."""
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3]))


def find_placeholder_index(color: Tuple[int, int, int, int],
                           threshold: int = 100) -> Optional[int]:
    """
    Find which placeholder index a color matches.

    Args:
        color: RGBA color to check
        threshold: Maximum squared distance to count as match

    Returns:
        Placeholder index (0-6) or None if no match
    """
    if color[3] < 32:  # Transparent
        return None

    for i, placeholder in enumerate(PLACEHOLDER_LIST):
        if color_distance(color, placeholder) < threshold:
            return i
    return None


def recolor_template(
    pixels: List[List[Tuple[int, int, int, int]]],
    target_palette: List[Tuple[int, int, int, int]],
    secondary_palette: Optional[List[Tuple[int, int, int, int]]] = None
) -> List[List[Tuple[int, int, int, int]]]:
    """
    Recolor a template by swapping placeholder colors with target palette.

    Args:
        pixels: 2D pixel array from template
        target_palette: Colors to replace placeholders with
                       [base, shadow1, shadow2, highlight1, highlight2, outline]
        secondary_palette: Optional separate palette for secondary color

    Returns:
        New 2D pixel array with colors replaced
    """
    height = len(pixels)
    width = len(pixels[0]) if height > 0 else 0

    result = []
    for y in range(height):
        row = []
        for x in range(width):
            color = pixels[y][x]

            # Check if transparent
            if color[3] < 32:
                row.append(color)
                continue

            # Find placeholder match
            idx = find_placeholder_index(color)

            if idx is not None:
                # Check if it's the secondary color slot
                if idx == 6 and secondary_palette:
                    # Use secondary palette base
                    new_color = secondary_palette[0] if secondary_palette else color
                elif idx < len(target_palette):
                    new_color = target_palette[idx]
                else:
                    new_color = color

                # Preserve original alpha
                new_color = (new_color[0], new_color[1], new_color[2], color[3])
                row.append(new_color)
            else:
                # Not a placeholder - keep original
                row.append(color)

        result.append(row)

    return result


def create_skin_palette(base_color: Tuple[int, int, int],
                        use_hue_shift: bool = True) -> List[Tuple[int, int, int, int]]:
    """
    Create a 6-color skin palette from a base color.

    Args:
        base_color: RGB base skin tone
        use_hue_shift: If True, shadows shift toward cool, highlights toward warm

    Returns:
        6-color palette [base, shadow1, shadow2, highlight1, highlight2, outline]
    """
    r, g, b = base_color

    if use_hue_shift:
        # Shadows: darken and shift toward purple/blue
        shadow1 = (
            int(r * 0.82),
            int(g * 0.78),
            int(b * 0.85),
            255
        )
        shadow2 = (
            int(r * 0.65),
            int(g * 0.58),
            int(b * 0.68),
            255
        )
        # Highlights: brighten and shift toward yellow/warm
        highlight1 = (
            min(255, int(r * 1.08)),
            min(255, int(g * 1.05)),
            min(255, int(b * 0.98)),
            255
        )
        highlight2 = (
            min(255, int(r * 1.15)),
            min(255, int(g * 1.12)),
            min(255, int(b * 1.02)),
            255
        )
    else:
        # Simple luminance-only shading
        shadow1 = (int(r * 0.8), int(g * 0.8), int(b * 0.8), 255)
        shadow2 = (int(r * 0.6), int(g * 0.6), int(b * 0.6), 255)
        highlight1 = (min(255, int(r * 1.1)), min(255, int(g * 1.1)), min(255, int(b * 1.1)), 255)
        highlight2 = (min(255, int(r * 1.2)), min(255, int(g * 1.2)), min(255, int(b * 1.2)), 255)

    outline = (int(r * 0.4), int(g * 0.35), int(b * 0.4), 255)

    return [
        (r, g, b, 255),  # Base
        shadow1,
        shadow2,
        highlight1,
        highlight2,
        outline,
    ]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_portrait_v2/test_recolor.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add generators/portrait_v2/recolor.py tests/test_portrait_v2/test_recolor.py
git commit -m "feat: implement template recolor system with palette swapping"
```

---

### Task 4: Create Template Directory Structure

**Files:**
- Create: `templates/anime_standard/profile.json`
- Create: `templates/anime_standard/faces/` (directory)
- Create: `templates/anime_standard/eyes/` (directory)
- Create: `templates/anime_standard/hair/` (directory)
- Create: `templates/anime_standard/bodies/` (directory)

**Step 1: Create directory structure**

```bash
mkdir -p templates/anime_standard/faces
mkdir -p templates/anime_standard/eyes
mkdir -p templates/anime_standard/noses
mkdir -p templates/anime_standard/mouths
mkdir -p templates/anime_standard/hair
mkdir -p templates/anime_standard/bodies
```

**Step 2: Create style profile**

Create `templates/anime_standard/profile.json`:

```json
{
  "name": "anime_standard",
  "description": "Standard anime style portrait",

  "canvas_size": [80, 128],

  "proportions": {
    "head_y": 0.08,
    "head_height_ratio": 0.38,
    "face_width_ratio": 0.35,
    "eye_y": 0.42,
    "nose_y": 0.58,
    "mouth_y": 0.68,
    "eye_spacing": 0.24
  },

  "templates": {
    "faces": ["oval"],
    "eyes": ["large"],
    "noses": ["dot"],
    "mouths": ["neutral"],
    "hair_back": ["wavy_back"],
    "hair_front": ["wavy_front"],
    "bodies": ["neutral", "holding"]
  },

  "coloring": {
    "use_hue_shift": true,
    "shadow_hue_shift": -15,
    "rim_light_color": [180, 210, 255],
    "rim_light_intensity": 0.7
  },

  "post_processing": {
    "outline": "thin",
    "outline_color": [40, 30, 50],
    "selective_aa": true
  }
}
```

**Step 3: Commit**

```bash
git add templates/
git commit -m "feat: create anime_standard template directory structure"
```

---

## Phase 2: Core Templates

### Task 5: Create Face Template

**Files:**
- Create: `templates/anime_standard/faces/oval.png`
- Create: `templates/anime_standard/faces/oval.json`

**Step 1: Create a simple oval face template programmatically**

Create a script `scripts/create_face_template.py`:

```python
#!/usr/bin/env python3
"""Create the oval face template."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas

# Template size
WIDTH, HEIGHT = 32, 40

# Placeholder colors
BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
OUTLINE = (100, 0, 0, 255)

def draw_oval_face():
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = WIDTH // 2, HEIGHT // 2
    rx, ry = 13, 18  # Radii for oval

    # Draw filled oval with shading
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Check if inside oval
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            dist = dx * dx + dy * dy

            if dist <= 1.0:
                # Inside face
                if dist > 0.85:
                    # Edge - outline
                    canvas.set_pixel_solid(x, y, OUTLINE)
                elif x < cx - 3 and dist > 0.5:
                    # Left shadow
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif y > cy + 5:
                    # Chin shadow
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 2 and y < cy - 5:
                    # Right highlight (forehead)
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                else:
                    # Base skin
                    canvas.set_pixel_solid(x, y, BASE)

    # Save
    os.makedirs("templates/anime_standard/faces", exist_ok=True)
    canvas.save("templates/anime_standard/faces/oval.png")
    print("Created: templates/anime_standard/faces/oval.png")

if __name__ == "__main__":
    draw_oval_face()
```

**Step 2: Run the script**

```bash
python3 scripts/create_face_template.py
```

**Step 3: Create metadata**

Create `templates/anime_standard/faces/oval.json`:

```json
{
  "name": "oval",
  "anchor": [16, 20],
  "bounds": {
    "eye_region_y": 14,
    "nose_region_y": 22,
    "mouth_region_y": 28
  }
}
```

**Step 4: Commit**

```bash
git add templates/anime_standard/faces/ scripts/create_face_template.py
git commit -m "feat: create oval face template"
```

---

### Task 6: Create Eye Template

**Files:**
- Create: `templates/anime_standard/eyes/large.png`
- Create: `templates/anime_standard/eyes/large.json`

**Step 1: Create eye template programmatically**

Create `scripts/create_eye_template.py`:

```python
#!/usr/bin/env python3
"""Create the large anime eye template."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas

# Single eye template - will be mirrored for right eye
WIDTH, HEIGHT = 12, 10

# Placeholder colors
BASE = (255, 0, 0, 255)        # Iris base
SHADOW1 = (200, 0, 0, 255)    # Iris dark (top)
SHADOW2 = (150, 0, 0, 255)    # Pupil
HIGHLIGHT = (255, 100, 100, 255)  # Iris highlight
HIGHLIGHT2 = (255, 180, 180, 255) # Catchlight
OUTLINE = (100, 0, 0, 255)    # Eyelid line
SECONDARY = (0, 255, 0, 255)  # Sclera (white)

def draw_anime_eye():
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = 6, 5

    # Sclera (eye white) - secondary color
    for y in range(2, 9):
        for x in range(1, 11):
            dx = abs(x - cx)
            dy = abs(y - cy)
            if dx < 5 and dy < 4 - dx * 0.3:
                canvas.set_pixel_solid(x, y, SECONDARY)

    # Iris - large oval
    iris_cx, iris_cy = 6, 5
    iris_rx, iris_ry = 3.5, 3.5

    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = (x - iris_cx) / iris_rx
            dy = (y - iris_cy) / iris_ry
            dist = dx * dx + dy * dy

            if dist <= 1.0:
                if y < iris_cy - 1:
                    # Top of iris - darker
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif dist > 0.3 and dist <= 0.5:
                    # Mid ring
                    canvas.set_pixel_solid(x, y, BASE)
                elif dist <= 0.3:
                    # Pupil
                    canvas.set_pixel_solid(x, y, SHADOW2)
                else:
                    # Outer iris
                    canvas.set_pixel_solid(x, y, BASE)

    # Catchlights
    canvas.set_pixel_solid(4, 3, HIGHLIGHT2)
    canvas.set_pixel_solid(5, 3, HIGHLIGHT2)
    canvas.set_pixel_solid(7, 6, HIGHLIGHT)

    # Upper eyelid line
    for x in range(2, 10):
        canvas.set_pixel_solid(x, 1, OUTLINE)
    canvas.set_pixel_solid(1, 2, OUTLINE)
    canvas.set_pixel_solid(10, 2, OUTLINE)

    # Lower eyelid hint
    canvas.set_pixel_solid(3, 8, OUTLINE)
    canvas.set_pixel_solid(8, 8, OUTLINE)

    # Save
    os.makedirs("templates/anime_standard/eyes", exist_ok=True)
    canvas.save("templates/anime_standard/eyes/large.png")
    print("Created: templates/anime_standard/eyes/large.png")

if __name__ == "__main__":
    draw_anime_eye()
```

**Step 2: Run the script**

```bash
python3 scripts/create_eye_template.py
```

**Step 3: Create metadata**

Create `templates/anime_standard/eyes/large.json`:

```json
{
  "name": "large",
  "anchor": [6, 5],
  "symmetric": true,
  "flip_for_right": true,
  "iris_color_slots": [0, 1, 2, 3, 4],
  "sclera_color_slot": 6
}
```

**Step 4: Commit**

```bash
git add templates/anime_standard/eyes/ scripts/create_eye_template.py
git commit -m "feat: create large anime eye template"
```

---

### Task 7: Create Nose and Mouth Templates

**Files:**
- Create: `templates/anime_standard/noses/dot.png`
- Create: `templates/anime_standard/mouths/neutral.png`

**Step 1: Create nose and mouth templates**

Create `scripts/create_feature_templates.py`:

```python
#!/usr/bin/env python3
"""Create nose and mouth templates."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas

SHADOW1 = (200, 0, 0, 255)
OUTLINE = (100, 0, 0, 255)

def create_dot_nose():
    """Minimal anime nose - just a small shadow."""
    canvas = Canvas(4, 3)

    # Small triangular shadow
    canvas.set_pixel_solid(1, 1, SHADOW1)
    canvas.set_pixel_solid(2, 1, SHADOW1)
    canvas.set_pixel_solid(2, 2, SHADOW1)

    os.makedirs("templates/anime_standard/noses", exist_ok=True)
    canvas.save("templates/anime_standard/noses/dot.png")
    print("Created: templates/anime_standard/noses/dot.png")

def create_neutral_mouth():
    """Simple neutral mouth line."""
    canvas = Canvas(8, 4)

    # Simple line
    for x in range(2, 6):
        canvas.set_pixel_solid(x, 1, OUTLINE)

    # Slight shadow below
    for x in range(3, 5):
        canvas.set_pixel_solid(x, 2, SHADOW1)

    os.makedirs("templates/anime_standard/mouths", exist_ok=True)
    canvas.save("templates/anime_standard/mouths/neutral.png")
    print("Created: templates/anime_standard/mouths/neutral.png")

if __name__ == "__main__":
    create_dot_nose()
    create_neutral_mouth()
```

**Step 2: Run the script**

```bash
python3 scripts/create_feature_templates.py
```

**Step 3: Create metadata files**

Create `templates/anime_standard/noses/dot.json`:
```json
{"name": "dot", "anchor": [2, 1]}
```

Create `templates/anime_standard/mouths/neutral.json`:
```json
{"name": "neutral", "anchor": [4, 1]}
```

**Step 4: Commit**

```bash
git add templates/anime_standard/noses/ templates/anime_standard/mouths/ scripts/create_feature_templates.py
git commit -m "feat: create nose and mouth templates"
```

---

## Phase 3: Composer

### Task 8: Implement Template Composer

**Files:**
- Modify: `generators/portrait_v2/composer.py`
- Create: `tests/test_portrait_v2/test_composer.py`

**Step 1: Write the failing test**

```python
"""Tests for template composer."""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.composer import TemplatePortraitGenerator
from core.canvas import Canvas


class TestComposer:
    def test_composer_produces_canvas(self):
        """Composer generates a canvas with content."""
        generator = TemplatePortraitGenerator(
            style_path="templates/anime_standard",
            skin_color=(232, 190, 160),
            eye_color=(100, 80, 60),
        )

        canvas = generator.render()

        assert isinstance(canvas, Canvas)
        assert canvas.width == 80
        assert canvas.height == 128

        # Should have some non-transparent pixels
        has_content = False
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    has_content = True
                    break
            if has_content:
                break

        assert has_content, "Canvas should have visible content"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_portrait_v2/test_composer.py -v
```

Expected: FAIL

**Step 3: Implement the composer**

```python
"""Template composition and portrait generation."""
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from generators.portrait_v2.loader import TemplateLoader, Template
from generators.portrait_v2.recolor import recolor_template, create_skin_palette


@dataclass
class StyleProfile:
    """Loaded style profile configuration."""
    name: str
    canvas_size: Tuple[int, int]
    proportions: Dict[str, float]
    templates: Dict[str, List[str]]
    coloring: Dict[str, any]
    post_processing: Dict[str, any]


class TemplatePortraitGenerator:
    """
    Generate portraits by compositing pre-designed templates.
    """

    def __init__(
        self,
        style_path: str = "templates/anime_standard",
        skin_color: Tuple[int, int, int] = (232, 190, 160),
        eye_color: Tuple[int, int, int] = (100, 80, 60),
        hair_color: Tuple[int, int, int] = (60, 40, 30),
        seed: Optional[int] = None,
    ):
        """
        Initialize the generator.

        Args:
            style_path: Path to style template directory
            skin_color: RGB base skin color
            eye_color: RGB iris color
            hair_color: RGB hair color
            seed: Random seed for variation
        """
        self.style_path = style_path
        self.skin_color = skin_color
        self.eye_color = eye_color
        self.hair_color = hair_color

        # Load style profile
        self.profile = self._load_profile()

        # Initialize loader
        self.loader = TemplateLoader(style_path)

        # Generate palettes
        self.skin_palette = create_skin_palette(skin_color,
            use_hue_shift=self.profile.coloring.get("use_hue_shift", True))
        self.eye_palette = create_skin_palette(eye_color, use_hue_shift=True)
        self.hair_palette = create_skin_palette(hair_color, use_hue_shift=True)

        # Sclera palette (white with slight warmth)
        self.sclera_palette = [
            (250, 248, 245, 255),
            (235, 230, 225, 255),
            (220, 210, 205, 255),
            (255, 252, 250, 255),
            (255, 255, 255, 255),
            (200, 190, 185, 255),
        ]

    def _load_profile(self) -> StyleProfile:
        """Load the style profile JSON."""
        profile_path = os.path.join(self.style_path, "profile.json")

        with open(profile_path, 'r') as f:
            data = json.load(f)

        return StyleProfile(
            name=data["name"],
            canvas_size=tuple(data["canvas_size"]),
            proportions=data["proportions"],
            templates=data["templates"],
            coloring=data.get("coloring", {}),
            post_processing=data.get("post_processing", {}),
        )

    def render(self) -> Canvas:
        """
        Render the portrait.

        Returns:
            Canvas with composited portrait
        """
        width, height = self.profile.canvas_size
        canvas = Canvas(width, height)

        # Calculate positions
        props = self.profile.proportions

        head_y = int(height * props.get("head_y", 0.08))
        head_height = int(height * props.get("head_height_ratio", 0.38))
        face_width = int(width * props.get("face_width_ratio", 0.35))

        face_cx = width // 2
        face_cy = head_y + head_height // 2

        # Render layers (back to front)

        # 1. Face base
        self._render_face(canvas, face_cx, face_cy)

        # 2. Eyes
        eye_y = head_y + int(head_height * props.get("eye_y", 0.42))
        eye_spacing = int(face_width * props.get("eye_spacing", 0.24))
        self._render_eyes(canvas, face_cx, eye_y, eye_spacing)

        # 3. Nose
        nose_y = head_y + int(head_height * props.get("nose_y", 0.58))
        self._render_nose(canvas, face_cx, nose_y)

        # 4. Mouth
        mouth_y = head_y + int(head_height * props.get("mouth_y", 0.68))
        self._render_mouth(canvas, face_cx, mouth_y)

        return canvas

    def _render_face(self, canvas: Canvas, cx: int, cy: int) -> None:
        """Render the face template."""
        face_templates = self.profile.templates.get("faces", ["oval"])
        template = self.loader.load(face_templates[0], "faces")

        # Recolor with skin palette
        recolored = recolor_template(template.pixels, self.skin_palette)

        # Composite onto canvas
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       cy - template.anchor[1])

    def _render_eyes(self, canvas: Canvas, cx: int, y: int, spacing: int) -> None:
        """Render both eyes."""
        eye_templates = self.profile.templates.get("eyes", ["large"])
        template = self.loader.load(eye_templates[0], "eyes")

        # Recolor iris with eye palette, sclera with white
        recolored = recolor_template(template.pixels, self.eye_palette,
                                     secondary_palette=self.sclera_palette)

        # Left eye
        left_x = cx - spacing - template.anchor[0]
        self._composite(canvas, recolored, left_x, y - template.anchor[1])

        # Right eye (flipped if needed)
        right_x = cx + spacing - (template.width - template.anchor[0])
        if template.flip_for_right:
            flipped = self._flip_horizontal(recolored)
            self._composite(canvas, flipped, right_x, y - template.anchor[1])
        else:
            self._composite(canvas, recolored, right_x, y - template.anchor[1])

    def _render_nose(self, canvas: Canvas, cx: int, y: int) -> None:
        """Render the nose."""
        nose_templates = self.profile.templates.get("noses", ["dot"])
        template = self.loader.load(nose_templates[0], "noses")

        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _render_mouth(self, canvas: Canvas, cx: int, y: int) -> None:
        """Render the mouth."""
        mouth_templates = self.profile.templates.get("mouths", ["neutral"])
        template = self.loader.load(mouth_templates[0], "mouths")

        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _composite(self, canvas: Canvas,
                   pixels: List[List[Tuple[int, int, int, int]]],
                   x: int, y: int) -> None:
        """Composite pixels onto canvas with alpha blending."""
        for py, row in enumerate(pixels):
            for px, color in enumerate(row):
                if color[3] > 0:  # Not transparent
                    canvas_x = x + px
                    canvas_y = y + py
                    if 0 <= canvas_x < canvas.width and 0 <= canvas_y < canvas.height:
                        if color[3] >= 255:
                            canvas.set_pixel_solid(canvas_x, canvas_y, color)
                        else:
                            # Alpha blend
                            existing = canvas.get_pixel(canvas_x, canvas_y)
                            if existing:
                                alpha = color[3] / 255
                                blended = (
                                    int(color[0] * alpha + existing[0] * (1 - alpha)),
                                    int(color[1] * alpha + existing[1] * (1 - alpha)),
                                    int(color[2] * alpha + existing[2] * (1 - alpha)),
                                    255
                                )
                                canvas.set_pixel_solid(canvas_x, canvas_y, blended)
                            else:
                                canvas.set_pixel_solid(canvas_x, canvas_y, color)

    def _flip_horizontal(self,
                         pixels: List[List[Tuple[int, int, int, int]]]
                         ) -> List[List[Tuple[int, int, int, int]]]:
        """Flip pixel array horizontally."""
        return [list(reversed(row)) for row in pixels]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_portrait_v2/test_composer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add generators/portrait_v2/composer.py tests/test_portrait_v2/test_composer.py
git commit -m "feat: implement template composer with face rendering"
```

---

### Task 9: Create Test Script and Verify Output

**Files:**
- Create: `scripts/test_template_portrait.py`

**Step 1: Create test script**

```python
#!/usr/bin/env python3
"""Test the template-based portrait generator."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait_v2 import TemplatePortraitGenerator


def main():
    print("=" * 60)
    print("TEMPLATE PORTRAIT TEST")
    print("=" * 60)

    # Generate a test portrait
    generator = TemplatePortraitGenerator(
        style_path="templates/anime_standard",
        skin_color=(232, 190, 160),  # Light skin
        eye_color=(80, 60, 180),     # Purple eyes
        hair_color=(140, 100, 180),  # Purple hair
    )

    canvas = generator.render()

    # Save
    output_path = "output/test_template_portrait.png"
    canvas.save(output_path)

    print(f"Saved to: {output_path}")
    print(f"Canvas size: {canvas.width}x{canvas.height}")

    # Count colors
    colors = set()
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                colors.add(pixel)

    print(f"Total colors: {len(colors)}")
    print()
    print("View output/test_template_portrait.png")


if __name__ == "__main__":
    main()
```

**Step 2: Run the test**

```bash
python3 scripts/test_template_portrait.py
```

**Step 3: Verify the output visually**

Check `output/test_template_portrait.png` - should show a basic face with eyes, nose, mouth.

**Step 4: Commit**

```bash
git add scripts/test_template_portrait.py
git commit -m "feat: add template portrait test script"
```

---

## Phase 4-6: Hair, Body, and Polish

> **Note:** Phases 4-6 follow the same pattern - create templates programmatically, add metadata, integrate into composer. These will be detailed in follow-up tasks once the foundation is verified working.

### Task 10 (Phase 4): Create Hair Templates
### Task 11 (Phase 4): Create Body Templates
### Task 12 (Phase 4): Integrate Hair and Body into Composer
### Task 13 (Phase 5): Add Rim Lighting Post-Processing
### Task 14 (Phase 5): Add Outline Support
### Task 15 (Phase 6): Create PortraitConfig Adapter

---

## Verification

After completing Tasks 1-9, run:

```bash
python3 scripts/test_template_portrait.py
```

Compare `output/test_template_portrait.png` to `UserExamples/HighRes.png`:
- [ ] Face is recognizable as a face
- [ ] Eyes are positioned correctly
- [ ] Nose and mouth are visible and centered
- [ ] Colors are applied correctly

If the basic face looks correct, proceed to Phase 4 (Hair & Body).
