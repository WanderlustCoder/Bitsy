"""
Base classes for Bitsy plugins.

All plugins should inherit from one of these base classes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    category: str
    plugin_type: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class Plugin(ABC):
    """Base class for all plugins."""

    # Required: unique identifier
    name: str = ""
    # Required: category within plugin type
    category: str = ""
    # Optional metadata
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list) if False else []
    tags: List[str] = field(default_factory=list) if False else []

    # Set by subclasses
    plugin_type: str = "base"

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name=self.name,
            category=self.category,
            plugin_type=self.plugin_type,
            description=self.description,
            version=self.version,
            author=self.author,
            dependencies=self.dependencies,
            tags=self.tags,
        )

    def validate(self) -> bool:
        """Validate plugin configuration."""
        if not self.name:
            raise ValueError("Plugin must have a name")
        if not self.category:
            raise ValueError("Plugin must have a category")
        return True


class GeneratorPlugin(Plugin):
    """Base class for generator plugins.

    Generators create sprites, characters, items, etc.

    Example:
        class MyCreature(GeneratorPlugin):
            name = "my_creature"
            category = "creature"

            def generate(self, width=32, height=32, seed=None, **kwargs):
                canvas = Canvas(width, height)
                # ... generation logic ...
                return canvas
    """

    plugin_type = "generator"

    @abstractmethod
    def generate(
        self,
        width: int = 32,
        height: int = 32,
        seed: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Generate a sprite.

        Args:
            width: Sprite width in pixels
            height: Sprite height in pixels
            seed: Random seed for reproducibility
            **kwargs: Additional generator-specific options

        Returns:
            Canvas with generated sprite
        """
        pass


class EffectPlugin(Plugin):
    """Base class for effect plugins.

    Effects modify canvases or create visual effects.

    Categories:
        - particle: Particle-based effects
        - screen: Screen-level effects (shake, flash)
        - post_process: Post-processing filters

    Example:
        class MyEffect(EffectPlugin):
            name = "my_effect"
            category = "post_process"

            def apply(self, canvas, **kwargs):
                # ... effect logic ...
                return modified_canvas
    """

    plugin_type = "effect"

    @abstractmethod
    def apply(self, canvas: Any, **kwargs) -> Any:
        """Apply effect to a canvas.

        Args:
            canvas: Input canvas
            **kwargs: Effect-specific options

        Returns:
            Modified canvas
        """
        pass


class ExporterPlugin(Plugin):
    """Base class for exporter plugins.

    Exporters write sprites/animations to various file formats.

    Example:
        class MyFormat(ExporterPlugin):
            name = "myformat"
            category = "image"
            extension = ".myfmt"

            def export(self, canvas_or_animation, path, **kwargs):
                # ... export logic ...
                pass
    """

    plugin_type = "exporter"

    # File extension for this format
    extension: str = ""

    @abstractmethod
    def export(
        self,
        data: Any,
        path: str,
        **kwargs
    ) -> None:
        """Export data to file.

        Args:
            data: Canvas or Animation to export
            path: Output file path
            **kwargs: Exporter-specific options
        """
        pass

    def validate(self) -> bool:
        """Validate exporter configuration."""
        super().validate()
        if not self.extension:
            raise ValueError("Exporter must have an extension")
        return True


class SoundPlugin(Plugin):
    """Base class for sound plugins.

    Sound plugins create audio effects.

    Categories:
        - sfx: Sound effects
        - music: Music/jingles
        - ambient: Ambient sounds

    Example:
        class MySound(SoundPlugin):
            name = "my_sound"
            category = "sfx"

            def generate(self, **kwargs):
                effect = SoundEffect(duration=0.3)
                # ... configure sound ...
                return effect
    """

    plugin_type = "sound"

    @abstractmethod
    def generate(self, **kwargs) -> Any:
        """Generate a sound effect.

        Args:
            **kwargs: Sound-specific options

        Returns:
            SoundEffect instance
        """
        pass


class PalettePlugin(Plugin):
    """Base class for palette plugins.

    Palette plugins provide color palettes.

    Example:
        class MyPalette(PalettePlugin):
            name = "my_palette"
            category = "retro"

            def get_colors(self):
                return [
                    Color(0, 0, 0),
                    Color(255, 255, 255),
                    # ...
                ]
    """

    plugin_type = "palette"

    @abstractmethod
    def get_colors(self) -> List[Any]:
        """Get palette colors.

        Returns:
            List of Color objects
        """
        pass


# Plugin type registry for validation
PLUGIN_TYPES: Dict[str, Type[Plugin]] = {
    "generator": GeneratorPlugin,
    "effect": EffectPlugin,
    "exporter": ExporterPlugin,
    "sound": SoundPlugin,
    "palette": PalettePlugin,
}


def get_plugin_type(name: str) -> Optional[Type[Plugin]]:
    """Get plugin base class by type name."""
    return PLUGIN_TYPES.get(name)


def list_plugin_types() -> List[str]:
    """List available plugin types."""
    return list(PLUGIN_TYPES.keys())
