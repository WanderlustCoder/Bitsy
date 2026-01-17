"""
Keyword extraction for natural language parsing.

Provides vocabulary-based keyword extraction that maps
natural language terms to generation parameters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
import re
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class ExtractedKeywords:
    """Result of keyword extraction."""
    sprite_type: Optional[str] = None
    preset: Optional[str] = None
    species: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    features: Dict[str, str] = field(default_factory=dict)
    modifiers: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    confidence: float = 0.0


class VocabularyRegistry:
    """Extensible vocabulary registry for keyword extraction."""

    _instance: Optional['VocabularyRegistry'] = None

    def __init__(self):
        self._mappings: Dict[str, Dict[str, str]] = {}
        self._synonyms: Dict[str, str] = {}
        self._load_defaults()

    @classmethod
    def get_instance(cls) -> 'VocabularyRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_defaults(self):
        """Load default vocabulary."""
        # Sprite types
        self._mappings['sprite_type'] = {
            # Character keywords
            'warrior': 'character', 'mage': 'character', 'knight': 'character',
            'rogue': 'character', 'wizard': 'character', 'hero': 'character',
            'villager': 'character', 'npc': 'character', 'person': 'character',
            'man': 'character', 'woman': 'character', 'boy': 'character',
            'girl': 'character', 'elf': 'character', 'dwarf': 'character',
            'orc': 'character', 'human': 'character',
            # Creature keywords
            'slime': 'creature', 'goblin': 'creature', 'dragon': 'creature',
            'skeleton': 'creature', 'monster': 'creature', 'beast': 'creature',
            'demon': 'creature', 'ghost': 'creature', 'zombie': 'creature',
            'spider': 'creature', 'wolf': 'creature', 'bat': 'creature',
            # Item keywords
            'sword': 'item', 'potion': 'item', 'key': 'item', 'coin': 'item',
            'gem': 'item', 'scroll': 'item', 'weapon': 'item', 'armor': 'item',
            'shield': 'item', 'staff': 'item', 'wand': 'item', 'bow': 'item',
            'axe': 'item', 'dagger': 'item', 'helmet': 'item',
            # Prop keywords
            'chest': 'prop', 'barrel': 'prop', 'crate': 'prop', 'table': 'prop',
            'chair': 'prop', 'tree': 'prop', 'rock': 'prop', 'bush': 'prop',
            'flower': 'prop', 'lamp': 'prop', 'sign': 'prop', 'door': 'prop',
            'torch': 'prop', 'fountain': 'prop', 'statue': 'prop',
            # Scene keywords
            'forest': 'scene', 'castle': 'scene', 'dungeon': 'scene',
            'cave': 'scene', 'village': 'scene', 'town': 'scene',
            'mountain': 'scene', 'beach': 'scene', 'desert': 'scene',
        }

        # Character presets
        self._mappings['preset'] = {
            'hero': 'hero', 'heroine': 'heroine', 'warrior': 'warrior',
            'mage': 'wizard', 'wizard': 'wizard', 'rogue': 'rogue',
            'knight': 'knight', 'princess': 'princess', 'villager': 'villager',
            'monster': 'monster', 'ghost': 'ghost', 'child': 'child',
            'elder': 'elder',
        }

        # Species
        self._mappings['species'] = {
            'human': 'human', 'elf': 'elf', 'dwarf': 'dwarf',
            'orc': 'orc', 'goblin': 'goblin', 'halfling': 'human',
        }

        # Colors
        self._mappings['color'] = {
            'red': 'red', 'blue': 'blue', 'green': 'green', 'yellow': 'yellow',
            'purple': 'purple', 'orange': 'orange', 'pink': 'pink',
            'brown': 'brown', 'black': 'black', 'white': 'white',
            'gray': 'gray', 'grey': 'gray', 'golden': 'golden', 'gold': 'golden',
            'silver': 'silver', 'bronze': 'bronze', 'copper': 'copper',
            'crimson': 'red', 'scarlet': 'red', 'azure': 'blue',
            'emerald': 'green', 'violet': 'purple',
        }

        # Hair styles
        self._mappings['hair_style'] = {
            'spiky': 'spiky', 'long': 'long', 'short': 'short',
            'curly': 'curly', 'bald': 'bald', 'ponytail': 'ponytail',
            'braided': 'braided', 'mohawk': 'mohawk',
        }

        # Modifiers (adjectives)
        self._mappings['modifier'] = {
            'fierce': 'fierce', 'angry': 'angry', 'happy': 'happy',
            'sad': 'sad', 'scary': 'scary', 'cute': 'cute',
            'small': 'small', 'large': 'large', 'big': 'big', 'tiny': 'tiny',
            'tall': 'tall', 'short': 'short', 'old': 'old', 'young': 'young',
            'armored': 'armored', 'magical': 'magical', 'glowing': 'glowing',
            'dark': 'dark', 'light': 'light', 'shiny': 'shiny',
        }

        # Time of day
        self._mappings['time_of_day'] = {
            'dawn': 'dawn', 'morning': 'morning', 'noon': 'noon',
            'afternoon': 'afternoon', 'dusk': 'dusk', 'sunset': 'dusk',
            'night': 'night', 'midnight': 'midnight', 'evening': 'dusk',
        }

        # Weather
        self._mappings['weather'] = {
            'clear': 'clear', 'sunny': 'clear', 'cloudy': 'cloudy',
            'rain': 'rain', 'rainy': 'rain', 'raining': 'rain',
            'snow': 'snow', 'snowy': 'snow', 'snowing': 'snow',
            'fog': 'fog', 'foggy': 'fog', 'storm': 'storm', 'stormy': 'storm',
        }

    def register(self, category: str, keywords: Dict[str, str]):
        """Add new keywords at runtime.

        Args:
            category: Vocabulary category
            keywords: Mapping of keyword -> value
        """
        self._mappings.setdefault(category, {}).update(keywords)

    def register_synonym(self, word: str, canonical: str):
        """Register a synonym.

        Args:
            word: The synonym
            canonical: The canonical form
        """
        self._synonyms[word.lower()] = canonical.lower()

    def register_from_file(self, path: str):
        """Load vocabulary from JSON file.

        Args:
            path: Path to JSON file
        """
        with open(path, 'r') as f:
            data = json.load(f)
        for category, keywords in data.items():
            if category == 'synonyms':
                for word, canonical in keywords.items():
                    self.register_synonym(word, canonical)
            else:
                self.register(category, keywords)

    def lookup(self, word: str, category: str) -> Optional[str]:
        """Look up a word in a category.

        Args:
            word: Word to look up
            category: Category to search

        Returns:
            Mapped value or None
        """
        word = word.lower()
        # Check synonyms first
        if word in self._synonyms:
            word = self._synonyms[word]
        # Look up in category
        if category in self._mappings:
            return self._mappings[category].get(word)
        return None

    def find_category(self, word: str) -> Optional[tuple]:
        """Find which category a word belongs to.

        Args:
            word: Word to find

        Returns:
            Tuple of (category, value) or None
        """
        word = word.lower()
        if word in self._synonyms:
            word = self._synonyms[word]

        for category, mapping in self._mappings.items():
            if word in mapping:
                return (category, mapping[word])
        return None

    def categories(self) -> List[str]:
        """List all categories."""
        return list(self._mappings.keys())

    def get_category(self, category: str) -> Dict[str, str]:
        """Get all keywords in a category."""
        return self._mappings.get(category, {}).copy()


def get_vocabulary() -> VocabularyRegistry:
    """Get the global vocabulary registry."""
    return VocabularyRegistry.get_instance()


def extract_keywords(prompt: str) -> ExtractedKeywords:
    """Extract keywords from a natural language prompt.

    Args:
        prompt: Natural language text

    Returns:
        ExtractedKeywords with extracted information
    """
    vocab = get_vocabulary()
    result = ExtractedKeywords()

    # Tokenize
    tokens = _tokenize(prompt)
    matched_tokens = set()

    # Extract sprite type
    for token in tokens:
        cat = vocab.find_category(token)
        if cat and cat[0] == 'sprite_type':
            result.sprite_type = cat[1]
            matched_tokens.add(token)
            break

    # Extract preset
    for token in tokens:
        if token in matched_tokens:
            continue
        val = vocab.lookup(token, 'preset')
        if val:
            result.preset = val
            matched_tokens.add(token)
            break

    # Extract species
    for token in tokens:
        if token in matched_tokens:
            continue
        val = vocab.lookup(token, 'species')
        if val:
            result.species = val
            matched_tokens.add(token)
            break

    # Extract colors
    for token in tokens:
        if token in matched_tokens:
            continue
        val = vocab.lookup(token, 'color')
        if val:
            result.colors.append(val)
            matched_tokens.add(token)

    # Extract modifiers
    for token in tokens:
        if token in matched_tokens:
            continue
        val = vocab.lookup(token, 'modifier')
        if val:
            result.modifiers.append(val)
            matched_tokens.add(token)

    # Extract features (color + type combinations like "red hair")
    for i, token in enumerate(tokens):
        if token in matched_tokens:
            continue
        # Check for "color feature" patterns
        if i > 0 and tokens[i-1] in result.colors:
            if token in ['hair', 'eyes', 'skin', 'armor', 'cape', 'robe']:
                result.features[token] = tokens[i-1]
                matched_tokens.add(token)

    # Collect unknown tokens
    stopwords = {'a', 'an', 'the', 'with', 'and', 'or', 'in', 'on', 'at', 'for', 'to'}
    for token in tokens:
        if token not in matched_tokens and token not in stopwords:
            result.unknown.append(token)

    # Calculate confidence
    total_tokens = len([t for t in tokens if t not in stopwords])
    if total_tokens > 0:
        result.confidence = len(matched_tokens) / total_tokens
    else:
        result.confidence = 0.0

    return result


def _tokenize(text: str) -> List[str]:
    """Tokenize text into words."""
    # Lowercase and split on non-alphanumeric
    text = text.lower()
    tokens = re.findall(r'[a-z]+', text)
    return tokens


def sync_vocabulary_with_generators():
    """Update vocabulary based on available generators."""
    vocab = get_vocabulary()

    try:
        from generators import list_creature_types, list_item_types, list_prop_types

        # Add creature types
        for name in list_creature_types():
            vocab.register('sprite_type', {name: 'creature'})

        # Add item types
        for name in list_item_types():
            vocab.register('sprite_type', {name: 'item'})

        # Add prop types
        for name in list_prop_types():
            vocab.register('sprite_type', {name: 'prop'})

    except ImportError:
        pass  # Generators not available
