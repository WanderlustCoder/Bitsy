"""
Test CLI Commands - Tests for CLI command functions.
"""

import sys
import os
import argparse
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase


class TestCommands(TestCase):
    """Tests for CLI command functions."""

    def test_create_parser(self):
        """create_parser returns parser with expected subcommands."""
        from cli.commands import create_parser

        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

        subparsers = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        self.assertEqual(len(subparsers), 1)
        choices = subparsers[0].choices

        for command in ("generate", "export", "validate", "batch"):
            self.assertIn(command, choices)

    def test_generate_command_character(self):
        """generate_command runs character generator."""
        from cli.commands import generate_command

        args = argparse.Namespace(
            type="character",
            output="character.png",
            seed=123,
            style="retro",
        )

        with patch("generators.generate_character", return_value="canvas") as generator, \
                patch("export.png.save_png") as save_png:
            result = generate_command(args)

        self.assertEqual(result, 0)
        generator.assert_called_once_with(seed=123, style="retro")
        save_png.assert_called_once_with("canvas", "character.png")

    def test_generate_command_item(self):
        """generate_command runs item generator."""
        from cli.commands import generate_command

        args = argparse.Namespace(
            type="item",
            output="item.png",
            seed=None,
            style=None,
        )

        with patch("generators.generate_item", return_value="canvas") as generator, \
                patch("export.png.save_png") as save_png:
            result = generate_command(args)

        self.assertEqual(result, 0)
        generator.assert_called_once_with()
        save_png.assert_called_once_with("canvas", "item.png")

    def test_generate_command_unknown_type(self):
        """generate_command returns error for unknown type."""
        from cli.commands import generate_command

        args = argparse.Namespace(type="unknown", output="out.png")
        result = generate_command(args)

        self.assertEqual(result, 1)

    def test_export_command_atlas(self):
        """export_command creates atlas output."""
        from cli.commands import export_command

        args = argparse.Namespace(
            format="atlas",
            input=["a.png", "b.png"],
            output="atlas_output",
        )

        atlas = Mock()
        with patch("export.png.load_png", return_value="canvas") as load_png, \
                patch("export.create_atlas", return_value=atlas) as create_atlas:
            result = export_command(args)

        self.assertEqual(result, 0)
        self.assertEqual(load_png.call_count, 2)
        create_atlas.assert_called_once()
        sprites = create_atlas.call_args[0][0]
        self.assertEqual(sprites[0][0], "a")
        self.assertEqual(sprites[0][1], "canvas")
        atlas.save.assert_called_once_with("atlas_output")

    def test_export_command_gif(self):
        """export_command creates GIF output."""
        from cli.commands import export_command

        args = argparse.Namespace(
            format="gif",
            input=["frame1.png", "frame2.png"],
            output="anim.gif",
            fps=10,
        )

        with patch("export.png.load_png", return_value="frame") as load_png, \
                patch("export.save_gif") as save_gif:
            result = export_command(args)

        self.assertEqual(result, 0)
        self.assertEqual(load_png.call_count, 2)
        save_gif.assert_called_once()
        self.assertEqual(save_gif.call_args[0][0], "anim.gif")

    def test_export_command_apng(self):
        """export_command creates APNG output."""
        from cli.commands import export_command

        args = argparse.Namespace(
            format="apng",
            input=["frame1.png"],
            output="anim.png",
            fps=8,
        )

        with patch("export.png.load_png", return_value="frame") as load_png, \
                patch("export.save_apng") as save_apng:
            result = export_command(args)

        self.assertEqual(result, 0)
        self.assertEqual(load_png.call_count, 1)
        save_apng.assert_called_once_with("anim.png", ["frame"], fps=8)

    def test_validate_command_success(self):
        """validate_command returns success when all inputs are valid."""
        from cli.commands import validate_command

        args = argparse.Namespace(input=["valid.png"])
        report = Mock(is_valid=True, errors=[])

        with patch("export.png.load_png", return_value="canvas") as load_png, \
                patch("quality.validators.validate_style", return_value=report) as validate_style:
            result = validate_command(args)

        self.assertEqual(result, 0)
        load_png.assert_called_once_with("valid.png")
        validate_style.assert_called_once_with("canvas")

    def test_validate_command_failure(self):
        """validate_command returns failure when issues found."""
        from cli.commands import validate_command

        args = argparse.Namespace(input=["invalid.png"])
        error = Mock(message="Bad pixels")
        report = Mock(is_valid=False, errors=[error])

        with patch("export.png.load_png", return_value="canvas") as load_png, \
                patch("quality.validators.validate_style", return_value=report) as validate_style:
            result = validate_command(args)

        self.assertEqual(result, 1)
        load_png.assert_called_once_with("invalid.png")
        validate_style.assert_called_once_with("canvas")

    def test_batch_command_missing_tasks(self):
        """batch_command returns failure when tasks file is missing."""
        from cli.commands import batch_command

        args = argparse.Namespace(tasks="missing.json", output="./out", force=False)

        with patch("cli.commands.os.path.exists", return_value=False):
            result = batch_command(args)

        self.assertEqual(result, 1)

    def test_batch_command_success(self):
        """batch_command returns success when pipeline succeeds."""
        from cli.commands import batch_command

        args = argparse.Namespace(tasks="tasks.json", output="./out", force=True)
        pipeline_result = {"success": 1, "skipped": 0, "failed": 0}

        with patch("cli.commands.os.path.exists", return_value=True), \
                patch("cli.commands.run_pipeline", return_value=pipeline_result) as run_pipeline:
            result = batch_command(args)

        self.assertEqual(result, 0)
        run_pipeline.assert_called_once_with("tasks.json", "./out", True)
