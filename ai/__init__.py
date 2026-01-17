"""
Bitsy AI Integration - LLM-powered sprite generation.

This module provides AI integration capabilities:
- Tool Interface: Python API, MCP server, JSON schemas
- NL Parser: Natural language to tool call conversion
- Agent: Autonomous generation with planning, memory, and refinement

Quick Start:

    # Parse and execute from natural language
    from ai import parse_prompt
    result = parse_prompt("a red-haired warrior")
    print(result.tool_call)

    # Use tools directly
    from ai.tools import generate_character, generate_scene

    # Agent with memory and planning
    from ai.agent import AgentMemory, Planner, Refiner
    memory = AgentMemory()
    planner = Planner()
    plan = planner.create_plan("a party of 4 heroes")

    # MCP server for Claude Code
    from ai.interfaces import run_server
    run_server()

    # Export schemas for OpenAI/Claude
    from ai.interfaces import export_openai_functions
    schemas = export_openai_functions()
"""

# Result types
from .tools.results import (
    GenerationResult,
    AnimationResult,
    ToolResult,
    QualityScore,
)

# Tool definitions
from .tools.definitions import tool, ToolRegistry

# High-level tools
from .tools import (
    get_tools,
    list_tools,
)

# Parser
from .parser import (
    parse_prompt,
    ParsedPrompt,
    ToolCall,
    ParserConfig,
    VocabularyRegistry,
    TemplateRegistry,
    get_vocabulary,
    get_templates,
    extract_keywords,
    match_templates,
)

# Agent
from .agent import (
    AgentMemory,
    GenerationRecord,
    StylePreferences,
    get_memory,
    reset_memory,
    QualityEvaluator,
    EvaluationCriteria,
    evaluate_canvas,
    Planner,
    ExecutionPlan,
    PlanStep,
    create_plan,
    Refiner,
    RefinementType,
    RefinementSuggestion,
    auto_refine,
)

# Interfaces
from .interfaces import (
    MCPServer,
    create_server,
    run_server,
    SchemaFormat,
    SchemaExporter,
    export_openai_functions,
    export_anthropic_tools,
    export_json_schema,
    save_schemas,
)

__all__ = [
    # Results
    'GenerationResult',
    'AnimationResult',
    'ToolResult',
    'QualityScore',

    # Tool definitions
    'tool',
    'ToolRegistry',
    'get_tools',
    'list_tools',

    # Parser
    'parse_prompt',
    'ParsedPrompt',
    'ToolCall',
    'ParserConfig',
    'VocabularyRegistry',
    'TemplateRegistry',
    'get_vocabulary',
    'get_templates',
    'extract_keywords',
    'match_templates',

    # Agent - Memory
    'AgentMemory',
    'GenerationRecord',
    'StylePreferences',
    'get_memory',
    'reset_memory',

    # Agent - Evaluator
    'QualityEvaluator',
    'EvaluationCriteria',
    'evaluate_canvas',

    # Agent - Planner
    'Planner',
    'ExecutionPlan',
    'PlanStep',
    'create_plan',

    # Agent - Refiner
    'Refiner',
    'RefinementType',
    'RefinementSuggestion',
    'auto_refine',

    # Interfaces
    'MCPServer',
    'create_server',
    'run_server',
    'SchemaFormat',
    'SchemaExporter',
    'export_openai_functions',
    'export_anthropic_tools',
    'export_json_schema',
    'save_schemas',
]
