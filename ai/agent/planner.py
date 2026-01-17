"""
Multi-step planning for complex sprite generation.

Decomposes complex requests into sequences of tool calls
and manages execution flow.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.parser import parse_prompt, ParsedPrompt, ToolCall
from ai.tools.results import GenerationResult, ToolResult


class StepStatus(Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_id: int
    description: str
    tool_call: ToolCall
    status: StepStatus = StepStatus.PENDING
    result: Optional[ToolResult] = None
    depends_on: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """A multi-step execution plan."""
    plan_id: str
    description: str
    steps: List[PlanStep]
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


class Planner:
    """Plans multi-step sprite generation tasks."""

    def __init__(self):
        """Initialize the planner."""
        self._plan_counter = 0
        self._patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Callable]:
        """Load planning patterns."""
        return {
            "character_set": self._plan_character_set,
            "animated_character": self._plan_animated_character,
            "scene_with_props": self._plan_scene_with_props,
            "variations": self._plan_variations,
            "style_transfer": self._plan_style_transfer,
        }

    def create_plan(self, prompt: str) -> ExecutionPlan:
        """Create an execution plan from a prompt.

        Args:
            prompt: User's request

        Returns:
            ExecutionPlan with steps
        """
        self._plan_counter += 1
        plan_id = f"plan_{self._plan_counter}"

        # Detect plan type
        plan_type = self._detect_plan_type(prompt)

        if plan_type and plan_type in self._patterns:
            return self._patterns[plan_type](prompt, plan_id)

        # Simple single-step plan
        parsed = parse_prompt(prompt)
        if parsed.tool_call:
            return ExecutionPlan(
                plan_id=plan_id,
                description=f"Single generation: {prompt}",
                steps=[
                    PlanStep(
                        step_id=0,
                        description=f"Generate {parsed.tool_call.tool_name}",
                        tool_call=parsed.tool_call,
                    )
                ],
            )

        # Fallback empty plan
        return ExecutionPlan(
            plan_id=plan_id,
            description="Could not create plan",
            steps=[],
        )

    def _detect_plan_type(self, prompt: str) -> Optional[str]:
        """Detect what type of plan is needed."""
        prompt_lower = prompt.lower()

        # Character set patterns
        if any(word in prompt_lower for word in ['set of', 'team', 'party', 'group']):
            return "character_set"

        # Animation patterns
        if any(word in prompt_lower for word in ['animated', 'walking', 'animation', 'idle', 'attack']):
            return "animated_character"

        # Scene patterns
        if any(word in prompt_lower for word in ['scene with', 'environment with', 'room with']):
            return "scene_with_props"

        # Variation patterns
        if any(word in prompt_lower for word in ['variations', 'alternatives', 'options']):
            return "variations"

        # Style transfer
        if 'in the style of' in prompt_lower or 'like the' in prompt_lower:
            return "style_transfer"

        return None

    def _plan_character_set(self, prompt: str, plan_id: str) -> ExecutionPlan:
        """Plan a character set generation."""
        import re

        # Try to extract count
        count_match = re.search(r'(\d+)\s*(?:characters?|heroes?|members?)', prompt.lower())
        count = int(count_match.group(1)) if count_match else 4

        # Parse base character description
        parsed = parse_prompt(prompt)
        base_params = parsed.tool_call.parameters if parsed.tool_call else {}

        steps = []
        presets = ['warrior', 'mage', 'rogue', 'knight', 'hero']

        for i in range(count):
            preset = presets[i % len(presets)]
            params = {**base_params, 'preset': preset}

            steps.append(PlanStep(
                step_id=i,
                description=f"Generate {preset}",
                tool_call=ToolCall(
                    tool_name="generate_character",
                    parameters=params,
                    confidence=0.8,
                    source="planner",
                ),
            ))

        return ExecutionPlan(
            plan_id=plan_id,
            description=f"Generate {count} character set",
            steps=steps,
            context={"set_type": "characters", "count": count},
        )

    def _plan_animated_character(self, prompt: str, plan_id: str) -> ExecutionPlan:
        """Plan an animated character generation."""
        # First generate the character, then animate
        parsed = parse_prompt(prompt)
        base_params = parsed.tool_call.parameters if parsed.tool_call else {}

        # Determine animation type
        anim_type = 'idle'
        prompt_lower = prompt.lower()
        if 'walk' in prompt_lower:
            anim_type = 'walk'
        elif 'attack' in prompt_lower:
            anim_type = 'attack'
        elif 'run' in prompt_lower:
            anim_type = 'run'

        steps = [
            PlanStep(
                step_id=0,
                description="Generate base character",
                tool_call=ToolCall(
                    tool_name="generate_character",
                    parameters=base_params,
                    confidence=0.8,
                    source="planner",
                ),
            ),
            PlanStep(
                step_id=1,
                description=f"Create {anim_type} animation",
                tool_call=ToolCall(
                    tool_name="create_animation",
                    parameters={"animation_type": anim_type},
                    confidence=0.8,
                    source="planner",
                ),
                depends_on=[0],
                metadata={"uses_previous_result": True},
            ),
        ]

        return ExecutionPlan(
            plan_id=plan_id,
            description=f"Create animated {anim_type} character",
            steps=steps,
            context={"animation_type": anim_type},
        )

    def _plan_scene_with_props(self, prompt: str, plan_id: str) -> ExecutionPlan:
        """Plan a scene with props."""
        import re

        # Parse scene description
        parsed = parse_prompt(prompt)
        scene_params = parsed.tool_call.parameters if parsed.tool_call else {}

        # Extract props from prompt
        prop_patterns = [
            r'with\s+(?:a\s+)?(\w+)',
            r'containing\s+(?:a\s+)?(\w+)',
            r'including\s+(?:a\s+)?(\w+)',
        ]

        props = []
        for pattern in prop_patterns:
            matches = re.findall(pattern, prompt.lower())
            props.extend(matches)

        steps = [
            PlanStep(
                step_id=0,
                description="Generate base scene",
                tool_call=ToolCall(
                    tool_name="generate_scene",
                    parameters=scene_params,
                    confidence=0.8,
                    source="planner",
                ),
            ),
        ]

        for i, prop in enumerate(props[:5]):  # Limit to 5 props
            steps.append(PlanStep(
                step_id=i + 1,
                description=f"Generate {prop}",
                tool_call=ToolCall(
                    tool_name="generate_prop",
                    parameters={"prop_type": prop},
                    confidence=0.7,
                    source="planner",
                ),
            ))

        return ExecutionPlan(
            plan_id=plan_id,
            description="Generate scene with props",
            steps=steps,
            context={"props": props},
        )

    def _plan_variations(self, prompt: str, plan_id: str) -> ExecutionPlan:
        """Plan variation generation."""
        import re

        # Extract count
        count_match = re.search(r'(\d+)\s*variation', prompt.lower())
        count = int(count_match.group(1)) if count_match else 3

        # Parse base
        parsed = parse_prompt(prompt)
        base_params = parsed.tool_call.parameters if parsed.tool_call else {}
        tool_name = parsed.tool_call.tool_name if parsed.tool_call else "generate_sprite"

        steps = []
        for i in range(count):
            params = {**base_params, 'seed': i * 1000}  # Different seeds for variation

            steps.append(PlanStep(
                step_id=i,
                description=f"Generate variation {i + 1}",
                tool_call=ToolCall(
                    tool_name=tool_name,
                    parameters=params,
                    confidence=0.8,
                    source="planner",
                ),
            ))

        return ExecutionPlan(
            plan_id=plan_id,
            description=f"Generate {count} variations",
            steps=steps,
            context={"variation_count": count},
        )

    def _plan_style_transfer(self, prompt: str, plan_id: str) -> ExecutionPlan:
        """Plan style transfer generation."""
        parsed = parse_prompt(prompt)
        base_params = parsed.tool_call.parameters if parsed.tool_call else {}
        tool_name = parsed.tool_call.tool_name if parsed.tool_call else "generate_sprite"

        steps = [
            PlanStep(
                step_id=0,
                description="Generate base sprite",
                tool_call=ToolCall(
                    tool_name=tool_name,
                    parameters=base_params,
                    confidence=0.8,
                    source="planner",
                ),
            ),
            PlanStep(
                step_id=1,
                description="Evaluate quality",
                tool_call=ToolCall(
                    tool_name="_internal_evaluate",
                    parameters={},
                    confidence=1.0,
                    source="planner",
                ),
                depends_on=[0],
                metadata={"internal": True, "uses_previous_result": True},
            ),
            PlanStep(
                step_id=2,
                description="Apply style refinements",
                tool_call=ToolCall(
                    tool_name="_agent_refine",
                    parameters={"style_match": True},
                    confidence=0.8,
                    source="planner",
                ),
                depends_on=[1],
                metadata={"uses_previous_result": True},
            ),
        ]

        return ExecutionPlan(
            plan_id=plan_id,
            description="Generate with style transfer",
            steps=steps,
        )

    def get_next_step(self, plan: ExecutionPlan) -> Optional[PlanStep]:
        """Get the next step to execute.

        Args:
            plan: The execution plan

        Returns:
            Next step or None if done
        """
        for step in plan.steps:
            if step.status == StepStatus.PENDING:
                # Check dependencies
                deps_met = all(
                    plan.steps[dep_id].status == StepStatus.COMPLETED
                    for dep_id in step.depends_on
                )
                if deps_met:
                    return step
        return None

    def mark_step_complete(
        self,
        plan: ExecutionPlan,
        step: PlanStep,
        result: ToolResult,
    ):
        """Mark a step as complete.

        Args:
            plan: The execution plan
            step: Step to mark complete
            result: The result
        """
        step.result = result
        step.status = StepStatus.COMPLETED if result.success else StepStatus.FAILED

    def is_plan_complete(self, plan: ExecutionPlan) -> bool:
        """Check if a plan is complete."""
        return all(
            step.status in (StepStatus.COMPLETED, StepStatus.SKIPPED, StepStatus.FAILED)
            for step in plan.steps
        )

    def get_plan_results(self, plan: ExecutionPlan) -> List[ToolResult]:
        """Get all successful results from a plan."""
        return [
            step.result
            for step in plan.steps
            if step.result and step.result.success
        ]


def create_plan(prompt: str) -> ExecutionPlan:
    """Convenience function to create a plan.

    Args:
        prompt: User's request

    Returns:
        ExecutionPlan
    """
    planner = Planner()
    return planner.create_plan(prompt)
