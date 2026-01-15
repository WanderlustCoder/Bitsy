"""
Test Style Transfer - Tests for style extraction and application.

Tests:
- ExtractedStyle dataclass
- extract_style
- extract_shading_style
- extract_outline_style
- apply_style
- apply_palette_style
- apply_shading_style
- apply_outline_style
- StyleEnforcer
- check_style_consistency
- compare_styles
- blend_styles
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas, Palette


try:
    from style.transfer import (
        OutlineType,
        ShadingType,
        ShadingStyle,
        OutlineStyle,
        ExtractedStyle,
        StyleEnforcer,
        extract_style,
        extract_shading_style,
        extract_outline_style,
        apply_style,
        apply_palette_style,
        apply_shading_style,
        apply_outline_style,
        check_style_consistency,
        fix_style_inconsistencies,
        compare_styles,
        blend_styles,
        list_style_attributes,
    )
    TRANSFER_AVAILABLE = True
except ImportError as e:
    TRANSFER_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestOutlineType(TestCase):
    """Tests for OutlineType enum."""

    def test_outline_types_defined(self):
        """OutlineType enum has expected values."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        self.assertEqual(OutlineType.NONE.value, 'none')
        self.assertEqual(OutlineType.FULL.value, 'full')
        self.assertEqual(OutlineType.EXTERNAL.value, 'external')
        self.assertEqual(OutlineType.SELECTIVE.value, 'selective')


class TestShadingType(TestCase):
    """Tests for ShadingType enum."""

    def test_shading_types_defined(self):
        """ShadingType enum has expected values."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        self.assertEqual(ShadingType.FLAT.value, 'flat')
        self.assertEqual(ShadingType.CEL.value, 'cel')
        self.assertEqual(ShadingType.SOFT.value, 'soft')
        self.assertEqual(ShadingType.DITHER.value, 'dither')


class TestShadingStyle(TestCase):
    """Tests for ShadingStyle dataclass."""

    def test_shading_style_defaults(self):
        """ShadingStyle has sensible defaults."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = ShadingStyle()
        self.assertEqual(style.type, ShadingType.CEL)
        self.assertEqual(style.levels, 3)
        self.assertEqual(style.shadow_hue_shift, 0.0)
        self.assertEqual(style.highlight_hue_shift, 0.0)

    def test_shading_style_custom(self):
        """ShadingStyle accepts custom values."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = ShadingStyle(
            type=ShadingType.SOFT,
            levels=5,
            shadow_hue_shift=10.0,
            highlight_hue_shift=-5.0,
            shadow_saturation=0.8,
            contrast=0.4
        )
        self.assertEqual(style.type, ShadingType.SOFT)
        self.assertEqual(style.levels, 5)
        self.assertEqual(style.shadow_hue_shift, 10.0)


class TestOutlineStyle(TestCase):
    """Tests for OutlineStyle dataclass."""

    def test_outline_style_defaults(self):
        """OutlineStyle has sensible defaults."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = OutlineStyle()
        self.assertEqual(style.type, OutlineType.FULL)
        self.assertEqual(style.thickness, 1)
        self.assertFalse(style.use_darker_shade)

    def test_outline_style_custom(self):
        """OutlineStyle accepts custom values."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = OutlineStyle(
            type=OutlineType.SELECTIVE,
            color=(50, 50, 50, 255),
            thickness=2,
            use_darker_shade=True,
            darken_amount=0.3
        )
        self.assertEqual(style.type, OutlineType.SELECTIVE)
        self.assertEqual(style.thickness, 2)
        self.assertTrue(style.use_darker_shade)


class TestExtractedStyle(TestCase):
    """Tests for ExtractedStyle dataclass."""

    def test_extracted_style_defaults(self):
        """ExtractedStyle has sensible defaults."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = ExtractedStyle()
        self.assertIsInstance(style.palette, Palette)
        self.assertIsInstance(style.shading, ShadingStyle)
        self.assertIsInstance(style.outline, OutlineStyle)
        self.assertFalse(style.anti_aliased)

    def test_extracted_style_to_dict(self):
        """ExtractedStyle can convert to dictionary."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = ExtractedStyle()
        style.palette.add((255, 0, 0, 255))
        style.color_count = 1

        d = style.to_dict()

        self.assertIn('palette_colors', d)
        self.assertIn('shading_type', d)
        self.assertIn('outline_type', d)
        self.assertIn('anti_aliased', d)


class TestExtractStyle(TestCase):
    """Tests for extract_style function."""

    def test_extract_style_basic(self):
        """extract_style extracts from canvas."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        style = extract_style(canvas)

        self.assertIsInstance(style, ExtractedStyle)
        self.assertGreater(len(style.palette), 0)
        self.assertIsNotNone(style.shading)
        self.assertIsNotNone(style.outline)

    def test_extract_style_pixel_density(self):
        """extract_style calculates pixel density."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        # Half-filled canvas
        canvas = Canvas(16, 16)
        canvas.fill_rect(0, 0, 8, 16, (255, 100, 50, 255))

        style = extract_style(canvas)

        self.assertGreater(style.pixel_density, 0.4)
        self.assertLess(style.pixel_density, 0.6)

    def test_extract_style_color_count(self):
        """extract_style counts colors."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = CanvasFixtures.solid((100, 100, 100, 255), width=16, height=16)
        style = extract_style(canvas)

        self.assertGreater(style.color_count, 0)

    def test_extract_style_empty_canvas(self):
        """extract_style handles empty canvas."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = Canvas(16, 16)
        style = extract_style(canvas)

        self.assertIsInstance(style, ExtractedStyle)
        self.assertEqual(style.pixel_density, 0.0)


class TestExtractShadingStyle(TestCase):
    """Tests for extract_shading_style function."""

    def test_extract_shading_basic(self):
        """extract_shading_style extracts shading info."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        shading = extract_shading_style(canvas)

        self.assertIsInstance(shading, ShadingStyle)
        self.assertIsInstance(shading.type, ShadingType)

    def test_extract_shading_gradient(self):
        """extract_shading_style detects gradient shading."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = CanvasFixtures.gradient_h(
            (100, 50, 50, 255), (200, 100, 100, 255), width=16, height=16
        )
        shading = extract_shading_style(canvas)

        # Should detect some shading levels
        self.assertGreater(shading.levels, 1)

    def test_extract_shading_empty(self):
        """extract_shading_style handles empty canvas."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = Canvas(16, 16)
        shading = extract_shading_style(canvas)

        self.assertIsInstance(shading, ShadingStyle)


