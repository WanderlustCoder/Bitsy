# Import Capabilities Design

## Overview

Phase 4.2 adds comprehensive import capabilities to Bitsy, enabling users to:
- Read Aseprite files (.ase/.aseprite)
- Automatically detect and split sprites from unaligned sheets
- Trace reference images into pixel art
- Enhanced palette extraction with color quantization

## Existing Capabilities

Already implemented:
- `editor/loader.py` - PNG reading with pure Python decoder
- `editor/palette_tools.py` - Basic palette extraction and remapping
- `export/spritesheet.py` - Grid-based sprite sheet splitting

## New Modules

### 1. `import_/aseprite.py` - Aseprite File Reader

Read .ase/.aseprite files (popular pixel art format).

```python
@dataclass
class AsepriteLayer:
    name: str
    visible: bool
    opacity: int
    blend_mode: str
    frames: List[Canvas]

@dataclass
class AsepriteFrame:
    duration: int  # milliseconds
    layers: Dict[str, Canvas]

@dataclass
class AsepriteFile:
    width: int
    height: int
    frames: List[AsepriteFrame]
    layers: List[AsepriteLayer]
    palette: Optional[Palette]
    tags: List[AsepriteTag]  # Animation tags

    def get_frame(self, index: int, flatten: bool = True) -> Canvas
    def get_animation(self, tag: Optional[str] = None) -> List[Canvas]
    def get_layer(self, name: str) -> List[Canvas]

def load_aseprite(path: str) -> AsepriteFile
def load_aseprite_from_bytes(data: bytes) -> AsepriteFile
```

Aseprite format specification: https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md

Key features:
- Read indexed and RGBA color modes
- Support layers and frames
- Extract animation tags
- Read embedded palettes
- Handle cel compression (zlib)

### 2. `import_/sprite_detect.py` - Automatic Sprite Detection

Detect individual sprites in unaligned or irregular sprite sheets.

```python
@dataclass
class DetectedSprite:
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    canvas: Canvas
    label: Optional[str]  # Auto-generated or from metadata

@dataclass
class DetectionConfig:
    min_size: int = 4  # Minimum sprite dimension
    max_size: int = 256  # Maximum sprite dimension
    background_color: Optional[Color] = None  # Auto-detect if None
    margin: int = 0  # Extra margin around detected sprites
    merge_nearby: bool = True  # Merge sprites close together
    merge_threshold: int = 2  # Max gap to merge

class SpriteDetector:
    def __init__(self, config: DetectionConfig = None)

    def detect(self, canvas: Canvas) -> List[DetectedSprite]
    def detect_background(self, canvas: Canvas) -> Color
    def find_connected_regions(self, canvas: Canvas, bg: Color) -> List[Region]

def detect_sprites(canvas: Canvas, **kwargs) -> List[DetectedSprite]
def split_by_color(canvas: Canvas, separator_color: Color) -> List[Canvas]
```

Detection algorithm:
1. Detect background color (most common edge color or transparency)
2. Find connected non-background regions using flood fill
3. Calculate bounding boxes for each region
4. Optionally merge nearby regions
5. Extract sprites with optional margin

### 3. `import_/tracer.py` - Reference Image Tracing

Convert reference images (photos, high-res art) into pixel art.

```python
@dataclass
class TraceConfig:
    target_width: int = 32
    target_height: Optional[int] = None  # Auto from aspect ratio
    color_count: int = 16
    outline: bool = True
    outline_color: Optional[Color] = None
    dither: bool = False
    smooth: bool = True
    preserve_details: bool = True

class ImageTracer:
    def __init__(self, config: TraceConfig = None)

    def trace(self, canvas: Canvas) -> Canvas
    def trace_with_palette(self, canvas: Canvas, palette: Palette) -> Canvas

    def _downsample(self, canvas: Canvas) -> Canvas
    def _quantize_colors(self, canvas: Canvas) -> Tuple[Canvas, Palette]
    def _detect_edges(self, canvas: Canvas) -> Canvas
    def _add_outlines(self, canvas: Canvas, edges: Canvas) -> Canvas

def trace_image(canvas: Canvas, width: int = 32, colors: int = 16) -> Canvas
def trace_to_palette(canvas: Canvas, palette: Palette, width: int = 32) -> Canvas
def auto_pixelate(canvas: Canvas, target_size: int = 32) -> Canvas
```

Tracing pipeline:
1. Downsample to target resolution (area averaging for quality)
2. Edge detection for outline preservation
3. Color quantization (median cut or k-means)
4. Optional dithering for gradients
5. Outline application on edges
6. Final cleanup pass

### 4. `import_/quantize.py` - Advanced Color Quantization

Better color reduction than simple k-means.

```python
class QuantizeMethod(Enum):
    MEDIAN_CUT = "median_cut"
    OCTREE = "octree"
    KMEANS = "kmeans"
    POPULARITY = "popularity"

@dataclass
class QuantizeConfig:
    method: QuantizeMethod = QuantizeMethod.MEDIAN_CUT
    color_count: int = 16
    preserve_exact: List[Color] = None  # Colors to keep exactly
    weight_saturation: float = 1.0  # Importance of saturated colors

class ColorQuantizer:
    def __init__(self, config: QuantizeConfig = None)

    def quantize(self, canvas: Canvas) -> Tuple[Canvas, Palette]
    def extract_palette(self, canvas: Canvas) -> Palette

    def _median_cut(self, colors: List[Color], n: int) -> List[Color]
    def _octree_quantize(self, colors: List[Color], n: int) -> List[Color]

def quantize_image(canvas: Canvas, colors: int = 16,
                   method: str = "median_cut") -> Tuple[Canvas, Palette]
def extract_palette(canvas: Canvas, colors: int = 16) -> Palette
```

## Module Organization

```
import_/
    __init__.py      # Public exports
    aseprite.py      # Aseprite file reader
    sprite_detect.py # Automatic sprite detection
    tracer.py        # Reference image tracing
    quantize.py      # Color quantization algorithms
```

## Integration with Existing Code

The new import module will:
- Use `Canvas` from `core/` for all image operations
- Use `Palette` from `core/palette.py` for color palettes
- Work with existing `editor/loader.py` for PNG loading
- Complement existing `editor/palette_tools.py` functionality

## Test Plan

- Test Aseprite reading with sample files (indexed, RGBA, layers, animations)
- Test sprite detection on various sheet layouts
- Test tracing with different source image types
- Test quantization algorithms for color accuracy
- Integration tests combining multiple features

## Dependencies

- Pure Python only (no external libraries)
- zlib for Aseprite cel decompression (standard library)
