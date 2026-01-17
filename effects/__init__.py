"""
Bitsy Effects - Visual effects system for pixel art.

This module provides:
- Particle systems for dynamic effects
- Motion trails and afterimages
- Screen effects (shake, flash, fade)
- Post-processing filters (blur, sharpen, emboss)
- Glow and bloom effects
- Color grading and LUTs
- Displacement effects (wave, ripple, twirl)
- Palette cycling animations

Example usage:

    # Create a spark effect
    from bitsy.effects import create_effect

    spark = create_effect('spark', x=100, y=100)
    spark.burst()

    # In game loop:
    spark.update(dt)
    spark.render(canvas)

    # Screen shake
    from bitsy.effects import ScreenEffects

    effects = ScreenEffects()
    effects.trigger_shake(intensity=5, duration=0.3)

    # In game loop:
    effects.update(dt)
    result = effects.apply(game_canvas)

    # Post-processing
    from bitsy.effects import blur, add_glow, apply_color_grade

    blurred = blur(canvas, radius=2)
    glowing = add_glow(canvas, threshold=200)
    graded = apply_color_grade(canvas, "cyberpunk")

    # Displacement
    from bitsy.effects import apply_wave, apply_ripple

    wavy = apply_wave(canvas, amplitude=3, frequency=0.2)
    rippled = apply_ripple(canvas, amplitude=4, wavelength=8)

    # Palette cycling
    from bitsy.effects import create_water_cycle

    cycler = create_water_cycle()
    cycler.update(dt)
    animated = cycler.apply(canvas)
"""

# Particles
from .particles import (
    # Shapes
    ParticleShape,
    # Core classes
    Particle,
    EmitterConfig,
    ParticleEmitter,
    ParticleSystem,
    # Effect presets
    create_spark_emitter,
    create_explosion_emitter,
    create_magic_emitter,
    create_fire_emitter,
    create_smoke_emitter,
    create_rain_emitter,
    create_snow_emitter,
    create_dust_emitter,
    create_heal_emitter,
    create_lightning_emitter,
    # Factory
    create_effect,
    list_effects,
    EFFECT_PRESETS,
)

# Trails
from .trails import (
    TrailPoint,
    Trail,
    LineTrail,
    RibbonTrail,
    AfterImageTrail,
    MotionBlur,
    SpeedLines,
)

# Weather effects
from .weather import (
    # Weather classes
    RainEffect,
    SnowEffect,
    FogEffect,
    LightningEffect,
    LightingEffect,
    # Config
    WeatherConfig,
    WeatherIntensity,
    # Convenience functions
    create_rain_overlay,
    create_snow_overlay,
    create_fog_overlay,
    apply_weather_to_scene,
    list_weather_types,
    list_intensity_levels,
)

# Screen effects
from .screen import (
    # Blend modes
    BlendMode,
    # Effect classes
    ScreenShake,
    ScreenFlash,
    ScreenFade,
    Vignette,
    ColorFilter,
    Scanlines,
    ChromaticAberration,
    # Manager
    ScreenEffects,
    # Presets
    create_hit_flash,
    create_damage_flash,
    create_heal_flash,
    create_impact_shake,
    create_rumble_shake,
)

# Post-processing effects
from .post_process import (
    # Base classes
    Effect,
    PostProcessor,
    ConvolutionKernel,
    # Convolution effects
    GaussianBlur,
    BoxBlur,
    Sharpen,
    Emboss,
    EdgeDetect,
    # Pixel-level effects
    Pixelate,
    Posterize,
    Dither,
    DitherMethod,
    Invert,
    Grayscale,
    Sepia,
    # Convenience functions
    blur,
    sharpen,
    pixelate,
    posterize,
    grayscale,
    sepia,
    invert,
    emboss,
    detect_edges,
)

# Glow and bloom effects
from .glow import (
    GlowEffect,
    BloomEffect,
    InnerGlow,
    OuterGlow,
    ColorGlow,
    add_glow,
    add_bloom,
    add_outer_glow,
    add_inner_glow,
)

# Color grading
from .color_grading import (
    LUT,
    ColorGrader,
    create_warm_grade,
    create_cool_grade,
    create_vintage_grade,
    create_cyberpunk_grade,
    create_noir_grade,
    create_golden_hour_grade,
    apply_color_grade,
    adjust_levels,
    adjust_temperature,
    list_color_grades,
)

