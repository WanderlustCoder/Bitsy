"""
AI Tools - Generation tools with schema support.

Provides typed functions that wrap Bitsy generation capabilities,
with automatic schema generation for MCP and OpenAI integration.
"""

from .definitions import tool, ToolRegistry
from .results import GenerationResult, AnimationResult, ToolResult, QualityScore


def get_tools() -> ToolRegistry:
    """Get the global tool registry."""
    return ToolRegistry.get_instance()


def list_tools():
    """List all registered tools."""
    return [t.name for t in ToolRegistry.get_instance().all()]

# Import all tool modules to register them
from . import characters
from . import items
from . import scenes
from . import animation
from . import export

# Re-export high-level tools
from .characters import generate_sprite, generate_character
from .scenes import generate_scene
from .animation import create_animation
from .export import export_sprite, export_atlas

# Effects
from .effects import apply_effect, apply_palette

__all__ = [
    # Infrastructure
    'tool',
    'ToolRegistry',
    'get_tools',
    'list_tools',

    # Results
    'GenerationResult',
    'AnimationResult',
    'ToolResult',
    'QualityScore',

    # High-level tools
    'generate_sprite',
    'generate_character',
    'generate_scene',
    'create_animation',
    'export_sprite',
    'export_atlas',
    'apply_effect',
    'apply_palette',
]
