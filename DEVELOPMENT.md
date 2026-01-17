# Development Guide

This document describes Bitsy's dual-agent development workflow using Claude and OpenAI Codex working in parallel.

## Philosophy

Bitsy is developed by AI agents under human direction. To maximize productivity, we employ a **parallel agent architecture**:

- **Claude** acts as both **orchestrator** and **developer**
- **Codex** acts as a **delegated developer** for suitable tasks
- Human provides requirements, feedback, and final approval

### Productivity Model

```
Traditional:     Claude ████████████████████ (1x throughput)

Parallel:        Claude ████████░░░░████████ (orchestrating + developing)
                 Codex  ░░░░████████░░░░████ (delegated tasks)
                                             (≈2x throughput)
```

When Codex is idle, Claude identifies and delegates appropriate tasks.
While Codex works, Claude continues development independently.
When Codex completes, Claude reviews and integrates the results.

---

## Task Delegation Protocol

### Complexity Assessment

Before delegating, Claude assesses each task on these dimensions:

| Factor | Delegate to Codex | Keep for Claude |
|--------|-------------------|-----------------|
| **Scope** | Single file, isolated function | Multi-file, cross-module |
| **Context needed** | Self-contained, well-defined | Requires conversation history |
| **Risk** | Low impact if incorrect | Core systems, breaking changes |
| **Dependencies** | Few or none | Depends on uncommitted work |
| **Review effort** | Easy to verify (tests, visual) | Requires deep review |

### Ideal Codex Tasks

- Writing unit tests for existing functions
- Implementing single generators (e.g., new item type)
- Adding recipe documentation
- Utility functions with clear specs
- Bug fixes with reproducible test cases
- Code formatting, refactoring isolated sections

### Claude-Only Tasks

- Architectural decisions
- Multi-file refactors
- Reviewing and integrating Codex output
- Tasks requiring conversation context
- Debugging complex issues
- Orchestration and planning

### Decision Rule

```
IF task is well-defined
   AND affects ≤2 files
   AND has clear success criteria
   AND Codex is idle
THEN delegate to Codex
ELSE Claude handles directly
```

---

## Handoff Protocol

### Delegating to Codex

When delegating, Claude provides a structured task description:

```
TASK: [Brief title]
───────────────────────────────────────
OBJECTIVE:
  [What needs to be accomplished]

FILES:
  - [file1.py] - [what to do]
  - [file2.py] - [what to do]

REQUIREMENTS:
  1. [Specific requirement]
  2. [Specific requirement]
  3. [Specific requirement]

SUCCESS CRITERIA:
  - [ ] [How to verify completion]
  - [ ] [Tests that must pass]
  - [ ] [Expected output/behavior]

CONTEXT:
  [Any relevant background, links to docs/recipes]

DO NOT:
  - [Explicit boundaries/constraints]
───────────────────────────────────────
```

### Example Handoff

```
TASK: Add RedPotion generator
───────────────────────────────────────
OBJECTIVE:
  Create a red health potion variant in the item generator

FILES:
  - generators/item.py - add RedPotion class

REQUIREMENTS:
  1. Follow existing Potion class pattern
  2. Use HEALTH_POTION palette from core/palette.py
  3. Include bubble particle effect

SUCCESS CRITERIA:
  - [ ] RedPotion().generate() produces 16x16 canvas
  - [ ] Tests pass: python -m tests.runner --filter item
  - [ ] Matches visual style of existing potions

CONTEXT:
  See recipes/objects/potions.md for rendering approach

DO NOT:
  - Modify existing potion classes
  - Add new dependencies
───────────────────────────────────────
```

---

## Review Protocol

### When Codex Completes

Claude must review all Codex output before integration.

### Review Checklist

```
□ CORRECTNESS
  - Does the code do what was requested?
  - Do all tests pass?
  - Any logic errors or edge cases missed?

□ CONSISTENCY
  - Follows project code style?
  - Matches patterns in similar modules?
  - Uses existing utilities (not reinventing)?

□ QUALITY
  - No over-engineering beyond requirements?
  - Appropriate error handling?
  - Clean, readable implementation?

□ SAFETY
  - No security issues introduced?
  - No breaking changes to public APIs?
  - Deterministic output (same seed = same result)?

□ DOCUMENTATION
  - Docstrings present and accurate?
  - Tests cover the new functionality?
```

### Integration Actions

| Review Result | Action |
|---------------|--------|
| **Pass** | Commit with attribution, mark task complete |
| **Minor issues** | Claude fixes directly, then commits |
| **Major issues** | Re-delegate with clarified requirements |
| **Fundamentally wrong** | Discard, Claude implements directly |

### Commit Attribution

All commits include authorship:

