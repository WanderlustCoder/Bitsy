# AI Integration Hooks Design

**Date:** 2025-01-17
**Status:** Approved
**Phase:** 4.3

## Overview

AI Integration system for Bitsy enabling LLM-powered sprite generation through a layered architecture: Tool Interface → Natural Language Parser → Autonomous Agent.

## Architecture

```
┌─────────────────────────────────────────────┐
│           Layer 3: Agent                    │
│  Planning, Memory, Refinement, Consistency  │
├─────────────────────────────────────────────┤
│           Layer 2: NL Parser                │
│   Keyword extraction + LLM fallback         │
├─────────────────────────────────────────────┤
│           Layer 1: Tool Interface           │
│   Python API + MCP Server + JSON Schemas    │
├─────────────────────────────────────────────┤
│         Existing Bitsy Modules              │
│  generators, animation, export, effects...  │
└─────────────────────────────────────────────┘
```

## Module Structure

```
ai/
├── __init__.py           # Public API exports
├── tools/
│   ├── __init__.py
│   ├── definitions.py    # Tool definitions with schemas
│   ├── characters.py     # Character generation tools
│   ├── items.py          # Item/prop tools
│   ├── scenes.py         # Scene/environment tools
│   ├── animation.py      # Animation tools
│   └── export.py         # Export tools
├── parser/
│   ├── __init__.py
│   ├── keywords.py       # Keyword extraction
│   ├── templates.py      # Template patterns
│   └── llm_fallback.py   # Optional LLM parsing
├── agent/
│   ├── __init__.py
│   ├── planner.py        # Multi-step planning
│   ├── evaluator.py      # Quality scoring
│   ├── memory.py         # Session context
│   └── refiner.py        # Iterative refinement
├── mcp_server.py         # MCP protocol wrapper
└── schemas.py            # JSON schema export
```

## Layer 1: Tool Interface

### Design Decisions

- **Python API as core** — typed functions with docstrings
- **MCP wrapper** — for Claude Code integration
- **JSON schema export** — for OpenAI/other providers
- **Both high-level and low-level tools** — convenience + granular control

### High-Level Tools

```python
@tool(name="generate_sprite", category="generation")
def generate_sprite(
    description: str,
    type: SpriteType = "auto",
    style: str = "default",
    size: Tuple[int, int] = (32, 32),
    seed: Optional[int] = None,
) -> GenerationResult:

@tool(name="generate_scene")
def generate_scene(
    description: str,
    width: int = 320,
    height: int = 180,
    time_of_day: str = "noon",
    weather: str = "clear",
) -> GenerationResult:

@tool(name="create_animation")
def create_animation(
    sprite: GenerationResult,
    animation_type: str,
    frames: int = 4,
    fps: int = 12,
) -> AnimationResult:
```

### Low-Level Tools

```python
@tool(name="set_character_hair")
def set_character_hair(character, style, color="brown") -> CharacterResult:

@tool(name="apply_palette")
def apply_palette(sprite, palette) -> GenerationResult:

@tool(name="add_effect")
def add_effect(sprite, effect, **params) -> GenerationResult:
```

### Result Types

```python
@dataclass
class GenerationResult:
    canvas: Canvas
    parameters: Dict[str, Any]
    seed: int
    metadata: Dict[str, Any]
```

## Layer 2: Natural Language Parser

### Design Decisions

- **Hybrid approach** — keyword/template for common cases, LLM fallback for complex
- **Extensible at runtime** — dynamic vocabulary and template registration
- **Auto-sync with generators** — new generators auto-update vocabulary

### Keyword Extraction

```python
class VocabularyRegistry:
    def register(self, category: str, keywords: Dict[str, str]):
        """Add new keywords at runtime."""

    def register_from_file(self, path: str):
        """Load vocabulary from JSON/YAML file."""
```

### Template Matching

```python
TEMPLATES = [
    Template(r"an?\s+(\w+)\s+(warrior|mage|...)", handler),
    Template(r"(warrior|mage|...)\s+with\s+(.+)", handler),
]
```

### Parser Pipeline

```
prompt → keyword extraction → template matching → confidence check
                                                      ↓
                                        high: return tool call
                                        low: LLM fallback (if available)
                                        no LLM: best guess + warnings
```

## Layer 3: Agent

### Capabilities

1. **Generation planning** — break complex requests into steps
2. **Quality evaluation** — score output, reject if below threshold
3. **Variation generation** — produce N variations, select best
4. **Iterative refinement** — adjust based on feedback
5. **Memory/context** — remember previous generations
6. **Style consistency** — ensure multiple sprites share style

### Planner

```python
class GenerationPlanner:
    def plan(self, request: str, context: AgentContext) -> Plan:
        """Create execution plan from request."""

    def execute(self, plan: Plan) -> List[GenerationResult]:
        """Execute plan steps, handling dependencies."""
```

### Memory

```python
class AgentMemory:
    generations: List[GenerationResult]
    style_context: Optional[StyleContext]
    references: Dict[str, GenerationResult]

    def remember(self, result, name=None): ...
    def recall(self, reference: str): ...
    def get_style_context(self): ...
```

### Evaluator

```python
class QualityEvaluator:
    def evaluate(self, result) -> QualityScore:
    def passes_threshold(self, result, min_score=0.7) -> bool:
    def select_best(self, results) -> GenerationResult:
```

### Refiner

```python
class IterativeRefiner:
    def refine(self, result, feedback: str) -> GenerationResult:
    def interpret_feedback(self, feedback, current) -> Adjustments:
```

## Integration Layer

### MCP Server

```python
class BitsyMCPServer:
    def _register_tools(self): ...
    def run(self, transport="stdio"): ...
```

### JSON Schema Export

```python
def export_openai_functions() -> List[Dict]:
def export_json_schemas(output_dir: str):
```

## Error Handling

```python
class AIError(Exception):
    suggestion: str

class ParseError(AIError): ...
class GenerationError(AIError): ...
class QualityError(AIError): ...

@dataclass
class ToolResult:
    success: bool
    result: Optional[GenerationResult]
    error: Optional[AIError]
    warnings: List[str]
```

## Public API

```python
# High-level
from ai import generate_sprite, generate_scene, create_animation
from ai import parse_prompt, Agent

# Building blocks
from ai import ToolRegistry, tool
from ai import VocabularyRegistry, TemplateRegistry
from ai import GenerationPlanner, AgentMemory, QualityEvaluator

# Integration
from ai import BitsyMCPServer
from ai import export_openai_functions, export_json_schemas
```

## Usage Examples

```python
# Simple one-liner
sprite = generate_sprite("a goblin with a torch")
sprite.canvas.save("goblin.png")

# Agent with memory
agent = Agent()
warrior = agent.generate("a knight in silver armor")
agent.generate("give him a flaming sword")
agent.generate("now make 3 variations")

# MCP server
BitsyMCPServer().run()
```

## Testing Strategy

- `tests/ai/test_tools.py` — unit tests for each tool
- `tests/ai/test_parser.py` — parser with known inputs
- `tests/ai/test_agent.py` — agent planning and memory
- `tests/ai/test_integration.py` — end-to-end flows

## Implementation Order

1. Layer 1: Tool Interface (Python API)
2. Layer 1: Result types and error handling
3. Layer 2: Keyword extraction
4. Layer 2: Template matching
5. Layer 3: Memory
6. Layer 3: Evaluator
7. Layer 3: Planner
8. Layer 3: Refiner
9. Integration: MCP Server
10. Integration: JSON Schema export
11. Layer 2: LLM fallback (optional)
