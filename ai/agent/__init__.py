"""
AI Agent - High-level orchestration for sprite generation.

Provides planning, evaluation, memory, and refinement capabilities
for intelligent sprite generation workflows.
"""

from .memory import (
    AgentMemory,
    GenerationRecord,
    StylePreferences,
    get_memory,
    reset_memory,
)

from .evaluator import (
    QualityEvaluator,
    EvaluationCriteria,
    evaluate_canvas,
    evaluate_for_style,
)

from .planner import (
    Planner,
    ExecutionPlan,
    PlanStep,
    StepStatus,
    create_plan,
)

from .refiner import (
    Refiner,
    RefinementType,
    RefinementSuggestion,
    RefinementResult,
    analyze_for_refinement,
    auto_refine,
)

__all__ = [
    # Memory
    'AgentMemory',
    'GenerationRecord',
    'StylePreferences',
    'get_memory',
    'reset_memory',

    # Evaluator
    'QualityEvaluator',
    'EvaluationCriteria',
    'evaluate_canvas',
    'evaluate_for_style',

    # Planner
    'Planner',
    'ExecutionPlan',
    'PlanStep',
    'StepStatus',
    'create_plan',

    # Refiner
    'Refiner',
    'RefinementType',
    'RefinementSuggestion',
    'RefinementResult',
    'analyze_for_refinement',
    'auto_refine',
]
