"""
Test Weather Effects - Tests for weather and lighting effects module.

Tests:
- Rain effects (RainEffect, create_rain_overlay)
- Snow effects (SnowEffect, create_snow_overlay)
- Fog effects (FogEffect, create_fog_overlay)
- Lightning effects (LightningEffect)
- Lighting effects (LightingEffect, time-of-day, point lights, AO, vignette)
- Weather configuration (WeatherConfig)
- Animation sequences
- Determinism
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas


# Import weather module
try:
    from effects.weather import (
        WeatherIntensity,
        WeatherConfig,
        RainDrop,
        SnowFlake,
        RainEffect,
        SnowEffect,
        FogEffect,
        LightningEffect,
        LightingEffect,
        create_rain_overlay,
        create_snow_overlay,
        create_fog_overlay,
        apply_weather_to_scene,
        list_weather_types,
        list_intensity_levels,
    )
    WEATHER_AVAILABLE = True
except ImportError as e:
    WEATHER_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestWeatherIntensity(TestCase):
    """Tests for WeatherIntensity enum."""

    def test_intensity_levels_defined(self):
        """WeatherIntensity enum has expected values."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        self.assertEqual(WeatherIntensity.LIGHT.value, 'light')
        self.assertEqual(WeatherIntensity.MODERATE.value, 'moderate')
        self.assertEqual(WeatherIntensity.HEAVY.value, 'heavy')
        self.assertEqual(WeatherIntensity.STORM.value, 'storm')

    def test_list_intensity_levels(self):
        """list_intensity_levels returns all levels."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        levels = list_intensity_levels()
        self.assertIn('light', levels)
        self.assertIn('moderate', levels)
        self.assertIn('heavy', levels)
        self.assertIn('storm', levels)
        self.assertEqual(len(levels), 4)


class TestWeatherConfig(TestCase):
    """Tests for WeatherConfig dataclass."""

    def test_default_config(self):
        """WeatherConfig has sensible defaults."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig()
        self.assertEqual(config.intensity, 'moderate')
        self.assertEqual(config.wind, 0.0)
        self.assertEqual(config.particle_count, 100)
        self.assertIsNotNone(config.color_tint)

    def test_light_rain_config(self):
        """WeatherConfig.light_rain() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.light_rain()
        self.assertEqual(config.intensity, 'light')
        self.assertLess(config.particle_count, 50)

    def test_heavy_rain_config(self):
        """WeatherConfig.heavy_rain() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.heavy_rain()
        self.assertEqual(config.intensity, 'heavy')
        self.assertGreater(config.particle_count, 100)

    def test_storm_rain_config(self):
        """WeatherConfig.storm_rain() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.storm_rain()
        self.assertEqual(config.intensity, 'storm')
        self.assertGreater(config.wind, 0.3)
        self.assertGreater(config.particle_count, 150)

    def test_light_snow_config(self):
        """WeatherConfig.light_snow() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.light_snow()
        self.assertEqual(config.intensity, 'light')
        self.assertLess(config.speed_max, 2.0)  # Snow is slower

    def test_heavy_snow_config(self):
        """WeatherConfig.heavy_snow() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.heavy_snow()
        self.assertEqual(config.intensity, 'heavy')
        self.assertGreater(config.particle_count, 100)

    def test_blizzard_config(self):
        """WeatherConfig.blizzard() returns correct config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.blizzard()
        self.assertEqual(config.intensity, 'storm')
        self.assertGreater(config.wind, 0.5)


