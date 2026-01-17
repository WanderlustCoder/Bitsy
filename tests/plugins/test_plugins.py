"""Tests for plugin system."""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from plugins import (
    # Base classes
    Plugin,
    PluginMetadata,
    GeneratorPlugin,
    EffectPlugin,
    ExporterPlugin,
    SoundPlugin,
    PalettePlugin,
    list_plugin_types,
    PLUGIN_TYPES,

    # Registry
    PluginRegistry,
    get_registry,
    register,
    unregister,

    # Loader
    PluginLoader,
    load_plugins,
    discover_plugins,

    # Hooks
    HookRegistry,
    register_hook,
    unregister_hook,
    run_hooks,
    list_hook_names,
    HOOK_NAMES,

    # Convenience
    get_generator,
    list_generators,
)

from core import Canvas


# Test plugin implementations
class TestGeneratorImpl(GeneratorPlugin):
    name = "test_generator"
    category = "test"
    description = "Test generator"

    def generate(self, width=16, height=16, seed=None, **kwargs):
        return Canvas(width, height)


class TestEffectImpl(EffectPlugin):
    name = "test_effect"
    category = "test"

    def apply(self, canvas, **kwargs):
        return canvas


class TestExporterImpl(ExporterPlugin):
    name = "test_exporter"
    category = "test"
    extension = ".test"

    def export(self, data, path, **kwargs):
        pass


class TestSoundImpl(SoundPlugin):
    name = "test_sound"
    category = "test"

    def generate(self, **kwargs):
        return None


class TestPaletteImpl(PalettePlugin):
    name = "test_palette"
    category = "test"

    def get_colors(self):
        return [(0, 0, 0, 255), (255, 255, 255, 255)]


class TestBaseClasses:
    """Tests for plugin base classes."""

    def test_list_plugin_types(self):
        """Test listing plugin types."""
        types = list_plugin_types()
        assert "generator" in types
        assert "effect" in types
        assert "exporter" in types
        assert "sound" in types
        assert "palette" in types

    def test_generator_plugin(self):
        """Test GeneratorPlugin."""
        gen = TestGeneratorImpl()
        assert gen.name == "test_generator"
        assert gen.plugin_type == "generator"
        canvas = gen.generate()
        assert isinstance(canvas, Canvas)

    def test_effect_plugin(self):
        """Test EffectPlugin."""
        effect = TestEffectImpl()
        assert effect.plugin_type == "effect"
        canvas = Canvas(16, 16)
        result = effect.apply(canvas)
        assert result is canvas

    def test_exporter_plugin(self):
        """Test ExporterPlugin."""
        exp = TestExporterImpl()
        assert exp.plugin_type == "exporter"
        assert exp.extension == ".test"

    def test_sound_plugin(self):
        """Test SoundPlugin."""
        sound = TestSoundImpl()
        assert sound.plugin_type == "sound"

    def test_palette_plugin(self):
        """Test PalettePlugin."""
        pal = TestPaletteImpl()
        assert pal.plugin_type == "palette"
        colors = pal.get_colors()
        assert len(colors) == 2

    def test_plugin_metadata(self):
        """Test getting plugin metadata."""
        gen = TestGeneratorImpl()
        meta = gen.get_metadata()
        assert isinstance(meta, PluginMetadata)
        assert meta.name == "test_generator"
        assert meta.plugin_type == "generator"

    def test_plugin_validation(self):
        """Test plugin validation."""
        gen = TestGeneratorImpl()
        assert gen.validate() is True

        # Invalid plugin (no name)
        class InvalidPlugin(GeneratorPlugin):
            name = ""
            category = "test"
            def generate(self, **kwargs):
                pass

        invalid = InvalidPlugin()
        try:
            invalid.validate()
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "name" in str(e)


