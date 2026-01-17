"""
CLI Commands - High-level command functions.

Provides command implementations for the CLI tool.
"""

from typing import List, Dict, Optional, Any
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_command(args: argparse.Namespace) -> int:
    """Generate assets based on arguments.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 = success)
    """
    from generators import (
        generate_character,
        generate_creature,
        generate_item,
        generate_prop,
    )
    from export.png import save_png

    generators = {
        "character": generate_character,
        "creature": generate_creature,
        "item": generate_item,
        "prop": generate_prop,
    }

    gen_type = getattr(args, 'type', 'character')
    generator = generators.get(gen_type)

    if not generator:
        print(f"Unknown generator type: {gen_type}")
        return 1

    # Build config from args
    config = {}
    if hasattr(args, 'seed') and args.seed:
        config['seed'] = args.seed
    if hasattr(args, 'style') and args.style:
        config['style'] = args.style

    try:
        canvas = generator(**config)
        output = getattr(args, 'output', f'{gen_type}.png')
        save_png(canvas, output)
        print(f"Generated: {output}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def export_command(args: argparse.Namespace) -> int:
    """Export assets based on arguments.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 = success)
    """
    from export import (
        save_gif,
        save_apng,
        create_atlas,
    )

    export_type = getattr(args, 'format', 'png')
    input_files = getattr(args, 'input', [])
    output = getattr(args, 'output', 'output')

    try:
        if export_type == 'atlas':
            # Load sprites from input files
            from core import Canvas
            from export.png import load_png

            sprites = []
            for path in input_files:
                name = os.path.splitext(os.path.basename(path))[0]
                canvas = load_png(path)
                sprites.append((name, canvas))

            atlas = create_atlas(sprites)
            atlas.save(output)
            print(f"Created atlas: {output}")

        elif export_type == 'gif':
            # Load frames
            from export.png import load_png
            frames = [load_png(path) for path in input_files]
            fps = getattr(args, 'fps', 12)
            delays = [int(1000 / fps)] * len(frames)
            save_gif(output, frames, delays)
            print(f"Created GIF: {output}")

        elif export_type == 'apng':
            from export.png import load_png
            frames = [load_png(path) for path in input_files]
            fps = getattr(args, 'fps', 12)
            save_apng(output, frames, fps=fps)
            print(f"Created APNG: {output}")

        else:
            print(f"Unknown export format: {export_type}")
            return 1

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def validate_command(args: argparse.Namespace) -> int:
    """Validate assets based on arguments.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 = all valid, 1 = issues found)
    """
    from quality.validators import validate_style
    from export.png import load_png

    input_files = getattr(args, 'input', [])
    issues = []

    for path in input_files:
        try:
            canvas = load_png(path)
            report = validate_style(canvas)

            if not report.is_valid:
                issues.append({
                    "file": path,
                    "errors": [e.message for e in report.errors]
                })
                print(f"FAIL: {path}")
                for error in report.errors:
                    print(f"  - {error.message}")
            else:
                print(f"OK: {path}")

        except Exception as e:
            issues.append({"file": path, "error": str(e)})
            print(f"ERROR: {path} - {e}")

    if issues:
        return 1
    return 0


def batch_command(args: argparse.Namespace) -> int:
    """Run batch processing based on arguments.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 = success)
    """
    from .pipeline import run_pipeline

    tasks_file = getattr(args, 'tasks', 'tasks.json')
    output_dir = getattr(args, 'output', './output')
    force = getattr(args, 'force', False)

    if not os.path.exists(tasks_file):
        print(f"Tasks file not found: {tasks_file}")
        return 1

    results = run_pipeline(tasks_file, output_dir, force)

    if results['failed'] > 0:
        return 1
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='bitsy',
        description='Bitsy - Pixel art generation toolkit'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate assets')
    gen_parser.add_argument('type', choices=['character', 'creature', 'item', 'prop'])
    gen_parser.add_argument('-o', '--output', default='output.png', help='Output file')
    gen_parser.add_argument('-s', '--seed', type=int, help='Random seed')
    gen_parser.add_argument('--style', help='Style preset')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export assets')
    export_parser.add_argument('format', choices=['atlas', 'gif', 'apng'])
    export_parser.add_argument('input', nargs='+', help='Input files')
    export_parser.add_argument('-o', '--output', default='output', help='Output path')
    export_parser.add_argument('--fps', type=int, default=12, help='Frames per second')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate assets')
    val_parser.add_argument('input', nargs='+', help='Input files')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch processing')
    batch_parser.add_argument('tasks', help='Tasks JSON file')
    batch_parser.add_argument('-o', '--output', default='./output', help='Output directory')
    batch_parser.add_argument('-f', '--force', action='store_true', help='Force rebuild')

    return parser


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        'generate': generate_command,
        'export': export_command,
        'validate': validate_command,
        'batch': batch_command,
    }

    command_func = commands.get(args.command)
    if command_func:
        return command_func(args)

    return 1


if __name__ == '__main__':
    sys.exit(main())