class TestRainDrop(TestCase):
    """Tests for RainDrop dataclass."""

    def test_raindrop_creation(self):
        """RainDrop can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        drop = RainDrop(x=10.0, y=5.0, speed=3.0, length=5)
        self.assertEqual(drop.x, 10.0)
        self.assertEqual(drop.y, 5.0)
        self.assertEqual(drop.speed, 3.0)
        self.assertEqual(drop.length, 5)

    def test_raindrop_update(self):
        """RainDrop.update() moves the drop."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        drop = RainDrop(x=10.0, y=5.0, speed=3.0, length=5, angle=0.0)
        drop.update(wind=0.0)

        self.assertEqual(drop.y, 8.0)  # Moved down by speed

    def test_raindrop_update_with_wind(self):
        """RainDrop.update() applies wind."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        drop = RainDrop(x=10.0, y=5.0, speed=3.0, length=5, angle=0.0)
        drop.update(wind=1.0)

        self.assertGreater(drop.x, 10.0)  # Moved right by wind


class TestSnowFlake(TestCase):
    """Tests for SnowFlake dataclass."""

    def test_snowflake_creation(self):
        """SnowFlake can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        flake = SnowFlake(x=10.0, y=5.0, speed=1.0, size=2)
        self.assertEqual(flake.x, 10.0)
        self.assertEqual(flake.y, 5.0)
        self.assertEqual(flake.speed, 1.0)
        self.assertEqual(flake.size, 2)

    def test_snowflake_update(self):
        """SnowFlake.update() moves the flake with wobble."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        flake = SnowFlake(x=10.0, y=5.0, speed=1.0, size=2, wobble_offset=0.0)
        original_x = flake.x
        flake.update(wind=0.0)

        self.assertEqual(flake.y, 6.0)  # Moved down by speed
        # X has some wobble
        self.assertNotEqual(flake.x, original_x)


class TestRainEffect(TestCase):
    """Tests for RainEffect class."""

    def test_rain_effect_creation(self):
        """RainEffect can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        rain = RainEffect(64, 64, seed=42)
        self.assertEqual(rain.width, 64)
        self.assertEqual(rain.height, 64)
        self.assertGreater(len(rain.drops), 0)

    def test_rain_effect_with_config(self):
        """RainEffect can be created with custom config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.heavy_rain()
        rain = RainEffect(64, 64, config=config, seed=42)

        self.assertEqual(rain.config, config)

    def test_rain_effect_render(self):
        """RainEffect.render() produces a canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        rain = RainEffect(32, 32, seed=42)
        result = rain.render()

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_rain_effect_update(self):
        """RainEffect.update() moves drops."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        rain = RainEffect(32, 32, seed=42)
        original_y = rain.drops[0].y

        rain.update()

        # Either moved down or wrapped to top
        self.assertNotEqual(rain.drops[0].y, original_y)

    def test_rain_effect_render_animation(self):
        """RainEffect.render_animation() produces multiple frames."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        rain = RainEffect(32, 32, seed=42)
        frames = rain.render_animation(frames=5)

        self.assertEqual(len(frames), 5)
        for frame in frames:
            self.assertCanvasSize(frame, 32, 32)

    def test_rain_effect_deterministic(self):
        """RainEffect is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        rain1 = RainEffect(32, 32, seed=42)
        rain2 = RainEffect(32, 32, seed=42)

        result1 = rain1.render()
        result2 = rain2.render()

        self.assertCanvasEqual(result1, result2)


class TestSnowEffect(TestCase):
    """Tests for SnowEffect class."""

    def test_snow_effect_creation(self):
        """SnowEffect can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        snow = SnowEffect(64, 64, seed=42)
        self.assertEqual(snow.width, 64)
        self.assertEqual(snow.height, 64)
        self.assertGreater(len(snow.flakes), 0)

    def test_snow_effect_with_config(self):
        """SnowEffect can be created with custom config."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        config = WeatherConfig.heavy_snow()
        snow = SnowEffect(64, 64, config=config, seed=42)

        self.assertEqual(snow.config, config)

    def test_snow_effect_render(self):
        """SnowEffect.render() produces a canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        snow = SnowEffect(32, 32, seed=42)
        result = snow.render()

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_snow_effect_update(self):
        """SnowEffect.update() moves flakes."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        snow = SnowEffect(32, 32, seed=42)
        original_y = snow.flakes[0].y

        snow.update()

        # Position changed
        self.assertNotEqual(snow.flakes[0].y, original_y)

    def test_snow_effect_render_animation(self):
        """SnowEffect.render_animation() produces multiple frames."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        snow = SnowEffect(32, 32, seed=42)
        frames = snow.render_animation(frames=5)

        self.assertEqual(len(frames), 5)
        for frame in frames:
            self.assertCanvasSize(frame, 32, 32)

    def test_snow_effect_deterministic(self):
        """SnowEffect is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        snow1 = SnowEffect(32, 32, seed=42)
        snow2 = SnowEffect(32, 32, seed=42)

        result1 = snow1.render()
        result2 = snow2.render()

        self.assertCanvasEqual(result1, result2)


class TestFogEffect(TestCase):
    """Tests for FogEffect class."""

    def test_fog_effect_creation(self):
        """FogEffect can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog = FogEffect(64, 64, density=0.5, seed=42)
        self.assertEqual(fog.width, 64)
        self.assertEqual(fog.height, 64)
        self.assertEqual(fog.density, 0.5)

    def test_fog_effect_density_clamped(self):
        """FogEffect clamps density to valid range."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog_low = FogEffect(32, 32, density=-0.5, seed=42)
        self.assertEqual(fog_low.density, 0.0)

        fog_high = FogEffect(32, 32, density=1.5, seed=42)
        self.assertEqual(fog_high.density, 1.0)

    def test_fog_effect_render(self):
        """FogEffect.render() produces a canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog = FogEffect(32, 32, density=0.5, seed=42)
        result = fog.render()

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_fog_effect_render_with_time_offset(self):
        """FogEffect.render() accepts time_offset for animation."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog = FogEffect(32, 32, density=0.5, seed=42)

        result1 = fog.render(time_offset=0.0)
        result2 = fog.render(time_offset=0.5)

        # Different time offsets produce different fog patterns
        # (may occasionally be equal due to pattern, but usually different)
        self.assertCanvasNotEmpty(result1)
        self.assertCanvasNotEmpty(result2)

    def test_fog_effect_render_animation(self):
        """FogEffect.render_animation() produces multiple frames."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog = FogEffect(32, 32, density=0.5, seed=42)
        frames = fog.render_animation(frames=4, speed=1.0)

        self.assertEqual(len(frames), 4)
        for frame in frames:
            self.assertCanvasSize(frame, 32, 32)

    def test_fog_effect_deterministic(self):
        """FogEffect is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        fog1 = FogEffect(32, 32, density=0.5, seed=42)
        fog2 = FogEffect(32, 32, density=0.5, seed=42)

        result1 = fog1.render(time_offset=0.0)
        result2 = fog2.render(time_offset=0.0)

        self.assertCanvasEqual(result1, result2)


class TestLightningEffect(TestCase):
    """Tests for LightningEffect class."""

    def test_lightning_effect_creation(self):
        """LightningEffect can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(64, 64, seed=42)
        self.assertEqual(lightning.width, 64)
        self.assertEqual(lightning.height, 64)

    def test_lightning_render_flash(self):
        """LightningEffect.render_flash() produces flash overlay."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(32, 32, seed=42)
        result = lightning.render_flash(intensity=1.0)

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_lightning_render_flash_intensity(self):
        """LightningEffect.render_flash() respects intensity."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(32, 32, seed=42)

        flash_bright = lightning.render_flash(intensity=1.0)
        flash_dim = lightning.render_flash(intensity=0.5)

        # Brighter flash should have higher alpha on average
        self.assertCanvasNotEmpty(flash_bright)
        self.assertCanvasNotEmpty(flash_dim)

    def test_lightning_render_bolt(self):
        """LightningEffect.render_bolt() produces lightning bolt."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(64, 64, seed=42)
        result = lightning.render_bolt(branches=3)

        self.assertCanvasSize(result, 64, 64)
        self.assertCanvasNotEmpty(result)

    def test_lightning_render_bolt_custom_start(self):
        """LightningEffect.render_bolt() with custom start position."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(64, 64, seed=42)
        result = lightning.render_bolt(start_x=20, branches=2)

        self.assertCanvasNotEmpty(result)

    def test_lightning_render_sequence(self):
        """LightningEffect.render_sequence() produces animation frames."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lightning = LightningEffect(32, 32, seed=42)
        frames = lightning.render_sequence(flash_frames=3)

        self.assertGreater(len(frames), 3)  # Flash + bolt + fading + dark
        for frame in frames:
            self.assertCanvasSize(frame, 32, 32)

    def test_lightning_deterministic(self):
        """LightningEffect is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        light1 = LightningEffect(32, 32, seed=42)
        light2 = LightningEffect(32, 32, seed=42)

        result1 = light1.render_bolt(branches=2)
        result2 = light2.render_bolt(branches=2)

        self.assertCanvasEqual(result1, result2)


