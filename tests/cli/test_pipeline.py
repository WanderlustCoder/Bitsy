"""
Test CLI Pipeline - Tests for asset pipeline utilities.
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase


class TestPipeline(TestCase):
    """Tests for pipeline classes and helpers."""

    def test_task_type_values(self):
        """TaskType enum values are stable."""
        from cli.pipeline import TaskType

        expected = {
            "GENERATE_CHARACTER": "generate_character",
            "GENERATE_CREATURE": "generate_creature",
            "GENERATE_ITEM": "generate_item",
            "GENERATE_TILESET": "generate_tileset",
            "GENERATE_SCENE": "generate_scene",
            "EXPORT_ATLAS": "export_atlas",
            "EXPORT_ANIMATION": "export_animation",
            "VALIDATE": "validate",
        }

        for name, value in expected.items():
            self.assertEqual(getattr(TaskType, name).value, value)

    def test_pipeline_config_defaults(self):
        """PipelineConfig defaults are correct."""
        from cli.pipeline import PipelineConfig

        config = PipelineConfig()
        self.assertEqual(config.input_dir, ".")
        self.assertEqual(config.output_dir, "./output")
        self.assertEqual(config.manifest_path, "./manifest.json")
        self.assertTrue(config.incremental)
        self.assertFalse(config.parallel)
        self.assertTrue(config.verbose)

    def test_asset_task_dataclass(self):
        """AssetTask holds task data."""
        from cli.pipeline import AssetTask, TaskType

        task = AssetTask(
            name="hero",
            task_type=TaskType.GENERATE_CHARACTER,
            config={"seed": 5},
            output_path="hero.png",
        )

        self.assertEqual(task.name, "hero")
        self.assertEqual(task.task_type, TaskType.GENERATE_CHARACTER)
        self.assertEqual(task.config, {"seed": 5})
        self.assertEqual(task.output_path, "hero.png")
        self.assertEqual(task.dependencies, [])
        self.assertTrue(task.enabled)

    def test_asset_pipeline_initialization(self):
        """AssetPipeline initializes with defaults."""
        from cli.pipeline import AssetPipeline, PipelineConfig, TaskType

        with patch("cli.pipeline.os.path.exists", return_value=False):
            pipeline = AssetPipeline()

        self.assertIsInstance(pipeline.config, PipelineConfig)
        self.assertEqual(pipeline.tasks, [])
        self.assertEqual(pipeline.manifest.assets, {})
        self.assertIn(TaskType.GENERATE_CHARACTER, pipeline._task_handlers)

    def test_run_pipeline(self):
        """run_pipeline wires tasks and executes the pipeline."""
        from cli.pipeline import run_pipeline, AssetPipeline, AssetTask, TaskType

        def add_tasks(self, path):
            self.tasks.append(
                AssetTask(
                    name="hero",
                    task_type=TaskType.GENERATE_CHARACTER,
                    config={},
                    output_path="hero.png",
                )
            )
            return 1

        results = {"success": 1, "skipped": 0, "failed": 0, "errors": []}

        with patch.object(AssetPipeline, "add_tasks_from_file", autospec=True, side_effect=add_tasks) as add_tasks_from_file, \
                patch.object(AssetPipeline, "run", autospec=True, return_value=results) as run:
            output = run_pipeline("tasks.json", output_dir="./out", force=True, verbose=False)

        self.assertEqual(output, results)
        self.assertEqual(add_tasks_from_file.call_args[0][1], "tasks.json")
        self.assertEqual(run.call_args[1]["force"], True)