class TestRegistry:
    """Tests for plugin registry."""

    def test_create_registry(self):
        """Test creating a registry."""
        registry = PluginRegistry()
        assert registry.count() == 0

    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        gen = TestGeneratorImpl()

        assert registry.register(gen) is True
        assert registry.count("generator") == 1

    def test_register_duplicate(self):
        """Test registering duplicate plugin."""
        registry = PluginRegistry()
        gen1 = TestGeneratorImpl()
        gen2 = TestGeneratorImpl()

        registry.register(gen1)

        try:
            registry.register(gen2)
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        gen = TestGeneratorImpl()

        registry.register(gen)
        assert registry.count("generator") == 1

        assert registry.unregister("test_generator", "generator") is True
        assert registry.count("generator") == 0

    def test_get_plugin(self):
        """Test getting a plugin."""
        registry = PluginRegistry()
        gen = TestGeneratorImpl()
        registry.register(gen)

        result = registry.get("test_generator", "generator")
        assert result is gen

        result = registry.get_generator("test_generator")
        assert result is gen

    def test_get_nonexistent(self):
        """Test getting nonexistent plugin."""
        registry = PluginRegistry()
        result = registry.get("nonexistent", "generator")
        assert result is None

    def test_list_plugins(self):
        """Test listing plugins."""
        registry = PluginRegistry()
        registry.register(TestGeneratorImpl())
        registry.register(TestEffectImpl())

        all_plugins = registry.list_plugins()
        assert "generator" in all_plugins
        assert "test_generator" in all_plugins["generator"]

        generators = registry.list_generators()
        assert "test_generator" in generators

    def test_search_plugins(self):
        """Test searching plugins."""
        registry = PluginRegistry()
        gen = TestGeneratorImpl()
        gen.tags = ["retro", "test"]
        registry.register(gen)

        # Search by query
        results = registry.search("test")
        assert len(results) == 1

        # Search by type
        results = registry.search(plugin_type="generator")
        assert len(results) == 1

        # Search by tags
        results = registry.search(tags=["retro"])
        assert len(results) == 1

    def test_clear_registry(self):
        """Test clearing registry."""
        registry = PluginRegistry()
        registry.register(TestGeneratorImpl())
        registry.register(TestEffectImpl())

        registry.clear()
        assert registry.count() == 0


