"""
Test CLI and Info modules - Developer experience tools.

Tests:
- CLI command parsing
- Info module functions
- Gallery generation
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.framework import TestCase


class TestInfoModule(TestCase):
    """Tests for the info module."""

    def test_import_info(self):
        """Info module can be imported."""
        import info
        self.assertTrue(hasattr(info, 'show'))
        self.assertTrue(hasattr(info, 'items'))
        self.assertTrue(hasattr(info, 'creatures'))

    def test_items_returns_list(self):
        """info.items() returns a list."""
        import info
        # Capture stdout
        result = info.items()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('sword', result)

    def test_creatures_returns_list(self):
        """info.creatures() returns a list."""
        import info
        result = info.creatures()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('slime', result)

    def test_textures_returns_list(self):
        """info.textures() returns a list."""
        import info
        result = info.textures()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('brick', result)

    def test_vehicles_returns_list(self):
        """info.vehicles() returns a list."""
        import info
        result = info.vehicles()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('car', result)

    def test_props_returns_list(self):
        """info.props() returns a list."""
        import info
        result = info.props()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_all_types_returns_dict(self):
        """info.all_types() returns comprehensive dict."""
        import info
        result = info.all_types()
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        self.assertIn('creatures', result)
        self.assertIn('textures', result)
        self.assertIn('vehicles', result)

    def test_search_finds_matches(self):
        """info.search() finds matching types."""
        import info
        result = info.search('sword')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Should find sword-related items
        found_sword = any('sword' in r.lower() for r in result)
        self.assertTrue(found_sword)

    def test_search_no_matches(self):
        """info.search() returns empty for no matches."""
        import info
        result = info.search('xyznonexistent')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestCLIModule(TestCase):
    """Tests for the CLI module."""

    def test_import_cli(self):
        """CLI module can be imported."""
        import cli
        self.assertTrue(hasattr(cli, 'main'))
        self.assertTrue(hasattr(cli, 'cmd_generate'))
        self.assertTrue(hasattr(cli, 'cmd_list'))
        self.assertTrue(hasattr(cli, 'cmd_info'))

    def test_cmd_list_all(self):
        """cmd_list handles 'all' category."""
        import cli
        from argparse import Namespace
        args = Namespace(category='all')
        result = cli.cmd_list(args)
        self.assertEqual(result, 0)

    def test_cmd_list_items(self):
        """cmd_list handles 'items' category."""
        import cli
        from argparse import Namespace
        args = Namespace(category='items')
        result = cli.cmd_list(args)
        self.assertEqual(result, 0)

    def test_cmd_info_general(self):
        """cmd_info shows general info."""
        import cli
        from argparse import Namespace
        args = Namespace(generator=None)
        result = cli.cmd_info(args)
        self.assertEqual(result, 0)

    def test_cmd_info_specific(self):
        """cmd_info shows specific generator info."""
        import cli
        from argparse import Namespace
        args = Namespace(generator='item')
        result = cli.cmd_info(args)
        self.assertEqual(result, 0)

    def test_cmd_generate_item(self):
        """cmd_generate creates item sprite."""
        import cli
        import tempfile
        from argparse import Namespace

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                type='item',
                variant='sword',
                size='16x16',
                output=output_path,
                seed=42,
                palette=None
            )
            result = cli.cmd_generate(args)
            self.assertEqual(result, 0)
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_cmd_generate_texture(self):
        """cmd_generate creates texture sprite."""
        import cli
        import tempfile
        from argparse import Namespace

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                type='texture',
                variant='brick',
                size='32x32',
                output=output_path,
                seed=42,
                palette=None
            )
            result = cli.cmd_generate(args)
            self.assertEqual(result, 0)
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_cmd_generate_vehicle(self):
        """cmd_generate creates vehicle sprite."""
        import cli
        import tempfile
        from argparse import Namespace

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                type='vehicle',
                variant='car_sedan',
                size='32x24',
                output=output_path,
                seed=42,
                palette=None
            )
            result = cli.cmd_generate(args)
            self.assertEqual(result, 0)
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_cmd_generate_missing_variant(self):
        """cmd_generate returns error for missing variant."""
        import cli
        from argparse import Namespace

        args = Namespace(
            type='item',
            variant=None,
            size='16x16',
            output=None,
            seed=42,
            palette=None
        )
        result = cli.cmd_generate(args)
        self.assertEqual(result, 1)

    def test_cmd_generate_invalid_type(self):
        """cmd_generate returns error for invalid type."""
        import cli
        from argparse import Namespace

        args = Namespace(
            type='invalid_generator',
            variant=None,
            size='16x16',
            output=None,
            seed=42,
            palette=None
        )
        result = cli.cmd_generate(args)
        self.assertEqual(result, 1)


class TestGalleryCommand(TestCase):
    """Tests for gallery generation."""

    def test_cmd_gallery(self):
        """cmd_gallery generates sprites."""
        import cli
        import tempfile
        import shutil
        from argparse import Namespace

        output_dir = tempfile.mkdtemp()

        try:
            args = Namespace(output=output_dir)
            result = cli.cmd_gallery(args)
            self.assertEqual(result, 0)

            # Check some files were created
            files = os.listdir(output_dir)
            self.assertGreater(len(files), 0)

            # Check specific files exist
            self.assertTrue(any('character' in f for f in files))
            self.assertTrue(any('item' in f for f in files))
            self.assertTrue(any('texture' in f for f in files))
        finally:
            shutil.rmtree(output_dir)