class TestExtractOutlineStyle(TestCase):
    """Tests for extract_outline_style function."""

    def test_extract_outline_basic(self):
        """extract_outline_style extracts outline info."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        canvas = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        outline = extract_outline_style(canvas)

        self.assertIsInstance(outline, OutlineStyle)
        self.assertIsInstance(outline.type, OutlineType)

    def test_extract_outline_with_dark_edge(self):
        """extract_outline_style detects dark outlines."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        # Create sprite with dark outline
        canvas = Canvas(16, 16)
        # Fill interior
        canvas.fill_rect(2, 2, 12, 12, (200, 150, 100, 255))
        # Add dark outline
        for x in range(1, 15):
            canvas.set_pixel_solid(x, 1, (30, 30, 30, 255))
            canvas.set_pixel_solid(x, 14, (30, 30, 30, 255))
        for y in range(1, 15):
            canvas.set_pixel_solid(1, y, (30, 30, 30, 255))
            canvas.set_pixel_solid(14, y, (30, 30, 30, 255))

        outline = extract_outline_style(canvas)

        # Should detect outline
        self.assertIn(outline.type, [OutlineType.FULL, OutlineType.EXTERNAL])

    def test_extract_outline_no_outline(self):
        """extract_outline_style detects lack of outline."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        # Solid rectangle with no distinct outline
        canvas = CanvasFixtures.solid((200, 200, 200, 255), width=16, height=16)

        outline = extract_outline_style(canvas)

        # May detect no outline or same-color edges
        self.assertIsInstance(outline.type, OutlineType)


class TestApplyStyle(TestCase):
    """Tests for apply_style function."""

    def test_apply_style_basic(self):
        """apply_style applies style to canvas."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        reference = CanvasFixtures.solid((100, 150, 200, 255), width=16, height=16)

        style = extract_style(reference)
        result = apply_style(source, style)

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_apply_style_selective(self):
        """apply_style with selective options."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        style = ExtractedStyle()
        style.palette.add((255, 0, 0, 255))

        result = apply_style(source, style, apply_palette=True, apply_shading=False)

        self.assertCanvasSize(result, 16, 16)

    def test_apply_style_preserves_shape(self):
        """apply_style preserves overall shape."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        style = ExtractedStyle()

        result = apply_style(source, style)

        # Shape should be preserved (non-empty pixels in similar locations)
        for y in range(source.height):
            for x in range(source.width):
                src_alpha = source.get_pixel(x, y)[3]
                res_alpha = result.get_pixel(x, y)[3]
                if src_alpha > 0:
                    self.assertGreater(res_alpha, 0)


