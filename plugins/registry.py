"""
Plugin registry for Bitsy.

Central registry for all loaded plugins.
"""

from typing import Any, Dict, List, Optional, Type
from .base import (
    Plugin,
    GeneratorPlugin,
    EffectPlugin,
    ExporterPlugin,
    SoundPlugin,
    PalettePlugin,
    PluginMetadata,
)


class PluginRegistry:
    """Central registry for all plugins.

    Manages registration, lookup, and listing of plugins.

    Example:
        registry = PluginRegistry()

        # Register a plugin
        registry.register(MyGeneratorPlugin())

        # Get a plugin
        gen = registry.get("my_generator", "generator")

        # List all generators
        generators = registry.list_plugins("generator")
    """

    def __init__(self):
        """Initialize empty registry."""
        self._plugins: Dict[str, Dict[str, Plugin]] = {
            "generator": {},
            "effect": {},
            "exporter": {},
            "sound": {},
            "palette": {},
        }
        self._metadata: Dict[str, PluginMetadata] = {}

    def register(self, plugin: Plugin) -> bool:
        """Register a plugin.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registered successfully

        Raises:
            ValueError: If plugin is invalid or already registered
        """
        # Validate plugin
        plugin.validate()

        plugin_type = plugin.plugin_type
        name = plugin.name

        if plugin_type not in self._plugins:
            raise ValueError(f"Unknown plugin type: {plugin_type}")

        if name in self._plugins[plugin_type]:
            raise ValueError(
                f"Plugin '{name}' already registered as {plugin_type}"
            )

        # Register
        self._plugins[plugin_type][name] = plugin
        self._metadata[f"{plugin_type}:{name}"] = plugin.get_metadata()

        return True

    def unregister(self, name: str, plugin_type: str) -> bool:
        """Unregister a plugin.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            True if unregistered successfully
        """
        if plugin_type not in self._plugins:
            return False

        if name not in self._plugins[plugin_type]:
            return False

        del self._plugins[plugin_type][name]
        key = f"{plugin_type}:{name}"
        if key in self._metadata:
            del self._metadata[key]

        return True

    def get(
        self,
        name: str,
        plugin_type: str
    ) -> Optional[Plugin]:
        """Get a plugin by name and type.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            Plugin instance or None if not found
        """
        if plugin_type not in self._plugins:
            return None
        return self._plugins[plugin_type].get(name)

    def get_generator(self, name: str) -> Optional[GeneratorPlugin]:
        """Get a generator plugin by name."""
        return self.get(name, "generator")

    def get_effect(self, name: str) -> Optional[EffectPlugin]:
        """Get an effect plugin by name."""
        return self.get(name, "effect")

    def get_exporter(self, name: str) -> Optional[ExporterPlugin]:
        """Get an exporter plugin by name."""
        return self.get(name, "exporter")

    def get_sound(self, name: str) -> Optional[SoundPlugin]:
        """Get a sound plugin by name."""
        return self.get(name, "sound")

    def get_palette(self, name: str) -> Optional[PalettePlugin]:
        """Get a palette plugin by name."""
        return self.get(name, "palette")

    def list_plugins(
        self,
        plugin_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """List registered plugins.

        Args:
            plugin_type: Filter by type (None for all)

        Returns:
            Dict mapping plugin type to list of names
        """
        if plugin_type:
            if plugin_type not in self._plugins:
                return {}
            return {plugin_type: list(self._plugins[plugin_type].keys())}

        return {
            ptype: list(plugins.keys())
            for ptype, plugins in self._plugins.items()
            if plugins
        }

    def list_generators(self) -> List[str]:
        """List generator plugin names."""
        return list(self._plugins["generator"].keys())

    def list_effects(self) -> List[str]:
        """List effect plugin names."""
        return list(self._plugins["effect"].keys())

    def list_exporters(self) -> List[str]:
        """List exporter plugin names."""
        return list(self._plugins["exporter"].keys())

    def list_sounds(self) -> List[str]:
        """List sound plugin names."""
        return list(self._plugins["sound"].keys())

    def list_palettes(self) -> List[str]:
        """List palette plugin names."""
        return list(self._plugins["palette"].keys())

    def get_metadata(
        self,
        name: str,
        plugin_type: str
    ) -> Optional[PluginMetadata]:
        """Get plugin metadata.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            PluginMetadata or None if not found
        """
        return self._metadata.get(f"{plugin_type}:{name}")

    def search(
        self,
        query: str = "",
        plugin_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[PluginMetadata]:
        """Search plugins by various criteria.

        Args:
            query: Search in name and description
            plugin_type: Filter by type
            category: Filter by category
            tags: Filter by tags (any match)

        Returns:
            List of matching plugin metadata
        """
        results = []
        query_lower = query.lower()

        for key, meta in self._metadata.items():
            # Type filter
            if plugin_type and meta.plugin_type != plugin_type:
                continue

            # Category filter
            if category and meta.category != category:
                continue

            # Tag filter
            if tags and not any(t in meta.tags for t in tags):
                continue

            # Query filter
            if query:
                if (query_lower not in meta.name.lower() and
                    query_lower not in meta.description.lower()):
                    continue

            results.append(meta)

        return results

    def clear(self) -> None:
        """Clear all registered plugins."""
        for plugin_type in self._plugins:
            self._plugins[plugin_type].clear()
        self._metadata.clear()

    def count(self, plugin_type: Optional[str] = None) -> int:
        """Count registered plugins.

        Args:
            plugin_type: Count only this type (None for all)

        Returns:
            Number of registered plugins
        """
        if plugin_type:
            return len(self._plugins.get(plugin_type, {}))
        return sum(len(p) for p in self._plugins.values())


# Global registry instance
_global_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    return _global_registry


def register(plugin: Plugin) -> bool:
    """Register a plugin in the global registry."""
    return _global_registry.register(plugin)


def unregister(name: str, plugin_type: str) -> bool:
    """Unregister a plugin from the global registry."""
    return _global_registry.unregister(name, plugin_type)


def get_plugin(name: str, plugin_type: str) -> Optional[Plugin]:
    """Get a plugin from the global registry."""
    return _global_registry.get(name, plugin_type)
