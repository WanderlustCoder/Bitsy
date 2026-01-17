"""
Asset Pipeline - Batch processing and automation.

Provides:
- Watch mode for auto-regeneration
- Asset manifest generation
- Dependency tracking
- Incremental builds
"""

from typing import List, Dict, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import time
import hashlib
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TaskType(Enum):
    """Types of pipeline tasks."""
    GENERATE_CHARACTER = "generate_character"
    GENERATE_CREATURE = "generate_creature"
    GENERATE_ITEM = "generate_item"
    GENERATE_TILESET = "generate_tileset"
    GENERATE_SCENE = "generate_scene"
    EXPORT_ATLAS = "export_atlas"
    EXPORT_ANIMATION = "export_animation"
    VALIDATE = "validate"


@dataclass
class AssetTask:
    """A single pipeline task."""
    name: str
    task_type: TaskType
    config: Dict[str, Any]
    output_path: str
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class PipelineConfig:
    """Configuration for the asset pipeline."""
    input_dir: str = "."
    output_dir: str = "./output"
    manifest_path: str = "./manifest.json"
    incremental: bool = True
    parallel: bool = False
    verbose: bool = True


@dataclass
class AssetManifest:
    """Manifest tracking generated assets."""
    version: str = "1.0"
    assets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_build: float = 0.0