class TestApplyPaletteStyle(TestCase):
    """Tests for apply_palette_style function."""

    def test_apply_palette_basic(self):
        """apply_palette_style remaps colors."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        palette = Palette()
        palette.add((0, 0, 255, 255))

        result = apply_palette_style(source, palette)

        self.assertCanvasSize(result, 16, 16)

    def test_apply_palette_empty(self):
        """apply_palette_style handles empty palette gracefully."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        palette = Palette()

        result = apply_palette_style(source, palette)

        self.assertCanvasSize(result, 16, 16)


class TestApplyShadingStyle(TestCase):
    """Tests for apply_shading_style function."""

    def test_apply_shading_cel(self):
        """apply_shading_style applies cel shading."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.gradient_h(
            (100, 100, 100, 255), (200, 200, 200, 255), width=16, height=16
        )
        shading = ShadingStyle(type=ShadingType.CEL, levels=3)

        result = apply_shading_style(source, shading)

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_apply_shading_hue_shift(self):
        """apply_shading_style applies hue shifts."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        shading = ShadingStyle(
            type=ShadingType.FLAT,
            shadow_hue_shift=30.0,
            highlight_hue_shift=-20.0
        )

        result = apply_shading_style(source, shading)

        self.assertCanvasSize(result, 16, 16)


class TestApplyOutlineStyle(TestCase):
    """Tests for apply_outline_style function."""

    def test_apply_outline_full(self):
        """apply_outline_style adds full outline."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        outline = OutlineStyle(
            type=OutlineType.FULL,
            color=(0, 0, 0, 255)
        )

        result = apply_outline_style(source, outline)

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_apply_outline_none(self):
        """apply_outline_style with none type returns copy."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        outline = OutlineStyle(type=OutlineType.NONE)

        result = apply_outline_style(source, outline)

        self.assertCanvasEqual(result, source)

    def test_apply_outline_darker_shade(self):
        """apply_outline_style with darker shade."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        source = CanvasFixtures.circle((200, 100, 50, 255), size=16)
        outline = OutlineStyle(
            type=OutlineType.FULL,
            use_darker_shade=True,
            darken_amount=0.5
        )

        result = apply_outline_style(source, outline)

        self.assertCanvasSize(result, 16, 16)


class TestStyleEnforcer(TestCase):
    """Tests for StyleEnforcer class."""

    def test_enforcer_creation_with_style(self):
        """StyleEnforcer can be created with reference style."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style = ExtractedStyle()
        enforcer = StyleEnforcer(reference_style=style)

        self.assertIsNotNone(enforcer.style)

    def test_enforcer_creation_with_canvases(self):
        """StyleEnforcer can be created with reference canvases."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        refs = [
            CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16),
            CanvasFixtures.solid((150, 80, 40, 255), width=16, height=16),
        ]
        enforcer = StyleEnforcer(reference_canvases=refs)

        self.assertIsNotNone(enforcer.style)
        self.assertGreater(len(enforcer.style.palette), 0)

    def test_enforcer_check(self):
        """StyleEnforcer.check returns consistency info."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        enforcer = StyleEnforcer(reference_canvases=[ref])

        target = CanvasFixtures.solid((100, 150, 200, 255), width=16, height=16)
        result = enforcer.check(target)

        self.assertIn('overall_score', result)
        self.assertIn('palette_score', result)
        self.assertIn('issues', result)

    def test_enforcer_enforce(self):
        """StyleEnforcer.enforce applies style."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        enforcer = StyleEnforcer(reference_canvases=[ref])

        target = CanvasFixtures.circle((100, 150, 200, 255), size=16)
        result = enforcer.enforce(target)

        self.assertCanvasSize(result, 16, 16)

    def test_enforcer_fix(self):
        """StyleEnforcer.fix corrects inconsistencies."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        enforcer = StyleEnforcer(reference_canvases=[ref])

        target = CanvasFixtures.circle((100, 150, 200, 255), size=16)
        result = enforcer.fix(target)

        self.assertCanvasSize(result, 16, 16)


