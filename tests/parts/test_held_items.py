"""
Test Held Items - Tests for books, bags, and other held items.

Tests:
- Held item creation
- Item rendering
- Item factory functions
- Different item types
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from parts.held_items import (
    HeldItem,
    Book,
    OpenBook,
    Scroll,
    Flower,
    Cup,
    Bag,
    create_held_item,
    list_held_item_types,
    HELD_ITEM_TYPES
)
from parts.equipment import EquipmentSlot, DrawLayer


class TestHeldItemBase(TestCase):
    """Tests for HeldItem base class."""

    def test_held_item_slot(self):
        """HeldItem uses HAND_RIGHT equipment slot."""
        book = Book()
        self.assertEqual(book.config.slot, EquipmentSlot.HAND_RIGHT)

    def test_held_item_layer(self):
        """HeldItem renders in front layer."""
        book = Book()
        self.assertEqual(book.config.layer, DrawLayer.FRONT)

    def test_held_item_hand(self):
        """HeldItem tracks which hand it uses."""
        book = Book()
        self.assertEqual(book.hand, 'both')

        flower = Flower()
        self.assertEqual(flower.hand, 'right')


class TestBook(TestCase):
    """Tests for Book class."""

    def test_book_creation(self):
        """Book can be created with default config."""
        book = Book()
        self.assertEqual(book.name, 'book')

    def test_book_custom_color(self):
        """Book can have custom cover color."""
        book = Book(cover_color=(50, 100, 150, 255))
        self.assertEqual(book.cover_color, (50, 100, 150, 255))

    def test_book_draw(self):
        """Book can draw to canvas."""
        canvas = Canvas(32, 32)
        book = Book()
        book.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)

    def test_book_has_pages(self):
        """Book has page color defined."""
        book = Book()
        self.assertIsNotNone(book.pages_color)


class TestOpenBook(TestCase):
    """Tests for OpenBook class."""

    def test_open_book_creation(self):
        """OpenBook can be created."""
        book = OpenBook()
        self.assertEqual(book.name, 'open_book')

    def test_open_book_draw(self):
        """OpenBook can draw to canvas."""
        canvas = Canvas(32, 32)
        book = OpenBook()
        book.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)

    def test_open_book_has_text_color(self):
        """OpenBook has text line color."""
        book = OpenBook()
        self.assertIsNotNone(book.text_color)


class TestScroll(TestCase):
    """Tests for Scroll class."""

    def test_scroll_creation(self):
        """Scroll can be created."""
        scroll = Scroll()
        self.assertEqual(scroll.name, 'scroll')

    def test_scroll_draw(self):
        """Scroll can draw to canvas."""
        canvas = Canvas(32, 32)
        scroll = Scroll()
        scroll.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)

    def test_scroll_has_rod(self):
        """Scroll has rod color defined."""
        scroll = Scroll()
        self.assertIsNotNone(scroll.rod_color)


class TestFlower(TestCase):
    """Tests for Flower class."""

    def test_flower_creation(self):
        """Flower can be created."""
        flower = Flower()
        self.assertEqual(flower.name, 'flower')
        self.assertEqual(flower.hand, 'right')

    def test_flower_custom_color(self):
        """Flower can have custom petal color."""
        flower = Flower(petal_color=(255, 200, 100, 255))
        self.assertEqual(flower.petal_color, (255, 200, 100, 255))

    def test_flower_draw(self):
        """Flower can draw to canvas."""
        canvas = Canvas(32, 32)
        flower = Flower()
        flower.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)


class TestCup(TestCase):
    """Tests for Cup class."""

    def test_cup_creation(self):
        """Cup can be created."""
        cup = Cup()
        self.assertEqual(cup.name, 'cup')
        self.assertEqual(cup.hand, 'right')

    def test_cup_custom_color(self):
        """Cup can have custom cup color."""
        cup = Cup(cup_color=(100, 150, 200, 255))
        self.assertEqual(cup.cup_color, (100, 150, 200, 255))

    def test_cup_draw(self):
        """Cup can draw to canvas."""
        canvas = Canvas(32, 32)
        cup = Cup()
        cup.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)

    def test_cup_has_liquid(self):
        """Cup has liquid color defined."""
        cup = Cup()
        self.assertIsNotNone(cup.liquid_color)


class TestBag(TestCase):
    """Tests for Bag class."""

    def test_bag_creation(self):
        """Bag can be created."""
        bag = Bag()
        self.assertEqual(bag.name, 'bag')
        self.assertEqual(bag.hand, 'left')

    def test_bag_custom_color(self):
        """Bag can have custom bag color."""
        bag = Bag(bag_color=(80, 50, 30, 255))
        self.assertEqual(bag.bag_color, (80, 50, 30, 255))

    def test_bag_draw(self):
        """Bag can draw to canvas."""
        canvas = Canvas(32, 32)
        bag = Bag()
        bag.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)

    def test_bag_has_buckle(self):
        """Bag has buckle color defined."""
        bag = Bag()
        self.assertIsNotNone(bag.buckle_color)


class TestHeldItemFactory(TestCase):
    """Tests for held item factory functions."""

    def test_create_held_item_book(self):
        """create_held_item creates book."""
        book = create_held_item('book')
        self.assertIsInstance(book, Book)

    def test_create_held_item_flower(self):
        """create_held_item creates flower."""
        flower = create_held_item('flower')
        self.assertIsInstance(flower, Flower)

    def test_create_held_item_with_kwargs(self):
        """create_held_item passes kwargs to constructor."""
        book = create_held_item('book', cover_color=(50, 50, 100, 255))
        self.assertEqual(book.cover_color, (50, 50, 100, 255))

    def test_create_held_item_invalid(self):
        """create_held_item raises for unknown type."""
        with self.assertRaises(ValueError):
            create_held_item('unknown_item')

    def test_list_held_item_types(self):
        """list_held_item_types returns all types."""
        types = list_held_item_types()

        self.assertIn('book', types)
        self.assertIn('open_book', types)
        self.assertIn('scroll', types)
        self.assertIn('flower', types)
        self.assertIn('cup', types)
        self.assertIn('bag', types)

    def test_held_item_types_dict(self):
        """HELD_ITEM_TYPES contains all item classes."""
        self.assertEqual(len(HELD_ITEM_TYPES), 6)


class TestHeldItemIntegration(TestCase):
    """Integration tests for held items."""

    def test_all_items_drawable(self):
        """All held item types can be drawn."""
        for item_type in HELD_ITEM_TYPES:
            canvas = Canvas(32, 32)
            item = create_held_item(item_type)
            item.draw(canvas, 16, 16, 24, 20)
            self.assertCanvasNotEmpty(canvas, f"{item_type} should draw content")
