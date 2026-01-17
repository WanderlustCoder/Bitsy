# Advanced Effects Design (Phase 4.1)

## Overview

Extend Bitsy's effects system with shader-like post-processing, glow/bloom, color grading, displacement effects, and palette cycling animations.

## Architecture

Build on existing `effects/` module structure:

```
effects/
├── __init__.py          # Updated exports
├── post_process.py      # NEW: Shader-like effects
├── glow.py              # NEW: Glow and bloom
├── color_grading.py     # NEW: LUTs and color grading
├── displacement.py      # NEW: Displacement effects
├── palette_cycle.py     # NEW: Palette cycling animations
├── particles.py         # Existing
├── trails.py            # Existing
├── screen.py            # Existing
└── weather.py           # Existing
```

## Components

### 1. Post-Processing Effects (`post_process.py`)

Shader-like pixel manipulation using convolution kernels and pixel operations.

```python
class PostProcessor:
    """Applies post-processing effects to canvases."""

    def apply(self, canvas: Canvas, effect: Effect) -> Canvas:
        """Apply a post-processing effect."""

class Effect(ABC):
    """Base class for post-processing effects."""

    @abstractmethod
    def process(self, canvas: Canvas) -> Canvas:
        pass

# Convolution-based effects
class GaussianBlur(Effect):
    """Gaussian blur with configurable radius."""
    def __init__(self, radius: int = 2)

class BoxBlur(Effect):
    """Fast box blur."""
    def __init__(self, radius: int = 2)

class Sharpen(Effect):
    """Sharpen image details."""
    def __init__(self, amount: float = 1.0)

class Emboss(Effect):
    """Emboss/relief effect."""
    def __init__(self, direction: str = "top-left", strength: float = 1.0)

class EdgeDetect(Effect):
    """Edge detection (Sobel, Prewitt, etc.)."""
    def __init__(self, method: str = "sobel")

# Pixel-level effects
class Pixelate(Effect):
    """Mosaic/pixelation effect."""
    def __init__(self, block_size: int = 4)

class Posterize(Effect):
    """Reduce color levels."""
    def __init__(self, levels: int = 4)

class Dither(Effect):
    """Apply dithering patterns."""
    def __init__(self, palette: List[Color], method: str = "ordered")
```

### 2. Glow and Bloom (`glow.py`)

Light bleeding effects for bright areas.

```python
class GlowEffect:
    """Add glow around bright pixels or specific colors."""

    def __init__(
        self,
        threshold: int = 200,        # Brightness threshold
        radius: int = 3,             # Glow spread
        intensity: float = 0.5,      # Glow brightness
        color: Optional[Color] = None  # Force glow color
    )

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply glow effect."""

class BloomEffect:
    """Bloom effect (bright areas bleed light)."""

    def __init__(
        self,
        threshold: int = 180,
        blur_radius: int = 4,
        intensity: float = 0.4,
        blend_mode: BlendMode = BlendMode.ADD
    )

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply bloom effect."""

class InnerGlow:
    """Glow from edges inward."""

    def __init__(self, color: Color, radius: int = 2, intensity: float = 0.5)

class OuterGlow:
    """Glow outward from sprite edges."""

    def __init__(self, color: Color, radius: int = 3, intensity: float = 0.6)
```

### 3. Color Grading and LUTs (`color_grading.py`)

Color manipulation for cinematic effects.

```python
@dataclass
class LUT:
    """3D Color Lookup Table."""
    size: int  # Usually 16, 32, or 64
    data: List[List[List[Color]]]  # [r][g][b] -> output color

    @classmethod
    def from_image(cls, image_path: str) -> 'LUT':
        """Load LUT from standard LUT image."""

    @classmethod
    def identity(cls, size: int = 16) -> 'LUT':
        """Create identity (no-op) LUT."""

class ColorGrader:
    """Apply color grading transformations."""

    def apply_lut(self, canvas: Canvas, lut: LUT) -> Canvas:
        """Apply LUT color transform."""

    def adjust_levels(
        self, canvas: Canvas,
        shadows: float = 0.0,
        midtones: float = 1.0,
        highlights: float = 1.0
    ) -> Canvas:
        """Adjust tonal levels."""

    def adjust_curves(
        self, canvas: Canvas,
        red_curve: List[Tuple[float, float]],
        green_curve: List[Tuple[float, float]],
        blue_curve: List[Tuple[float, float]]
    ) -> Canvas:
        """Apply RGB curves adjustment."""

    def color_balance(
        self, canvas: Canvas,
        shadows_shift: Tuple[int, int, int] = (0, 0, 0),
        midtones_shift: Tuple[int, int, int] = (0, 0, 0),
        highlights_shift: Tuple[int, int, int] = (0, 0, 0)
    ) -> Canvas:
        """Shift colors in different tonal ranges."""

# Preset color grades
def create_warm_grade() -> ColorGrader
def create_cool_grade() -> ColorGrader
def create_vintage_grade() -> ColorGrader
def create_cyberpunk_grade() -> ColorGrader
def create_noir_grade() -> ColorGrader
```

