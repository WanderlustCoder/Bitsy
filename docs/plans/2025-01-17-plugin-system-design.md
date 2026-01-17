# Plugin System Design

## Overview

A simple, pure-Python plugin system for extending Bitsy with custom generators, effects, exporters, sounds, and palettes.

## Goals

- **Simple**: Easy to create and use plugins
- **Non-intrusive**: Core functionality works without plugins
- **Discoverable**: Auto-discover plugins from standard locations
- **Type-safe**: Base classes with clear interfaces
- **Pure Python**: No external dependencies

## Plugin Locations

Plugins are discovered from (in order):
1. `./bitsy_plugins/` - Project-local plugins
2. `~/.bitsy/plugins/` - User plugins
3. Programmatic registration via API

## Plugin Types

### 1. GeneratorPlugin
Add custom sprite generators.

```python
from plugins import GeneratorPlugin

class MyCreaturePlugin(GeneratorPlugin):
    name = "my_creature"
    category = "creature"  # character, item, creature, prop, etc.

    def generate(self, width=32, height=32, seed=None, **kwargs):
        # Return Canvas with generated sprite
        pass
```

### 2. EffectPlugin
Add custom visual effects.

```python
from plugins import EffectPlugin

class MyEffectPlugin(EffectPlugin):
    name = "my_effect"
    category = "post_process"  # particle, screen, post_process

    def apply(self, canvas, **kwargs):
        # Return modified canvas
        pass
```

### 3. ExporterPlugin
Add custom export formats.

```python
from plugins import ExporterPlugin

class MyFormatPlugin(ExporterPlugin):
    name = "myformat"
    extension = ".myfmt"

    def export(self, canvas_or_animation, path, **kwargs):
        # Write to file
        pass
```

### 4. SoundPlugin
Add custom sound presets.

```python
from plugins import SoundPlugin

class MySoundPlugin(SoundPlugin):
    name = "my_sound"
    category = "sfx"  # sfx, music, ambient

    def generate(self, **kwargs):
        # Return SoundEffect
        pass
```

### 5. PalettePlugin
Add custom color palettes.

```python
from plugins import PalettePlugin

class MyPalettePlugin(PalettePlugin):
    name = "my_palette"

    def get_colors(self):
        # Return list of Color objects
        pass
```

## Module Structure

```
plugins/
├── __init__.py      # Public API
├── base.py          # Base plugin classes
├── loader.py        # Discovery and loading
├── registry.py      # Central registry
└── hooks.py         # Extension hooks
```

## Core Components

### PluginRegistry
Central registry for all plugins.

```python
class PluginRegistry:
    _generators: Dict[str, GeneratorPlugin]
    _effects: Dict[str, EffectPlugin]
    _exporters: Dict[str, ExporterPlugin]
    _sounds: Dict[str, SoundPlugin]
    _palettes: Dict[str, PalettePlugin]

    def register(self, plugin): ...
    def unregister(self, name, plugin_type): ...
    def get(self, name, plugin_type): ...
    def list_plugins(self, plugin_type=None): ...
```

### PluginLoader
Discovers and loads plugins.

```python
class PluginLoader:
    def discover_plugins(self, paths=None): ...
    def load_plugin(self, path): ...
    def load_all(self): ...
```

### Hook System
Allow plugins to modify behavior at specific points.

```python
# Hooks for extending behavior
HOOKS = {
    'pre_generate': [],      # Before generation
    'post_generate': [],     # After generation
    'pre_export': [],        # Before export
    'post_export': [],       # After export
    'pre_render': [],        # Before rendering
    'post_render': [],       # After rendering
}

def register_hook(hook_name, callback): ...
def run_hooks(hook_name, *args, **kwargs): ...
```

## Usage Examples

### Creating a Plugin

```python
# bitsy_plugins/retro_creature.py
from plugins import GeneratorPlugin
from core import Canvas, Color

class RetroCreaturePlugin(GeneratorPlugin):
    """Generates retro-style creatures."""

    name = "retro_creature"
    category = "creature"
    description = "8-bit style creature generator"
    version = "1.0.0"
    author = "Plugin Author"

    def generate(self, width=16, height=16, seed=None, **kwargs):
        canvas = Canvas(width, height)
        # ... generation logic ...
        return canvas

# Auto-registered when file is loaded
```

### Using Plugins

```python
from plugins import load_plugins, get_generator, list_generators

# Load all plugins
load_plugins()

# List available generators (includes plugins)
print(list_generators())  # [..., 'retro_creature', ...]

# Use plugin generator
sprite = get_generator('retro_creature').generate(width=16, height=16)
```

### Plugin with Dependencies

```python
from plugins import GeneratorPlugin
from generators import generate_character  # Use existing generators

class ArmoredKnightPlugin(GeneratorPlugin):
    name = "armored_knight"
    category = "character"
    dependencies = ['character']  # Requires base character generator

    def generate(self, **kwargs):
        # Build on existing generator
        base = generate_character(style='knight', **kwargs)
        # Add armor details
        return self.add_armor(base)
```

## Plugin Metadata

Each plugin can have optional metadata:

```python
class MyPlugin(GeneratorPlugin):
    name = "my_plugin"           # Required: unique identifier
    category = "creature"        # Required: plugin category
    description = "..."          # Optional: description
    version = "1.0.0"           # Optional: version string
    author = "Name"             # Optional: author
    dependencies = []           # Optional: required plugins
    tags = ['retro', '8bit']    # Optional: searchable tags
```

## Integration with Existing Code

Plugins integrate seamlessly with existing registries:

```python
# In generators/__init__.py
from plugins import get_registered_generators

# CREATURE_GENERATORS includes both built-in and plugin generators
def list_creature_types():
    built_in = list(CREATURE_GENERATORS.keys())
    plugins = list(get_registered_generators('creature').keys())
    return built_in + plugins
```

## Error Handling

- Invalid plugins are skipped with warning
- Missing dependencies are reported
- Plugin errors don't crash the main application

## Testing

```python
def test_plugin_registration():
    registry = PluginRegistry()

    class TestGen(GeneratorPlugin):
        name = "test"
        category = "creature"
        def generate(self, **kwargs):
            return Canvas(16, 16)

    registry.register(TestGen())
    assert "test" in registry.list_plugins("generator")
```
