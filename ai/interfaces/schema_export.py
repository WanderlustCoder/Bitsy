"""
JSON Schema export for LLM tool integration.

Exports Bitsy tools as JSON schemas compatible with
OpenAI function calling, Claude tools, and other LLM providers.
"""

import json
import inspect
from typing import Dict, List, Any, Optional, get_type_hints, Union
from dataclasses import dataclass, asdict
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.tools import ToolRegistry


class SchemaFormat(Enum):
    """Supported schema export formats."""
    OPENAI = "openai"           # OpenAI function calling format
    ANTHROPIC = "anthropic"     # Anthropic/Claude tools format
    GENERIC = "generic"         # Generic JSON schema


@dataclass
class ParameterSchema:
    """Schema for a single parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None


@dataclass
class FunctionSchema:
    """Schema for a function/tool."""
    name: str
    description: str
    parameters: List[ParameterSchema]
    returns: Optional[str] = None


class SchemaExporter:
    """Exports tool schemas in various formats."""

    def __init__(self):
        """Initialize the exporter."""
        self._registry = ToolRegistry.get_instance()

    def export_all(self, format: SchemaFormat = SchemaFormat.OPENAI) -> List[Dict[str, Any]]:
        """Export all tools in the specified format.

        Args:
            format: Output format

        Returns:
            List of tool schemas
        """
        schemas = []

        for tool in self._registry.all():
            schema = self._build_function_schema(tool)
            formatted = self._format_schema(schema, format)
            schemas.append(formatted)

        return schemas

    def export_one(self, tool_name: str, format: SchemaFormat = SchemaFormat.OPENAI) -> Optional[Dict[str, Any]]:
        """Export a single tool schema.

        Args:
            tool_name: Name of the tool
            format: Output format

        Returns:
            Tool schema or None if not found
        """
        tool = self._registry.get(tool_name)
        if tool is None:
            return None

        schema = self._build_function_schema(tool)
        return self._format_schema(schema, format)

    def export_by_category(
        self,
        category: str,
        format: SchemaFormat = SchemaFormat.OPENAI,
    ) -> List[Dict[str, Any]]:
        """Export tools in a specific category.

        Args:
            category: Tool category
            format: Output format

        Returns:
            List of tool schemas
        """
        schemas = []

        for tool in self._registry.all():
            if tool.category == category:
                schema = self._build_function_schema(tool)
                formatted = self._format_schema(schema, format)
                schemas.append(formatted)

        return schemas

    def _build_function_schema(self, tool) -> FunctionSchema:
        """Build a FunctionSchema from a registered tool."""
        sig = inspect.signature(tool.function)

        # Get type hints
        try:
            hints = get_type_hints(tool.function)
        except Exception:
            hints = getattr(tool.function, '__annotations__', {})

        # Get docstring for parameter descriptions
        doc = inspect.getdoc(tool.function) or ""
        param_docs = self._parse_docstring_params(doc)

        parameters = []
        for name, param in sig.parameters.items():
            if name in ('self', 'cls'):
                continue

            # Get type
            hint = hints.get(name)
            json_type = self._python_type_to_json_type(hint)

            # Get description from docstring
            description = param_docs.get(name, f"Parameter: {name}")

            # Check if required
            required = param.default is inspect.Parameter.empty

            # Get default value
            default = None if required else param.default

            # Check for enum types
            enum_values = None
            if hint and hasattr(hint, '__origin__'):
                # Handle Literal types
                if str(hint).startswith('typing.Literal'):
                    enum_values = list(hint.__args__)

            parameters.append(ParameterSchema(
                name=name,
                type=json_type,
                description=description,
                required=required,
                default=default,
                enum=enum_values,
            ))

        # Get return type
        return_hint = hints.get('return')
        return_type = self._python_type_to_json_type(return_hint) if return_hint else None

        return FunctionSchema(
            name=tool.name,
            description=tool.description or self._extract_description(doc),
            parameters=parameters,
            returns=return_type,
        )

    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring."""
        params = {}
        in_args = False

        for line in docstring.split('\n'):
            line = line.strip()
            if line.lower().startswith('args:'):
                in_args = True
                continue
            if line.lower().startswith('returns:'):
                in_args = False
                continue

            if in_args and ':' in line:
                # Parse "param_name: description"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    description = parts[1].strip()
                    params[param_name] = description

        return params

    def _extract_description(self, docstring: str) -> str:
        """Extract the main description from a docstring."""
        lines = docstring.split('\n')
        description_lines = []

        for line in lines:
            line = line.strip()
            if line.lower().startswith(('args:', 'returns:', 'raises:', 'example:')):
                break
            if line:
                description_lines.append(line)

        return ' '.join(description_lines)

    def _python_type_to_json_type(self, hint) -> str:
        """Convert Python type hint to JSON schema type."""
        if hint is None:
            return "string"

        type_str = str(hint)

        # Handle Optional types
        if 'Optional' in type_str or 'Union' in type_str:
            # Extract the inner type
            if hasattr(hint, '__args__'):
                for arg in hint.__args__:
                    if arg is not type(None):
                        return self._python_type_to_json_type(arg)

        # Basic types
        if hint == int or 'int' in type_str:
            return "integer"
        elif hint == float or 'float' in type_str:
            return "number"
        elif hint == bool or 'bool' in type_str:
            return "boolean"
        elif hint == str or 'str' in type_str:
            return "string"
        elif 'List' in type_str or 'list' in type_str:
            return "array"
        elif 'Dict' in type_str or 'dict' in type_str:
            return "object"

        return "string"

    def _format_schema(self, schema: FunctionSchema, format: SchemaFormat) -> Dict[str, Any]:
        """Format a schema for the specified output format."""
        if format == SchemaFormat.OPENAI:
            return self._format_openai(schema)
        elif format == SchemaFormat.ANTHROPIC:
            return self._format_anthropic(schema)
        else:
            return self._format_generic(schema)

    def _format_openai(self, schema: FunctionSchema) -> Dict[str, Any]:
        """Format for OpenAI function calling."""
        properties = {}
        required = []

        for param in schema.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": schema.name,
                "description": schema.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def _format_anthropic(self, schema: FunctionSchema) -> Dict[str, Any]:
        """Format for Anthropic/Claude tools."""
        properties = {}
        required = []

        for param in schema.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": schema.name,
            "description": schema.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _format_generic(self, schema: FunctionSchema) -> Dict[str, Any]:
        """Format as generic JSON schema."""
        properties = {}
        required = []

        for param in schema.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": schema.name,
            "description": schema.description,
            "type": "object",
            "properties": properties,
            "required": required,
        }


