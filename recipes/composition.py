"""
Compositional Grammar System - Parse natural language into scene structures.

Handles:
- Individual objects: "a red potion bottle"
- Individual characters: "a happy elf girl"
- Full scenes: "a knight holding a sword in a dark castle"

Grammar structure:
    Scene = {
        'type': 'character' | 'object' | 'scene',
        'subjects': [...],      # Main focus (characters, creatures)
        'objects': [...],       # Items, props
        'environment': {...},   # Background, setting
        'relationships': [...], # How elements connect
        'atmosphere': {...},    # Mood, lighting, style
    }
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class ElementType(Enum):
    CHARACTER = 'character'
    OBJECT = 'object'
    ENVIRONMENT = 'environment'


class Relationship(Enum):
    # Holding/carrying
    HOLDING = 'holding'
    CARRYING = 'carrying'
    WIELDING = 'wielding'

    # Position relative to object
    SITTING_ON = 'sitting_on'
    STANDING_ON = 'standing_on'
    LEANING_ON = 'leaning_on'
    LYING_ON = 'lying_on'

    # Position relative to other
    NEXT_TO = 'next_to'
    BEHIND = 'behind'
    IN_FRONT_OF = 'in_front_of'
    ABOVE = 'above'
    BELOW = 'below'

    # Inside/outside
    INSIDE = 'inside'
    OUTSIDE = 'outside'

    # Actions
    LOOKING_AT = 'looking_at'
    REACHING_FOR = 'reaching_for'

    # Default
    NONE = 'none'


class Position(Enum):
    CENTER = 'center'
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'
    TOP_LEFT = 'top_left'
    TOP_RIGHT = 'top_right'
    BOTTOM_LEFT = 'bottom_left'
    BOTTOM_RIGHT = 'bottom_right'
    FOREGROUND = 'foreground'
    MIDGROUND = 'midground'
    BACKGROUND = 'background'


@dataclass
class Element:
    """Base class for scene elements."""
    type: ElementType
    name: str  # e.g., "sword", "girl", "forest"
    attributes: Dict[str, Any] = field(default_factory=dict)
    position: Position = Position.CENTER
    scale: float = 1.0
    layer: int = 0  # Render order (higher = front)


@dataclass
class Character(Element):
    """A character/creature in the scene."""
    def __init__(self, name: str = "character", **kwargs):
        super().__init__(
            type=ElementType.CHARACTER,
            name=name,
            **kwargs
        )
        # Character-specific defaults
        if 'layer' not in kwargs:
            self.layer = 50  # Characters typically in midground


@dataclass
class Object(Element):
    """An item/prop in the scene."""
    def __init__(self, name: str = "object", **kwargs):
        super().__init__(
            type=ElementType.OBJECT,
            name=name,
            **kwargs
        )


@dataclass
class Environment(Element):
    """A background/setting."""
    def __init__(self, name: str = "environment", **kwargs):
        super().__init__(
            type=ElementType.ENVIRONMENT,
            name=name,
            **kwargs
        )
        if 'layer' not in kwargs:
            self.layer = 0  # Background is always behind


@dataclass
class RelationshipLink:
    """Connects two elements with a relationship."""
    subject: Element
    relationship: Relationship
    target: Element


@dataclass
class Scene:
    """Complete scene structure."""
    # What type of output
    type: str = 'scene'  # 'character', 'object', or 'scene'

    # Scene elements
    subjects: List[Character] = field(default_factory=list)
    objects: List[Object] = field(default_factory=list)
    environment: Optional[Environment] = None

    # How elements relate
    relationships: List[RelationshipLink] = field(default_factory=list)

    # Overall mood/style
    atmosphere: Dict[str, Any] = field(default_factory=dict)

    # Canvas settings
    size: int = 128
    background_color: Tuple[int, int, int] = (45, 40, 55)

    def get_all_elements(self) -> List[Element]:
        """Get all elements sorted by layer (back to front)."""
        elements = []
        if self.environment:
            elements.append(self.environment)
        elements.extend(self.objects)
        elements.extend(self.subjects)
        return sorted(elements, key=lambda e: e.layer)

    def is_simple_character(self) -> bool:
        """Check if this is just a single character (no objects/scene)."""
        return (
            len(self.subjects) == 1 and
            len(self.objects) == 0 and
            self.environment is None
        )

    def is_simple_object(self) -> bool:
        """Check if this is just a single object."""
        return (
            len(self.subjects) == 0 and
            len(self.objects) == 1 and
            self.environment is None
        )


# =============================================================================
# OBJECT KEYWORDS - Items, props, tools
# =============================================================================

OBJECT_KEYWORDS = {
    # === Books & Writing ===
    'book': {'category': 'books', 'name': 'book'},
    'tome': {'category': 'books', 'name': 'tome', 'style': 'ancient'},
    'spellbook': {'category': 'books', 'name': 'spellbook', 'style': 'magical'},
    'grimoire': {'category': 'books', 'name': 'grimoire', 'style': 'dark'},
    'journal': {'category': 'books', 'name': 'journal', 'style': 'personal'},
    'diary': {'category': 'books', 'name': 'diary', 'style': 'personal'},
    'notebook': {'category': 'books', 'name': 'notebook'},
    'scroll': {'category': 'books', 'name': 'scroll'},
    'letter': {'category': 'books', 'name': 'letter'},
    'map': {'category': 'books', 'name': 'map'},
    'quill': {'category': 'writing', 'name': 'quill'},
    'pen': {'category': 'writing', 'name': 'pen'},
    'pencil': {'category': 'writing', 'name': 'pencil'},
    'ink': {'category': 'writing', 'name': 'ink_bottle'},

    # === Weapons ===
    'sword': {'category': 'weapons', 'name': 'sword'},
    'blade': {'category': 'weapons', 'name': 'sword'},
    'longsword': {'category': 'weapons', 'name': 'longsword'},
    'shortsword': {'category': 'weapons', 'name': 'shortsword'},
    'dagger': {'category': 'weapons', 'name': 'dagger'},
    'knife': {'category': 'weapons', 'name': 'knife'},
    'katana': {'category': 'weapons', 'name': 'katana'},
    'rapier': {'category': 'weapons', 'name': 'rapier'},
    'axe': {'category': 'weapons', 'name': 'axe'},
    'battleaxe': {'category': 'weapons', 'name': 'battleaxe'},
    'hatchet': {'category': 'weapons', 'name': 'hatchet'},
    'hammer': {'category': 'weapons', 'name': 'hammer'},
    'warhammer': {'category': 'weapons', 'name': 'warhammer'},
    'mace': {'category': 'weapons', 'name': 'mace'},
    'club': {'category': 'weapons', 'name': 'club'},
    'staff': {'category': 'weapons', 'name': 'staff', 'style': 'magical'},
    'wand': {'category': 'weapons', 'name': 'wand', 'style': 'magical'},
    'rod': {'category': 'weapons', 'name': 'rod'},
    'bow': {'category': 'weapons', 'name': 'bow'},
    'crossbow': {'category': 'weapons', 'name': 'crossbow'},
    'arrow': {'category': 'weapons', 'name': 'arrow'},
    'arrows': {'category': 'weapons', 'name': 'arrows'},
    'quiver': {'category': 'weapons', 'name': 'quiver'},
    'spear': {'category': 'weapons', 'name': 'spear'},
    'lance': {'category': 'weapons', 'name': 'lance'},
    'halberd': {'category': 'weapons', 'name': 'halberd'},
    'trident': {'category': 'weapons', 'name': 'trident'},
    'scythe': {'category': 'weapons', 'name': 'scythe'},
    'sickle': {'category': 'weapons', 'name': 'sickle'},
    'whip': {'category': 'weapons', 'name': 'whip'},
    'flail': {'category': 'weapons', 'name': 'flail'},
    'gun': {'category': 'weapons', 'name': 'gun'},
    'pistol': {'category': 'weapons', 'name': 'pistol'},
    'rifle': {'category': 'weapons', 'name': 'rifle'},
    'cannon': {'category': 'weapons', 'name': 'cannon'},

    # === Armor & Shield ===
    'shield': {'category': 'armor', 'name': 'shield'},
    'buckler': {'category': 'armor', 'name': 'buckler'},
    'helmet': {'category': 'armor', 'name': 'helmet'},
    'helm': {'category': 'armor', 'name': 'helmet'},
    'crown': {'category': 'armor', 'name': 'crown'},
    'tiara': {'category': 'armor', 'name': 'tiara'},
    'armor': {'category': 'armor', 'name': 'armor'},
    'chestplate': {'category': 'armor', 'name': 'chestplate'},
    'gauntlet': {'category': 'armor', 'name': 'gauntlet'},
    'gauntlets': {'category': 'armor', 'name': 'gauntlets'},

    # === Potions & Bottles ===
    'potion': {'category': 'potions', 'name': 'potion'},
    'bottle': {'category': 'potions', 'name': 'bottle'},
    'vial': {'category': 'potions', 'name': 'vial'},
    'flask': {'category': 'potions', 'name': 'flask'},
    'elixir': {'category': 'potions', 'name': 'elixir'},
    'health potion': {'category': 'potions', 'name': 'health_potion', 'color': 'red'},
    'mana potion': {'category': 'potions', 'name': 'mana_potion', 'color': 'blue'},
    'poison': {'category': 'potions', 'name': 'poison', 'color': 'green'},
    'antidote': {'category': 'potions', 'name': 'antidote', 'color': 'yellow'},

    # === Food & Drink ===
    'apple': {'category': 'food', 'name': 'apple'},
    'bread': {'category': 'food', 'name': 'bread'},
    'cheese': {'category': 'food', 'name': 'cheese'},
    'meat': {'category': 'food', 'name': 'meat'},
    'fish': {'category': 'food', 'name': 'fish'},
    'cake': {'category': 'food', 'name': 'cake'},
    'pie': {'category': 'food', 'name': 'pie'},
    'cookie': {'category': 'food', 'name': 'cookie'},
    'cookies': {'category': 'food', 'name': 'cookies'},
    'candy': {'category': 'food', 'name': 'candy'},
    'fruit': {'category': 'food', 'name': 'fruit'},
    'vegetables': {'category': 'food', 'name': 'vegetables'},
    'cup': {'category': 'drink', 'name': 'cup'},
    'mug': {'category': 'drink', 'name': 'mug'},
    'goblet': {'category': 'drink', 'name': 'goblet'},
    'chalice': {'category': 'drink', 'name': 'chalice'},
    'wine': {'category': 'drink', 'name': 'wine'},
    'ale': {'category': 'drink', 'name': 'ale'},
    'beer': {'category': 'drink', 'name': 'beer'},
    'tea': {'category': 'drink', 'name': 'tea'},
    'coffee': {'category': 'drink', 'name': 'coffee'},
    'teacup': {'category': 'drink', 'name': 'teacup'},
    'teapot': {'category': 'drink', 'name': 'teapot'},

    # === Jewelry & Accessories ===
    'ring': {'category': 'jewelry', 'name': 'ring'},
    'necklace': {'category': 'jewelry', 'name': 'necklace'},
    'pendant': {'category': 'jewelry', 'name': 'pendant'},
    'amulet': {'category': 'jewelry', 'name': 'amulet'},
    'bracelet': {'category': 'jewelry', 'name': 'bracelet'},
    'earring': {'category': 'jewelry', 'name': 'earring'},
    'earrings': {'category': 'jewelry', 'name': 'earrings'},
    'brooch': {'category': 'jewelry', 'name': 'brooch'},
    'locket': {'category': 'jewelry', 'name': 'locket'},

    # === Magical Items ===
    'orb': {'category': 'magical', 'name': 'orb'},
    'crystal': {'category': 'magical', 'name': 'crystal'},
    'gem': {'category': 'magical', 'name': 'gem'},
    'gemstone': {'category': 'magical', 'name': 'gemstone'},
    'diamond': {'category': 'magical', 'name': 'diamond'},
    'ruby': {'category': 'magical', 'name': 'ruby'},
    'emerald': {'category': 'magical', 'name': 'emerald'},
    'sapphire': {'category': 'magical', 'name': 'sapphire'},
    'amethyst': {'category': 'magical', 'name': 'amethyst'},
    'pearl': {'category': 'magical', 'name': 'pearl'},
    'rune': {'category': 'magical', 'name': 'rune'},
    'runes': {'category': 'magical', 'name': 'runes'},
    'talisman': {'category': 'magical', 'name': 'talisman'},
    'charm': {'category': 'magical', 'name': 'charm'},
    'artifact': {'category': 'magical', 'name': 'artifact'},
    'relic': {'category': 'magical', 'name': 'relic'},

    # === Tools ===
    'pickaxe': {'category': 'tools', 'name': 'pickaxe'},
    'shovel': {'category': 'tools', 'name': 'shovel'},
    'hoe': {'category': 'tools', 'name': 'hoe'},
    'rake': {'category': 'tools', 'name': 'rake'},
    'saw': {'category': 'tools', 'name': 'saw'},
    'wrench': {'category': 'tools', 'name': 'wrench'},
    'screwdriver': {'category': 'tools', 'name': 'screwdriver'},
    'pliers': {'category': 'tools', 'name': 'pliers'},
    'anvil': {'category': 'tools', 'name': 'anvil'},
    'forge': {'category': 'tools', 'name': 'forge'},
    'bellows': {'category': 'tools', 'name': 'bellows'},
    'needle': {'category': 'tools', 'name': 'needle'},
    'thread': {'category': 'tools', 'name': 'thread'},
    'scissors': {'category': 'tools', 'name': 'scissors'},

    # === Containers ===
    'chest': {'category': 'containers', 'name': 'chest'},
    'treasure chest': {'category': 'containers', 'name': 'treasure_chest'},
    'box': {'category': 'containers', 'name': 'box'},
    'crate': {'category': 'containers', 'name': 'crate'},
    'barrel': {'category': 'containers', 'name': 'barrel'},
    'bag': {'category': 'containers', 'name': 'bag'},
    'sack': {'category': 'containers', 'name': 'sack'},
    'pouch': {'category': 'containers', 'name': 'pouch'},
    'backpack': {'category': 'containers', 'name': 'backpack'},
    'basket': {'category': 'containers', 'name': 'basket'},
    'jar': {'category': 'containers', 'name': 'jar'},
    'pot': {'category': 'containers', 'name': 'pot'},
    'cauldron': {'category': 'containers', 'name': 'cauldron'},
    'urn': {'category': 'containers', 'name': 'urn'},
    'vase': {'category': 'containers', 'name': 'vase'},

    # === Light Sources ===
    'torch': {'category': 'light', 'name': 'torch'},
    'lantern': {'category': 'light', 'name': 'lantern'},
    'candle': {'category': 'light', 'name': 'candle'},
    'candles': {'category': 'light', 'name': 'candles'},
    'candlestick': {'category': 'light', 'name': 'candlestick'},
    'lamp': {'category': 'light', 'name': 'lamp'},
    'chandelier': {'category': 'light', 'name': 'chandelier'},
    'fireplace': {'category': 'light', 'name': 'fireplace'},
    'campfire': {'category': 'light', 'name': 'campfire'},
    'bonfire': {'category': 'light', 'name': 'bonfire'},

    # === Furniture ===
    'chair': {'category': 'furniture', 'name': 'chair'},
    'throne': {'category': 'furniture', 'name': 'throne'},
    'stool': {'category': 'furniture', 'name': 'stool'},
    'bench': {'category': 'furniture', 'name': 'bench'},
    'table': {'category': 'furniture', 'name': 'table'},
    'desk': {'category': 'furniture', 'name': 'desk'},
    'bed': {'category': 'furniture', 'name': 'bed'},
    'shelf': {'category': 'furniture', 'name': 'shelf'},
    'bookshelf': {'category': 'furniture', 'name': 'bookshelf'},
    'cabinet': {'category': 'furniture', 'name': 'cabinet'},
    'wardrobe': {'category': 'furniture', 'name': 'wardrobe'},
    'mirror': {'category': 'furniture', 'name': 'mirror'},
    'rug': {'category': 'furniture', 'name': 'rug'},
    'carpet': {'category': 'furniture', 'name': 'carpet'},
    'curtain': {'category': 'furniture', 'name': 'curtain'},
    'curtains': {'category': 'furniture', 'name': 'curtains'},
    'door': {'category': 'furniture', 'name': 'door'},
    'window': {'category': 'furniture', 'name': 'window'},

    # === Musical Instruments ===
    'lute': {'category': 'music', 'name': 'lute'},
    'harp': {'category': 'music', 'name': 'harp'},
    'lyre': {'category': 'music', 'name': 'lyre'},
    'flute': {'category': 'music', 'name': 'flute'},
    'drum': {'category': 'music', 'name': 'drum'},
    'drums': {'category': 'music', 'name': 'drums'},
    'violin': {'category': 'music', 'name': 'violin'},
    'guitar': {'category': 'music', 'name': 'guitar'},
    'piano': {'category': 'music', 'name': 'piano'},
    'horn': {'category': 'music', 'name': 'horn'},
    'trumpet': {'category': 'music', 'name': 'trumpet'},

    # === Nature Objects ===
    'flower': {'category': 'nature', 'name': 'flower'},
    'flowers': {'category': 'nature', 'name': 'flowers'},
    'rose': {'category': 'nature', 'name': 'rose'},
    'roses': {'category': 'nature', 'name': 'roses'},
    'lily': {'category': 'nature', 'name': 'lily'},
    'sunflower': {'category': 'nature', 'name': 'sunflower'},
    'tulip': {'category': 'nature', 'name': 'tulip'},
    'daisy': {'category': 'nature', 'name': 'daisy'},
    'leaf': {'category': 'nature', 'name': 'leaf'},
    'leaves': {'category': 'nature', 'name': 'leaves'},
    'branch': {'category': 'nature', 'name': 'branch'},
    'twig': {'category': 'nature', 'name': 'twig'},
    'acorn': {'category': 'nature', 'name': 'acorn'},
    'pinecone': {'category': 'nature', 'name': 'pinecone'},
    'mushroom': {'category': 'nature', 'name': 'mushroom'},
    'mushrooms': {'category': 'nature', 'name': 'mushrooms'},
    'stone': {'category': 'nature', 'name': 'stone'},
    'rock': {'category': 'nature', 'name': 'rock'},
    'boulder': {'category': 'nature', 'name': 'boulder'},
    'pebble': {'category': 'nature', 'name': 'pebble'},
    'shell': {'category': 'nature', 'name': 'shell'},
    'seashell': {'category': 'nature', 'name': 'seashell'},
    'feather': {'category': 'nature', 'name': 'feather'},
    'bone': {'category': 'nature', 'name': 'bone'},
    'skull': {'category': 'nature', 'name': 'skull'},

    # === Money & Treasure ===
    'coin': {'category': 'treasure', 'name': 'coin'},
    'coins': {'category': 'treasure', 'name': 'coins'},
    'gold': {'category': 'treasure', 'name': 'gold'},
    'silver': {'category': 'treasure', 'name': 'silver'},
    'treasure': {'category': 'treasure', 'name': 'treasure'},
    'money': {'category': 'treasure', 'name': 'money'},
    'key': {'category': 'treasure', 'name': 'key'},
    'keys': {'category': 'treasure', 'name': 'keys'},

    # === Misc Items ===
    'rope': {'category': 'misc', 'name': 'rope'},
    'chain': {'category': 'misc', 'name': 'chain'},
    'chains': {'category': 'misc', 'name': 'chains'},
    'clock': {'category': 'misc', 'name': 'clock'},
    'hourglass': {'category': 'misc', 'name': 'hourglass'},
    'compass': {'category': 'misc', 'name': 'compass'},
    'telescope': {'category': 'misc', 'name': 'telescope'},
    'spyglass': {'category': 'misc', 'name': 'spyglass'},
    'magnifying glass': {'category': 'misc', 'name': 'magnifying_glass'},
    'glasses': {'category': 'misc', 'name': 'glasses'},
    'monocle': {'category': 'misc', 'name': 'monocle'},
    'flag': {'category': 'misc', 'name': 'flag'},
    'banner': {'category': 'misc', 'name': 'banner'},
    'mask': {'category': 'misc', 'name': 'mask'},
    'cloak': {'category': 'misc', 'name': 'cloak'},
    'cape': {'category': 'misc', 'name': 'cape'},
    'hat': {'category': 'misc', 'name': 'hat'},
    'hood': {'category': 'misc', 'name': 'hood'},
    'umbrella': {'category': 'misc', 'name': 'umbrella'},
    'parasol': {'category': 'misc', 'name': 'parasol'},
    'fan': {'category': 'misc', 'name': 'fan'},
    'broom': {'category': 'misc', 'name': 'broom'},
    'mop': {'category': 'misc', 'name': 'mop'},
    'bucket': {'category': 'misc', 'name': 'bucket'},
    'pail': {'category': 'misc', 'name': 'pail'},
    'wheel': {'category': 'misc', 'name': 'wheel'},
    'cart': {'category': 'misc', 'name': 'cart'},
    'wagon': {'category': 'misc', 'name': 'wagon'},
    'boat': {'category': 'misc', 'name': 'boat'},
    'ship': {'category': 'misc', 'name': 'ship'},
    'anchor': {'category': 'misc', 'name': 'anchor'},

    # === Tech/Modern ===
    'phone': {'category': 'tech', 'name': 'phone'},
    'smartphone': {'category': 'tech', 'name': 'smartphone'},
    'laptop': {'category': 'tech', 'name': 'laptop'},
    'computer': {'category': 'tech', 'name': 'computer'},
    'tablet': {'category': 'tech', 'name': 'tablet'},
    'headphones': {'category': 'tech', 'name': 'headphones'},
    'camera': {'category': 'tech', 'name': 'camera'},
    'controller': {'category': 'tech', 'name': 'controller'},
    'gamepad': {'category': 'tech', 'name': 'gamepad'},
    'robot': {'category': 'tech', 'name': 'robot'},
    'drone': {'category': 'tech', 'name': 'drone'},
}


# =============================================================================
# ENVIRONMENT KEYWORDS - Settings, backgrounds
# =============================================================================

ENVIRONMENT_KEYWORDS = {
    # === Indoor Spaces ===
    'room': {'category': 'indoor', 'name': 'room'},
    'bedroom': {'category': 'indoor', 'name': 'bedroom'},
    'living room': {'category': 'indoor', 'name': 'living_room'},
    'kitchen': {'category': 'indoor', 'name': 'kitchen'},
    'bathroom': {'category': 'indoor', 'name': 'bathroom'},
    'library': {'category': 'indoor', 'name': 'library'},
    'study': {'category': 'indoor', 'name': 'study'},
    'office': {'category': 'indoor', 'name': 'office'},
    'classroom': {'category': 'indoor', 'name': 'classroom'},
    'school': {'category': 'indoor', 'name': 'school'},
    'laboratory': {'category': 'indoor', 'name': 'laboratory'},
    'lab': {'category': 'indoor', 'name': 'laboratory'},
    'workshop': {'category': 'indoor', 'name': 'workshop'},
    'forge': {'category': 'indoor', 'name': 'forge'},
    'smithy': {'category': 'indoor', 'name': 'smithy'},
    'kitchen': {'category': 'indoor', 'name': 'kitchen'},
    'dining room': {'category': 'indoor', 'name': 'dining_room'},
    'ballroom': {'category': 'indoor', 'name': 'ballroom'},
    'hall': {'category': 'indoor', 'name': 'hall'},
    'throne room': {'category': 'indoor', 'name': 'throne_room'},
    'dungeon': {'category': 'indoor', 'name': 'dungeon'},
    'prison': {'category': 'indoor', 'name': 'prison'},
    'jail': {'category': 'indoor', 'name': 'jail'},
    'cell': {'category': 'indoor', 'name': 'cell'},
    'basement': {'category': 'indoor', 'name': 'basement'},
    'attic': {'category': 'indoor', 'name': 'attic'},
    'cellar': {'category': 'indoor', 'name': 'cellar'},
    'wine cellar': {'category': 'indoor', 'name': 'wine_cellar'},
    'tower': {'category': 'indoor', 'name': 'tower'},
    'chapel': {'category': 'indoor', 'name': 'chapel'},
    'church': {'category': 'indoor', 'name': 'church'},
    'temple': {'category': 'indoor', 'name': 'temple'},
    'shrine': {'category': 'indoor', 'name': 'shrine'},
    'cathedral': {'category': 'indoor', 'name': 'cathedral'},
    'monastery': {'category': 'indoor', 'name': 'monastery'},
    'tavern': {'category': 'indoor', 'name': 'tavern'},
    'inn': {'category': 'indoor', 'name': 'inn'},
    'pub': {'category': 'indoor', 'name': 'pub'},
    'bar': {'category': 'indoor', 'name': 'bar'},
    'cafe': {'category': 'indoor', 'name': 'cafe'},
    'restaurant': {'category': 'indoor', 'name': 'restaurant'},
    'bakery': {'category': 'indoor', 'name': 'bakery'},
    'shop': {'category': 'indoor', 'name': 'shop'},
    'store': {'category': 'indoor', 'name': 'store'},
    'market': {'category': 'indoor', 'name': 'market'},
    'warehouse': {'category': 'indoor', 'name': 'warehouse'},
    'barn': {'category': 'indoor', 'name': 'barn'},
    'stable': {'category': 'indoor', 'name': 'stable'},
    'arena': {'category': 'indoor', 'name': 'arena'},
    'colosseum': {'category': 'indoor', 'name': 'colosseum'},
    'museum': {'category': 'indoor', 'name': 'museum'},
    'gallery': {'category': 'indoor', 'name': 'gallery'},
    'theater': {'category': 'indoor', 'name': 'theater'},
    'stage': {'category': 'indoor', 'name': 'stage'},
    'hospital': {'category': 'indoor', 'name': 'hospital'},
    'infirmary': {'category': 'indoor', 'name': 'infirmary'},

    # === Outdoor Nature ===
    'forest': {'category': 'nature', 'name': 'forest'},
    'woods': {'category': 'nature', 'name': 'forest'},
    'woodland': {'category': 'nature', 'name': 'forest'},
    'jungle': {'category': 'nature', 'name': 'jungle'},
    'rainforest': {'category': 'nature', 'name': 'rainforest'},
    'grove': {'category': 'nature', 'name': 'grove'},
    'glade': {'category': 'nature', 'name': 'glade'},
    'clearing': {'category': 'nature', 'name': 'clearing'},
    'meadow': {'category': 'nature', 'name': 'meadow'},
    'field': {'category': 'nature', 'name': 'field'},
    'plains': {'category': 'nature', 'name': 'plains'},
    'prairie': {'category': 'nature', 'name': 'prairie'},
    'grassland': {'category': 'nature', 'name': 'grassland'},
    'savanna': {'category': 'nature', 'name': 'savanna'},
    'hill': {'category': 'nature', 'name': 'hill'},
    'hills': {'category': 'nature', 'name': 'hills'},
    'mountain': {'category': 'nature', 'name': 'mountain'},
    'mountains': {'category': 'nature', 'name': 'mountains'},
    'peak': {'category': 'nature', 'name': 'peak'},
    'summit': {'category': 'nature', 'name': 'summit'},
    'cliff': {'category': 'nature', 'name': 'cliff'},
    'cliffs': {'category': 'nature', 'name': 'cliffs'},
    'canyon': {'category': 'nature', 'name': 'canyon'},
    'ravine': {'category': 'nature', 'name': 'ravine'},
    'valley': {'category': 'nature', 'name': 'valley'},
    'cave': {'category': 'nature', 'name': 'cave'},
    'cavern': {'category': 'nature', 'name': 'cavern'},
    'grotto': {'category': 'nature', 'name': 'grotto'},
    'river': {'category': 'nature', 'name': 'river'},
    'stream': {'category': 'nature', 'name': 'stream'},
    'brook': {'category': 'nature', 'name': 'brook'},
    'creek': {'category': 'nature', 'name': 'creek'},
    'waterfall': {'category': 'nature', 'name': 'waterfall'},
    'lake': {'category': 'nature', 'name': 'lake'},
    'pond': {'category': 'nature', 'name': 'pond'},
    'swamp': {'category': 'nature', 'name': 'swamp'},
    'marsh': {'category': 'nature', 'name': 'marsh'},
    'bog': {'category': 'nature', 'name': 'bog'},
    'wetland': {'category': 'nature', 'name': 'wetland'},
    'ocean': {'category': 'nature', 'name': 'ocean'},
    'sea': {'category': 'nature', 'name': 'sea'},
    'beach': {'category': 'nature', 'name': 'beach'},
    'shore': {'category': 'nature', 'name': 'shore'},
    'coast': {'category': 'nature', 'name': 'coast'},
    'island': {'category': 'nature', 'name': 'island'},
    'desert': {'category': 'nature', 'name': 'desert'},
    'dunes': {'category': 'nature', 'name': 'dunes'},
    'oasis': {'category': 'nature', 'name': 'oasis'},
    'tundra': {'category': 'nature', 'name': 'tundra'},
    'arctic': {'category': 'nature', 'name': 'arctic'},
    'ice': {'category': 'nature', 'name': 'ice'},
    'glacier': {'category': 'nature', 'name': 'glacier'},
    'volcano': {'category': 'nature', 'name': 'volcano'},

    # === Urban/Built ===
    'city': {'category': 'urban', 'name': 'city'},
    'town': {'category': 'urban', 'name': 'town'},
    'village': {'category': 'urban', 'name': 'village'},
    'street': {'category': 'urban', 'name': 'street'},
    'alley': {'category': 'urban', 'name': 'alley'},
    'plaza': {'category': 'urban', 'name': 'plaza'},
    'square': {'category': 'urban', 'name': 'square'},
    'courtyard': {'category': 'urban', 'name': 'courtyard'},
    'garden': {'category': 'urban', 'name': 'garden'},
    'park': {'category': 'urban', 'name': 'park'},
    'fountain': {'category': 'urban', 'name': 'fountain'},
    'bridge': {'category': 'urban', 'name': 'bridge'},
    'dock': {'category': 'urban', 'name': 'dock'},
    'docks': {'category': 'urban', 'name': 'docks'},
    'pier': {'category': 'urban', 'name': 'pier'},
    'harbor': {'category': 'urban', 'name': 'harbor'},
    'port': {'category': 'urban', 'name': 'port'},
    'marketplace': {'category': 'urban', 'name': 'marketplace'},
    'bazaar': {'category': 'urban', 'name': 'bazaar'},
    'castle': {'category': 'urban', 'name': 'castle'},
    'fortress': {'category': 'urban', 'name': 'fortress'},
    'palace': {'category': 'urban', 'name': 'palace'},
    'mansion': {'category': 'urban', 'name': 'mansion'},
    'manor': {'category': 'urban', 'name': 'manor'},
    'estate': {'category': 'urban', 'name': 'estate'},
    'cottage': {'category': 'urban', 'name': 'cottage'},
    'cabin': {'category': 'urban', 'name': 'cabin'},
    'hut': {'category': 'urban', 'name': 'hut'},
    'house': {'category': 'urban', 'name': 'house'},
    'home': {'category': 'urban', 'name': 'home'},
    'apartment': {'category': 'urban', 'name': 'apartment'},
    'ruins': {'category': 'urban', 'name': 'ruins'},
    'graveyard': {'category': 'urban', 'name': 'graveyard'},
    'cemetery': {'category': 'urban', 'name': 'cemetery'},
    'tomb': {'category': 'urban', 'name': 'tomb'},
    'crypt': {'category': 'urban', 'name': 'crypt'},
    'mausoleum': {'category': 'urban', 'name': 'mausoleum'},
    'pyramid': {'category': 'urban', 'name': 'pyramid'},
    'tower': {'category': 'urban', 'name': 'tower'},
    'lighthouse': {'category': 'urban', 'name': 'lighthouse'},
    'windmill': {'category': 'urban', 'name': 'windmill'},
    'mill': {'category': 'urban', 'name': 'mill'},
    'farm': {'category': 'urban', 'name': 'farm'},
    'ranch': {'category': 'urban', 'name': 'ranch'},

    # === Fantasy Locations ===
    'enchanted forest': {'category': 'fantasy', 'name': 'enchanted_forest'},
    'magical forest': {'category': 'fantasy', 'name': 'magical_forest'},
    'fairy realm': {'category': 'fantasy', 'name': 'fairy_realm'},
    'fae realm': {'category': 'fantasy', 'name': 'fae_realm'},
    'elfland': {'category': 'fantasy', 'name': 'elfland'},
    'elven city': {'category': 'fantasy', 'name': 'elven_city'},
    'dwarven halls': {'category': 'fantasy', 'name': 'dwarven_halls'},
    'dwarven mine': {'category': 'fantasy', 'name': 'dwarven_mine'},
    'dragon lair': {'category': 'fantasy', 'name': 'dragon_lair'},
    "dragon's lair": {'category': 'fantasy', 'name': 'dragon_lair'},
    'wizard tower': {'category': 'fantasy', 'name': 'wizard_tower'},
    "witch's hut": {'category': 'fantasy', 'name': 'witch_hut'},
    'witch hut': {'category': 'fantasy', 'name': 'witch_hut'},
    'haunted house': {'category': 'fantasy', 'name': 'haunted_house'},
    'haunted mansion': {'category': 'fantasy', 'name': 'haunted_mansion'},
    'crystal cave': {'category': 'fantasy', 'name': 'crystal_cave'},
    'floating island': {'category': 'fantasy', 'name': 'floating_island'},
    'cloud city': {'category': 'fantasy', 'name': 'cloud_city'},
    'underwater': {'category': 'fantasy', 'name': 'underwater'},
    'undersea': {'category': 'fantasy', 'name': 'undersea'},
    'atlantis': {'category': 'fantasy', 'name': 'atlantis'},
    'abyss': {'category': 'fantasy', 'name': 'abyss'},
    'void': {'category': 'fantasy', 'name': 'void'},
    'portal': {'category': 'fantasy', 'name': 'portal'},
    'dimension': {'category': 'fantasy', 'name': 'dimension'},
    'realm': {'category': 'fantasy', 'name': 'realm'},
    'heaven': {'category': 'fantasy', 'name': 'heaven'},
    'hell': {'category': 'fantasy', 'name': 'hell'},
    'underworld': {'category': 'fantasy', 'name': 'underworld'},
    'netherworld': {'category': 'fantasy', 'name': 'netherworld'},
    'limbo': {'category': 'fantasy', 'name': 'limbo'},
    'purgatory': {'category': 'fantasy', 'name': 'purgatory'},

    # === Sci-Fi Locations ===
    'spaceship': {'category': 'scifi', 'name': 'spaceship'},
    'spacecraft': {'category': 'scifi', 'name': 'spacecraft'},
    'space station': {'category': 'scifi', 'name': 'space_station'},
    'space': {'category': 'scifi', 'name': 'space'},
    'cosmos': {'category': 'scifi', 'name': 'cosmos'},
    'galaxy': {'category': 'scifi', 'name': 'galaxy'},
    'nebula': {'category': 'scifi', 'name': 'nebula'},
    'planet': {'category': 'scifi', 'name': 'planet'},
    'moon': {'category': 'scifi', 'name': 'moon'},
    'asteroid': {'category': 'scifi', 'name': 'asteroid'},
    'alien world': {'category': 'scifi', 'name': 'alien_world'},
    'cyberpunk city': {'category': 'scifi', 'name': 'cyberpunk_city'},
    'neon city': {'category': 'scifi', 'name': 'neon_city'},
    'futuristic city': {'category': 'scifi', 'name': 'futuristic_city'},
    'dystopia': {'category': 'scifi', 'name': 'dystopia'},
    'utopia': {'category': 'scifi', 'name': 'utopia'},
    'virtual reality': {'category': 'scifi', 'name': 'virtual_reality'},
    'cyberspace': {'category': 'scifi', 'name': 'cyberspace'},
    'matrix': {'category': 'scifi', 'name': 'matrix'},
    'holodeck': {'category': 'scifi', 'name': 'holodeck'},

    # === Time of Day / Weather as environment modifiers ===
    'daytime': {'category': 'time', 'name': 'day', 'modifier': True},
    'day': {'category': 'time', 'name': 'day', 'modifier': True},
    'morning': {'category': 'time', 'name': 'morning', 'modifier': True},
    'dawn': {'category': 'time', 'name': 'dawn', 'modifier': True},
    'sunrise': {'category': 'time', 'name': 'sunrise', 'modifier': True},
    'noon': {'category': 'time', 'name': 'noon', 'modifier': True},
    'afternoon': {'category': 'time', 'name': 'afternoon', 'modifier': True},
    'evening': {'category': 'time', 'name': 'evening', 'modifier': True},
    'dusk': {'category': 'time', 'name': 'dusk', 'modifier': True},
    'sunset': {'category': 'time', 'name': 'sunset', 'modifier': True},
    'twilight': {'category': 'time', 'name': 'twilight', 'modifier': True},
    'night': {'category': 'time', 'name': 'night', 'modifier': True},
    'nighttime': {'category': 'time', 'name': 'night', 'modifier': True},
    'midnight': {'category': 'time', 'name': 'midnight', 'modifier': True},
    'starry': {'category': 'time', 'name': 'starry', 'modifier': True},
    'moonlit': {'category': 'time', 'name': 'moonlit', 'modifier': True},

    'sunny': {'category': 'weather', 'name': 'sunny', 'modifier': True},
    'cloudy': {'category': 'weather', 'name': 'cloudy', 'modifier': True},
    'overcast': {'category': 'weather', 'name': 'overcast', 'modifier': True},
    'rainy': {'category': 'weather', 'name': 'rainy', 'modifier': True},
    'raining': {'category': 'weather', 'name': 'rainy', 'modifier': True},
    'stormy': {'category': 'weather', 'name': 'stormy', 'modifier': True},
    'storm': {'category': 'weather', 'name': 'storm', 'modifier': True},
    'thunder': {'category': 'weather', 'name': 'thunder', 'modifier': True},
    'lightning': {'category': 'weather', 'name': 'lightning', 'modifier': True},
    'snowy': {'category': 'weather', 'name': 'snowy', 'modifier': True},
    'snowing': {'category': 'weather', 'name': 'snowy', 'modifier': True},
    'winter': {'category': 'weather', 'name': 'winter', 'modifier': True},
    'spring': {'category': 'weather', 'name': 'spring', 'modifier': True},
    'summer': {'category': 'weather', 'name': 'summer', 'modifier': True},
    'autumn': {'category': 'weather', 'name': 'autumn', 'modifier': True},
    'fall': {'category': 'weather', 'name': 'fall', 'modifier': True},
    'foggy': {'category': 'weather', 'name': 'foggy', 'modifier': True},
    'misty': {'category': 'weather', 'name': 'misty', 'modifier': True},
    'windy': {'category': 'weather', 'name': 'windy', 'modifier': True},
}


# =============================================================================
# RELATIONSHIP KEYWORDS - How elements connect
# =============================================================================

RELATIONSHIP_KEYWORDS = {
    # === Holding/Carrying ===
    'holding': Relationship.HOLDING,
    'holds': Relationship.HOLDING,
    'hold': Relationship.HOLDING,
    'carrying': Relationship.CARRYING,
    'carries': Relationship.CARRYING,
    'carry': Relationship.CARRYING,
    'wielding': Relationship.WIELDING,
    'wields': Relationship.WIELDING,
    'wield': Relationship.WIELDING,
    'gripping': Relationship.HOLDING,
    'grips': Relationship.HOLDING,
    'grasping': Relationship.HOLDING,
    'grasps': Relationship.HOLDING,
    'clutching': Relationship.HOLDING,
    'clutches': Relationship.HOLDING,
    'brandishing': Relationship.WIELDING,
    'brandishes': Relationship.WIELDING,
    'with': Relationship.HOLDING,  # "girl with sword" implies holding

    # === Sitting ===
    'sitting on': Relationship.SITTING_ON,
    'sits on': Relationship.SITTING_ON,
    'sit on': Relationship.SITTING_ON,
    'seated on': Relationship.SITTING_ON,
    'perched on': Relationship.SITTING_ON,
    'resting on': Relationship.SITTING_ON,

    # === Standing ===
    'standing on': Relationship.STANDING_ON,
    'stands on': Relationship.STANDING_ON,
    'stand on': Relationship.STANDING_ON,
    'atop': Relationship.STANDING_ON,
    'on top of': Relationship.STANDING_ON,

    # === Leaning ===
    'leaning on': Relationship.LEANING_ON,
    'leans on': Relationship.LEANING_ON,
    'leaning against': Relationship.LEANING_ON,
    'leans against': Relationship.LEANING_ON,
    'propped against': Relationship.LEANING_ON,

    # === Lying ===
    'lying on': Relationship.LYING_ON,
    'lies on': Relationship.LYING_ON,
    'laying on': Relationship.LYING_ON,
    'lays on': Relationship.LYING_ON,
    'sprawled on': Relationship.LYING_ON,

    # === Next to ===
    'next to': Relationship.NEXT_TO,
    'beside': Relationship.NEXT_TO,
    'by': Relationship.NEXT_TO,
    'near': Relationship.NEXT_TO,
    'close to': Relationship.NEXT_TO,
    'alongside': Relationship.NEXT_TO,

    # === Behind/In front ===
    'behind': Relationship.BEHIND,
    'in front of': Relationship.IN_FRONT_OF,
    'before': Relationship.IN_FRONT_OF,
    'facing': Relationship.IN_FRONT_OF,

    # === Above/Below ===
    'above': Relationship.ABOVE,
    'over': Relationship.ABOVE,
    'below': Relationship.BELOW,
    'under': Relationship.BELOW,
    'beneath': Relationship.BELOW,
    'underneath': Relationship.BELOW,

    # === Inside/Outside ===
    # Note: 'in' alone causes false matches (e.g., "in a library")
    # Only match explicit inside/outside phrases
    'inside': Relationship.INSIDE,
    'inside of': Relationship.INSIDE,
    'within': Relationship.INSIDE,
    'trapped in': Relationship.INSIDE,
    'stuck in': Relationship.INSIDE,
    'outside': Relationship.OUTSIDE,
    'outside of': Relationship.OUTSIDE,
    'out of': Relationship.OUTSIDE,

    # === Looking ===
    'looking at': Relationship.LOOKING_AT,
    'looks at': Relationship.LOOKING_AT,
    'gazing at': Relationship.LOOKING_AT,
    'gazes at': Relationship.LOOKING_AT,
    'staring at': Relationship.LOOKING_AT,
    'stares at': Relationship.LOOKING_AT,
    'watching': Relationship.LOOKING_AT,
    'watches': Relationship.LOOKING_AT,

    # === Reaching ===
    'reaching for': Relationship.REACHING_FOR,
    'reaches for': Relationship.REACHING_FOR,
    'reaching toward': Relationship.REACHING_FOR,
    'reaching towards': Relationship.REACHING_FOR,

    # === Actions (imply holding/using) ===
    'reading': Relationship.HOLDING,
    'reads': Relationship.HOLDING,
    'read': Relationship.HOLDING,
    'writing': Relationship.HOLDING,
    'writes': Relationship.HOLDING,
    'drinking': Relationship.HOLDING,
    'drinks': Relationship.HOLDING,
    'eating': Relationship.HOLDING,
    'eats': Relationship.HOLDING,
    'playing': Relationship.HOLDING,
    'plays': Relationship.HOLDING,
    'using': Relationship.HOLDING,
    'uses': Relationship.HOLDING,
    'swinging': Relationship.WIELDING,
    'swings': Relationship.WIELDING,
    'throwing': Relationship.HOLDING,
    'throws': Relationship.HOLDING,
    'casting': Relationship.WIELDING,
    'casts': Relationship.WIELDING,
    'aiming': Relationship.WIELDING,
    'aims': Relationship.WIELDING,
    'shooting': Relationship.WIELDING,
    'shoots': Relationship.WIELDING,
    'drawing': Relationship.HOLDING,
    'draws': Relationship.HOLDING,
    'painting': Relationship.HOLDING,
    'paints': Relationship.HOLDING,
}


# =============================================================================
# POSITION KEYWORDS - Where in the frame
# =============================================================================

POSITION_KEYWORDS = {
    'center': Position.CENTER,
    'centered': Position.CENTER,
    'middle': Position.CENTER,
    'left': Position.LEFT,
    'on the left': Position.LEFT,
    'to the left': Position.LEFT,
    'right': Position.RIGHT,
    'on the right': Position.RIGHT,
    'to the right': Position.RIGHT,
    'top': Position.TOP,
    'at the top': Position.TOP,
    'upper': Position.TOP,
    'bottom': Position.BOTTOM,
    'at the bottom': Position.BOTTOM,
    'lower': Position.BOTTOM,
    'top left': Position.TOP_LEFT,
    'upper left': Position.TOP_LEFT,
    'top right': Position.TOP_RIGHT,
    'upper right': Position.TOP_RIGHT,
    'bottom left': Position.BOTTOM_LEFT,
    'lower left': Position.BOTTOM_LEFT,
    'bottom right': Position.BOTTOM_RIGHT,
    'lower right': Position.BOTTOM_RIGHT,
    'foreground': Position.FOREGROUND,
    'in the foreground': Position.FOREGROUND,
    'front': Position.FOREGROUND,
    'in front': Position.FOREGROUND,
    'midground': Position.MIDGROUND,
    'background': Position.BACKGROUND,
    'in the background': Position.BACKGROUND,
    'behind': Position.BACKGROUND,
    'distant': Position.BACKGROUND,
    'far': Position.BACKGROUND,
}


# =============================================================================
# CHARACTER TYPE KEYWORDS - Detect if describing a person/creature
# =============================================================================

CHARACTER_KEYWORDS = {
    # === Generic People ===
    'person': 'human',
    'people': 'human',
    'human': 'human',
    'man': 'human',
    'woman': 'human',
    'boy': 'human',
    'girl': 'human',
    'child': 'human',
    'kid': 'human',
    'baby': 'human',
    'teen': 'human',
    'teenager': 'human',
    'adult': 'human',
    'elder': 'human',
    'elderly': 'human',
    'old man': 'human',
    'old woman': 'human',
    'gentleman': 'human',
    'lady': 'human',
    'guy': 'human',
    'gal': 'human',
    'dude': 'human',
    'fellow': 'human',
    'figure': 'human',
    'someone': 'human',
    'somebody': 'human',
    'character': 'human',
    'protagonist': 'human',
    'hero': 'human',
    'heroine': 'human',
    'villain': 'human',
    'antagonist': 'human',

    # === Fantasy Races (also in natural_language.py but needed here) ===
    'elf': 'elf',
    'elven': 'elf',
    'elfin': 'elf',
    'elfish': 'elf',
    'dwarf': 'dwarf',
    'dwarven': 'dwarf',
    'halfling': 'halfling',
    'hobbit': 'halfling',
    'gnome': 'gnome',
    'orc': 'orc',
    'orcish': 'orc',
    'goblin': 'goblin',
    'troll': 'troll',
    'giant': 'giant',
    'ogre': 'ogre',
    'fairy': 'fairy',
    'fae': 'fairy',
    'pixie': 'fairy',
    'sprite': 'fairy',
    'nymph': 'fairy',
    'dryad': 'fairy',
    'mermaid': 'merfolk',
    'merman': 'merfolk',
    'merfolk': 'merfolk',
    'siren': 'merfolk',
    'angel': 'angel',
    'seraph': 'angel',
    'cherub': 'angel',
    'demon': 'demon',
    'devil': 'demon',
    'imp': 'demon',
    'succubus': 'demon',
    'incubus': 'demon',
    'vampire': 'vampire',
    'vampiric': 'vampire',
    'werewolf': 'werewolf',
    'lycanthrope': 'werewolf',
    'zombie': 'undead',
    'skeleton': 'undead',
    'ghost': 'undead',
    'specter': 'undead',
    'wraith': 'undead',
    'lich': 'undead',
    'undead': 'undead',
    'dragon': 'dragon',
    'dragonborn': 'dragonborn',
    'dragonkin': 'dragonborn',
    'tiefling': 'tiefling',
    'aasimar': 'aasimar',
    'genasi': 'genasi',
    'goliath': 'goliath',
    'tabaxi': 'beastfolk',
    'catfolk': 'beastfolk',
    'catgirl': 'beastfolk',
    'catboy': 'beastfolk',
    'neko': 'beastfolk',
    'kitsune': 'beastfolk',
    'foxgirl': 'beastfolk',
    'foxboy': 'beastfolk',
    'wolfgirl': 'beastfolk',
    'wolfboy': 'beastfolk',
    'bunnygirl': 'beastfolk',
    'bunnyboy': 'beastfolk',
    'kemono': 'beastfolk',
    'furry': 'beastfolk',
    'anthro': 'beastfolk',
    'centaur': 'centaur',
    'satyr': 'satyr',
    'faun': 'satyr',
    'minotaur': 'minotaur',
    'harpy': 'harpy',
    'lamia': 'lamia',
    'naga': 'naga',
    'medusa': 'medusa',
    'gorgon': 'gorgon',
    'golem': 'construct',
    'automaton': 'construct',
    'robot': 'robot',
    'android': 'android',
    'cyborg': 'cyborg',
    'alien': 'alien',
    'extraterrestrial': 'alien',
    'slime': 'slime',
    'elemental': 'elemental',

    # === Professions/Roles as character identifiers ===
    'knight': 'human',
    'warrior': 'human',
    'soldier': 'human',
    'guard': 'human',
    'paladin': 'human',
    'wizard': 'human',
    'mage': 'human',
    'sorcerer': 'human',
    'sorceress': 'human',
    'witch': 'human',
    'warlock': 'human',
    'necromancer': 'human',
    'cleric': 'human',
    'priest': 'human',
    'priestess': 'human',
    'monk': 'human',
    'nun': 'human',
    'druid': 'human',
    'shaman': 'human',
    'bard': 'human',
    'rogue': 'human',
    'thief': 'human',
    'assassin': 'human',
    'ninja': 'human',
    'samurai': 'human',
    'pirate': 'human',
    'captain': 'human',
    'sailor': 'human',
    'merchant': 'human',
    'trader': 'human',
    'blacksmith': 'human',
    'smith': 'human',
    'farmer': 'human',
    'hunter': 'human',
    'archer': 'human',
    'ranger': 'human',
    'healer': 'human',
    'doctor': 'human',
    'nurse': 'human',
    'scholar': 'human',
    'scribe': 'human',
    'librarian': 'human',
    'student': 'human',
    'teacher': 'human',
    'professor': 'human',
    'king': 'human',
    'queen': 'human',
    'prince': 'human',
    'princess': 'human',
    'noble': 'human',
    'lord': 'human',
    'lady': 'human',
    'duke': 'human',
    'duchess': 'human',
    'emperor': 'human',
    'empress': 'human',
    'peasant': 'human',
    'beggar': 'human',
    'servant': 'human',
    'maid': 'human',
    'butler': 'human',
    'chef': 'human',
    'cook': 'human',
    'baker': 'human',
    'bartender': 'human',
    'innkeeper': 'human',
    'adventurer': 'human',
    'explorer': 'human',
    'traveler': 'human',
    'wanderer': 'human',
    'hermit': 'human',
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _word_boundary_match(keyword: str, text: str) -> bool:
    """Check if keyword exists as a whole word/phrase in text."""
    # Escape special regex characters in keyword
    escaped = re.escape(keyword)
    # Match with word boundaries
    pattern = r'\b' + escaped + r'\b'
    return bool(re.search(pattern, text))


def _find_all_matches(keyword: str, text: str) -> List[Tuple[int, int]]:
    """Find all (start, end) positions of keyword in text."""
    escaped = re.escape(keyword)
    pattern = r'\b' + escaped + r'\b'
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


# Items that are worn/carried as accessories, not standalone objects
ACCESSORY_OBJECTS = {'glasses', 'monocle', 'hat', 'hood', 'cloak', 'cape', 'mask'}


# =============================================================================
# SCENE PARSER
# =============================================================================

def parse_scene(description: str) -> Scene:
    """
    Parse a natural language description into a Scene structure.

    Examples:
        "a red potion bottle" → Scene with single object
        "happy elf girl with glasses" → Scene with single character
        "knight holding a sword in a dark castle" → Full scene
    """
    desc_lower = description.lower().strip()
    scene = Scene()

    # Track what we've found
    found_characters = []
    found_objects = []
    found_environment = None
    found_relationships = []
    env_modifiers = []

    # Track matched spans to avoid duplicates
    matched_spans = set()
    matched_object_names = set()

    def is_overlapping(start: int, end: int) -> bool:
        """Check if span overlaps with already matched spans."""
        for ms, me in matched_spans:
            if start < me and end > ms:
                return True
        return False

    # Sort keywords by length (longer first) to match multi-word phrases
    sorted_char_keywords = sorted(CHARACTER_KEYWORDS.keys(), key=len, reverse=True)
    sorted_obj_keywords = sorted(OBJECT_KEYWORDS.keys(), key=len, reverse=True)
    sorted_env_keywords = sorted(ENVIRONMENT_KEYWORDS.keys(), key=len, reverse=True)
    sorted_rel_keywords = sorted(RELATIONSHIP_KEYWORDS.keys(), key=len, reverse=True)

    # 1. Find characters first (to determine if accessories should be skipped)
    has_character = False
    for keyword in sorted_char_keywords:
        if _word_boundary_match(keyword, desc_lower):
            matches = _find_all_matches(keyword, desc_lower)
            if matches and not is_overlapping(matches[0][0], matches[0][1]):
                race = CHARACTER_KEYWORDS[keyword]
                char = Character(
                    name=keyword,
                    attributes={'race': race}
                )
                found_characters.append(char)
                matched_spans.add(matches[0])
                has_character = True
                # Only match first character mention for now
                break

    # 2. Find environment
    for keyword in sorted_env_keywords:
        if _word_boundary_match(keyword, desc_lower):
            matches = _find_all_matches(keyword, desc_lower)
            if matches and not is_overlapping(matches[0][0], matches[0][1]):
                env_data = ENVIRONMENT_KEYWORDS[keyword]
                if env_data.get('modifier'):
                    env_modifiers.append(env_data)
                elif found_environment is None:
                    found_environment = Environment(
                        name=env_data['name'],
                        attributes={'category': env_data['category']}
                    )
                    matched_spans.add(matches[0])

    # 3. Find objects (skip accessories if character present)
    for keyword in sorted_obj_keywords:
        if _word_boundary_match(keyword, desc_lower):
            # Skip accessory items when describing a character
            if has_character and keyword in ACCESSORY_OBJECTS:
                continue

            matches = _find_all_matches(keyword, desc_lower)
            for start, end in matches:
                if not is_overlapping(start, end):
                    obj_data = OBJECT_KEYWORDS[keyword]
                    # Skip if we already have an object with this name
                    if obj_data['name'] in matched_object_names:
                        continue

                    obj = Object(
                        name=obj_data['name'],
                        attributes={
                            'category': obj_data['category'],
                            **{k: v for k, v in obj_data.items() if k not in ('name', 'category')}
                        }
                    )
                    found_objects.append(obj)
                    matched_spans.add((start, end))
                    matched_object_names.add(obj_data['name'])
                    break  # Only one instance per object type

    # 4. Find relationships
    for keyword in sorted_rel_keywords:
        if _word_boundary_match(keyword, desc_lower):
            rel = RELATIONSHIP_KEYWORDS[keyword]
            if found_characters and found_objects:
                # Link first character to first object
                link = RelationshipLink(
                    subject=found_characters[0],
                    relationship=rel,
                    target=found_objects[0]
                )
                found_relationships.append(link)
                break

    # 5. Assemble scene
    scene.subjects = found_characters
    scene.objects = found_objects
    scene.environment = found_environment
    scene.relationships = found_relationships

    # Add modifiers to atmosphere
    if env_modifiers:
        scene.atmosphere['time'] = [m['name'] for m in env_modifiers if m['category'] == 'time']
        scene.atmosphere['weather'] = [m['name'] for m in env_modifiers if m['category'] == 'weather']

    # Determine scene type
    if found_characters and (found_objects or found_environment):
        scene.type = 'scene'
    elif found_characters:
        scene.type = 'character'
    elif found_objects:
        scene.type = 'object'
    elif found_environment:
        scene.type = 'scene'
    else:
        scene.type = 'unknown'

    return scene


def describe_scene(scene: Scene) -> str:
    """Generate a human-readable summary of a parsed scene."""
    parts = []

    parts.append(f"Type: {scene.type}")

    if scene.subjects:
        chars = ', '.join(s.name for s in scene.subjects)
        parts.append(f"Characters: {chars}")

    if scene.objects:
        objs = ', '.join(o.name for o in scene.objects)
        parts.append(f"Objects: {objs}")

    if scene.environment:
        parts.append(f"Environment: {scene.environment.name}")

    if scene.relationships:
        rels = ', '.join(f"{r.subject.name} {r.relationship.value} {r.target.name}"
                        for r in scene.relationships)
        parts.append(f"Relationships: {rels}")

    if scene.atmosphere:
        atmo = ', '.join(f"{k}: {v}" for k, v in scene.atmosphere.items() if v)
        if atmo:
            parts.append(f"Atmosphere: {atmo}")

    return '\n'.join(parts)


# =============================================================================
# INTEGRATION WITH CHARACTER PARSER
# =============================================================================

def parse_full_description(description: str) -> dict:
    """
    Parse any description, routing to appropriate parser.

    Returns a unified structure that can handle:
    - Individual objects
    - Individual characters (uses natural_language.py)
    - Full scenes with multiple elements
    """
    # First, parse as a scene to understand structure
    scene = parse_scene(description)

    result = {
        'type': scene.type,
        'scene': scene,
        'render_instructions': []
    }

    # If it's a character or scene with characters, parse character details
    if scene.type in ('character', 'scene') and scene.subjects:
        # Import the character parser
        try:
            from recipes.natural_language import parse_description as parse_character
            char_spec = parse_character(description)
            result['character_spec'] = char_spec
        except ImportError:
            result['character_spec'] = None

    # Build render instructions (layer order)
    instructions = []

    # Background first
    if scene.environment:
        instructions.append({
            'layer': 0,
            'type': 'environment',
            'element': scene.environment.name,
            'attributes': scene.environment.attributes
        })

    # Objects that are background/furniture
    for obj in scene.objects:
        if obj.attributes.get('category') in ('furniture', 'containers', 'light'):
            instructions.append({
                'layer': 10,
                'type': 'object',
                'element': obj.name,
                'attributes': obj.attributes
            })

    # Characters
    for i, char in enumerate(scene.subjects):
        instructions.append({
            'layer': 50 + i,
            'type': 'character',
            'element': char.name,
            'attributes': char.attributes
        })

    # Held/foreground objects
    for obj in scene.objects:
        if obj.attributes.get('category') not in ('furniture', 'containers', 'light'):
            # Check if being held
            is_held = any(r.target == obj and r.relationship in
                         (Relationship.HOLDING, Relationship.WIELDING, Relationship.CARRYING)
                         for r in scene.relationships)
            instructions.append({
                'layer': 60 if is_held else 40,
                'type': 'object',
                'element': obj.name,
                'attributes': obj.attributes,
                'held': is_held
            })

    result['render_instructions'] = sorted(instructions, key=lambda x: x['layer'])

    return result
