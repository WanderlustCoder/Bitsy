"""
Test Environment Generator - Tests for environment/background generation.

Tests:
- Sky generation with different times of day
- Ground/terrain generation
- Parallax layer generation
- Room interior generation
- Palette systems
- Determinism
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from generators.environment import (
    EnvironmentGenerator,
    SkyPalette,
    GroundPalette,
    TimeOfDay,
    Weather,
    TerrainType,
    RoomType,
    generate_sky,
    generate_ground,
    generate_parallax,
    generate_room,
    list_time_of_day,
    list_weather,
    list_terrain_types,
    list_room_types,
)


class TestEnvironmentGenerator(TestCase):
    """Tests for EnvironmentGenerator class."""

    def test_constructor(self):
        """EnvironmentGenerator initializes correctly."""
        gen = EnvironmentGenerator(64, 64, seed=42)

        self.assertEqual(gen.width, 64)
        self.assertEqual(gen.height, 64)
        self.assertEqual(gen.seed, 42)

    def test_custom_dimensions(self):
        """Custom dimensions are respected."""
        gen = EnvironmentGenerator(128, 96, seed=42)

        self.assertEqual(gen.width, 128)
        self.assertEqual(gen.height, 96)

    def test_set_seed(self):
        """set_seed changes random seed."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.set_seed(100)

        self.assertEqual(gen.seed, 100)
        self.assertEqual(result, gen)  # Returns self for chaining


class TestSkyGeneration(TestCase):
    """Tests for sky background generation."""

    def test_generate_sky_returns_canvas(self):
        """generate_sky returns Canvas."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky()

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)

    def test_day_sky(self):
        """Day sky generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(time_of_day='day')

        self.assertIsInstance(result, Canvas)

    def test_night_sky(self):
        """Night sky generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(time_of_day='night', include_stars=True)

        self.assertIsInstance(result, Canvas)

    def test_dawn_sky(self):
        """Dawn sky generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(time_of_day='dawn')

        self.assertIsInstance(result, Canvas)

    def test_dusk_sky(self):
        """Dusk sky generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(time_of_day='dusk')

        self.assertIsInstance(result, Canvas)

    def test_cloudy_weather(self):
        """Cloudy weather generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(weather='cloudy', cloud_density=0.5)

        self.assertIsInstance(result, Canvas)

    def test_storm_weather(self):
        """Storm weather generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(weather='storm')

        self.assertIsInstance(result, Canvas)

    def test_sky_with_sun(self):
        """Sky with sun includes sun."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(include_sun=True)

        # Should have visible content
        pixel_count = sum(1 for y in range(result.height)
                         for x in range(result.width)
                         if result.get_pixel(x, y)[3] > 0)
        self.assertGreater(pixel_count, 0)

    def test_sky_without_sun(self):
        """Sky without sun parameter works."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_sky(include_sun=False)

        self.assertIsInstance(result, Canvas)


class TestGroundGeneration(TestCase):
    """Tests for ground/terrain generation."""

    def test_generate_ground_returns_canvas(self):
        """generate_ground returns Canvas."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground()

        self.assertIsInstance(result, Canvas)

    def test_grass_terrain(self):
        """Grass terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='grass')

        self.assertIsInstance(result, Canvas)

    def test_stone_terrain(self):
        """Stone terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='stone')

        self.assertIsInstance(result, Canvas)

    def test_sand_terrain(self):
        """Sand terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='sand')

        self.assertIsInstance(result, Canvas)

    def test_snow_terrain(self):
        """Snow terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='snow')

        self.assertIsInstance(result, Canvas)

    def test_dirt_terrain(self):
        """Dirt terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='dirt')

        self.assertIsInstance(result, Canvas)

    def test_water_terrain(self):
        """Water terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='water')

        self.assertIsInstance(result, Canvas)

    def test_lava_terrain(self):
        """Lava terrain generates successfully."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='lava')

        self.assertIsInstance(result, Canvas)

    def test_ground_with_details(self):
        """Ground with details generates correctly."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='grass', include_details=True)

        self.assertIsInstance(result, Canvas)

    def test_ground_without_details(self):
        """Ground without details works."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground(terrain='grass', include_details=False)

        self.assertIsInstance(result, Canvas)

    def test_height_variance(self):
        """Height variance parameter affects output."""
        gen = EnvironmentGenerator(64, 64, seed=42)

        flat = gen.generate_ground(height_variance=0.0)
        hilly = gen.generate_ground(height_variance=0.5)

        self.assertIsInstance(flat, Canvas)
        self.assertIsInstance(hilly, Canvas)


class TestParallaxGeneration(TestCase):
    """Tests for parallax layer generation."""

    def test_generate_parallax_returns_list(self):
        """generate_parallax_layers returns list of canvases."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers()

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_parallax_layer_count(self):
        """Correct number of layers generated."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers(num_layers=5)

        self.assertEqual(len(result), 5)

    def test_forest_theme(self):
        """Forest parallax theme generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers(theme='forest')

        self.assertIsInstance(result, list)
        for layer in result:
            self.assertIsInstance(layer, Canvas)

    def test_mountains_theme(self):
        """Mountains parallax theme generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers(theme='mountains')

        self.assertIsInstance(result, list)

    def test_city_theme(self):
        """City parallax theme generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers(theme='city')

        self.assertIsInstance(result, list)

    def test_cave_theme(self):
        """Cave parallax theme generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_parallax_layers(theme='cave')

        self.assertIsInstance(result, list)

    def test_all_layers_correct_size(self):
        """All parallax layers have correct dimensions."""
        gen = EnvironmentGenerator(64, 48, seed=42)
        result = gen.generate_parallax_layers(num_layers=3)

        for layer in result:
            self.assertEqual(layer.width, 64)
            self.assertEqual(layer.height, 48)


class TestRoomGeneration(TestCase):
    """Tests for room interior generation."""

    def test_generate_room_returns_canvas(self):
        """generate_room_interior returns Canvas."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_room_interior()

        self.assertIsInstance(result, Canvas)

    def test_dungeon_room(self):
        """Dungeon room generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_room_interior(room_type='dungeon')

        self.assertIsInstance(result, Canvas)

    def test_house_room(self):
        """House room generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_room_interior(room_type='house')

        self.assertIsInstance(result, Canvas)

    def test_castle_room(self):
        """Castle room generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_room_interior(room_type='castle')

        self.assertIsInstance(result, Canvas)

    def test_cave_room(self):
        """Cave room generates."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_room_interior(room_type='cave')

        self.assertIsInstance(result, Canvas)