### 4. Displacement Effects (`displacement.py`)

Spatial distortion effects.

```python
class WaveDisplacement:
    """Sinusoidal wave distortion."""

    def __init__(
        self,
        amplitude: float = 3.0,     # Wave height in pixels
        frequency: float = 0.2,     # Waves per pixel
        direction: str = "horizontal",
        phase: float = 0.0          # Animation offset
    )

    def apply(self, canvas: Canvas) -> Canvas

class RippleDisplacement:
    """Circular ripple effect from a point."""

    def __init__(
        self,
        center: Tuple[int, int],
        amplitude: float = 4.0,
        wavelength: float = 8.0,
        decay: float = 0.5,
        phase: float = 0.0
    )

class TwirlDisplacement:
    """Twirl/spiral distortion."""

    def __init__(
        self,
        center: Tuple[int, int],
        angle: float = 45.0,        # Max rotation in degrees
        radius: float = 0.8         # Effect radius (0-1)
    )

class BulgeDisplacement:
    """Bulge/pinch effect."""

    def __init__(
        self,
        center: Tuple[int, int],
        strength: float = 0.5,      # Positive=bulge, negative=pinch
        radius: float = 0.6
    )

class NoiseDisplacement:
    """Random noise displacement."""

    def __init__(
        self,
        strength: float = 2.0,
        seed: int = 42,
        smoothness: float = 0.5     # 0=noise, 1=perlin-like
    )
```

### 5. Palette Cycling Animations (`palette_cycle.py`)

Animate by cycling palette colors.

```python
@dataclass
class CycleRange:
    """A range of colors to cycle."""
    start_index: int
    end_index: int
    speed: float        # Steps per second
    reverse: bool = False
    bounce: bool = False  # Ping-pong

class PaletteCycler:
    """Manages palette cycling animations."""

    def __init__(self, base_palette: Palette):
        self.base_palette = base_palette
        self.ranges: List[CycleRange] = []
        self.elapsed = 0.0

    def add_range(self, range: CycleRange):
        """Add a cycling range."""

    def update(self, dt: float):
        """Update cycle state."""

    def get_current_palette(self) -> Palette:
        """Get palette with current cycle state."""

    def apply(self, canvas: Canvas) -> Canvas:
        """Remap canvas colors to cycled palette."""

# Preset cycles
def create_water_cycle(palette: Palette) -> PaletteCycler
def create_fire_cycle(palette: Palette) -> PaletteCycler
def create_rainbow_cycle(palette: Palette) -> PaletteCycler
def create_shimmer_cycle(palette: Palette) -> PaletteCycler
```

## Implementation Plan

### Order of Implementation

1. **Post-Processing** - Foundation for other effects (blur needed for glow)
2. **Glow/Bloom** - Uses blur from post-processing
3. **Color Grading** - Standalone, useful immediately
4. **Displacement** - Standalone spatial effects
5. **Palette Cycling** - Animation integration

### Integration

All effects integrate with existing `ScreenEffects` manager:

```python
class ScreenEffects:
    # Existing...
    post_processor: Optional[PostProcessor] = None
    glow: Optional[GlowEffect] = None
    bloom: Optional[BloomEffect] = None
    color_grader: Optional[ColorGrader] = None
    displacement: Optional[Displacement] = None
    palette_cycler: Optional[PaletteCycler] = None
```

### AI Tool Integration

Add tools to `ai/tools/effects.py`:

```python
@tool(name="apply_glow", category="effects")
def apply_glow(sprite: GenerationResult, radius: int = 3, intensity: float = 0.5) -> ToolResult

@tool(name="apply_bloom", category="effects")
def apply_bloom(sprite: GenerationResult, threshold: int = 180) -> ToolResult

@tool(name="apply_blur", category="effects")
def apply_blur(sprite: GenerationResult, radius: int = 2) -> ToolResult

@tool(name="apply_color_grade", category="effects")
def apply_color_grade(sprite: GenerationResult, preset: str = "warm") -> ToolResult

@tool(name="apply_displacement", category="effects")
def apply_displacement(sprite: GenerationResult, effect: str = "wave") -> ToolResult
```

## Testing Strategy

- Unit tests for each effect type
- Visual regression tests (generate known outputs)
- Integration tests with screen effects manager
- Performance tests (effects should be fast enough for real-time preview)

## Dependencies

- No external dependencies (pure Python)
- Uses existing `core.Canvas`, `core.Color`, `core.Palette`
- Uses existing `effects.BlendMode`
