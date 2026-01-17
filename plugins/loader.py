"""
Plugin loader for Bitsy.

Discovers and loads plugins from standard locations.
"""

import importlib.util
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type
import warnings

from .base import Plugin, PLUGIN_TYPES
from .registry import PluginRegistry, get_registry


# Default plugin search paths
DEFAULT_PATHS = [
    "./bitsy_plugins",           # Project-local plugins
    "~/.bitsy/plugins",          # User plugins
]


class PluginLoader:
    """Discovers and loads plugins.

    Searches standard locations for plugin files and loads them.

    Example:
        loader = PluginLoader()

        # Discover plugins
        found = loader.discover_plugins()

        # Load all discovered plugins
        loaded = loader.load_all()
    """

    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        paths: Optional[List[str]] = None
    ):
        """Initialize loader.

        Args:
            registry: Plugin registry (uses global if None)
            paths: Search paths (uses defaults if None)
        """
        self.registry = registry or get_registry()
        self.paths = [Path(p).expanduser() for p in (paths or DEFAULT_PATHS)]
        self._discovered: Dict[str, Path] = {}
        self._loaded: Set[str] = set()
        self._errors: List[str] = []

    def add_path(self, path: str) -> None:
        """Add a search path.

        Args:
            path: Directory path to search
        """
        p = Path(path).expanduser()
        if p not in self.paths:
            self.paths.append(p)

    def discover_plugins(self) -> Dict[str, Path]:
        """Discover plugins in search paths.

        Searches for Python files that define plugin classes.

        Returns:
            Dict mapping module name to file path
        """
        self._discovered.clear()
        self._errors.clear()

        for search_path in self.paths:
            if not search_path.exists():
                continue

            if not search_path.is_dir():
                continue

            # Find Python files
            for py_file in search_path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                module_name = f"bitsy_plugin_{py_file.stem}"

                if module_name in self._discovered:
                    # Already found in earlier path
                    continue

                # Quick check if file contains plugin classes
                if self._might_contain_plugins(py_file):
                    self._discovered[module_name] = py_file

            # Also check subdirectories with __init__.py
            for init_file in search_path.glob("*/__init__.py"):
                pkg_dir = init_file.parent
                if pkg_dir.name.startswith("_"):
                    continue

                module_name = f"bitsy_plugin_{pkg_dir.name}"

                if module_name in self._discovered:
                    continue

                if self._might_contain_plugins(init_file):
                    self._discovered[module_name] = init_file

        return self._discovered.copy()

    def _might_contain_plugins(self, path: Path) -> bool:
        """Quick check if file might contain plugins.

        Args:
            path: Path to Python file

        Returns:
            True if file might define plugins
        """
        try:
            content = path.read_text(encoding='utf-8')
            # Look for plugin base class imports or inheritance
            indicators = [
                "GeneratorPlugin",
                "EffectPlugin",
                "ExporterPlugin",
                "SoundPlugin",
                "PalettePlugin",
                "from plugins import",
                "from bitsy.plugins import",
            ]
            return any(ind in content for ind in indicators)
        except Exception:
            return False

    def load_plugin(self, module_name: str, path: Path) -> List[Plugin]:
        """Load a plugin module.

        Args:
            module_name: Module name to use
            path: Path to Python file

        Returns:
            List of loaded plugin instances
        """
        plugins = []

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                self._errors.append(f"Cannot load {path}: invalid spec")
                return plugins

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find plugin classes in module
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue

                attr = getattr(module, attr_name)

                # Check if it's a plugin class (not base class)
                if (isinstance(attr, type) and
                    issubclass(attr, Plugin) and
                    attr not in PLUGIN_TYPES.values() and
                    attr is not Plugin):

                    # Instantiate and register
                    try:
                        instance = attr()
                        self.registry.register(instance)
                        plugins.append(instance)
                    except Exception as e:
                        self._errors.append(
                            f"Failed to instantiate {attr_name}: {e}"
                        )

        except Exception as e:
            self._errors.append(f"Failed to load {path}: {e}")

        return plugins

    def load_all(self) -> List[Plugin]:
        """Load all discovered plugins.

        Returns:
            List of all loaded plugin instances
        """
        if not self._discovered:
            self.discover_plugins()

        all_plugins = []

        for module_name, path in self._discovered.items():
            if module_name in self._loaded:
                continue

            plugins = self.load_plugin(module_name, path)
            all_plugins.extend(plugins)
            self._loaded.add(module_name)

        return all_plugins

    def load_from_file(self, path: str) -> List[Plugin]:
        """Load plugins from a specific file.

        Args:
            path: Path to Python file

        Returns:
            List of loaded plugin instances
        """
        p = Path(path)
        if not p.exists():
            self._errors.append(f"File not found: {path}")
            return []

        module_name = f"bitsy_plugin_{p.stem}"
        return self.load_plugin(module_name, p)

    def get_errors(self) -> List[str]:
        """Get list of errors from loading."""
        return self._errors.copy()

    def get_discovered(self) -> Dict[str, Path]:
        """Get discovered plugin paths."""
        return self._discovered.copy()

    def get_loaded(self) -> Set[str]:
        """Get names of loaded modules."""
        return self._loaded.copy()


# Global loader instance
_global_loader: Optional[PluginLoader] = None


def get_loader() -> PluginLoader:
    """Get or create the global plugin loader."""
    global _global_loader
    if _global_loader is None:
        _global_loader = PluginLoader()
    return _global_loader


def load_plugins(paths: Optional[List[str]] = None) -> List[Plugin]:
    """Load all plugins from standard locations.

    Args:
        paths: Additional search paths (optional)

    Returns:
        List of loaded plugins
    """
    loader = get_loader()

    if paths:
        for p in paths:
            loader.add_path(p)

    return loader.load_all()


def discover_plugins(paths: Optional[List[str]] = None) -> Dict[str, Path]:
    """Discover plugins without loading them.

    Args:
        paths: Additional search paths (optional)

    Returns:
        Dict mapping module name to file path
    """
    loader = get_loader()

    if paths:
        for p in paths:
            loader.add_path(p)

    return loader.discover_plugins()
