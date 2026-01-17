"""
AI Interfaces - External integration points.

Provides MCP server and schema export capabilities
for integrating with AI assistants and LLM APIs.
"""

from .mcp_server import (
    MCPServer,
    MCPTool,
    MCPToolResult,
    create_server,
    run_server,
)

from .schema_export import (
    SchemaFormat,
    SchemaExporter,
    FunctionSchema,
    ParameterSchema,
    export_openai_functions,
    export_anthropic_tools,
    export_json_schema,
    save_schemas,
    get_schema_for_tool,
)

__all__ = [
    # MCP Server
    'MCPServer',
    'MCPTool',
    'MCPToolResult',
    'create_server',
    'run_server',

    # Schema Export
    'SchemaFormat',
    'SchemaExporter',
    'FunctionSchema',
    'ParameterSchema',
    'export_openai_functions',
    'export_anthropic_tools',
    'export_json_schema',
    'save_schemas',
    'get_schema_for_tool',
]