class TestSkyPalette(TestCase):
    """Tests for SkyPalette class."""

    def test_default_palette(self):
        """Default sky palette has all colors."""
        palette = SkyPalette()

        self.assertIsNotNone(palette.top)
        self.assertIsNotNone(palette.middle)
        self.assertIsNotNone(palette.horizon)
        self.assertIsNotNone(palette.sun)
        self.assertIsNotNone(palette.cloud)

    def test_day_palette(self):
        """Day palette preset works."""
        palette = SkyPalette.day()

        # Day sky should be blue-ish
        self.assertGreater(palette.top[2], palette.top[0])  # Blue > Red

    def test_night_palette(self):
        """Night palette preset works."""
        palette = SkyPalette.night()

        # Night sky should be dark
        self.assertLess(palette.top[0], 50)
        self.assertLess(palette.top[1], 50)

    def test_dawn_palette(self):
        """Dawn palette preset works."""
        palette = SkyPalette.dawn()
        self.assertIsNotNone(palette.horizon)

    def test_dusk_palette(self):
        """Dusk palette preset works."""
        palette = SkyPalette.dusk()
        self.assertIsNotNone(palette.horizon)

    def test_storm_palette(self):
        """Storm palette preset works."""
        palette = SkyPalette.storm()
        # Storm should be gray/dark
        self.assertLess(palette.top[0], 100)


class TestGroundPalette(TestCase):
    """Tests for GroundPalette class."""

    def test_grass_palette(self):
        """Grass palette has green tones."""
        palette = GroundPalette.grass()

        # Green should be dominant
        self.assertGreater(palette.base[1], palette.base[0])

    def test_sand_palette(self):
        """Sand palette has warm tones."""
        palette = GroundPalette.sand()

        # Should be yellowish
        self.assertGreater(palette.base[0], palette.base[2])
        self.assertGreater(palette.base[1], palette.base[2])

    def test_stone_palette(self):
        """Stone palette has gray tones."""
        palette = GroundPalette.stone()

        # Should be grayish (channels close)
        r, g, b = palette.base[0], palette.base[1], palette.base[2]
        self.assertLess(abs(r - g), 30)

    def test_snow_palette(self):
        """Snow palette has white/light tones."""
        palette = GroundPalette.snow()

        # Should be very light
        self.assertGreater(palette.base[0], 200)
        self.assertGreater(palette.base[1], 200)
        self.assertGreater(palette.base[2], 200)


