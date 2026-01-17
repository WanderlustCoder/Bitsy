"""
MCP Server for Bitsy sprite generation.

Provides Model Context Protocol interface for AI assistants
like Claude to interact with Bitsy's generation tools.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.tools import ToolRegistry, get_tools
from ai.tools.results import GenerationResult, ToolResult
from ai.parser import parse_prompt, ParsedPrompt


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class MCPToolResult:
    """MCP Tool execution result."""
    content: List[Dict[str, Any]]
    isError: bool = False


class MCPServer:
    """MCP Server for Bitsy tools.

    Implements the Model Context Protocol to expose Bitsy's
    sprite generation capabilities to AI assistants.
    """

    def __init__(self):
        """Initialize MCP server."""
        self._registry = ToolRegistry.get_instance()
        self._session_id = None

    def get_tools(self) -> List[MCPTool]:
        """Get all available tools in MCP format.

        Returns:
            List of MCPTool definitions
        """
        tools = []

        for registered in self._registry.all():
            schema = self._build_schema(registered)
            tools.append(MCPTool(
                name=registered.name,
                description=registered.description or f"Tool: {registered.name}",
                inputSchema=schema,
            ))

        # Add high-level natural language tool
        tools.append(MCPTool(
            name="generate_from_prompt",
            description="Generate a sprite from a natural language description. "
                        "Example: 'a red-haired warrior' or 'blue slime monster'",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Natural language description of what to generate",
                    },
                },
                "required": ["prompt"],
            },
        ))

        return tools

    def _build_schema(self, tool) -> Dict[str, Any]:
        """Build JSON schema for a tool's parameters."""
        import inspect

        schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        sig = inspect.signature(tool.function)
        hints = tool.function.__annotations__ if hasattr(tool.function, '__annotations__') else {}

        for name, param in sig.parameters.items():
            if name in ('self', 'cls'):
                continue

            prop = {"description": f"Parameter: {name}"}

            # Infer type from annotation
            hint = hints.get(name)
            if hint:
                prop["type"] = self._python_type_to_json(hint)
            else:
                prop["type"] = "string"

            # Check for default value
            if param.default is inspect.Parameter.empty:
                schema["required"].append(name)
            else:
                prop["default"] = param.default if not callable(param.default) else None

            schema["properties"][name] = prop

        return schema

    def _python_type_to_json(self, hint) -> str:
        """Convert Python type hint to JSON schema type."""
        type_str = str(hint)

        if 'int' in type_str:
            return "integer"
        elif 'float' in type_str:
            return "number"
        elif 'bool' in type_str:
            return "boolean"
        elif 'List' in type_str or 'list' in type_str:
            return "array"
        elif 'Dict' in type_str or 'dict' in type_str:
            return "object"
        else:
            return "string"

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool call.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            MCPToolResult with execution result
        """
        try:
            # Handle natural language tool
            if name == "generate_from_prompt":
                return self._handle_prompt(arguments.get("prompt", ""))

            # Get registered tool
            tool = self._registry.get(name)
            if tool is None:
                return MCPToolResult(
                    content=[{"type": "text", "text": f"Unknown tool: {name}"}],
                    isError=True,
                )

            # Execute tool
            result = tool.function(**arguments)

            # Format result
            return self._format_result(result)

        except Exception as e:
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                isError=True,
            )

    def _handle_prompt(self, prompt: str) -> MCPToolResult:
        """Handle natural language prompt."""
        parsed = parse_prompt(prompt)

        if parsed.needs_clarification:
            options = "\n".join(f"- {opt}" for opt in parsed.clarification_options)
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": f"I need more information. What would you like to generate?\n{options}",
                }],
            )

        if parsed.tool_call is None:
            return MCPToolResult(
                content=[{"type": "text", "text": "Could not understand the request."}],
                isError=True,
            )

        # Execute the parsed tool call
        return self.call_tool(parsed.tool_call.tool_name, parsed.tool_call.parameters)

    def _format_result(self, result: Any) -> MCPToolResult:
        """Format a tool result for MCP response."""
        content = []

        if isinstance(result, ToolResult):
            if not result.success:
                return MCPToolResult(
                    content=[{"type": "text", "text": f"Error: {result.error}"}],
                    isError=True,
                )
            result = result.result

        if isinstance(result, GenerationResult):
            # Include text description
            content.append({
                "type": "text",
                "text": f"Generated {result.sprite_type or 'sprite'} "
                        f"({result.canvas.width}x{result.canvas.height}) "
                        f"in {result.generation_time_ms:.1f}ms",
            })

            # Include quality score if available
            if result.quality_score:
                content.append({
                    "type": "text",
                    "text": f"Quality: {result.quality_score.overall:.2f}",
                })

            # Include image data as base64 PNG
            try:
                import base64
                import io
                from export.png import save_png

                # Save to bytes buffer
                buffer = io.BytesIO()
                # Create temp file path
                temp_path = "/tmp/mcp_sprite.png"
                save_png(result.canvas, temp_path)
                with open(temp_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')

                content.append({
                    "type": "image",
                    "data": image_data,
                    "mimeType": "image/png",
                })
            except Exception:
                # Image encoding failed, just return text
                pass

        elif isinstance(result, dict):
            content.append({
                "type": "text",
                "text": json.dumps(result, indent=2, default=str),
            })

        elif isinstance(result, list):
            content.append({
                "type": "text",
                "text": json.dumps(result, indent=2, default=str),
            })

        else:
            content.append({
                "type": "text",
                "text": str(result),
            })

        return MCPToolResult(content=content)

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP message.

        Args:
            message: MCP protocol message

        Returns:
            MCP response message
        """
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "bitsy-sprite-generator",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "tools/list":
            tools = self.get_tools()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [asdict(t) for t in tools],
                },
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = self.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": asdict(result),
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

    def run_stdio(self):
        """Run the MCP server using stdio transport."""
        import sys

        while True:
            try:
                # Read message
                line = sys.stdin.readline()
                if not line:
                    break

                message = json.loads(line)
                response = self.handle_message(message)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": str(e),
                    },
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


def create_server() -> MCPServer:
    """Create an MCP server instance."""
    return MCPServer()


def run_server():
    """Run the MCP server."""
    server = create_server()
    server.run_stdio()


if __name__ == "__main__":
    run_server()
