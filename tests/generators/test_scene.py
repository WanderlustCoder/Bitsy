"""Tests for scene composition system."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random

from tests.framework import TestCase
from generators.scene import (
    Scene,
    SceneLayer,
    SceneConfig,
    LightSource,
    TimeOfDay,
    WeatherType,
    create_scene,
    generate_parallax_background,
    list_times_of_day,
    list_weather_types,
)
from core import Canvas
from editor.layers import BlendMode


def _solid_canvas(width, height, color):
    canvas = Canvas(width, height, (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            canvas.set_pixel_solid(x, y, color)
    return canvas


def _scene_with_solid_layer(width, height, color, seed=None):
    scene = Scene(width, height, seed=seed)
    layer_canvas = _solid_canvas(width, height, color)
    scene.add_layer(SceneLayer(name="base", canvas=layer_canvas))
    return scene


class TestTimeOfDay(TestCase):
    """Tests for TimeOfDay enum."""

    def test_all_times_exist(self):
        """All expected times of day exist."""
        self.assertEqual(TimeOfDay.DAWN.value, "dawn")
        self.assertEqual(TimeOfDay.MORNING.value, "morning")
        self.assertEqual(TimeOfDay.NOON.value, "noon")
        self.assertEqual(TimeOfDay.AFTERNOON.value, "afternoon")
        self.assertEqual(TimeOfDay.DUSK.value, "dusk")
        self.assertEqual(TimeOfDay.NIGHT.value, "night")
        self.assertEqual(TimeOfDay.MIDNIGHT.value, "midnight")


class TestWeatherType(TestCase):
    """Tests for WeatherType enum."""

    def test_all_weather_types_exist(self):
        """All expected weather types exist."""
        self.assertEqual(WeatherType.CLEAR.value, "clear")
        self.assertEqual(WeatherType.CLOUDY.value, "cloudy")
        self.assertEqual(WeatherType.RAIN.value, "rain")
        self.assertEqual(WeatherType.SNOW.value, "snow")
        self.assertEqual(WeatherType.FOG.value, "fog")
        self.assertEqual(WeatherType.STORM.value, "storm")


class TestSceneConfig(TestCase):
    """Tests for SceneConfig."""

    def test_config_defaults(self):
        """SceneConfig has sensible defaults."""
        config = SceneConfig()
        self.assertEqual(config.width, 320)
        self.assertEqual(config.height, 180)
        self.assertEqual(config.time_of_day, TimeOfDay.NOON)
        self.assertEqual(config.weather, WeatherType.CLEAR)
        self.assertEqual(config.ambient_light, 1.0)
        self.assertIsNone(config.seed)

    def test_config_custom(self):
        """SceneConfig accepts custom values."""
        config = SceneConfig(
            width=640,
            height=360,
            time_of_day=TimeOfDay.DUSK,
            weather=WeatherType.RAIN,
            ambient_light=0.5,
            seed=42
        )
        self.assertEqual(config.width, 640)
        self.assertEqual(config.height, 360)
        self.assertEqual(config.time_of_day, TimeOfDay.DUSK)
        self.assertEqual(config.weather, WeatherType.RAIN)
        self.assertEqual(config.ambient_light, 0.5)
        self.assertEqual(config.seed, 42)


class TestSceneLayer(TestCase):
    """Tests for SceneLayer."""

    def test_layer_defaults(self):
        """SceneLayer has sensible defaults."""
        canvas = Canvas(16, 16)
        layer = SceneLayer(name="test", canvas=canvas)
        self.assertEqual(layer.name, "test")
        self.assertEqual(layer.parallax_x, 1.0)
        self.assertEqual(layer.parallax_y, 1.0)
        self.assertEqual(layer.z_order, 0)
        self.assertEqual(layer.offset_x, 0)
        self.assertEqual(layer.offset_y, 0)
        self.assertEqual(layer.opacity, 1.0)
        self.assertEqual(layer.blend_mode, BlendMode.NORMAL)
        self.assertFalse(layer.is_background)
        self.assertFalse(layer.casts_shadow)

    def test_layer_custom(self):
        """SceneLayer accepts custom values."""
        canvas = Canvas(32, 32)
        layer = SceneLayer(
            name="background",
            canvas=canvas,
            parallax_x=0.5,
            parallax_y=0.3,
            z_order=-10,
            offset_x=5,
            offset_y=7,
            opacity=0.8,
            blend_mode=BlendMode.ADD,
            is_background=True,
            casts_shadow=True
        )
        self.assertEqual(layer.parallax_x, 0.5)
        self.assertEqual(layer.parallax_y, 0.3)
        self.assertEqual(layer.z_order, -10)
        self.assertEqual(layer.offset_x, 5)
        self.assertEqual(layer.offset_y, 7)
        self.assertEqual(layer.opacity, 0.8)
        self.assertEqual(layer.blend_mode, BlendMode.ADD)
        self.assertTrue(layer.is_background)
        self.assertTrue(layer.casts_shadow)


class TestLightSource(TestCase):
    """Tests for LightSource."""

    def test_light_defaults(self):
        """LightSource has sensible defaults."""
        light = LightSource(x=100, y=50, radius=64)
        self.assertEqual(light.x, 100)
        self.assertEqual(light.y, 50)
        self.assertEqual(light.radius, 64)
        self.assertEqual(light.color, (255, 255, 200, 255))
        self.assertEqual(light.intensity, 1.0)
        self.assertEqual(light.falloff, 1.0)

    def test_light_custom(self):
        """LightSource accepts custom values."""
        light = LightSource(
            x=200,
            y=100,
            radius=128,
            color=(255, 200, 100, 255),
            intensity=0.7,
            falloff=2.0
        )
        self.assertEqual(light.x, 200)
        self.assertEqual(light.radius, 128)
        self.assertEqual(light.color, (255, 200, 100, 255))
        self.assertEqual(light.intensity, 0.7)
        self.assertEqual(light.falloff, 2.0)


class TestScene(TestCase):
    """Tests for Scene class."""

    def test_scene_creation(self):
        """Scene can be created."""
        scene = Scene(320, 180)
        self.assertEqual(scene.width, 320)
        self.assertEqual(scene.height, 180)
        self.assertEqual(len(scene.layers), 0)
        self.assertEqual(len(scene.lights), 0)

    def test_scene_with_seed(self):
        """Scene accepts random seed."""
        scene = Scene(320, 180, seed=42)
        self.assertEqual(scene.seed, 42)

    def test_add_layer(self):
        """Can add layers to scene."""
        scene = Scene(320, 180)
        canvas = Canvas(320, 180)
        layer = SceneLayer(name="test", canvas=canvas, z_order=0)
        scene.add_layer(layer)
        self.assertEqual(len(scene.layers), 1)

    def test_layers_sorted_by_z_order(self):
        """Layers are sorted by z_order."""
        scene = Scene(320, 180)
        canvas = Canvas(16, 16)
        scene.add_layer(SceneLayer(name="front", canvas=canvas, z_order=10))
        scene.add_layer(SceneLayer(name="back", canvas=canvas, z_order=-10))
        scene.add_layer(SceneLayer(name="mid", canvas=canvas, z_order=0))
        self.assertEqual(scene.layers[0].name, "back")
        self.assertEqual(scene.layers[1].name, "mid")
        self.assertEqual(scene.layers[2].name, "front")

    def test_add_light(self):
        """Can add lights to scene."""
        scene = Scene(320, 180)
        light = LightSource(x=160, y=90, radius=64)
        scene.add_light(light)
        self.assertEqual(len(scene.lights), 1)

    def test_set_time_of_day(self):
        """Can set time of day."""
        scene = Scene(320, 180)
        scene.set_time_of_day(TimeOfDay.NIGHT)
        self.assertEqual(scene.time_of_day, TimeOfDay.NIGHT)
        self.assertLess(scene.ambient_light, 0.5)

    def test_set_time_of_day_updates_ambient(self):
        """Setting time of day updates ambient light for all values."""
        scene = Scene(16, 16)
        expected = {
            TimeOfDay.DAWN: 0.6,
            TimeOfDay.MORNING: 0.9,
            TimeOfDay.NOON: 1.0,
            TimeOfDay.AFTERNOON: 0.95,
            TimeOfDay.DUSK: 0.5,
            TimeOfDay.NIGHT: 0.2,
            TimeOfDay.MIDNIGHT: 0.1,
        }
        for time, ambient in expected.items():
            scene.set_time_of_day(time)
            self.assertEqual(scene.ambient_light, ambient)

    def test_set_weather(self):
        """Can set weather."""
        scene = Scene(320, 180)
        scene.set_weather(WeatherType.RAIN)
        self.assertEqual(scene.weather, WeatherType.RAIN)

    def test_render_empty_scene(self):
        """Can render empty scene."""
        scene = Scene(64, 64)
        result = scene.render()
        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)

    def test_render_empty(self):
        """Can render empty scene."""
        scene = Scene(64, 64)
        result = scene.render()
        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)

    def test_render_with_layer(self):
        """Can render scene with layer."""
        scene = Scene(64, 64)
        layer_canvas = Canvas(64, 64)
        # Fill canvas manually
        for y in range(64):
            for x in range(64):
                layer_canvas.set_pixel_solid(x, y, (255, 0, 0, 255))
        layer = SceneLayer(name="red", canvas=layer_canvas)
        scene.add_layer(layer)
        result = scene.render()
        pixel = result.get_pixel(32, 32)
        self.assertIsNotNone(pixel)
        self.assertGreater(pixel[0], 0)  # Has red component

    def test_render_respects_z_order(self):
        """Render respects layer z-order."""
        scene = Scene(8, 8)
        back = _solid_canvas(8, 8, (10, 20, 30, 255))
        front = _solid_canvas(8, 8, (200, 100, 50, 255))
        scene.add_layer(SceneLayer(name="back", canvas=back, z_order=-1))
        scene.add_layer(SceneLayer(name="front", canvas=front, z_order=1))
        result = scene.render()
        self.assertEqual(result.get_pixel(4, 4), (200, 100, 50, 255))

    def test_render_with_parallax(self):
        """Render applies parallax offset."""
        scene = Scene(10, 10)
        layer_canvas = Canvas(1, 1)
        layer_canvas.set_pixel_solid(0, 0, (0, 255, 0, 255))
        layer = SceneLayer(name="dot", canvas=layer_canvas, parallax_x=0.5)
        scene.add_layer(layer)
        result1 = scene.render(camera_x=0)
        result2 = scene.render(camera_x=10)
        self.assertEqual(result1.get_pixel(0, 0), (0, 255, 0, 255))
        self.assertEqual(result2.get_pixel(5, 0), (0, 255, 0, 255))
        self.assertEqual(result2.get_pixel(0, 0), (0, 0, 0, 0))

    def test_render_with_light_source(self):
        """Rendering applies light sources to layers."""
        scene = Scene(5, 5)
        layer_canvas = _solid_canvas(5, 5, (100, 100, 100, 255))
        scene.add_layer(SceneLayer(name="base", canvas=layer_canvas))
        scene.ambient_light = 0.0
        scene.add_light(LightSource(x=2, y=2, radius=2, intensity=0.5))
        result = scene.render()
        self.assertEqual(result.get_pixel(2, 2), (50, 50, 50, 255))

    def test_render_time_grading_dusk(self):
        """Time grading applies tint for dusk."""
        scene = Scene(4, 4)
        layer_canvas = _solid_canvas(4, 4, (100, 100, 100, 255))
        scene.add_layer(SceneLayer(name="base", canvas=layer_canvas))
        scene.set_time_of_day(TimeOfDay.DUSK)
        scene.ambient_light = 1.0
        result = scene.render()
        self.assertEqual(result.get_pixel(1, 1), (131, 110, 100, 255))

    def test_render_weather_fog(self):
        """Fog weather blends a color overlay."""
        scene = _scene_with_solid_layer(4, 4, (10, 20, 30, 255))
        scene.set_weather(WeatherType.FOG)
        result = scene.render()
        self.assertEqual(result.get_pixel(0, 0), (67, 74, 84, 255))

    def test_render_weather_rain_deterministic(self):
        """Rain weather produces deterministic streaks with seed."""
        seed = 7
        width = 10
        height = 10
        base_color = (10, 10, 10, 255)
        scene = _scene_with_solid_layer(width, height, base_color, seed=seed)
        scene.set_weather(WeatherType.RAIN)
        result = scene.render()
        rng = random.Random(seed)
        expected_positions = set()
        for _ in range(width * height // 100):
            x = rng.randint(0, width - 1)
            y = rng.randint(0, height - 1)
            length = rng.randint(3, 8)
            for i in range(length):
                ry = y + i
                if 0 <= ry < height:
                    expected_positions.add((x, ry))
        for x, y in expected_positions:
            self.assertEqual(result.get_pixel(x, y), (60, 60, 70, 255))
        untouched = next(
            (pos for pos in [(0, 0), (1, 1), (2, 2), (3, 3)] if pos not in expected_positions),
            None
        )
        if untouched:
            self.assertEqual(result.get_pixel(untouched[0], untouched[1]), base_color)

    def test_render_weather_snow_deterministic(self):
        """Snow weather produces deterministic particles with seed."""
        seed = 11
        width = 10
        height = 10
        base_color = (20, 30, 40, 255)
        scene = _scene_with_solid_layer(width, height, base_color, seed=seed)
        scene.set_weather(WeatherType.SNOW)
        result = scene.render()
        rng = random.Random(seed)
        expected_positions = set()
        for _ in range(width * height // 80):
            x = rng.randint(0, width - 1)
            y = rng.randint(0, height - 1)
            expected_positions.add((x, y))
        for x, y in expected_positions:
            self.assertEqual(result.get_pixel(x, y), (255, 255, 255, 200))
        untouched = next(
            (pos for pos in [(0, 0), (1, 1), (2, 2), (3, 3)] if pos not in expected_positions),
            None
        )
        if untouched:
            self.assertEqual(result.get_pixel(untouched[0], untouched[1]), base_color)

    def test_render_weather_no_effect(self):
        """Cloudy and storm weather leave the scene unchanged."""
        base_color = (5, 15, 25, 255)
        for weather in (WeatherType.CLOUDY, WeatherType.STORM, WeatherType.CLEAR):
            scene = _scene_with_solid_layer(4, 4, base_color, seed=3)
            scene.set_weather(weather)
            result = scene.render()
            self.assertEqual(result.get_pixel(2, 2), base_color)


class TestGenerateParallaxBackground(TestCase):
    """Tests for generate_parallax_background function."""

    def test_generate_default(self):
        """generate_parallax_background creates layers."""
        layers = generate_parallax_background(320, 180)
        self.assertIsInstance(layers, list)
        self.assertGreater(len(layers), 0)

    def test_generate_custom_layer_count(self):
        """generate_parallax_background respects layer count."""
        layers = generate_parallax_background(320, 180, layers=5)
        # +1 for sky layer
        self.assertEqual(len(layers), 6)

    def test_generate_deterministic(self):
        """generate_parallax_background is deterministic with seed."""
        layers1 = generate_parallax_background(160, 90, seed=42)
        layers2 = generate_parallax_background(160, 90, seed=42)
        self.assertEqual(len(layers1), len(layers2))
        self.assertEqual(
            layers1[1].canvas.get_pixel(0, 0),
            layers2[1].canvas.get_pixel(0, 0)
        )

    def test_deterministic(self):
        """generate_parallax_background is deterministic with seed."""
        layers1 = generate_parallax_background(160, 90, seed=42)
        layers2 = generate_parallax_background(160, 90, seed=42)
        self.assertEqual(len(layers1), len(layers2))
        self.assertEqual(
            layers1[1].canvas.get_pixel(0, 0),
            layers2[1].canvas.get_pixel(0, 0)
        )

    def test_layers_have_parallax(self):
        """Generated layers have varying parallax values."""
        layers = generate_parallax_background(320, 180, layers=3)
        parallax_values = [l.parallax_x for l in layers]
        # Should have some variation
        self.assertGreater(len(set(parallax_values)), 1)

    def test_sky_layer_properties(self):
        """Sky layer has expected default properties."""
        layers = generate_parallax_background(64, 32, layers=2, seed=5)
        sky = layers[0]
        self.assertEqual(sky.name, "sky")
        self.assertEqual(sky.parallax_x, 0.0)
        self.assertEqual(sky.parallax_y, 0.0)
        self.assertEqual(sky.z_order, -100)
        self.assertTrue(sky.is_background)


class TestCreateScene(TestCase):
    """Tests for create_scene function."""

    def test_create_default(self):
        """create_scene creates scene with defaults."""
        scene = create_scene()
        self.assertIsInstance(scene, Scene)
        self.assertEqual(scene.width, 320)
        self.assertEqual(scene.height, 180)

    def test_create_custom_size(self):
        """create_scene respects custom size."""
        scene = create_scene(640, 360)
        self.assertEqual(scene.width, 640)
        self.assertEqual(scene.height, 360)

    def test_create_with_config(self):
        """create_scene respects config."""
        config = SceneConfig(
            width=256,
            height=144,
            time_of_day=TimeOfDay.DUSK,
            weather=WeatherType.FOG,
            ambient_light=0.4,
            seed=7
        )
        scene = create_scene(config=config)
        self.assertEqual(scene.width, 256)
        self.assertEqual(scene.height, 144)
        self.assertEqual(scene.time_of_day, TimeOfDay.DUSK)
        self.assertEqual(scene.weather, WeatherType.FOG)
        self.assertEqual(scene.ambient_light, 0.4)
        self.assertEqual(scene.seed, 7)


class TestListFunctions(TestCase):
    """Tests for list functions."""

    def test_list_times_of_day(self):
        """list_times_of_day returns list."""
        times = list_times_of_day()
        self.assertIsInstance(times, list)
        self.assertEqual(
            times,
            ["dawn", "morning", "noon", "afternoon", "dusk", "night", "midnight"]
        )

    def test_list_weather_types(self):
        """list_weather_types returns list."""
        weather = list_weather_types()
        self.assertIsInstance(weather, list)
        self.assertEqual(
            weather,
            ["clear", "cloudy", "rain", "snow", "fog", "storm"]
        )