class TestEnvironmentEnums(TestCase):
    """Tests for environment enum types."""

    def test_time_of_day_values(self):
        """TimeOfDay enum has expected values."""
        self.assertEqual(TimeOfDay.DAY.value, 'day')
        self.assertEqual(TimeOfDay.NIGHT.value, 'night')
        self.assertEqual(TimeOfDay.DAWN.value, 'dawn')
        self.assertEqual(TimeOfDay.DUSK.value, 'dusk')

    def test_weather_values(self):
        """Weather enum has expected values."""
        self.assertEqual(Weather.CLEAR.value, 'clear')
        self.assertEqual(Weather.CLOUDY.value, 'cloudy')
        self.assertEqual(Weather.STORM.value, 'storm')

    def test_terrain_type_values(self):
        """TerrainType enum has expected values."""
        self.assertEqual(TerrainType.GRASS.value, 'grass')
        self.assertEqual(TerrainType.STONE.value, 'stone')
        self.assertEqual(TerrainType.SAND.value, 'sand')

    def test_room_type_values(self):
        """RoomType enum has expected values."""
        self.assertEqual(RoomType.DUNGEON.value, 'dungeon')
        self.assertEqual(RoomType.HOUSE.value, 'house')
        self.assertEqual(RoomType.CASTLE.value, 'castle')


class TestConvenienceFunctions(TestCase):
    """Tests for module-level convenience functions."""

    def test_generate_sky_function(self):
        """generate_sky convenience function works."""
        result = generate_sky(64, 64, 'day', 'clear', 42)

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)

    def test_generate_ground_function(self):
        """generate_ground convenience function works."""
        result = generate_ground(64, 64, 'grass', 42)

        self.assertIsInstance(result, Canvas)

    def test_generate_parallax_function(self):
        """generate_parallax convenience function works."""
        result = generate_parallax(64, 64, 'forest', 3, 42)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_generate_room_function(self):
        """generate_room convenience function works."""
        result = generate_room(64, 64, 'dungeon', 42)

        self.assertIsInstance(result, Canvas)

    def test_list_time_of_day(self):
        """list_time_of_day returns all times."""
        times = list_time_of_day()

        self.assertIn('day', times)
        self.assertIn('night', times)
        self.assertIn('dawn', times)
        self.assertIn('dusk', times)

    def test_list_weather(self):
        """list_weather returns all weather types."""
        weather = list_weather()

        self.assertIn('clear', weather)
        self.assertIn('cloudy', weather)
        self.assertIn('storm', weather)

    def test_list_terrain_types(self):
        """list_terrain_types returns all terrain types."""
        terrains = list_terrain_types()

        self.assertIn('grass', terrains)
        self.assertIn('stone', terrains)
        self.assertIn('sand', terrains)

    def test_list_room_types(self):
        """list_room_types returns all room types."""
        rooms = list_room_types()

        self.assertIn('dungeon', rooms)
        self.assertIn('house', rooms)
        self.assertIn('castle', rooms)


class TestDeterminism(TestCase):
    """Tests for deterministic generation."""

    def test_same_seed_same_sky(self):
        """Same seed produces identical sky."""
        gen1 = EnvironmentGenerator(64, 64, seed=42)
        gen2 = EnvironmentGenerator(64, 64, seed=42)

        result1 = gen1.generate_sky()
        result2 = gen2.generate_sky()

        for y in range(result1.height):
            for x in range(result1.width):
                self.assertEqual(result1.get_pixel(x, y), result2.get_pixel(x, y))

    def test_different_seeds_different_output(self):
        """Different seeds produce different output."""
        gen1 = EnvironmentGenerator(64, 64, seed=42)
        gen2 = EnvironmentGenerator(64, 64, seed=123)

        result1 = gen1.generate_sky(weather='cloudy', cloud_density=0.5)
        result2 = gen2.generate_sky(weather='cloudy', cloud_density=0.5)

        # Should have at least some different pixels
        different = False
        for y in range(result1.height):
            for x in range(result1.width):
                if result1.get_pixel(x, y) != result2.get_pixel(x, y):
                    different = True
                    break

        self.assertTrue(different)


class TestEnvironmentVisuals(TestCase):
    """Tests for visual properties of generated environments."""

    def test_sky_fills_canvas(self):
        """Sky fills entire canvas."""
        gen = EnvironmentGenerator(32, 32, seed=42)
        result = gen.generate_sky()

        # Every pixel should be filled (no transparent)
        for y in range(result.height):
            for x in range(result.width):
                self.assertGreater(result.get_pixel(x, y)[3], 0)

    def test_ground_has_content(self):
        """Ground has visible content."""
        gen = EnvironmentGenerator(64, 64, seed=42)
        result = gen.generate_ground()

        pixel_count = sum(1 for y in range(result.height)
                         for x in range(result.width)
                         if result.get_pixel(x, y)[3] > 0)
        self.assertGreater(pixel_count, 0)

    def test_larger_environments(self):
        """Larger canvas sizes work correctly."""
        gen = EnvironmentGenerator(128, 128, seed=42)
        sky = gen.generate_sky()
        ground = gen.generate_ground()

        self.assertEqual(sky.width, 128)
        self.assertEqual(sky.height, 128)
        self.assertEqual(ground.width, 128)
        self.assertEqual(ground.height, 128)