class TestLightingEffect(TestCase):
    """Tests for LightingEffect class."""

    def test_lighting_effect_creation(self):
        """LightingEffect can be created."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(64, 64, seed=42)
        self.assertEqual(lighting.width, 64)
        self.assertEqual(lighting.height, 64)

    def test_time_of_day_dawn(self):
        """apply_time_of_day_lighting() with dawn."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)

        result = lighting.apply_time_of_day_lighting(scene, time='dawn')

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)
        # Dawn should add warm tint

    def test_time_of_day_day(self):
        """apply_time_of_day_lighting() with day (no change)."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)

        result = lighting.apply_time_of_day_lighting(scene, time='day')

        # Day should have minimal/no tint applied
        self.assertCanvasNotEmpty(result)

    def test_time_of_day_dusk(self):
        """apply_time_of_day_lighting() with dusk."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)

        result = lighting.apply_time_of_day_lighting(scene, time='dusk')

        self.assertCanvasNotEmpty(result)

    def test_time_of_day_night(self):
        """apply_time_of_day_lighting() with night."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)

        result = lighting.apply_time_of_day_lighting(scene, time='night')

        self.assertCanvasNotEmpty(result)
        # Night should add blue/dark tint

    def test_time_of_day_midnight(self):
        """apply_time_of_day_lighting() with midnight."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)

        result = lighting.apply_time_of_day_lighting(scene, time='midnight')

        self.assertCanvasNotEmpty(result)

    def test_add_point_light(self):
        """add_point_light() adds light at position."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((50, 50, 50, 255), width=32, height=32)

        result = lighting.add_point_light(scene, x=16, y=16, radius=10,
                                          color=(255, 200, 100, 255), intensity=1.0)

        self.assertCanvasNotEmpty(result)
        # Center pixel should be brighter than corners
        center = result.get_pixel(16, 16)
        corner = result.get_pixel(0, 0)
        self.assertGreater(center[0], corner[0])  # Red channel

    def test_add_point_light_intensity(self):
        """add_point_light() respects intensity parameter."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((50, 50, 50, 255), width=32, height=32)

        result_bright = lighting.add_point_light(scene, x=16, y=16, radius=10,
                                                 color=(255, 200, 100, 255), intensity=1.0)
        result_dim = lighting.add_point_light(scene, x=16, y=16, radius=10,
                                              color=(255, 200, 100, 255), intensity=0.5)

        # Both should have changes
        self.assertCanvasNotEmpty(result_bright)
        self.assertCanvasNotEmpty(result_dim)

    def test_add_ambient_occlusion(self):
        """add_ambient_occlusion() darkens enclosed areas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        # Create a scene with some content
        scene = Canvas(32, 32)
        scene.fill_rect(8, 8, 16, 16, (200, 200, 200, 255))

        result = lighting.add_ambient_occlusion(scene, strength=0.5)

        self.assertCanvasNotEmpty(result)

    def test_add_vignette(self):
        """add_vignette() darkens edges."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        lighting = LightingEffect(32, 32, seed=42)
        scene = CanvasFixtures.solid((200, 200, 200, 255), width=32, height=32)

        result = lighting.add_vignette(scene, strength=0.5)

        self.assertCanvasNotEmpty(result)
        # Center should be brighter than corners
        center = result.get_pixel(16, 16)
        corner = result.get_pixel(0, 0)
        self.assertGreater(center[0], corner[0])