def export_openai_functions() -> List[Dict[str, Any]]:
    """Export all tools as OpenAI function schemas.

    Returns:
        List of function schemas for OpenAI API
    """
    exporter = SchemaExporter()
    return exporter.export_all(SchemaFormat.OPENAI)


def export_anthropic_tools() -> List[Dict[str, Any]]:
    """Export all tools as Anthropic/Claude tool schemas.

    Returns:
        List of tool schemas for Claude API
    """
    exporter = SchemaExporter()
    return exporter.export_all(SchemaFormat.ANTHROPIC)


def export_json_schema() -> List[Dict[str, Any]]:
    """Export all tools as generic JSON schemas.

    Returns:
        List of JSON schemas
    """
    exporter = SchemaExporter()
    return exporter.export_all(SchemaFormat.GENERIC)


def save_schemas(
    path: str,
    format: SchemaFormat = SchemaFormat.OPENAI,
    pretty: bool = True,
):
    """Save all tool schemas to a file.

    Args:
        path: Output file path
        format: Schema format
        pretty: Pretty-print JSON
    """
    exporter = SchemaExporter()
    schemas = exporter.export_all(format)

    with open(path, 'w') as f:
        if pretty:
            json.dump(schemas, f, indent=2)
        else:
            json.dump(schemas, f)


def get_schema_for_tool(
    tool_name: str,
    format: SchemaFormat = SchemaFormat.OPENAI,
) -> Optional[Dict[str, Any]]:
    """Get schema for a specific tool.

    Args:
        tool_name: Name of the tool
        format: Schema format

    Returns:
        Tool schema or None
    """
    exporter = SchemaExporter()
    return exporter.export_one(tool_name, format)
