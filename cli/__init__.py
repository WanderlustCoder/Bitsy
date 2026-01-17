"""
Bitsy CLI - Command-line interface for asset generation.

Provides batch processing, watch mode, and asset pipeline tools.
"""

from .pipeline import (
    AssetPipeline,
    PipelineConfig,
    AssetTask,
    TaskType,
    run_pipeline,
    watch_directory,
)

from .commands import (
    generate_command,
    export_command,
    validate_command,
    batch_command,
)

__all__ = [
    # Pipeline
    'AssetPipeline',
    'PipelineConfig',
    'AssetTask',
    'TaskType',
    'run_pipeline',
    'watch_directory',
    # Commands
    'generate_command',
    'export_command',
    'validate_command',
    'batch_command',
]
