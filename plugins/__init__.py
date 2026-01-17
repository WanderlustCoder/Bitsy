"""
Bitsy Plugins - Extensibility system for Bitsy.

Create custom generators, effects, exporters, sounds, and palettes.

Example - Creating a plugin:

    # bitsy_plugins/my_generator.py
    from plugins import GeneratorPlugin
    from core import Canvas

    class MyCreature(GeneratorPlugin):
        name = "my_creature"
        category = "creature"
        description = "Generates my custom creature"

        def generate(self, width=32, height=32, seed=None, **kwargs):
            canvas = Canvas(width, height)
            # ... generation logic ...
            return canvas

Example - Using plugins:

    from plugins import load_plugins, get_generator

    # Load all plugins
    load_plugins()

    # Use a plugin generator
    gen = get_generator("my_creature")
    if gen:
        sprite = gen.generate(width=32, height=32)

Example - Using hooks:

    from plugins import register_hook

    def add_watermark(canvas, **kwargs):
        # Add watermark to all generated sprites
        return add_text(canvas, "Made with Bitsy")

    register_hook("post_generate", add_watermark)
"""

# Base plugin classes
from .base import (
    Plugin,
    PluginMetadata,
    GeneratorPlugin,
    EffectPlugin,
    ExporterPlugin,
    SoundPlugin,
    PalettePlugin,
    get_plugin_type,
    list_plugin_types,
    PLUGIN_TYPES,
)

# Registry
from .registry import (
    PluginRegistry,
    get_registry,
    register,
    unregister,
    get_plugin,
)

# Loader
from .loader import (
    PluginLoader,
    get_loader,
    load_plugins,
    discover_plugins,
)

# Hooks
from .hooks import (
    HookRegistry,
    HookCallback,
    get_hooks,
    register_hook,
    unregister_hook,
    run_hooks,
    list_hook_names,
    HOOK_NAMES,
)


# Convenience functions for accessing plugins
def get_generator(name: str) -> GeneratorPlugin:
    """Get a generator plugin by name."""
    return get_registry().get_generator(name)


def get_effect(name: str) -> EffectPlugin:
    """Get an effect plugin by name."""
    return get_registry().get_effect(name)


def get_exporter(name: str) -> ExporterPlugin:
    """Get an exporter plugin by name."""
    return get_registry().get_exporter(name)


def get_sound(name: str) -> SoundPlugin:
    """Get a sound plugin by name."""
    return get_registry().get_sound(name)


def get_palette(name: str) -> PalettePlugin:
    """Get a palette plugin by name."""
    return get_registry().get_palette(name)


def list_generators() -> list:
    """List all registered generator plugins."""
    return get_registry().list_generators()


def list_effects() -> list:
    """List all registered effect plugins."""
    return get_registry().list_effects()


def list_exporters() -> list:
    """List all registered exporter plugins."""
    return get_registry().list_exporters()


def list_sounds() -> list:
    """List all registered sound plugins."""
    return get_registry().list_sounds()


def list_palettes() -> list:
    """List all registered palette plugins."""
    return get_registry().list_palettes()


def search_plugins(
    query: str = "",
    plugin_type: str = None,
    category: str = None,
    tags: list = None
) -> list:
    """Search plugins by criteria."""
    return get_registry().search(query, plugin_type, category, tags)


__all__ = [
    # Base classes
    'Plugin',
    'PluginMetadata',
    'GeneratorPlugin',
    'EffectPlugin',
    'ExporterPlugin',
    'SoundPlugin',
    'PalettePlugin',
    'get_plugin_type',
    'list_plugin_types',
    'PLUGIN_TYPES',

    # Registry
    'PluginRegistry',
    'get_registry',
    'register',
    'unregister',
    'get_plugin',

    # Loader
    'PluginLoader',
    'get_loader',
    'load_plugins',
    'discover_plugins',

    # Hooks
    'HookRegistry',
    'HookCallback',
    'get_hooks',
    'register_hook',
    'unregister_hook',
    'run_hooks',
    'list_hook_names',
    'HOOK_NAMES',

    # Convenience functions
    'get_generator',
    'get_effect',
    'get_exporter',
    'get_sound',
    'get_palette',
    'list_generators',
    'list_effects',
    'list_exporters',
    'list_sounds',
    'list_palettes',
    'search_plugins',
]