# Displacement effects
from .displacement import (
    Displacement,
    WaveDisplacement,
    RippleDisplacement,
    TwirlDisplacement,
    BulgeDisplacement,
    NoiseDisplacement,
    BarrelDisplacement,
    ShearDisplacement,
    CompositeDisplacement,
    apply_wave,
    apply_ripple,
    apply_twirl,
    apply_bulge,
    apply_noise,
    apply_barrel,
)

# Palette cycling
from .palette_cycle import (
    CycleRange,
    PaletteCycler,
    ColorShifter,
    PaletteCycleAnimation,
    create_water_palette,
    create_fire_palette,
    create_rainbow_palette,
    create_lava_palette,
    create_water_cycle,
    create_fire_cycle,
    create_rainbow_cycle,
    create_shimmer_cycle,
    create_lava_cycle,
    create_cycle,
    list_cycle_presets,
)

__all__ = [
    # Particles
    'ParticleShape',
    'Particle',
    'EmitterConfig',
    'ParticleEmitter',
    'ParticleSystem',
    'create_spark_emitter',
    'create_explosion_emitter',
    'create_magic_emitter',
    'create_fire_emitter',
    'create_smoke_emitter',
    'create_rain_emitter',
    'create_snow_emitter',
    'create_dust_emitter',
    'create_heal_emitter',
    'create_lightning_emitter',
    'create_effect',
    'list_effects',
    'EFFECT_PRESETS',

    # Trails
    'TrailPoint',
    'Trail',
    'LineTrail',
    'RibbonTrail',
    'AfterImageTrail',
    'MotionBlur',
    'SpeedLines',

    # Screen effects
    'BlendMode',
    'ScreenShake',
    'ScreenFlash',
    'ScreenFade',
    'Vignette',
    'ColorFilter',
    'Scanlines',
    'ChromaticAberration',
    'ScreenEffects',
    'create_hit_flash',
    'create_damage_flash',
    'create_heal_flash',
    'create_impact_shake',
    'create_rumble_shake',

    # Weather effects
    'RainEffect',
    'SnowEffect',
    'FogEffect',
    'LightningEffect',
    'LightingEffect',
    'WeatherConfig',
    'WeatherIntensity',
    'create_rain_overlay',
    'create_snow_overlay',
    'create_fog_overlay',
    'apply_weather_to_scene',
    'list_weather_types',
    'list_intensity_levels',

    # Post-processing
    'Effect',
    'PostProcessor',
    'ConvolutionKernel',
    'GaussianBlur',
    'BoxBlur',
    'Sharpen',
    'Emboss',
    'EdgeDetect',
    'Pixelate',
    'Posterize',
    'Dither',
    'DitherMethod',
    'Invert',
    'Grayscale',
    'Sepia',
    'blur',
    'sharpen',
    'pixelate',
    'posterize',
    'grayscale',
    'sepia',
    'invert',
    'emboss',
    'detect_edges',

    # Glow and bloom
    'GlowEffect',
    'BloomEffect',
    'InnerGlow',
    'OuterGlow',
    'ColorGlow',
    'add_glow',
    'add_bloom',
    'add_outer_glow',
    'add_inner_glow',

    # Color grading
    'LUT',
    'ColorGrader',
    'create_warm_grade',
    'create_cool_grade',
    'create_vintage_grade',
    'create_cyberpunk_grade',
    'create_noir_grade',
    'create_golden_hour_grade',
    'apply_color_grade',
    'adjust_levels',
    'adjust_temperature',
    'list_color_grades',

    # Displacement
    'Displacement',
    'WaveDisplacement',
    'RippleDisplacement',
    'TwirlDisplacement',
    'BulgeDisplacement',
    'NoiseDisplacement',
    'BarrelDisplacement',
    'ShearDisplacement',
    'CompositeDisplacement',
    'apply_wave',
    'apply_ripple',
    'apply_twirl',
    'apply_bulge',
    'apply_noise',
    'apply_barrel',

    # Palette cycling
    'CycleRange',
    'PaletteCycler',
    'ColorShifter',
    'PaletteCycleAnimation',
    'create_water_palette',
    'create_fire_palette',
    'create_rainbow_palette',
    'create_lava_palette',
    'create_water_cycle',
    'create_fire_cycle',
    'create_rainbow_cycle',
    'create_shimmer_cycle',
    'create_lava_cycle',
    'create_cycle',
    'list_cycle_presets',
]