class AssetPipeline:
    """Asset generation and export pipeline."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.tasks: List[AssetTask] = []
        self.manifest = AssetManifest()
        self._task_handlers: Dict[TaskType, Callable] = {}
        self._file_hashes: Dict[str, str] = {}

        # Register default handlers
        self._register_default_handlers()

        # Load existing manifest
        self._load_manifest()

    def add_task(self, task: AssetTask) -> None:
        """Add a task to the pipeline."""
        self.tasks.append(task)

    def add_tasks_from_file(self, path: str) -> int:
        """Load tasks from a JSON file.

        Args:
            path: Path to tasks JSON file

        Returns:
            Number of tasks added
        """
        with open(path) as f:
            data = json.load(f)

        count = 0
        for task_data in data.get("tasks", []):
            task = AssetTask(
                name=task_data["name"],
                task_type=TaskType(task_data["type"]),
                config=task_data.get("config", {}),
                output_path=task_data.get("output", f"{task_data['name']}.png"),
                dependencies=task_data.get("dependencies", []),
                enabled=task_data.get("enabled", True)
            )
            self.add_task(task)
            count += 1

        return count

    def run(self, force: bool = False) -> Dict[str, Any]:
        """Run the pipeline.

        Args:
            force: Force rebuild all assets

        Returns:
            Build results
        """
        results = {
            "success": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }

        # Ensure output directory exists
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        # Sort tasks by dependencies
        sorted_tasks = self._sort_by_dependencies()

        for task in sorted_tasks:
            if not task.enabled:
                results["skipped"] += 1
                continue

            # Check if rebuild is needed
            if not force and self.config.incremental:
                if not self._needs_rebuild(task):
                    if self.config.verbose:
                        print(f"  Skip: {task.name} (up to date)")
                    results["skipped"] += 1
                    continue

            # Run the task
            try:
                if self.config.verbose:
                    print(f"  Build: {task.name}")

                output_path = os.path.join(self.config.output_dir, task.output_path)
                self._run_task(task, output_path)

                # Update manifest
                self._update_manifest(task, output_path)
                results["success"] += 1

            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"task": task.name, "error": str(e)})
                if self.config.verbose:
                    print(f"  Error: {task.name} - {e}")

        # Save manifest
        self._save_manifest()
        self.manifest.last_build = time.time()

        return results

    def clean(self) -> int:
        """Clean all generated assets.

        Returns:
            Number of files removed
        """
        removed = 0
        for asset_name, asset_data in self.manifest.assets.items():
            path = asset_data.get("path")
            if path and os.path.exists(path):
                os.remove(path)
                removed += 1

        self.manifest.assets = {}
        self._save_manifest()
        return removed

    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status.

        Returns:
            Status information
        """
        return {
            "tasks": len(self.tasks),
            "assets": len(self.manifest.assets),
            "last_build": self.manifest.last_build,
            "config": {
                "input_dir": self.config.input_dir,
                "output_dir": self.config.output_dir,
                "incremental": self.config.incremental
            }
        }

    def register_handler(self, task_type: TaskType, handler: Callable) -> None:
        """Register a custom task handler.

        Args:
            task_type: Type of task to handle
            handler: Handler function(task, output_path) -> None
        """
        self._task_handlers[task_type] = handler

    def _register_default_handlers(self) -> None:
        """Register default task handlers."""
        self._task_handlers[TaskType.GENERATE_CHARACTER] = self._handle_generate_character
        self._task_handlers[TaskType.GENERATE_CREATURE] = self._handle_generate_creature
        self._task_handlers[TaskType.GENERATE_ITEM] = self._handle_generate_item
        self._task_handlers[TaskType.GENERATE_TILESET] = self._handle_generate_tileset
        self._task_handlers[TaskType.GENERATE_SCENE] = self._handle_generate_scene
        self._task_handlers[TaskType.EXPORT_ATLAS] = self._handle_export_atlas
        self._task_handlers[TaskType.EXPORT_ANIMATION] = self._handle_export_animation
        self._task_handlers[TaskType.VALIDATE] = self._handle_validate

    def _run_task(self, task: AssetTask, output_path: str) -> None:
        """Run a single task."""
        handler = self._task_handlers.get(task.task_type)
        if handler:
            handler(task, output_path)
        else:
            raise ValueError(f"No handler for task type: {task.task_type}")

    def _handle_generate_character(self, task: AssetTask, output_path: str) -> None:
        """Handle character generation task."""
        from generators import generate_character
        from export.png import save_png

        canvas = generate_character(**task.config)
        save_png(canvas, output_path)

    def _handle_generate_creature(self, task: AssetTask, output_path: str) -> None:
        """Handle creature generation task."""
        from generators import generate_creature
        from export.png import save_png

        canvas = generate_creature(**task.config)
        save_png(canvas, output_path)

    def _handle_generate_item(self, task: AssetTask, output_path: str) -> None:
        """Handle item generation task."""
        from generators import generate_item
        from export.png import save_png

        canvas = generate_item(**task.config)
        save_png(canvas, output_path)

    def _handle_generate_tileset(self, task: AssetTask, output_path: str) -> None:
        """Handle tileset generation task."""
        from generators import generate_terrain_tileset
        from export.png import save_png
        from export.spritesheet import create_grid_sheet

        tiles = generate_terrain_tileset(**task.config)
        sheet = create_grid_sheet(tiles)
        save_png(sheet, output_path)

    def _handle_generate_scene(self, task: AssetTask, output_path: str) -> None:
        """Handle scene generation task."""
        from generators import create_scene, generate_parallax_background
        from export.png import save_png

        scene = create_scene(**task.config)

        # Add parallax background if requested
        if task.config.get("parallax"):
            layers = generate_parallax_background(
                scene.width, scene.height,
                **task.config.get("parallax_config", {})
            )
            for layer in layers:
                scene.add_layer(layer)

        canvas = scene.render()
        save_png(canvas, output_path)

    def _handle_export_atlas(self, task: AssetTask, output_path: str) -> None:
        """Handle atlas export task."""
        from export.atlas import create_atlas

        sprites = task.config.get("sprites", [])
        atlas = create_atlas(sprites, **task.config.get("atlas_config", {}))
        atlas.save(output_path.replace('.png', ''))

    def _handle_export_animation(self, task: AssetTask, output_path: str) -> None:
        """Handle animation export task."""
        from export.animation_formats import export_bitsy_animation, AnimationExport

        anim = AnimationExport(
            name=task.name,
            frames=task.config.get("frames", []),
            fps=task.config.get("fps", 12),
            loop=task.config.get("loop", True)
        )
        export_bitsy_animation(anim, output_path.replace('.json', ''))

    def _handle_validate(self, task: AssetTask, output_path: str) -> None:
        """Handle validation task."""
        # Validation doesn't produce output files
        pass

    def _sort_by_dependencies(self) -> List[AssetTask]:
        """Sort tasks by dependencies (topological sort)."""
        # Build dependency graph
        task_map = {t.name: t for t in self.tasks}
        in_degree = {t.name: 0 for t in self.tasks}
        deps = {t.name: [] for t in self.tasks}

        for task in self.tasks:
            for dep in task.dependencies:
                if dep in task_map:
                    deps[dep].append(task.name)
                    in_degree[task.name] += 1

        # Kahn's algorithm
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            name = queue.pop(0)
            result.append(task_map[name])

            for dependent in deps[name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result

    def _needs_rebuild(self, task: AssetTask) -> bool:
        """Check if task needs to be rebuilt."""
        asset = self.manifest.assets.get(task.name)
        if not asset:
            return True

        # Check if output exists
        output_path = os.path.join(self.config.output_dir, task.output_path)
        if not os.path.exists(output_path):
            return True

        # Check if config changed
        config_hash = self._hash_config(task.config)
        if asset.get("config_hash") != config_hash:
            return True

        # Check dependencies
        for dep in task.dependencies:
            dep_asset = self.manifest.assets.get(dep)
            if dep_asset and dep_asset.get("modified", 0) > asset.get("built", 0):
                return True

        return False

    def _hash_config(self, config: Dict[str, Any]) -> str:
        """Hash configuration for change detection."""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    def _update_manifest(self, task: AssetTask, output_path: str) -> None:
        """Update manifest after task completion."""
        self.manifest.assets[task.name] = {
            "path": output_path,
            "type": task.task_type.value,
            "config_hash": self._hash_config(task.config),
            "built": time.time(),
            "modified": time.time()
        }

    def _load_manifest(self) -> None:
        """Load manifest from disk."""
        if os.path.exists(self.config.manifest_path):
            try:
                with open(self.config.manifest_path) as f:
                    data = json.load(f)
                self.manifest.assets = data.get("assets", {})
                self.manifest.last_build = data.get("last_build", 0)
            except Exception:
                pass

    def _save_manifest(self) -> None:
        """Save manifest to disk."""
        data = {
            "version": self.manifest.version,
            "assets": self.manifest.assets,
            "last_build": self.manifest.last_build
        }
        with open(self.config.manifest_path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# Watch Mode
# =============================================================================

def watch_directory(
    directory: str,
    pipeline: AssetPipeline,
    patterns: Optional[List[str]] = None,
    interval: float = 1.0
) -> None:
    """Watch directory for changes and trigger rebuilds.

    Args:
        directory: Directory to watch
        pipeline: Pipeline to run on changes
        patterns: File patterns to watch (e.g., ["*.json", "*.yaml"])
        interval: Check interval in seconds
    """
    patterns = patterns or ["*.json"]
    last_check = time.time()
    file_times: Dict[str, float] = {}

    print(f"Watching {directory} for changes...")

    while True:
        try:
            time.sleep(interval)
            changed = False

            # Check for file changes
            for pattern in patterns:
                for path in Path(directory).glob(pattern):
                    mtime = path.stat().st_mtime
                    if str(path) not in file_times:
                        file_times[str(path)] = mtime
                    elif file_times[str(path)] < mtime:
                        file_times[str(path)] = mtime
                        changed = True
                        print(f"  Changed: {path}")

            if changed:
                print("Rebuilding...")
                results = pipeline.run()
                print(f"  Done: {results['success']} built, {results['skipped']} skipped")

        except KeyboardInterrupt:
            print("\nWatch mode stopped.")
            break


# =============================================================================
# Convenience Functions
# =============================================================================

def run_pipeline(
    tasks_file: str,
    output_dir: str = "./output",
    force: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run pipeline from tasks file.

    Args:
        tasks_file: Path to tasks JSON file
        output_dir: Output directory
        force: Force rebuild all
        verbose: Print progress

    Returns:
        Build results
    """
    config = PipelineConfig(
        output_dir=output_dir,
        verbose=verbose
    )
    pipeline = AssetPipeline(config)
    pipeline.add_tasks_from_file(tasks_file)

    if verbose:
        print(f"Running pipeline with {len(pipeline.tasks)} tasks...")

    results = pipeline.run(force=force)

    if verbose:
        print(f"\nResults: {results['success']} success, "
              f"{results['skipped']} skipped, {results['failed']} failed")

    return results