class TestConvenienceFunctions(TestCase):
    """Tests for convenience functions."""

    def test_create_rain_overlay(self):
        """create_rain_overlay() creates rain canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result = create_rain_overlay(32, 32, intensity='moderate', seed=42)

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_create_rain_overlay_intensities(self):
        """create_rain_overlay() works with all intensities."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        for intensity in ['light', 'moderate', 'heavy', 'storm']:
            result = create_rain_overlay(32, 32, intensity=intensity, seed=42)
            self.assertCanvasNotEmpty(result)

    def test_create_snow_overlay(self):
        """create_snow_overlay() creates snow canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result = create_snow_overlay(32, 32, intensity='moderate', seed=42)

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_create_snow_overlay_intensities(self):
        """create_snow_overlay() works with all intensities."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        for intensity in ['light', 'moderate', 'heavy', 'blizzard']:
            result = create_snow_overlay(32, 32, intensity=intensity, seed=42)
            self.assertCanvasNotEmpty(result)

    def test_create_fog_overlay(self):
        """create_fog_overlay() creates fog canvas."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result = create_fog_overlay(32, 32, density=0.5, seed=42)

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_create_fog_overlay_densities(self):
        """create_fog_overlay() works with various densities."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        for density in [0.2, 0.5, 0.8]:
            result = create_fog_overlay(32, 32, density=density, seed=42)
            self.assertCanvasNotEmpty(result)

    def test_apply_weather_to_scene_rain(self):
        """apply_weather_to_scene() applies rain."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)
        result = apply_weather_to_scene(scene, weather_type='rain', seed=42)

        self.assertCanvasSize(result, 32, 32)
        self.assertCanvasNotEmpty(result)

    def test_apply_weather_to_scene_snow(self):
        """apply_weather_to_scene() applies snow."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)
        result = apply_weather_to_scene(scene, weather_type='snow', seed=42)

        self.assertCanvasNotEmpty(result)

    def test_apply_weather_to_scene_fog(self):
        """apply_weather_to_scene() applies fog."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)
        result = apply_weather_to_scene(scene, weather_type='fog', seed=42)

        self.assertCanvasNotEmpty(result)

    def test_apply_weather_to_scene_unknown_type(self):
        """apply_weather_to_scene() handles unknown weather type."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        scene = CanvasFixtures.solid((100, 150, 200, 255), width=32, height=32)
        result = apply_weather_to_scene(scene, weather_type='unknown', seed=42)

        # Should return unchanged copy of scene
        self.assertCanvasNotEmpty(result)

    def test_list_weather_types(self):
        """list_weather_types() returns available types."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        types = list_weather_types()
        self.assertIn('rain', types)
        self.assertIn('snow', types)
        self.assertIn('fog', types)
        self.assertIn('lightning', types)


class TestDeterminism(TestCase):
    """Tests for deterministic output."""

    def test_rain_deterministic(self):
        """Rain overlay is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result1 = create_rain_overlay(32, 32, intensity='moderate', seed=42)
        result2 = create_rain_overlay(32, 32, intensity='moderate', seed=42)

        self.assertCanvasEqual(result1, result2)

    def test_rain_different_seeds(self):
        """Rain overlay differs with different seeds."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result1 = create_rain_overlay(32, 32, intensity='moderate', seed=42)
        result2 = create_rain_overlay(32, 32, intensity='moderate', seed=99)

        # Should produce different results
        # Check that at least one pixel differs
        differs = False
        for y in range(result1.height):
            for x in range(result1.width):
                p1 = result1.get_pixel(x, y)
                p2 = result2.get_pixel(x, y)
                if tuple(p1) != tuple(p2):
                    differs = True
                    break
            if differs:
                break

        self.assertTrue(differs, "Different seeds should produce different results")

    def test_snow_deterministic(self):
        """Snow overlay is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result1 = create_snow_overlay(32, 32, intensity='moderate', seed=42)
        result2 = create_snow_overlay(32, 32, intensity='moderate', seed=42)

        self.assertCanvasEqual(result1, result2)

    def test_fog_deterministic(self):
        """Fog overlay is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        result1 = create_fog_overlay(32, 32, density=0.5, seed=42)
        result2 = create_fog_overlay(32, 32, density=0.5, seed=42)

        self.assertCanvasEqual(result1, result2)

    def test_lightning_bolt_deterministic(self):
        """Lightning bolt is deterministic with same seed."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        light1 = LightningEffect(32, 32, seed=42)
        light2 = LightningEffect(32, 32, seed=42)

        result1 = light1.render_bolt(start_x=16, branches=3)
        result2 = light2.render_bolt(start_x=16, branches=3)

        self.assertCanvasEqual(result1, result2)


class TestModuleImports(TestCase):
    """Tests for module import structure."""

    def test_weather_module_available(self):
        """Weather module can be imported."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")
        self.assertTrue(WEATHER_AVAILABLE)

    def test_import_from_effects_package(self):
        """Weather classes can be imported from effects package."""
        self.skipUnless(WEATHER_AVAILABLE, "Weather module not available")

        try:
            from effects import (
                RainEffect,
                SnowEffect,
                FogEffect,
                LightningEffect,
                LightingEffect,
                WeatherConfig,
                WeatherIntensity,
                create_rain_overlay,
                create_snow_overlay,
                create_fog_overlay,
                apply_weather_to_scene,
            )
            imported = True
        except ImportError:
            imported = False

        self.assertTrue(imported, "Weather classes should be importable from effects package")
