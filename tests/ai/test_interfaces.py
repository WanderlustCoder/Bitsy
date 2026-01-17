"""Tests for AI interfaces module."""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.interfaces import (
    MCPServer,
    MCPTool,
    MCPToolResult,
    create_server,
    SchemaFormat,
    SchemaExporter,
    export_openai_functions,
    export_anthropic_tools,
    export_json_schema,
    get_schema_for_tool,
)


class TestMCPServer:
    """Tests for MCP server."""

    def test_create_server(self):
        """Test server creation."""
        server = create_server()
        assert isinstance(server, MCPServer)

    def test_get_tools(self):
        """Test getting tool list."""
        server = MCPServer()
        tools = server.get_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(t, MCPTool) for t in tools)

    def test_tool_has_schema(self):
        """Test that tools have valid schemas."""
        server = MCPServer()
        tools = server.get_tools()

        for tool in tools:
            assert tool.name
            assert tool.description
            assert isinstance(tool.inputSchema, dict)
            assert tool.inputSchema.get("type") == "object"

    def test_natural_language_tool(self):
        """Test natural language tool is present."""
        server = MCPServer()
        tools = server.get_tools()

        nl_tool = None
        for tool in tools:
            if tool.name == "generate_from_prompt":
                nl_tool = tool
                break

        assert nl_tool is not None
        assert "prompt" in nl_tool.inputSchema.get("properties", {})

    def test_handle_initialize(self):
        """Test initialize message handling."""
        server = MCPServer()
        response = server.handle_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })

        assert response["id"] == 1
        assert "result" in response
        assert "protocolVersion" in response["result"]
        assert "capabilities" in response["result"]

    def test_handle_tools_list(self):
        """Test tools/list message handling."""
        server = MCPServer()
        response = server.handle_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })

        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0

    def test_handle_unknown_method(self):
        """Test handling unknown method."""
        server = MCPServer()
        response = server.handle_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {},
        })

        assert response["id"] == 3
        assert "error" in response
        assert response["error"]["code"] == -32601


class TestMCPToolResult:
    """Tests for MCP tool results."""

    def test_success_result(self):
        """Test successful result."""
        result = MCPToolResult(
            content=[{"type": "text", "text": "Success"}],
            isError=False,
        )

        assert result.isError is False
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"

    def test_error_result(self):
        """Test error result."""
        result = MCPToolResult(
            content=[{"type": "text", "text": "Error occurred"}],
            isError=True,
        )

        assert result.isError is True


class TestSchemaExporter:
    """Tests for schema exporter."""

    def test_export_all_openai(self):
        """Test exporting all tools in OpenAI format."""
        schemas = export_openai_functions()

        assert isinstance(schemas, list)
        assert len(schemas) > 0

        for schema in schemas:
            assert schema.get("type") == "function"
            assert "function" in schema
            assert "name" in schema["function"]
            assert "parameters" in schema["function"]

    def test_export_all_anthropic(self):
        """Test exporting all tools in Anthropic format."""
        schemas = export_anthropic_tools()

        assert isinstance(schemas, list)
        assert len(schemas) > 0

        for schema in schemas:
            assert "name" in schema
            assert "input_schema" in schema
            assert schema["input_schema"].get("type") == "object"

    def test_export_json_schema(self):
        """Test exporting generic JSON schemas."""
        schemas = export_json_schema()

        assert isinstance(schemas, list)
        assert len(schemas) > 0

        for schema in schemas:
            assert "$schema" in schema or "title" in schema
            assert "properties" in schema

    def test_get_specific_tool_schema(self):
        """Test getting schema for specific tool."""
        # Get a tool that we know exists
        from ai.tools import get_tools
        registry = get_tools()
        tools = registry.all()

        if tools:
            tool_name = tools[0].name
            schema = get_schema_for_tool(tool_name)

            assert schema is not None
            assert "function" in schema

    def test_get_nonexistent_tool_schema(self):
        """Test getting schema for nonexistent tool."""
        schema = get_schema_for_tool("nonexistent_tool_xyz")
        assert schema is None

    def test_schema_has_required_fields(self):
        """Test that schemas have required fields marked."""
        schemas = export_openai_functions()

        for schema in schemas:
            func = schema.get("function", {})
            params = func.get("parameters", {})

            assert "properties" in params
            assert "required" in params
            assert isinstance(params["required"], list)

    def test_export_by_category(self):
        """Test exporting tools by category."""
        exporter = SchemaExporter()

        # Export generation tools
        schemas = exporter.export_by_category("generation")
        # May be empty if no tools have that category
        assert isinstance(schemas, list)


class TestSchemaFormat:
    """Tests for schema format enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert SchemaFormat.OPENAI.value == "openai"
        assert SchemaFormat.ANTHROPIC.value == "anthropic"
        assert SchemaFormat.GENERIC.value == "generic"


class TestSchemaIntegration:
    """Integration tests for schema export."""

    def test_openai_schema_is_valid_json(self):
        """Test that OpenAI schemas are valid JSON."""
        schemas = export_openai_functions()
        json_str = json.dumps(schemas)
        parsed = json.loads(json_str)
        assert parsed == schemas

    def test_anthropic_schema_is_valid_json(self):
        """Test that Anthropic schemas are valid JSON."""
        schemas = export_anthropic_tools()
        json_str = json.dumps(schemas)
        parsed = json.loads(json_str)
        assert parsed == schemas

    def test_schema_parameter_types(self):
        """Test that parameter types are valid JSON schema types."""
        valid_types = {"string", "integer", "number", "boolean", "array", "object"}
        schemas = export_json_schema()

        for schema in schemas:
            properties = schema.get("properties", {})
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type")
                assert prop_type in valid_types, f"Invalid type {prop_type} for {prop_name}"