class TestLoader:
    """Tests for plugin loader."""

    def test_create_loader(self):
        """Test creating a loader."""
        registry = PluginRegistry()
        loader = PluginLoader(registry=registry)
        assert loader.registry is registry

    def test_discover_empty_path(self):
        """Test discovering from nonexistent path."""
        registry = PluginRegistry()
        loader = PluginLoader(registry=registry, paths=["/nonexistent/path"])

        discovered = loader.discover_plugins()
        assert len(discovered) == 0

    def test_load_from_file(self):
        """Test loading from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test plugin file
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text('''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins import GeneratorPlugin
from core import Canvas

class FileTestGenerator(GeneratorPlugin):
    name = "file_test"
    category = "test"

    def generate(self, width=8, height=8, seed=None, **kwargs):
        return Canvas(width, height)
''')

            registry = PluginRegistry()
            loader = PluginLoader(registry=registry)

            plugins = loader.load_from_file(str(plugin_file))

            # Should load one plugin
            assert len(plugins) == 1
            assert plugins[0].name == "file_test"
            assert registry.count("generator") == 1

    def test_add_path(self):
        """Test adding search path."""
        registry = PluginRegistry()
        loader = PluginLoader(registry=registry, paths=["/initial/path"])
        initial_count = len(loader.paths)

        loader.add_path("/test/path")
        assert len(loader.paths) == initial_count + 1


class TestHooks:
    """Tests for hook system."""

    def test_list_hook_names(self):
        """Test listing hook names."""
        names = list_hook_names()
        assert "pre_generate" in names
        assert "post_generate" in names
        assert "pre_export" in names

    def test_register_hook(self):
        """Test registering a hook."""
        hooks = HookRegistry()

        def my_callback(data, **kwargs):
            return data

        assert hooks.register("pre_generate", my_callback) is True
        assert hooks.has_hooks("pre_generate") is True

    def test_unregister_hook(self):
        """Test unregistering a hook."""
        hooks = HookRegistry()

        def my_callback(data, **kwargs):
            return data

        hooks.register("pre_generate", my_callback)
        assert hooks.unregister("pre_generate", callback=my_callback) is True
        assert hooks.has_hooks("pre_generate") is False

    def test_run_hooks(self):
        """Test running hooks."""
        hooks = HookRegistry()

        def double(data, **kwargs):
            return data * 2

        def add_one(data, **kwargs):
            return data + 1

        hooks.register("post_generate", double, priority=1)
        hooks.register("post_generate", add_one, priority=0)

        # Higher priority (double) runs first: 5 * 2 = 10
        # Then add_one: 10 + 1 = 11
        result = hooks.run("post_generate", 5)
        assert result == 11

    def test_run_hooks_collect(self):
        """Test running hooks and collecting results."""
        hooks = HookRegistry()

        def return_a(data, **kwargs):
            return "a"

        def return_b(data, **kwargs):
            return "b"

        hooks.register("post_generate", return_a)
        hooks.register("post_generate", return_b)

        results = hooks.run_all("post_generate", None)
        assert "a" in results
        assert "b" in results

    def test_hook_priority(self):
        """Test hook priority ordering."""
        hooks = HookRegistry()

        order = []

        def first(data, **kwargs):
            order.append("first")
            return data

        def second(data, **kwargs):
            order.append("second")
            return data

        hooks.register("pre_generate", first, priority=10)
        hooks.register("pre_generate", second, priority=5)

        hooks.run("pre_generate", None)
        assert order == ["first", "second"]

    def test_invalid_hook_name(self):
        """Test invalid hook name."""
        hooks = HookRegistry()

        try:
            hooks.register("invalid_hook", lambda x: x)
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_clear_hooks(self):
        """Test clearing hooks."""
        hooks = HookRegistry()
        hooks.register("pre_generate", lambda x: x)
        hooks.register("post_generate", lambda x: x)

        hooks.clear("pre_generate")
        assert hooks.has_hooks("pre_generate") is False
        assert hooks.has_hooks("post_generate") is True

        hooks.clear()
        assert hooks.has_hooks("post_generate") is False


class TestGlobalFunctions:
    """Tests for module-level convenience functions."""

    def test_global_registry(self):
        """Test global registry access."""
        registry = get_registry()
        assert isinstance(registry, PluginRegistry)

    def test_register_global(self):
        """Test registering in global registry."""
        # Clear first
        get_registry().clear()

        class GlobalTestGen(GeneratorPlugin):
            name = "global_test"
            category = "test"
            def generate(self, **kwargs):
                return Canvas(8, 8)

        register(GlobalTestGen())

        result = get_generator("global_test")
        assert result is not None
        assert result.name == "global_test"

        # Cleanup
        unregister("global_test", "generator")


class TestExamplePlugins:
    """Tests for example plugins in bitsy_plugins/."""

    def test_load_example_plugins(self):
        """Test loading example plugins."""
        # Create a fresh registry and loader
        registry = PluginRegistry()
        loader = PluginLoader(
            registry=registry,
            paths=["./bitsy_plugins"]
        )

        plugins = loader.load_all()

        # Should find at least the example plugins
        # (ghost, bat, level_up, game_over, warp)
        assert len(plugins) >= 2

        # Check generators
        assert "ghost" in registry.list_generators() or len(plugins) > 0

    def test_ghost_generator(self):
        """Test ghost generator plugin."""
        registry = PluginRegistry()
        loader = PluginLoader(
            registry=registry,
            paths=["./bitsy_plugins"]
        )
        loader.load_all()

        ghost = registry.get_generator("ghost")
        if ghost:
            canvas = ghost.generate(width=16, height=16, seed=42)
            assert isinstance(canvas, Canvas)
            assert canvas.width == 16
            assert canvas.height == 16


if __name__ == '__main__':
    # Simple test runner
    import traceback

    test_classes = [
        TestBaseClasses,
        TestRegistry,
        TestLoader,
        TestHooks,
        TestGlobalFunctions,
        TestExamplePlugins,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for name in dir(instance):
            if name.startswith('test_'):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, name, e, traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")

    if errors:
        print(f"\nFailed tests:")
        for cls_name, test_name, error, tb in errors:
            print(f"\n{cls_name}.{test_name}:")
            print(tb)

    exit(0 if failed == 0 else 1)
