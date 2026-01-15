"""
Bitsy Effects - Visual effects system for pixel art.

This module provides:
- Particle systems for dynamic effects
- Motion trails and afterimages
- Screen effects (shake, flash, fade)
- Post-processing filters

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
]