```bash
git commit -m "Add RedPotion generator

Implemented by Codex, reviewed by Claude.

Co-Authored-By: OpenAI Codex <codex@openai.com>
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Parallel Work Tracking

### Status Format

During development sessions, Claude maintains a status block:

```
╔═══════════════════════════════════════════════════════════╗
║ PARALLEL DEVELOPMENT STATUS                               ║
╠═══════════════════════════════════════════════════════════╣
║ CLAUDE                        │ CODEX                     ║
║ ───────────────────────────── │ ─────────────────────────║
║ [●] Implementing HD canvas    │ [●] Writing particle tests║
║     core/hd_canvas.py         │     tests/effects/        ║
║     Progress: 60%             │     Status: In progress   ║
╠═══════════════════════════════════════════════════════════╣
║ QUEUE                                                     ║
║ [ ] Add selout quality filter                             ║
║ [ ] Update hair recipe with new styles                    ║
║ [ ] Fix gradient dithering edge case                      ║
╠═══════════════════════════════════════════════════════════╣
║ COMPLETED THIS SESSION                                    ║
║ [✓] Style presets system (Claude)                         ║
║ [✓] Eye expression variants (Codex → reviewed)            ║
╚═══════════════════════════════════════════════════════════╝
```

### Status Symbols

| Symbol | Meaning |
|--------|---------|
| `[●]` | In progress |
| `[○]` | Delegated, awaiting result |
| `[✓]` | Completed |
| `[!]` | Blocked / needs attention |
| `[ ]` | Queued |

### When to Update Status

- When delegating a new task to Codex
- When Codex completes (before review)
- When completing own tasks
- When adding items to queue
- When encountering blockers

---

## Using the Codex Bridge

### Invocation

Claude delegates via the MCP tool:

```python
delegate_to_codex(
    task="[Structured task description from handoff format]",
    working_directory="/path/to/bitsy",
    auto_approve=False  # Recommended: require approval for safety
)
```

### Workflow Example

```
1. Human: "Add creature variants: slime, ghost, and bat"

2. Claude assesses:
   - 3 independent tasks
   - Each is single-file, well-defined
   - Ideal for parallel work

3. Claude delegates slime to Codex:
   → Task handoff with requirements

4. While Codex works on slime, Claude implements ghost

5. Codex completes → Claude reviews slime
   → Minor fix needed → Claude fixes

6. Claude delegates bat to Codex

7. Claude continues with other work or starts integration

8. Codex completes bat → Claude reviews → Pass

9. All three committed, status updated
```

### Best Practices

| Do | Don't |
|----|-------|
| Batch similar tasks for Codex | Delegate tasks that need context from chat |
| Provide explicit file paths | Assume Codex knows project structure |
| Include test commands in success criteria | Skip verification steps |
| Review before committing | Auto-commit Codex output |
| Keep Codex tasks focused (<30 min) | Delegate sprawling, undefined work |

### Error Handling

| Situation | Response |
|-----------|----------|
| Codex fails to complete | Claude implements directly |
| Codex output doesn't compile | Re-delegate with error context |
| Tests fail after integration | Claude debugs and fixes |
| Codex is unavailable | Continue single-agent mode |

---

## Quick Reference

### Delegation Decision Tree

```
                    ┌─────────────────┐
                    │  New task       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Well-defined?   │
                    └────────┬────────┘
                      yes    │    no
               ┌─────────────┴─────────────┐
               │                           │
      ┌────────▼────────┐                  │
      │ ≤2 files?       │           ┌──────▼──────┐
      └────────┬────────┘           │ Claude does │
        yes    │    no              └─────────────┘
      ┌────────┴─────────────┐
      │                      │
┌─────▼─────┐          ┌─────▼─────┐
│ Codex     │          │ Claude    │
│ idle?     │          │ does      │
└─────┬─────┘          └───────────┘
  yes │    no
┌─────▼─────┐    ┌───────────┐
│ Delegate  │    │ Queue for │
│ to Codex  │    │ Codex     │
└───────────┘    └───────────┘
```

### Command Cheat Sheet

```bash
# Run tests (always before committing)
python -m tests.runner

# Run specific category
python -m tests.runner --category generators

# Run with filter
python -m tests.runner --filter item
```

### Commit Templates

```bash
# Claude solo work
git commit -m "Add feature X

Co-Authored-By: Claude <noreply@anthropic.com>"

# Codex work (reviewed by Claude)
git commit -m "Add feature Y

Implemented by Codex, reviewed by Claude.

Co-Authored-By: OpenAI Codex <codex@openai.com>
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Session Startup Checklist

```
□ Run tests to verify clean state
□ Review ROADMAP.md for priorities
□ Check git status for uncommitted work
□ Identify parallelizable tasks
□ Initialize status tracker
```

---

*Last updated: January 2025*
