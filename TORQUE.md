# TORQUE Integration Guide - bitsy

TORQUE (Task Orchestration & Resource Queue Engine) enables parallel task execution for your Python AI development project.

## Project Overview

Bitsy is a Python project with AI capabilities, animation support, and comprehensive development documentation including a roadmap.

## MCP Configuration

Your `.mcp.json` already exists. Add TORQUE:

```json
{
  "mcpServers": {
    "torque": {
      "command": "node",
      "args": ["/mnt/c/Users/Werem/Projects/Torque/dist/index.js"],
      "env": {}
    }
  }
}
```

## Recommended Task Templates

### Run Tests
```
Submit task: "Run pytest on all test files with coverage report"
```

### AI Module Testing
```
Submit task: "Test ai/ module functionality and validate outputs"
```

### Animation Processing
```
Submit task: "Process animation/ assets and verify rendering"
```

## Example Workflows

### Development Pipeline
```
Create pipeline:
1. Install dependencies (pip install -e .)
2. Run linting (ruff or flake8)
3. Run type checking (mypy)
4. Run unit tests (pytest)
5. Run AI module integration tests
6. Generate documentation
```

### Parallel Component Testing
```
Queue tasks in parallel:
- "Test ai/ module"
- "Test animation/ module"
- "Validate UserExamples/"
```

### Roadmap Progress
```
Submit task: "Analyze ROADMAP.md and report completion status of current milestone"
```

### User Example Validation
```
Submit task: "Run all examples in UserExamples/ and verify expected outputs"
```

## Worktree Support

Your project has .worktrees/ for parallel development:
```
Queue tasks in parallel (different worktrees):
- "Develop feature-a in .worktrees/feature-a"
- "Develop feature-b in .worktrees/feature-b"
```

## Tips

- Use `timeout_minutes: 15` for AI model operations
- Tag tasks by component: `tags: ["ai", "test"]` or `tags: ["animation", "render"]`
- Reference DEVELOPMENT.md for coding standards
- Reference ROADMAP.md for feature priorities
- Use pipelines for lint -> test -> build sequences
- Leverage worktrees for isolated parallel work