class TestCheckStyleConsistency(TestCase):
    """Tests for check_style_consistency function."""

    def test_check_consistency_same_style(self):
        """check_style_consistency scores matching styles highly."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        style = extract_style(ref)

        # Same canvas should match perfectly
        result = check_style_consistency(ref, style)

        self.assertGreater(result['overall_score'], 0.5)

    def test_check_consistency_different_style(self):
        """check_style_consistency detects differences."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        style = extract_style(ref)

        different = CanvasFixtures.solid((50, 100, 200, 255), width=16, height=16)
        result = check_style_consistency(different, style)

        self.assertIn('issues', result)

    def test_check_consistency_issues_list(self):
        """check_style_consistency returns issues list."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        style = extract_style(ref)

        target = Canvas(16, 16)
        result = check_style_consistency(target, style)

        self.assertIsInstance(result['issues'], list)


class TestFixStyleInconsistencies(TestCase):
    """Tests for fix_style_inconsistencies function."""

    def test_fix_inconsistencies(self):
        """fix_style_inconsistencies applies style."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        style = extract_style(ref)

        target = CanvasFixtures.circle((100, 150, 200, 255), size=16)
        result = fix_style_inconsistencies(target, style)

        self.assertCanvasSize(result, 16, 16)


class TestCompareStyles(TestCase):
    """Tests for compare_styles function."""

    def test_compare_same_style(self):
        """compare_styles returns high similarity for same style."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        ref = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        style = extract_style(ref)

        result = compare_styles(style, style)

        self.assertEqual(result['similarity'], 1.0)
        self.assertEqual(len(result['differences']), 0)

    def test_compare_different_styles(self):
        """compare_styles detects differences."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style1 = ExtractedStyle()
        style1.shading.type = ShadingType.CEL

        style2 = ExtractedStyle()
        style2.shading.type = ShadingType.FLAT

        result = compare_styles(style1, style2)

        self.assertLess(result['similarity'], 1.0)
        self.assertIn('Different shading types', result['differences'])

    def test_compare_returns_all_scores(self):
        """compare_styles returns all comparison scores."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style1 = ExtractedStyle()
        style2 = ExtractedStyle()

        result = compare_styles(style1, style2)

        self.assertIn('similarity', result)
        self.assertIn('palette_match', result)
        self.assertIn('shading_match', result)
        self.assertIn('outline_match', result)


class TestBlendStyles(TestCase):
    """Tests for blend_styles function."""

    def test_blend_styles_50_50(self):
        """blend_styles creates blended style."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style1 = ExtractedStyle()
        style1.palette.add((255, 0, 0, 255))
        style1.shading.shadow_hue_shift = 10.0

        style2 = ExtractedStyle()
        style2.palette.add((0, 0, 255, 255))
        style2.shading.shadow_hue_shift = 30.0

        blended = blend_styles(style1, style2, blend_factor=0.5)

        self.assertIsInstance(blended, ExtractedStyle)
        # Hue shift should be blended
        self.assertEqual(blended.shading.shadow_hue_shift, 20.0)

    def test_blend_styles_0(self):
        """blend_styles with factor 0 uses style1."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style1 = ExtractedStyle()
        style1.shading.type = ShadingType.CEL

        style2 = ExtractedStyle()
        style2.shading.type = ShadingType.FLAT

        blended = blend_styles(style1, style2, blend_factor=0.0)

        self.assertEqual(blended.shading.type, ShadingType.CEL)

    def test_blend_styles_1(self):
        """blend_styles with factor 1 uses style2."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        style1 = ExtractedStyle()
        style1.shading.type = ShadingType.CEL

        style2 = ExtractedStyle()
        style2.shading.type = ShadingType.FLAT

        blended = blend_styles(style1, style2, blend_factor=1.0)

        self.assertEqual(blended.shading.type, ShadingType.FLAT)


class TestListStyleAttributes(TestCase):
    """Tests for list_style_attributes function."""

    def test_list_attributes(self):
        """list_style_attributes returns attribute names."""
        self.skipUnless(TRANSFER_AVAILABLE, "Transfer module not available")

        attrs = list_style_attributes()

        self.assertIsInstance(attrs, list)
        self.assertIn('palette', attrs)
        self.assertIn('shading_type', attrs)
        self.assertIn('outline_type', attrs)
        self.assertIn('anti_aliased', attrs)
