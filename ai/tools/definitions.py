"""
Tool definitions and registry.

Provides the @tool decorator for registering functions as AI tools,
with automatic schema generation for different LLM providers.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List, Optional, get_type_hints, Union
from functools import wraps
import inspect
import json


@dataclass
class ToolSchema:
    """Schema for a tool's parameters."""
    properties: Dict[str, Dict[str, Any]]
    required: List[str]

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        return {
            "type": "object",
            "properties": self.properties,
            "required": self.required,
        }

    def to_openai_function(self, name: str, description: str) -> Dict[str, Any]:
        """Convert to OpenAI function format."""
        return {
            "name": name,
            "description": description,
            "parameters": self.to_json_schema(),
        }


@dataclass
class RegisteredTool:
    """A registered tool with metadata."""
    name: str
    function: Callable
    description: str
    category: str
    schema: ToolSchema
    tags: List[str] = field(default_factory=list)

    @property
    def docstring(self) -> str:
        """Get full docstring."""
        return self.function.__doc__ or self.description


class ToolRegistry:
    """Registry of available AI tools."""

    _instance: Optional['ToolRegistry'] = None

    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}
        self._categories: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """Get singleton registry instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        name: str,
        function: Callable,
        description: str = "",
        category: str = "general",
        tags: List[str] = None,
    ) -> RegisteredTool:
        """Register a tool."""
        schema = _build_schema(function)
        tool = RegisteredTool(
            name=name,
            function=function,
            description=description or (function.__doc__ or "").split("\n")[0],
            category=category,
            schema=schema,
            tags=tags or [],
        )
        self._tools[name] = tool
        self._categories.setdefault(category, []).append(name)
        return tool

    def get(self, name: str) -> Optional[RegisteredTool]:
        """Get tool by name."""
        return self._tools.get(name)

    def all(self) -> List[RegisteredTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def by_category(self, category: str) -> List[RegisteredTool]:
        """Get tools in a category."""
        names = self._categories.get(category, [])
        return [self._tools[n] for n in names if n in self._tools]

    def categories(self) -> List[str]:
        """List all categories."""
        return list(self._categories.keys())

    def search(self, query: str) -> List[RegisteredTool]:
        """Search tools by name, description, or tags."""
        query = query.lower()
        results = []
        for tool in self._tools.values():
            if (query in tool.name.lower() or
                query in tool.description.lower() or
                any(query in tag.lower() for tag in tool.tags)):
                results.append(tool)
        return results


def tool(
    name: Optional[str] = None,
    category: str = "general",
    tags: List[str] = None,
    description: str = "",
):
    """Decorator to register a function as an AI tool.

    Args:
        name: Tool name (defaults to function name)
        category: Tool category for organization
        tags: Searchable tags
        description: Short description (defaults to first line of docstring)

    Example:
        @tool(name="generate_sprite", category="generation")
        def generate_sprite(description: str, size: int = 32) -> GenerationResult:
            '''Generate a sprite from description.'''
            ...
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        registry = ToolRegistry.get_instance()
        registry.register(
            name=tool_name,
            function=func,
            description=description,
            category=category,
            tags=tags or [],
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._tool_name = tool_name
        return wrapper

    return decorator


def _build_schema(func: Callable) -> ToolSchema:
    """Build JSON schema from function signature."""
    sig = inspect.signature(func)
    hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue

        param_type = hints.get(param_name, Any)
        prop = _type_to_schema(param_type)

        # Add description from docstring if available
        prop["description"] = _extract_param_description(func, param_name)

        properties[param_name] = prop

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return ToolSchema(properties=properties, required=required)


def _type_to_schema(python_type) -> Dict[str, Any]:
    """Convert Python type to JSON schema type."""
    origin = getattr(python_type, '__origin__', None)

    # Handle Optional
    if origin is Union:
        args = python_type.__args__
        # Optional[X] is Union[X, None]
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _type_to_schema(non_none[0])

    # Handle List
    if origin is list:
        item_type = python_type.__args__[0] if python_type.__args__ else Any
        return {"type": "array", "items": _type_to_schema(item_type)}

    # Handle Dict
    if origin is dict:
        return {"type": "object"}

    # Handle Tuple
    if origin is tuple:
        return {"type": "array"}

    # Basic types
    type_map = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        type(None): {"type": "null"},
    }

    if python_type in type_map:
        return type_map[python_type]

    # Enum
    if hasattr(python_type, '__members__'):
        return {
            "type": "string",
            "enum": list(python_type.__members__.keys()),
        }

    # Default
    return {"type": "string"}


def _extract_param_description(func: Callable, param_name: str) -> str:
    """Extract parameter description from docstring."""
    if not func.__doc__:
        return ""

    # Look for Args: section in docstring
    lines = func.__doc__.split('\n')
    in_args = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('Args:'):
            in_args = True
            continue
        if in_args:
            if stripped.startswith(f'{param_name}:'):
                return stripped.split(':', 1)[1].strip()
            if stripped and not stripped.startswith(' ') and ':' not in stripped:
                break

    return ""
