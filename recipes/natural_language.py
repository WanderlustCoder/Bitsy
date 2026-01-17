"""
Natural Language Interface - Parse descriptions into character specs.

Converts natural language like:
  "a happy girl with blonde hair and round glasses"

Into a structured spec that the loader can render.
"""

import re
from typing import Dict, Any, Optional, List, Tuple


# =============================================================================
# EXPANDED KEYWORD MAPPINGS
# =============================================================================

# Hair color keywords → spec values
HAIR_COLOR_KEYWORDS = {
    # === Browns ===
    'brown': 'brown',
    'brunette': 'brown',
    'chestnut': 'brown',
    'chocolate': 'brown',
    'cocoa': 'brown',
    'coffee': 'brown',
    'mocha': 'brown',
    'hazel': 'brown',
    'tawny': 'brown',
    'umber': 'brown',
    'sepia': 'brown',
    'walnut': 'brown',
    'cinnamon': 'brown',
    'caramel': 'brown',
    'bronze': 'brown',
    'tan hair': 'brown',
    'light brown': 'brown',
    'medium brown': 'brown',

    'dark brown': 'dark_brown',
    'deep brown': 'dark_brown',
    'espresso': 'dark_brown',
    'mahogany': 'dark_brown',

    # === Black ===
    'black': 'black',
    'dark': 'black',
    'raven': 'black',
    'ebony': 'black',
    'jet black': 'black',
    'ink black': 'black',
    'midnight': 'black',
    'onyx': 'black',
    'obsidian': 'black',
    'charcoal': 'black',
    'sable': 'black',
    'coal': 'black',
    'noir': 'black',

    # === Blonde ===
    'blonde': 'blonde',
    'blond': 'blonde',
    'golden': 'blonde',
    'gold': 'blonde',
    'yellow': 'blonde',
    'platinum': 'blonde',
    'sandy': 'blonde',
    'honey': 'blonde',
    'wheat': 'blonde',
    'flaxen': 'blonde',
    'champagne': 'blonde',
    'cream': 'blonde',
    'ivory': 'blonde',
    'pale blonde': 'blonde',
    'light blonde': 'blonde',
    'ash blonde': 'blonde',
    'dirty blonde': 'blonde',
    'strawberry blonde': 'blonde',
    'butterscotch': 'blonde',
    'cornsilk': 'blonde',
    'fair hair': 'blonde',
    'light hair': 'blonde',
    'sunny': 'blonde',

    # === Red/Auburn ===
    'red': 'auburn',
    'auburn': 'auburn',
    'ginger': 'auburn',
    'copper': 'auburn',
    'redhead': 'auburn',
    'orange': 'auburn',
    'rust': 'auburn',
    'crimson': 'auburn',
    'scarlet': 'auburn',
    'vermillion': 'auburn',
    'burgundy': 'auburn',
    'maroon': 'auburn',
    'wine': 'auburn',
    'cherry': 'auburn',
    'flame': 'auburn',
    'fire': 'auburn',
    'fiery': 'auburn',
    'carrot': 'auburn',
    'russet': 'auburn',
    'terracotta': 'auburn',
    'henna': 'auburn',
    'titian': 'auburn',
    'rufous': 'auburn',

    # === Gray/White/Silver ===
    'gray': 'blonde',  # maps to light (closest to gray/white)
    'grey': 'blonde',
    'silver': 'blonde',  # light/platinum for fantasy characters
    'white': 'blonde',  # maps to light blonde
    'platinum white': 'blonde',
    'snow white': 'blonde',
    'ashen': 'black',
    'salt and pepper': 'black',

    # === Fantasy Colors (map to closest) ===
    'pink': 'auburn',  # reddish
    'rose': 'auburn',
    'magenta': 'auburn',
    'purple': 'black',  # dark with color tint
    'violet': 'black',
    'lavender': 'blonde',  # light
    'blue': 'black',
    'navy': 'black',
    'teal': 'black',
    'cyan': 'blonde',
    'aqua': 'blonde',
    'green': 'black',
    'mint': 'blonde',
    'pastel': 'blonde',
}

# Hair style keywords → spec values
HAIR_STYLE_KEYWORDS = {
    # === Bun ===
    'bun': 'bun',
    'hair bun': 'bun',
    'updo': 'bun',
    'tied up': 'bun',
    'top knot': 'bun',
    'topknot': 'bun',
    'chignon': 'bun',
    'ballet bun': 'bun',
    'messy bun': 'bun',
    'high bun': 'bun',
    'low bun': 'bun',

    # === Long ===
    'long': 'long',
    'long hair': 'long',
    'flowing': 'long',
    'lengthy': 'long',
    'waist-length': 'long',
    'hip-length': 'long',
    'floor-length': 'long',
    'rapunzel': 'long',
    'loose': 'long',
    'down': 'long',
    'let down': 'long',
    'untied': 'long',

    # === Short ===
    'short': 'short',
    'short hair': 'short',
    'pixie': 'short',
    'pixie cut': 'short',
    'bob': 'short',
    'cropped': 'short',
    'crew cut': 'short',
    'buzz': 'short',
    'buzzed': 'short',
    'shaved': 'short',
    'undercut': 'short',
    'boyish': 'short',
    'tomboyish': 'short',
    'chin-length': 'short',
    'ear-length': 'short',

    # === Ponytail ===
    'ponytail': 'ponytail',
    'pony tail': 'ponytail',
    'pony': 'ponytail',
    'tied back': 'ponytail',
    'pulled back': 'ponytail',
    'high ponytail': 'ponytail',
    'low ponytail': 'ponytail',
    'side ponytail': 'ponytail',
    'pigtails': 'ponytail',
    'twin tails': 'ponytail',
    'twintails': 'ponytail',
    'double ponytail': 'ponytail',

    # === Texture descriptors (default to current style) ===
    'curly': 'bun',
    'wavy': 'long',
    'straight': 'long',
    'frizzy': 'bun',
    'messy': 'bun',
    'neat': 'bun',
    'tidy': 'bun',
    'wild': 'long',
    'spiky': 'short',
    'spiked': 'short',
    'slicked': 'short',
    'braided': 'bun',
    'braids': 'bun',
}

# Eye color keywords → spec values
EYE_COLOR_KEYWORDS = {
    # === Brown ===
    'brown eyes': 'brown',
    'brown': 'brown',
    'dark eyes': 'brown',
    'hazel': 'brown',
    'amber': 'brown',
    'copper eyes': 'brown',
    'chocolate eyes': 'brown',
    'coffee eyes': 'brown',
    'chestnut eyes': 'brown',
    'mahogany eyes': 'brown',
    'honey eyes': 'brown',
    'caramel eyes': 'brown',
    'tawny eyes': 'brown',
    'golden brown': 'brown',
    'warm eyes': 'brown',
    'earthy': 'brown',

    # === Blue ===
    'blue': 'blue',
    'blue eyes': 'blue',
    'sky blue': 'blue',
    'ocean': 'blue',
    'ocean eyes': 'blue',
    'sapphire': 'blue',
    'cerulean': 'blue',
    'azure': 'blue',
    'cobalt': 'blue',
    'navy': 'blue',
    'ice blue': 'blue',
    'steel blue': 'blue',
    'bright blue': 'blue',
    'light blue': 'blue',
    'deep blue': 'blue',
    'aquamarine': 'blue',
    'teal': 'blue',
    'turquoise': 'blue',
    'cyan': 'blue',
    'aqua': 'blue',
    'sea': 'blue',
    'crystal': 'blue',
    'cornflower': 'blue',
    'periwinkle': 'blue',

    # === Green ===
    'green': 'green',
    'green eyes': 'green',
    'emerald': 'green',
    'jade': 'green',
    'forest': 'green',
    'olive': 'green',
    'moss': 'green',
    'sage': 'green',
    'mint': 'green',
    'seafoam': 'green',
    'lime': 'green',
    'chartreuse': 'green',
    'viridian': 'green',
    'hunter green': 'green',
    'bright green': 'green',
    'leaf': 'green',
    'spring green': 'green',

    # === Gray ===
    'gray': 'gray',
    'grey': 'gray',
    'gray eyes': 'gray',
    'grey eyes': 'gray',
    'silver': 'gray',
    'silver eyes': 'gray',
    'steel': 'gray',
    'slate': 'gray',
    'ash': 'gray',
    'ashen': 'gray',
    'pewter': 'gray',
    'charcoal eyes': 'gray',
    'smoke': 'gray',
    'smoky': 'gray',
    'storm': 'gray',
    'stormy': 'gray',
    'cloudy': 'gray',
    'pale eyes': 'gray',
    'light eyes': 'gray',
    'cold eyes': 'gray',

    # === Fantasy/Unusual ===
    'red eyes': 'brown',  # closest match
    'crimson eyes': 'brown',
    'ruby': 'brown',
    'scarlet eyes': 'brown',
    'violet': 'blue',
    'purple': 'blue',
    'lavender': 'blue',
    'amethyst': 'blue',
    'pink eyes': 'brown',
    'gold eyes': 'brown',
    'golden eyes': 'brown',
    'yellow eyes': 'brown',
    'orange eyes': 'brown',
    'heterochromia': 'blue',  # default to interesting color
    'mismatched': 'blue',
    'black eyes': 'brown',
    'dark': 'brown',
    'white eyes': 'gray',
    'blind': 'gray',
}

# Expression keywords → (eye_expression, mouth_expression)
EXPRESSION_KEYWORDS = {
    # === Happy/Positive ===
    'happy': ('happy', 'happy'),
    'smiling': ('happy', 'happy'),
    'smile': ('happy', 'happy'),
    'cheerful': ('happy', 'happy'),
    'joyful': ('happy', 'happy'),
    'joyous': ('happy', 'happy'),
    'grinning': ('happy', 'happy'),
    'grin': ('happy', 'happy'),
    'beaming': ('happy', 'happy'),
    'radiant': ('happy', 'happy'),
    'gleeful': ('happy', 'happy'),
    'delighted': ('happy', 'happy'),
    'pleased': ('happy', 'happy'),
    'content': ('happy', 'happy'),
    'satisfied': ('happy', 'happy'),
    'elated': ('happy', 'happy'),
    'ecstatic': ('happy', 'happy'),
    'overjoyed': ('happy', 'happy'),
    'thrilled': ('happy', 'happy'),
    'excited': ('happy', 'happy'),
    'enthusiastic': ('happy', 'happy'),
    'optimistic': ('happy', 'happy'),
    'positive': ('happy', 'happy'),
    'upbeat': ('happy', 'happy'),
    'chipper': ('happy', 'happy'),
    'bubbly': ('happy', 'happy'),
    'perky': ('happy', 'happy'),
    'lively': ('happy', 'happy'),
    'vibrant': ('happy', 'happy'),
    'warm': ('happy', 'happy'),
    'friendly': ('happy', 'happy'),
    'welcoming': ('happy', 'happy'),
    'kind': ('happy', 'happy'),
    'gentle': ('happy', 'happy'),
    'sweet': ('happy', 'happy'),
    'lovely': ('happy', 'happy'),
    'adorable': ('happy', 'happy'),
    'cute': ('happy', 'happy'),
    'laughing': ('happy', 'happy'),
    'giggling': ('happy', 'happy'),
    'amused': ('happy', 'happy'),
    'entertained': ('happy', 'happy'),

    # === Sad/Negative ===
    'sad': ('sad', 'sad'),
    'unhappy': ('sad', 'sad'),
    'frowning': ('sad', 'sad'),
    'frown': ('sad', 'sad'),
    'melancholy': ('sad', 'sad'),
    'melancholic': ('sad', 'sad'),
    'upset': ('sad', 'sad'),
    'disappointed': ('sad', 'sad'),
    'depressed': ('sad', 'sad'),
    'dejected': ('sad', 'sad'),
    'downcast': ('sad', 'sad'),
    'down': ('sad', 'sad'),
    'blue': ('sad', 'sad'),
    'gloomy': ('sad', 'sad'),
    'glum': ('sad', 'sad'),
    'somber': ('sad', 'sad'),
    'morose': ('sad', 'sad'),
    'mournful': ('sad', 'sad'),
    'sorrowful': ('sad', 'sad'),
    'heartbroken': ('sad', 'sad'),
    'hurt': ('sad', 'sad'),
    'pained': ('sad', 'sad'),
    'distressed': ('sad', 'sad'),
    'troubled': ('sad', 'sad'),
    'worried': ('sad', 'sad'),
    'anxious': ('sad', 'sad'),
    'nervous': ('sad', 'sad'),
    'uneasy': ('sad', 'sad'),
    'tearful': ('sad', 'sad'),
    'crying': ('sad', 'sad'),
    'weeping': ('sad', 'sad'),
    'sobbing': ('sad', 'sad'),
    'lonely': ('sad', 'sad'),
    'forlorn': ('sad', 'sad'),
    'wistful': ('sad', 'sad'),
    'nostalgic': ('sad', 'sad'),
    'regretful': ('sad', 'sad'),
    'remorseful': ('sad', 'sad'),
    'guilty': ('sad', 'sad'),
    'ashamed': ('sad', 'sad'),
    'embarrassed': ('sad', 'sad'),
    'shy': ('sad', 'neutral'),
    'timid': ('sad', 'neutral'),
    'meek': ('sad', 'neutral'),

    # === Surprised ===
    'surprised': ('surprised', 'surprised'),
    'shocked': ('surprised', 'surprised'),
    'amazed': ('surprised', 'surprised'),
    'astonished': ('surprised', 'surprised'),
    'astounded': ('surprised', 'surprised'),
    'stunned': ('surprised', 'surprised'),
    'startled': ('surprised', 'surprised'),
    'bewildered': ('surprised', 'surprised'),
    'dumbfounded': ('surprised', 'surprised'),
    'flabbergasted': ('surprised', 'surprised'),
    'speechless': ('surprised', 'surprised'),
    'wide-eyed': ('surprised', 'surprised'),
    'jaw dropped': ('surprised', 'surprised'),
    'awestruck': ('surprised', 'surprised'),
    'awed': ('surprised', 'surprised'),
    'wonder': ('surprised', 'surprised'),
    'wondering': ('surprised', 'surprised'),
    'curious': ('surprised', 'neutral'),
    'intrigued': ('surprised', 'neutral'),
    'fascinated': ('surprised', 'neutral'),
    'interested': ('surprised', 'neutral'),
    'confused': ('surprised', 'sad'),
    'puzzled': ('surprised', 'neutral'),
    'perplexed': ('surprised', 'neutral'),
    'baffled': ('surprised', 'neutral'),

    # === Neutral/Calm ===
    'neutral': ('neutral', 'neutral'),
    'calm': ('neutral', 'neutral'),
    'relaxed': ('neutral', 'neutral'),
    'serene': ('neutral', 'neutral'),
    'peaceful': ('neutral', 'neutral'),
    'tranquil': ('neutral', 'neutral'),
    'composed': ('neutral', 'neutral'),
    'collected': ('neutral', 'neutral'),
    'stoic': ('neutral', 'neutral'),
    'expressionless': ('neutral', 'neutral'),
    'blank': ('neutral', 'neutral'),
    'deadpan': ('neutral', 'neutral'),
    'poker face': ('neutral', 'neutral'),
    'impassive': ('neutral', 'neutral'),
    'indifferent': ('neutral', 'neutral'),
    'apathetic': ('neutral', 'neutral'),
    'bored': ('neutral', 'neutral'),
    'uninterested': ('neutral', 'neutral'),
    'tired': ('neutral', 'neutral'),
    'sleepy': ('neutral', 'neutral'),
    'drowsy': ('neutral', 'neutral'),
    'exhausted': ('neutral', 'sad'),
    'weary': ('neutral', 'sad'),
    'pensive': ('neutral', 'neutral'),
    'thoughtful': ('neutral', 'neutral'),
    'contemplative': ('neutral', 'neutral'),
    'reflective': ('neutral', 'neutral'),
    'meditative': ('neutral', 'neutral'),
    'focused': ('neutral', 'neutral'),
    'concentrated': ('neutral', 'neutral'),
    'determined': ('neutral', 'neutral'),
    'resolute': ('neutral', 'neutral'),
    'serious': ('neutral', 'neutral'),
    'stern': ('neutral', 'neutral'),
    'solemn': ('neutral', 'neutral'),
    'grave': ('neutral', 'neutral'),
    'professional': ('neutral', 'neutral'),
    'formal': ('neutral', 'neutral'),
    'dignified': ('neutral', 'neutral'),
    'regal': ('neutral', 'neutral'),
    'noble': ('neutral', 'neutral'),
    'elegant': ('neutral', 'neutral'),
    'sophisticated': ('neutral', 'neutral'),
    'refined': ('neutral', 'neutral'),
    'poised': ('neutral', 'neutral'),
    'graceful': ('neutral', 'neutral'),
    'mysterious': ('neutral', 'neutral'),
    'enigmatic': ('neutral', 'neutral'),
    'cryptic': ('neutral', 'neutral'),
    'aloof': ('neutral', 'neutral'),
    'distant': ('neutral', 'neutral'),
    'detached': ('neutral', 'neutral'),
    'reserved': ('neutral', 'neutral'),
    'quiet': ('neutral', 'neutral'),
    'silent': ('neutral', 'neutral'),

    # === Playful/Mischievous (cat smile) ===
    'cat smile': ('neutral', 'cat_smile'),
    'playful': ('neutral', 'cat_smile'),
    'mischievous': ('neutral', 'cat_smile'),
    'cheeky': ('neutral', 'cat_smile'),
    'impish': ('neutral', 'cat_smile'),
    'teasing': ('neutral', 'cat_smile'),
    'tease': ('neutral', 'cat_smile'),
    'sly': ('neutral', 'cat_smile'),
    'cunning': ('neutral', 'cat_smile'),
    'sneaky': ('neutral', 'cat_smile'),
    'devious': ('neutral', 'cat_smile'),
    'wily': ('neutral', 'cat_smile'),
    'crafty': ('neutral', 'cat_smile'),
    'scheming': ('neutral', 'cat_smile'),
    'plotting': ('neutral', 'cat_smile'),
    'smirk': ('neutral', 'cat_smile'),
    'smirking': ('neutral', 'cat_smile'),
    'coy': ('neutral', 'cat_smile'),
    'flirty': ('neutral', 'cat_smile'),
    'flirtatious': ('neutral', 'cat_smile'),
    'seductive': ('neutral', 'cat_smile'),
    'suggestive': ('neutral', 'cat_smile'),
    'knowing': ('neutral', 'cat_smile'),
    'sassy': ('neutral', 'cat_smile'),
    'confident': ('neutral', 'cat_smile'),
    'cocky': ('neutral', 'cat_smile'),
    'smug': ('neutral', 'cat_smile'),
    'self-satisfied': ('neutral', 'cat_smile'),
    'proud': ('neutral', 'cat_smile'),
    'triumphant': ('neutral', 'cat_smile'),
    'victorious': ('neutral', 'cat_smile'),
    'catlike': ('neutral', 'cat_smile'),
    'feline': ('neutral', 'cat_smile'),
    'kitty': ('neutral', 'cat_smile'),
    'neko': ('neutral', 'cat_smile'),
    'uwu': ('neutral', 'cat_smile'),
    'anime': ('neutral', 'cat_smile'),
    'kawaii': ('happy', 'cat_smile'),

    # === Angry (map to neutral for now, but distinct detection) ===
    'angry': ('neutral', 'neutral'),
    'mad': ('neutral', 'neutral'),
    'furious': ('neutral', 'neutral'),
    'enraged': ('neutral', 'neutral'),
    'livid': ('neutral', 'neutral'),
    'irate': ('neutral', 'neutral'),
    'outraged': ('neutral', 'neutral'),
    'annoyed': ('neutral', 'neutral'),
    'irritated': ('neutral', 'neutral'),
    'frustrated': ('neutral', 'neutral'),
    'exasperated': ('neutral', 'neutral'),
    'grumpy': ('neutral', 'neutral'),
    'cranky': ('neutral', 'neutral'),
    'moody': ('neutral', 'neutral'),
    'sulky': ('neutral', 'neutral'),
    'sullen': ('neutral', 'neutral'),
    'resentful': ('neutral', 'neutral'),
    'bitter': ('neutral', 'neutral'),
    'hostile': ('neutral', 'neutral'),
    'aggressive': ('neutral', 'neutral'),
    'fierce': ('neutral', 'neutral'),
    'intense': ('neutral', 'neutral'),
    'intimidating': ('neutral', 'neutral'),
    'menacing': ('neutral', 'neutral'),
    'threatening': ('neutral', 'neutral'),
    'scary': ('neutral', 'neutral'),
    'terrifying': ('neutral', 'neutral'),
    'evil': ('neutral', 'cat_smile'),
    'villainous': ('neutral', 'cat_smile'),
    'wicked': ('neutral', 'cat_smile'),
    'sinister': ('neutral', 'cat_smile'),
    'dark': ('neutral', 'neutral'),
    'brooding': ('neutral', 'neutral'),
}

# Glasses keywords
GLASSES_KEYWORDS = {
    # === General ===
    'glasses': 'round',
    'spectacles': 'round',
    'specs': 'round',
    'eyeglasses': 'round',
    'eyewear': 'round',
    'frames': 'round',
    'lenses': 'round',
    'corrective lenses': 'round',
    'reading glasses': 'rectangular',
    'prescription': 'round',
    'four eyes': 'round',
    'bespectacled': 'round',
    'wearing glasses': 'round',
    'with glasses': 'round',

    # === Round ===
    'round glasses': 'round',
    'circular glasses': 'round',
    'circle glasses': 'round',
    'oval glasses': 'round',
    'harry potter glasses': 'round',
    'lennon glasses': 'round',
    'john lennon': 'round',
    'wire frame': 'round',
    'wireframe': 'round',
    'thin frame': 'round',
    'delicate glasses': 'round',
    'vintage glasses': 'round',
    'retro glasses': 'round',
    'hipster glasses': 'round',
    'nerdy glasses': 'round',
    'geek glasses': 'round',
    'nerd glasses': 'round',
    'academic': 'round',
    'scholarly': 'round',
    'librarian': 'round',
    'professor': 'round',
    'intellectual': 'round',

    # === Rectangular ===
    'rectangular glasses': 'rectangular',
    'rectangle glasses': 'rectangular',
    'square glasses': 'rectangular',
    'squared glasses': 'rectangular',
    'box glasses': 'rectangular',
    'angular glasses': 'rectangular',
    'sharp glasses': 'rectangular',
    'modern glasses': 'rectangular',
    'business glasses': 'rectangular',
    'professional glasses': 'rectangular',
    'executive': 'rectangular',
    'corporate': 'rectangular',
    'office': 'rectangular',
    'thick frame': 'rectangular',
    'thick rimmed': 'rectangular',
    'bold frame': 'rectangular',
    'chunky glasses': 'rectangular',
    'heavy frame': 'rectangular',
    'plastic frame': 'rectangular',
    'wayfarer': 'rectangular',

    # === Cat-eye ===
    'cat eye glasses': 'cateye',
    'cat-eye glasses': 'cateye',
    'cateye glasses': 'cateye',
    'cat eye': 'cateye',
    'cat-eye': 'cateye',
    'cateye': 'cateye',
    'winged glasses': 'cateye',
    'upswept': 'cateye',
    'pointed glasses': 'cateye',
    'feminine glasses': 'cateye',
    'glamorous glasses': 'cateye',
    'retro feminine': 'cateye',
    '50s glasses': 'cateye',
    '1950s': 'cateye',
    'secretary': 'cateye',
    'pinup': 'cateye',
    'pin-up': 'cateye',

    # === Sunglasses (map to rectangular tinted) ===
    'sunglasses': 'rectangular',
    'shades': 'rectangular',
    'sunnies': 'rectangular',
    'aviators': 'rectangular',
    'aviator': 'rectangular',

    # === No glasses ===
    'no glasses': None,
    'without glasses': None,
    'not wearing glasses': None,
    'bare face': None,
    'no eyewear': None,
}

# Frame color keywords
FRAME_COLOR_KEYWORDS = {
    # === Dark/Black ===
    'black frame': 'dark',
    'black frames': 'dark',
    'black glasses': 'dark',
    'dark frame': 'dark',
    'dark frames': 'dark',
    'dark glasses': 'dark',
    'ebony frame': 'dark',
    'matte black': 'dark',
    'glossy black': 'dark',

    # === Brown/Tortoise ===
    'brown frame': 'brown',
    'brown frames': 'brown',
    'brown glasses': 'brown',
    'tortoise': 'brown',
    'tortoiseshell': 'brown',
    'tortoise shell': 'brown',
    'havana': 'brown',
    'amber frame': 'brown',
    'wooden': 'brown',
    'wood': 'brown',

    # === Gold ===
    'gold frame': 'gold',
    'gold frames': 'gold',
    'gold glasses': 'gold',
    'golden frame': 'gold',
    'golden frames': 'gold',
    'golden glasses': 'gold',
    'brass': 'gold',
    'bronze frame': 'gold',
    'copper frame': 'gold',

    # === Silver ===
    'silver frame': 'silver',
    'silver frames': 'silver',
    'silver glasses': 'silver',
    'chrome': 'silver',
    'steel': 'silver',
    'stainless': 'silver',
    'platinum frame': 'silver',
    'metallic': 'silver',
    'metal frame': 'silver',
    'wire': 'silver',
    'wire rim': 'silver',
    'wire-rim': 'silver',
    'rimless': 'silver',
    'frameless': 'silver',
    'titanium': 'silver',
    'gunmetal': 'silver',

    # === Red ===
    'red frame': 'red',
    'red frames': 'red',
    'red glasses': 'red',
    'crimson frame': 'red',
    'burgundy frame': 'red',
    'maroon frame': 'red',

    # === Other colors (map to closest) ===
    'blue frame': 'dark',
    'navy frame': 'dark',
    'green frame': 'dark',
    'purple frame': 'dark',
    'pink frame': 'red',
    'white frame': 'silver',
    'clear frame': 'silver',
    'transparent': 'silver',
}

# Skin tone keywords
SKIN_TONE_KEYWORDS = {
    # === Fair/Light ===
    'fair': 'fair',
    'fair skin': 'fair',
    'fair-skinned': 'fair',
    'pale': 'fair',
    'pale skin': 'fair',
    'pale-skinned': 'fair',
    'light skin': 'fair',
    'light-skinned': 'fair',
    'white': 'fair',
    'white skin': 'fair',
    'porcelain': 'fair',
    'porcelain skin': 'fair',
    'ivory': 'fair',
    'ivory skin': 'fair',
    'alabaster': 'fair',
    'creamy': 'fair',
    'cream skin': 'fair',
    'milky': 'fair',
    'snow white': 'fair',
    'rosy': 'fair',
    'pink skin': 'fair',
    'peach': 'fair',
    'peaches and cream': 'fair',
    'caucasian': 'fair',
    'european': 'fair',
    'nordic': 'fair',
    'scandinavian': 'fair',
    'irish': 'fair',
    'scottish': 'fair',
    'english': 'fair',
    'british': 'fair',
    'russian': 'fair',
    'eastern european': 'fair',
    'western': 'fair',

    # === Medium ===
    'medium': 'medium',
    'medium skin': 'medium',
    'medium-skinned': 'medium',
    'olive': 'medium',
    'olive skin': 'medium',
    'olive-skinned': 'medium',
    'mediterranean': 'medium',
    'italian': 'medium',
    'greek': 'medium',
    'spanish': 'medium',
    'portuguese': 'medium',
    'middle eastern': 'medium',
    'arab': 'medium',
    'arabic': 'medium',
    'persian': 'medium',
    'turkish': 'medium',
    'latino': 'medium',
    'latina': 'medium',
    'latinx': 'medium',
    'hispanic': 'medium',
    'mexican': 'medium',
    'south american': 'medium',
    'brazilian': 'medium',
    'indian': 'medium',
    'south asian': 'medium',
    'pakistani': 'medium',
    'bengali': 'medium',
    'sri lankan': 'medium',
    'golden': 'medium',
    'warm skin': 'medium',
    'beige': 'medium',
    'wheat': 'medium',

    # === Tan ===
    'tan': 'tan',
    'tan skin': 'tan',
    'tanned': 'tan',
    'tanned skin': 'tan',
    'sun-kissed': 'tan',
    'sunkissed': 'tan',
    'bronze': 'tan',
    'bronze skin': 'tan',
    'bronzed': 'tan',
    'caramel': 'tan',
    'caramel skin': 'tan',
    'honey': 'tan',
    'honey skin': 'tan',
    'golden brown': 'tan',
    'light brown skin': 'tan',
    'southeast asian': 'tan',
    'filipino': 'tan',
    'thai': 'tan',
    'vietnamese': 'tan',
    'indonesian': 'tan',
    'malaysian': 'tan',
    'pacific islander': 'tan',
    'polynesian': 'tan',
    'hawaiian': 'tan',
    'native american': 'tan',
    'indigenous': 'tan',
    'mixed': 'tan',
    'biracial': 'tan',
    'multiracial': 'tan',

    # === Dark ===
    'dark': 'dark',
    'dark skin': 'dark',
    'dark-skinned': 'dark',
    'brown skin': 'dark',
    'brown-skinned': 'dark',
    'black': 'dark',
    'black skin': 'dark',
    'ebony': 'dark',
    'ebony skin': 'dark',
    'deep brown': 'dark',
    'rich brown': 'dark',
    'mahogany': 'dark',
    'mahogany skin': 'dark',
    'chocolate': 'dark',
    'chocolate skin': 'dark',
    'cocoa': 'dark',
    'cocoa skin': 'dark',
    'coffee': 'dark',
    'espresso': 'dark',
    'mocha': 'dark',
    'mocha skin': 'dark',
    'african': 'dark',
    'african american': 'dark',
    'afro': 'dark',
    'caribbean': 'dark',
    'jamaican': 'dark',
    'haitian': 'dark',
    'nigerian': 'dark',
    'ethiopian': 'dark',
    'kenyan': 'dark',
    'somali': 'dark',
    'sudanese': 'dark',
    'west african': 'dark',
    'east african': 'dark',
    'south african': 'dark',

    # === East Asian (map to fair/medium) ===
    'asian': 'fair',
    'east asian': 'fair',
    'chinese': 'fair',
    'japanese': 'fair',
    'korean': 'fair',
    'taiwanese': 'fair',
    'mongolian': 'medium',
}

# Blush keywords
BLUSH_KEYWORDS = {
    'blushing': 0.5,
    'blush': 0.4,
    'rosy cheeks': 0.5,
    'rosy': 0.4,
    'flushed': 0.6,
    'flushing': 0.5,
    'embarrassed': 0.5,
    'shy': 0.4,
    'bashful': 0.4,
    'coy': 0.3,
    'pink cheeks': 0.4,
    'red cheeks': 0.6,
    'warm cheeks': 0.3,
    'glowing': 0.3,
    'radiant': 0.3,
    'healthy glow': 0.3,
    'sun-kissed cheeks': 0.3,
    'no blush': 0.0,
    'without blush': 0.0,
    'pale face': 0.0,
}


# =============================================================================
# AGE INDICATORS
# =============================================================================

AGE_KEYWORDS = {
    # === Child ===
    'child': 'child',
    'kid': 'child',
    'little': 'child',
    'young child': 'child',
    'toddler': 'child',
    'infant': 'child',
    'baby': 'child',
    'small child': 'child',
    'elementary': 'child',
    'prepubescent': 'child',

    # === Teen ===
    'teen': 'teen',
    'teenager': 'teen',
    'teenage': 'teen',
    'adolescent': 'teen',
    'young': 'teen',
    'youth': 'teen',
    'youthful': 'teen',
    'high school': 'teen',
    'highschool': 'teen',
    'student': 'teen',
    'schoolgirl': 'teen',
    'schoolboy': 'teen',
    'juvenile': 'teen',
    'pubescent': 'teen',

    # === Young Adult ===
    'young adult': 'young_adult',
    'college': 'young_adult',
    'university': 'young_adult',
    'twenties': 'young_adult',
    '20s': 'young_adult',
    'early twenties': 'young_adult',
    'late teens': 'young_adult',

    # === Adult ===
    'adult': 'adult',
    'grown': 'adult',
    'grown up': 'adult',
    'mature': 'adult',
    'thirties': 'adult',
    '30s': 'adult',
    'forties': 'adult',
    '40s': 'adult',
    'middle aged': 'adult',
    'middle-aged': 'adult',
    'midlife': 'adult',

    # === Elderly ===
    'elderly': 'elderly',
    'old': 'elderly',
    'aged': 'elderly',
    'senior': 'elderly',
    'elder': 'elderly',
    'ancient': 'elderly',
    'grandma': 'elderly',
    'grandmother': 'elderly',
    'grandpa': 'elderly',
    'grandfather': 'elderly',
    'granny': 'elderly',
    'fifties': 'elderly',
    '50s': 'elderly',
    'sixties': 'elderly',
    '60s': 'elderly',
    'seventies': 'elderly',
    '70s': 'elderly',
    'eighties': 'elderly',
    '80s': 'elderly',
    'wrinkled': 'elderly',
    'weathered': 'elderly',
    'wise': 'elderly',
    'venerable': 'elderly',
}


# =============================================================================
# FACIAL FEATURES
# =============================================================================

FACIAL_FEATURE_KEYWORDS = {
    # === Freckles ===
    'freckles': 'freckles',
    'freckled': 'freckles',
    'freckling': 'freckles',
    'spotted': 'freckles',
    'dotted': 'freckles',

    # === Dimples ===
    'dimples': 'dimples',
    'dimpled': 'dimples',

    # === Moles/Beauty marks ===
    'mole': 'mole',
    'beauty mark': 'mole',
    'beauty spot': 'mole',

    # === Scars ===
    'scar': 'scar',
    'scarred': 'scar',
    'scarring': 'scar',
    'facial scar': 'scar',
    'battle scar': 'scar',

    # === Face shape ===
    'round face': 'round_face',
    'chubby face': 'round_face',
    'baby face': 'round_face',
    'cherubic': 'round_face',
    'soft features': 'round_face',
    'oval face': 'oval_face',
    'heart shaped face': 'heart_face',
    'heart-shaped face': 'heart_face',
    'angular face': 'angular_face',
    'sharp features': 'angular_face',
    'chiseled': 'angular_face',
    'defined features': 'angular_face',
    'prominent cheekbones': 'angular_face',
    'high cheekbones': 'angular_face',
    'square face': 'square_face',
    'square jaw': 'square_face',
    'strong jaw': 'square_face',
    'jawline': 'square_face',
    'long face': 'long_face',
    'narrow face': 'long_face',
    'thin face': 'long_face',

    # === Eyes shape ===
    'almond eyes': 'almond_eyes',
    'almond-shaped': 'almond_eyes',
    'round eyes': 'round_eyes',
    'big eyes': 'round_eyes',
    'large eyes': 'round_eyes',
    'wide eyes': 'round_eyes',
    'doe eyes': 'round_eyes',
    'narrow eyes': 'narrow_eyes',
    'small eyes': 'narrow_eyes',
    'slit eyes': 'narrow_eyes',
    'hooded eyes': 'hooded_eyes',
    'droopy eyes': 'hooded_eyes',
    'upturned eyes': 'upturned_eyes',
    'cat eyes': 'upturned_eyes',
    'fox eyes': 'upturned_eyes',
    'downturned eyes': 'downturned_eyes',
    'sad eyes': 'downturned_eyes',
    'monolid': 'monolid',
    'single eyelid': 'monolid',
    'double eyelid': 'double_eyelid',

    # === Eyebrows ===
    'thick eyebrows': 'thick_brows',
    'bushy eyebrows': 'thick_brows',
    'bold eyebrows': 'thick_brows',
    'thin eyebrows': 'thin_brows',
    'delicate eyebrows': 'thin_brows',
    'arched eyebrows': 'arched_brows',
    'high arched': 'arched_brows',
    'straight eyebrows': 'straight_brows',
    'flat eyebrows': 'straight_brows',
    'furrowed brow': 'furrowed_brows',
    'knitted brows': 'furrowed_brows',
    'unibrow': 'unibrow',
    'monobrow': 'unibrow',

    # === Nose ===
    'button nose': 'button_nose',
    'small nose': 'button_nose',
    'cute nose': 'button_nose',
    'upturned nose': 'button_nose',
    'long nose': 'long_nose',
    'prominent nose': 'long_nose',
    'aquiline nose': 'aquiline_nose',
    'roman nose': 'aquiline_nose',
    'hooked nose': 'aquiline_nose',
    'hawk nose': 'aquiline_nose',
    'wide nose': 'wide_nose',
    'broad nose': 'wide_nose',
    'flat nose': 'flat_nose',
    'snub nose': 'snub_nose',

    # === Lips ===
    'full lips': 'full_lips',
    'plump lips': 'full_lips',
    'pouty lips': 'full_lips',
    'thick lips': 'full_lips',
    'thin lips': 'thin_lips',
    'narrow lips': 'thin_lips',
    'heart shaped lips': 'heart_lips',
    'cupid bow': 'heart_lips',
    'cupids bow': 'heart_lips',

    # === Chin/Jaw ===
    'pointed chin': 'pointed_chin',
    'sharp chin': 'pointed_chin',
    'v-shaped chin': 'pointed_chin',
    'rounded chin': 'round_chin',
    'soft chin': 'round_chin',
    'double chin': 'double_chin',
    'cleft chin': 'cleft_chin',
    'dimpled chin': 'cleft_chin',
    'butt chin': 'cleft_chin',

    # === Ears ===
    'pointed ears': 'pointed_ears',
    'elf ears': 'pointed_ears',
    'large ears': 'large_ears',
    'big ears': 'large_ears',
    'small ears': 'small_ears',
    'attached earlobes': 'attached_ears',
    'detached earlobes': 'detached_ears',

    # === Other ===
    'birthmark': 'birthmark',
    'tattoo': 'face_tattoo',
    'facial tattoo': 'face_tattoo',
    'face tattoo': 'face_tattoo',
    'piercing': 'piercing',
    'piercings': 'piercing',
    'nose ring': 'nose_piercing',
    'nose piercing': 'nose_piercing',
    'lip ring': 'lip_piercing',
    'lip piercing': 'lip_piercing',
    'eyebrow piercing': 'brow_piercing',
    'facial hair': 'facial_hair',
    'beard': 'beard',
    'mustache': 'mustache',
    'moustache': 'mustache',
    'goatee': 'goatee',
    'stubble': 'stubble',
    'five oclock shadow': 'stubble',
    'clean shaven': 'clean_shaven',
    'clean-shaven': 'clean_shaven',
}


# =============================================================================
# MAKEUP
# =============================================================================

MAKEUP_KEYWORDS = {
    # === General ===
    'makeup': 'natural',
    'make-up': 'natural',
    'made up': 'natural',
    'wearing makeup': 'natural',
    'no makeup': 'none',
    'without makeup': 'none',
    'bare faced': 'none',
    'natural look': 'natural',
    'natural makeup': 'natural',
    'light makeup': 'natural',
    'subtle makeup': 'natural',
    'minimal makeup': 'natural',
    'heavy makeup': 'heavy',
    'full makeup': 'heavy',
    'dramatic makeup': 'heavy',
    'bold makeup': 'heavy',
    'glam': 'glam',
    'glamorous': 'glam',
    'glamourous': 'glam',

    # === Lipstick ===
    'lipstick': 'lipstick',
    'red lipstick': 'red_lips',
    'red lips': 'red_lips',
    'crimson lips': 'red_lips',
    'ruby lips': 'red_lips',
    'pink lipstick': 'pink_lips',
    'pink lips': 'pink_lips',
    'rose lips': 'pink_lips',
    'nude lips': 'nude_lips',
    'nude lipstick': 'nude_lips',
    'natural lips': 'nude_lips',
    'dark lipstick': 'dark_lips',
    'dark lips': 'dark_lips',
    'black lipstick': 'dark_lips',
    'purple lipstick': 'dark_lips',
    'berry lips': 'dark_lips',
    'lip gloss': 'gloss',
    'glossy lips': 'gloss',
    'shiny lips': 'gloss',

    # === Eyes ===
    'eyeshadow': 'eyeshadow',
    'eye shadow': 'eyeshadow',
    'smoky eye': 'smoky_eye',
    'smokey eye': 'smoky_eye',
    'smoky eyes': 'smoky_eye',
    'dark eyeshadow': 'smoky_eye',
    'dramatic eyes': 'smoky_eye',
    'natural eyeshadow': 'natural_eye',
    'subtle eyeshadow': 'natural_eye',
    'colorful eyeshadow': 'colorful_eye',
    'bright eyeshadow': 'colorful_eye',
    'blue eyeshadow': 'colorful_eye',
    'green eyeshadow': 'colorful_eye',
    'purple eyeshadow': 'colorful_eye',
    'pink eyeshadow': 'colorful_eye',
    'gold eyeshadow': 'gold_eye',
    'glitter': 'glitter',
    'sparkle': 'glitter',
    'shimmer': 'glitter',

    # === Eyeliner ===
    'eyeliner': 'eyeliner',
    'eye liner': 'eyeliner',
    'winged eyeliner': 'winged_liner',
    'cat eye makeup': 'winged_liner',
    'cat eye liner': 'winged_liner',
    'thick eyeliner': 'thick_liner',
    'heavy eyeliner': 'thick_liner',
    'kohl': 'kohl',
    'kohl eyeliner': 'kohl',
    'raccoon eyes': 'kohl',

    # === Mascara/Lashes ===
    'mascara': 'mascara',
    'long lashes': 'long_lashes',
    'thick lashes': 'long_lashes',
    'full lashes': 'long_lashes',
    'fake lashes': 'false_lashes',
    'false lashes': 'false_lashes',
    'false eyelashes': 'false_lashes',
    'lash extensions': 'false_lashes',
    'spider lashes': 'spider_lashes',
    'clumpy mascara': 'spider_lashes',

    # === Blush (cosmetic) ===
    'blush makeup': 'blush_makeup',
    'rouge': 'blush_makeup',
    'bronzer': 'bronzer',
    'contour': 'contour',
    'contouring': 'contour',
    'highlight': 'highlight',
    'highlighter': 'highlight',
    'strobing': 'highlight',

    # === Eyebrows ===
    'filled eyebrows': 'filled_brows',
    'drawn eyebrows': 'filled_brows',
    'microbladed': 'filled_brows',
    'laminated brows': 'laminated_brows',
    'soap brows': 'laminated_brows',
    'fluffy brows': 'laminated_brows',

    # === Nails (less relevant but included) ===
    'nail polish': 'nail_polish',
    'painted nails': 'nail_polish',
    'manicure': 'nail_polish',
    'red nails': 'red_nails',
    'long nails': 'long_nails',
    'acrylic nails': 'long_nails',
}


# =============================================================================
# HAIR ACCESSORIES
# =============================================================================

HAIR_ACCESSORY_KEYWORDS = {
    # === Ribbons/Bows ===
    'ribbon': 'ribbon',
    'hair ribbon': 'ribbon',
    'bow': 'bow',
    'hair bow': 'bow',
    'big bow': 'bow',
    'red ribbon': 'red_ribbon',
    'red bow': 'red_bow',
    'pink ribbon': 'pink_ribbon',
    'pink bow': 'pink_bow',
    'white ribbon': 'white_ribbon',
    'white bow': 'white_bow',
    'black ribbon': 'black_ribbon',
    'black bow': 'black_bow',

    # === Clips/Pins ===
    'hair clip': 'clip',
    'hairclip': 'clip',
    'clip': 'clip',
    'barrette': 'barrette',
    'hair pin': 'hairpin',
    'hairpin': 'hairpin',
    'bobby pin': 'bobby_pin',
    'bobby pins': 'bobby_pin',

    # === Bands ===
    'headband': 'headband',
    'head band': 'headband',
    'alice band': 'headband',
    'hair band': 'hairband',
    'hairband': 'hairband',
    'scrunchie': 'scrunchie',
    'hair tie': 'hair_tie',
    'elastic': 'hair_tie',
    'ponytail holder': 'hair_tie',

    # === Decorative ===
    'flower': 'flower',
    'hair flower': 'flower',
    'flower crown': 'flower_crown',
    'floral crown': 'flower_crown',
    'wreath': 'flower_crown',
    'tiara': 'tiara',
    'crown': 'crown',
    'diadem': 'crown',
    'jeweled': 'jeweled',
    'jewels': 'jeweled',
    'crystals': 'jeweled',
    'rhinestones': 'jeweled',
    'pearls': 'pearls',
    'pearl': 'pearls',
    'feather': 'feather',
    'feathers': 'feather',
    'hair feather': 'feather',
    'stars': 'stars',
    'star clips': 'stars',
    'butterfly clips': 'butterfly',
    'butterfly': 'butterfly',

    # === Hats/Headwear ===
    'hat': 'hat',
    'cap': 'cap',
    'baseball cap': 'cap',
    'beanie': 'beanie',
    'beret': 'beret',
    'bonnet': 'bonnet',
    'hood': 'hood',
    'hooded': 'hood',
    'veil': 'veil',
    'headscarf': 'headscarf',
    'hijab': 'hijab',
    'turban': 'turban',
    'bandana': 'bandana',
    'bandanna': 'bandana',
    'kerchief': 'bandana',

    # === Cultural/Traditional ===
    'kanzashi': 'kanzashi',
    'chopsticks': 'chopsticks',
    'hair sticks': 'chopsticks',
    'maang tikka': 'tikka',
    'bindi': 'bindi',
}


# =============================================================================
# CHARACTER ARCHETYPES
# =============================================================================

ARCHETYPE_KEYWORDS = {
    # === Fantasy Classes ===
    'warrior': 'warrior',
    'fighter': 'warrior',
    'soldier': 'warrior',
    'knight': 'knight',
    'paladin': 'knight',
    'crusader': 'knight',
    'mage': 'mage',
    'wizard': 'mage',
    'witch': 'witch',
    'sorceress': 'witch',
    'sorcerer': 'mage',
    'warlock': 'mage',
    'enchantress': 'witch',
    'necromancer': 'necromancer',
    'healer': 'healer',
    'cleric': 'healer',
    'priest': 'healer',
    'priestess': 'healer',
    'monk': 'monk',
    'rogue': 'rogue',
    'thief': 'rogue',
    'assassin': 'assassin',
    'ninja': 'ninja',
    'ranger': 'ranger',
    'archer': 'archer',
    'hunter': 'hunter',
    'druid': 'druid',
    'shaman': 'shaman',
    'bard': 'bard',
    'minstrel': 'bard',

    # === Royalty/Nobility ===
    'princess': 'princess',
    'prince': 'prince',
    'queen': 'queen',
    'king': 'king',
    'empress': 'empress',
    'emperor': 'emperor',
    'noble': 'noble',
    'nobleman': 'noble',
    'noblewoman': 'noble',
    'aristocrat': 'noble',
    'lady': 'noble',
    'lord': 'noble',
    'duchess': 'noble',
    'duke': 'noble',
    'countess': 'noble',
    'count': 'noble',
    'baroness': 'noble',
    'baron': 'noble',

    # === Occupations ===
    'scholar': 'scholar',
    'librarian': 'scholar',
    'researcher': 'scholar',
    'scientist': 'scientist',
    'doctor': 'doctor',
    'nurse': 'nurse',
    'teacher': 'teacher',
    'professor': 'professor',
    'artist': 'artist',
    'painter': 'artist',
    'musician': 'musician',
    'singer': 'singer',
    'dancer': 'dancer',
    'ballerina': 'ballerina',
    'chef': 'chef',
    'cook': 'chef',
    'maid': 'maid',
    'servant': 'servant',
    'butler': 'butler',
    'merchant': 'merchant',
    'trader': 'merchant',
    'shopkeeper': 'merchant',
    'blacksmith': 'blacksmith',
    'smith': 'blacksmith',
    'farmer': 'farmer',
    'peasant': 'peasant',
    'commoner': 'peasant',
    'sailor': 'sailor',
    'pirate': 'pirate',
    'captain': 'captain',
    'pilot': 'pilot',
    'astronaut': 'astronaut',
    'explorer': 'explorer',
    'adventurer': 'adventurer',

    # === Modern Roles ===
    'office worker': 'office',
    'businessman': 'business',
    'businesswoman': 'business',
    'executive': 'executive',
    'ceo': 'executive',
    'secretary': 'secretary',
    'assistant': 'secretary',
    'detective': 'detective',
    'investigator': 'detective',
    'police': 'police',
    'cop': 'police',
    'officer': 'police',
    'firefighter': 'firefighter',
    'athlete': 'athlete',
    'sports': 'athlete',
    'gamer': 'gamer',
    'streamer': 'streamer',
    'influencer': 'influencer',
    'idol': 'idol',
    'popstar': 'idol',
    'celebrity': 'celebrity',
    'model': 'model',
    'fashion': 'fashion',

    # === Character Types ===
    'hero': 'hero',
    'heroine': 'heroine',
    'protagonist': 'hero',
    'villain': 'villain',
    'antagonist': 'villain',
    'antihero': 'antihero',
    'anti-hero': 'antihero',
    'sidekick': 'sidekick',
    'mentor': 'mentor',
    'guide': 'mentor',
    'sage': 'sage',
    'oracle': 'oracle',
    'prophet': 'oracle',
    'chosen one': 'chosen',
    'prodigy': 'prodigy',
    'genius': 'genius',
    'outcast': 'outcast',
    'loner': 'loner',
    'rebel': 'rebel',
    'revolutionary': 'rebel',
    'leader': 'leader',
    'commander': 'leader',
    'general': 'leader',

    # === Anime/Manga Tropes ===
    'tsundere': 'tsundere',
    'yandere': 'yandere',
    'kuudere': 'kuudere',
    'dandere': 'dandere',
    'deredere': 'deredere',
    'ojou': 'ojou',
    'ojou-sama': 'ojou',
    'imouto': 'imouto',
    'onee-san': 'oneesan',
    'senpai': 'senpai',
    'kouhai': 'kouhai',
    'sensei': 'sensei',
    'magical girl': 'magical_girl',
    'mahou shoujo': 'magical_girl',
    'idol': 'idol',
    'delinquent': 'delinquent',
    'yankee': 'delinquent',
    'gyaru': 'gyaru',
    'gal': 'gyaru',
    'otaku': 'otaku',
    'nerd': 'nerd',
    'geek': 'geek',
    'bookworm': 'bookworm',
    'class president': 'class_president',
    'student council': 'student_council',
}


# =============================================================================
# ART STYLE
# =============================================================================

ART_STYLE_KEYWORDS = {
    # === Anime/Manga ===
    'anime': 'anime',
    'anime style': 'anime',
    'manga': 'anime',
    'manga style': 'anime',
    'japanese style': 'anime',
    'shonen': 'anime',
    'shoujo': 'anime',
    'seinen': 'anime',
    'josei': 'anime',

    # === Chibi/Cute ===
    'chibi': 'chibi',
    'chibi style': 'chibi',
    'super deformed': 'chibi',
    'sd': 'chibi',
    'cute': 'chibi',
    'kawaii': 'chibi',
    'adorable': 'chibi',
    'moe': 'chibi',

    # === Realistic ===
    'realistic': 'realistic',
    'realistic style': 'realistic',
    'photorealistic': 'realistic',
    'lifelike': 'realistic',
    'detailed': 'realistic',
    'hyper detailed': 'realistic',

    # === Semi-realistic ===
    'semi-realistic': 'semi_realistic',
    'semi realistic': 'semi_realistic',
    'stylized': 'semi_realistic',

    # === Cartoon ===
    'cartoon': 'cartoon',
    'cartoon style': 'cartoon',
    'cartoony': 'cartoon',
    'western': 'cartoon',
    'disney': 'cartoon',
    'pixar': 'cartoon',
    'dreamworks': 'cartoon',

    # === Retro/Vintage ===
    'retro': 'retro',
    '80s': 'retro',
    '90s': 'retro',
    'vintage': 'vintage',
    'classic': 'vintage',
    'old school': 'vintage',
    'old-school': 'vintage',

    # === Pixel Art ===
    'pixel': 'pixel',
    'pixel art': 'pixel',
    'pixelated': 'pixel',
    '8-bit': 'pixel',
    '8bit': 'pixel',
    '16-bit': 'pixel',
    '16bit': 'pixel',
    'retro game': 'pixel',

    # === Other Styles ===
    'minimalist': 'minimalist',
    'simple': 'minimalist',
    'flat': 'flat',
    'flat design': 'flat',
    'vector': 'flat',
    'painterly': 'painterly',
    'oil painting': 'painterly',
    'watercolor': 'watercolor',
    'sketch': 'sketch',
    'sketchy': 'sketch',
    'line art': 'lineart',
    'lineart': 'lineart',
    'cel shaded': 'cel_shaded',
    'cel-shaded': 'cel_shaded',
    'toon shaded': 'cel_shaded',
    'comic': 'comic',
    'comic book': 'comic',
    'marvel': 'comic',
    'dc': 'comic',
    'superhero': 'comic',
}


# =============================================================================
# FANTASY RACES / SPECIES
# =============================================================================

FANTASY_RACE_KEYWORDS = {
    # === Elves ===
    'elf': 'elf',
    'elven': 'elf',
    'elvish': 'elf',
    'elfish': 'elf',
    'high elf': 'high_elf',
    'wood elf': 'wood_elf',
    'dark elf': 'dark_elf',
    'drow': 'dark_elf',
    'night elf': 'dark_elf',
    'blood elf': 'blood_elf',
    'half elf': 'half_elf',
    'half-elf': 'half_elf',

    # === Other Fantasy ===
    'dwarf': 'dwarf',
    'dwarven': 'dwarf',
    'halfling': 'halfling',
    'hobbit': 'halfling',
    'gnome': 'gnome',
    'orc': 'orc',
    'orcish': 'orc',
    'half-orc': 'half_orc',
    'goblin': 'goblin',
    'troll': 'troll',
    'ogre': 'ogre',
    'giant': 'giant',
    'fairy': 'fairy',
    'fae': 'fairy',
    'faerie': 'fairy',
    'pixie': 'pixie',
    'sprite': 'sprite',
    'nymph': 'nymph',
    'dryad': 'dryad',
    'mermaid': 'mermaid',
    'merman': 'merman',
    'siren': 'siren',

    # === Supernatural ===
    'vampire': 'vampire',
    'vampiric': 'vampire',
    'dhampir': 'vampire',
    'werewolf': 'werewolf',
    'lycanthrope': 'werewolf',
    'wolf': 'werewolf',
    'demon': 'demon',
    'demonic': 'demon',
    'devil': 'demon',
    'fiend': 'demon',
    'succubus': 'succubus',
    'incubus': 'incubus',
    'angel': 'angel',
    'angelic': 'angel',
    'seraph': 'angel',
    'fallen angel': 'fallen_angel',
    'ghost': 'ghost',
    'spirit': 'spirit',
    'specter': 'ghost',
    'wraith': 'wraith',
    'undead': 'undead',
    'zombie': 'zombie',
    'skeleton': 'skeleton',
    'lich': 'lich',

    # === Animal-hybrids ===
    'catgirl': 'catgirl',
    'cat girl': 'catgirl',
    'nekomimi': 'catgirl',
    'neko': 'catgirl',
    'cat ears': 'catgirl',
    'kemonomimi': 'kemonomimi',
    'animal ears': 'kemonomimi',
    'fox girl': 'foxgirl',
    'foxgirl': 'foxgirl',
    'kitsune': 'kitsune',
    'fox ears': 'foxgirl',
    'wolf girl': 'wolfgirl',
    'wolf ears': 'wolfgirl',
    'bunny girl': 'bunnygirl',
    'rabbit ears': 'bunnygirl',
    'bunny ears': 'bunnygirl',
    'dog girl': 'doggirl',
    'dog ears': 'doggirl',
    'inumimi': 'doggirl',

    # === Dragons/Reptiles ===
    'dragon': 'dragon',
    'dragonborn': 'dragonborn',
    'half-dragon': 'half_dragon',
    'dragon girl': 'dragon_girl',
    'lizard': 'lizardfolk',
    'lizardfolk': 'lizardfolk',
    'snake': 'lamia',
    'lamia': 'lamia',
    'naga': 'naga',
    'medusa': 'medusa',
    'gorgon': 'medusa',

    # === Other ===
    'android': 'android',
    'robot': 'robot',
    'cyborg': 'cyborg',
    'mechanical': 'robot',
    'automaton': 'robot',
    'golem': 'golem',
    'elemental': 'elemental',
    'slime': 'slime',
    'alien': 'alien',
    'extraterrestrial': 'alien',
    'human': 'human',
    'mortal': 'human',
}


# =============================================================================
# ATMOSPHERE / MOOD / SETTING
# =============================================================================

ATMOSPHERE_KEYWORDS = {
    # === Lighting/Tone ===
    'dark': 'dark',
    'darkness': 'dark',
    'shadowy': 'dark',
    'dim': 'dark',
    'gloomy': 'dark',
    'moody': 'dark',
    'noir': 'dark',
    'light': 'light',
    'bright': 'light',
    'sunny': 'light',
    'radiant': 'light',
    'glowing': 'light',
    'luminous': 'light',

    # === Temperature ===
    'warm': 'warm',
    'hot': 'warm',
    'fiery': 'warm',
    'golden hour': 'warm',
    'sunset': 'warm',
    'sunrise': 'warm',
    'cool': 'cool',
    'cold': 'cool',
    'icy': 'cool',
    'frozen': 'cool',
    'winter': 'cool',
    'moonlit': 'cool',
    'moonlight': 'cool',

    # === Mood ===
    'romantic': 'romantic',
    'dreamy': 'dreamy',
    'ethereal': 'ethereal',
    'mystical': 'mystical',
    'magical': 'magical',
    'enchanted': 'magical',
    'whimsical': 'whimsical',
    'fantastical': 'fantastical',
    'surreal': 'surreal',
    'psychedelic': 'psychedelic',
    'trippy': 'psychedelic',
    'eerie': 'eerie',
    'creepy': 'creepy',
    'spooky': 'spooky',
    'haunting': 'haunting',
    'ominous': 'ominous',
    'foreboding': 'foreboding',
    'sinister': 'sinister',
    'menacing': 'menacing',
    'peaceful': 'peaceful',
    'serene': 'peaceful',
    'tranquil': 'peaceful',
    'calming': 'peaceful',
    'relaxing': 'peaceful',
    'melancholic': 'melancholic',
    'nostalgic': 'nostalgic',
    'bittersweet': 'bittersweet',
    'hopeful': 'hopeful',
    'inspiring': 'inspiring',
    'epic': 'epic',
    'heroic': 'heroic',
    'dramatic': 'dramatic',
    'intense': 'intense',
    'action': 'action',
    'dynamic': 'dynamic',
    'energetic': 'energetic',

    # === Setting/Time ===
    'fantasy': 'fantasy',
    'medieval': 'medieval',
    'renaissance': 'renaissance',
    'victorian': 'victorian',
    'steampunk': 'steampunk',
    'cyberpunk': 'cyberpunk',
    'futuristic': 'futuristic',
    'sci-fi': 'scifi',
    'sci fi': 'scifi',
    'science fiction': 'scifi',
    'space': 'space',
    'modern': 'modern',
    'contemporary': 'modern',
    'urban': 'urban',
    'city': 'urban',
    'rural': 'rural',
    'countryside': 'rural',
    'forest': 'forest',
    'woodland': 'forest',
    'ocean': 'ocean',
    'underwater': 'underwater',
    'beach': 'beach',
    'tropical': 'tropical',
    'desert': 'desert',
    'arctic': 'arctic',
    'mountain': 'mountain',
    'sky': 'sky',
    'clouds': 'sky',
    'heavenly': 'heavenly',
    'celestial': 'celestial',
    'hellish': 'hellish',
    'infernal': 'hellish',

    # === Seasons ===
    'spring': 'spring',
    'summer': 'summer',
    'autumn': 'autumn',
    'fall': 'autumn',
    'winter': 'winter',

    # === Time of Day ===
    'morning': 'morning',
    'dawn': 'dawn',
    'daytime': 'day',
    'afternoon': 'afternoon',
    'evening': 'evening',
    'dusk': 'dusk',
    'twilight': 'twilight',
    'night': 'night',
    'nighttime': 'night',
    'midnight': 'midnight',
}


# =============================================================================
# PARSER
# =============================================================================

def _find_keyword(text: str, keyword_map: Dict[str, Any], default: Any = None) -> Any:
    """Find the first matching keyword in text."""
    text_lower = text.lower()

    # Sort by length (longer first) to match more specific phrases first
    sorted_keywords = sorted(keyword_map.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        if keyword in text_lower:
            return keyword_map[keyword]

    return default


def _find_all_keywords(text: str, keyword_map: Dict[str, Any]) -> List[Any]:
    """Find all matching keywords in text."""
    text_lower = text.lower()
    found = []

    sorted_keywords = sorted(keyword_map.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        if keyword in text_lower:
            value = keyword_map[keyword]
            if value not in found:
                found.append(value)

    return found


def parse_description(description: str) -> Dict[str, Any]:
    """
    Parse a natural language description into a character spec.

    Examples:
        "a happy girl with blonde hair and glasses"
        "character with red hair, green eyes, looking surprised"
        "dark-skinned person with black hair in a bun"
        "elven princess with silver hair and pointed ears"
        "cyberpunk android with glowing blue eyes"

    Returns:
        A spec dictionary ready for render_from_spec()
    """
    text = description.lower()

    spec = {
        'size': 128,
        'character': {},
        'meta': {}  # Store detected but not-yet-rendered attributes
    }

    char = spec['character']
    meta = spec['meta']

    # --- Hair ---
    hair_color = _find_keyword(text, HAIR_COLOR_KEYWORDS, 'brown')
    hair_style = _find_keyword(text, HAIR_STYLE_KEYWORDS, 'bun')

    char['hair'] = {
        'style': hair_style,
        'color': hair_color,
    }

    # --- Hair Accessories ---
    hair_accessory = _find_keyword(text, HAIR_ACCESSORY_KEYWORDS)
    if hair_accessory:
        meta['hair_accessory'] = hair_accessory

    # --- Eyes ---
    eye_color = _find_keyword(text, EYE_COLOR_KEYWORDS, 'brown')

    char['eyes'] = {
        'color': eye_color,
    }

    # --- Expression ---
    expression = _find_keyword(text, EXPRESSION_KEYWORDS, ('neutral', 'neutral'))
    if expression:
        eye_expr, mouth_expr = expression
        char['eyes']['expression'] = eye_expr
        char['face'] = char.get('face', {})
        char['face']['mouth'] = mouth_expr

    # --- Skin tone ---
    skin_tone = _find_keyword(text, SKIN_TONE_KEYWORDS)
    if skin_tone:
        char['skin'] = {'tone': skin_tone}

    # --- Blush ---
    blush = _find_keyword(text, BLUSH_KEYWORDS)
    if blush is not None:
        char['face'] = char.get('face', {})
        char['face']['blush'] = blush

    # --- Age ---
    age = _find_keyword(text, AGE_KEYWORDS)
    if age:
        meta['age'] = age

    # --- Facial Features ---
    facial_features = _find_all_keywords(text, FACIAL_FEATURE_KEYWORDS)
    if facial_features:
        meta['facial_features'] = facial_features

    # --- Makeup ---
    makeup = _find_all_keywords(text, MAKEUP_KEYWORDS)
    if makeup:
        meta['makeup'] = makeup

    # --- Glasses ---
    glasses_style = _find_keyword(text, GLASSES_KEYWORDS)

    # Check for explicit "no glasses"
    if 'no glasses' in text or 'without glasses' in text:
        glasses_style = None

    if glasses_style:
        frame_color = _find_keyword(text, FRAME_COLOR_KEYWORDS, 'dark')

        char['accessories'] = char.get('accessories', {})
        char['accessories']['glasses'] = {
            'style': glasses_style,
            'frame_color': frame_color,
            'glare': True,
        }

    # --- Character Archetype ---
    archetype = _find_keyword(text, ARCHETYPE_KEYWORDS)
    if archetype:
        meta['archetype'] = archetype

    # --- Art Style ---
    art_style = _find_keyword(text, ART_STYLE_KEYWORDS)
    if art_style:
        meta['art_style'] = art_style

    # --- Fantasy Race ---
    race = _find_keyword(text, FANTASY_RACE_KEYWORDS)
    if race:
        meta['race'] = race
        # Add pointed ears for elves
        if race in ['elf', 'high_elf', 'wood_elf', 'dark_elf', 'blood_elf', 'half_elf']:
            if 'facial_features' not in meta:
                meta['facial_features'] = []
            if 'pointed_ears' not in meta['facial_features']:
                meta['facial_features'].append('pointed_ears')

    # --- Atmosphere ---
    atmosphere = _find_keyword(text, ATMOSPHERE_KEYWORDS)
    if atmosphere:
        meta['atmosphere'] = atmosphere

    return spec


def describe_spec(spec: Dict[str, Any]) -> str:
    """
    Generate a human-readable description of a spec.
    Useful for confirming what was parsed.
    """
    char = spec.get('character', {})
    meta = spec.get('meta', {})

    parts = []

    # Race (if not human)
    race = meta.get('race')
    if race and race != 'human':
        parts.append(race.replace('_', ' '))

    # Archetype
    archetype = meta.get('archetype')
    if archetype:
        parts.append(archetype.replace('_', ' '))

    # Age
    age = meta.get('age')
    if age:
        parts.append(age.replace('_', ' '))

    # Skin
    skin = char.get('skin', {})
    tone = skin.get('tone')
    if tone:
        parts.append(f"{tone} skin")

    # Hair
    hair = char.get('hair', {})
    hair_color = hair.get('color', 'brown')
    hair_style = hair.get('style', 'bun')
    parts.append(f"{hair_color} {hair_style} hair")

    # Hair accessory
    hair_accessory = meta.get('hair_accessory')
    if hair_accessory:
        parts.append(f"with {hair_accessory.replace('_', ' ')}")

    # Eyes
    eyes = char.get('eyes', {})
    eye_color = eyes.get('color', 'brown')
    parts.append(f"{eye_color} eyes")

    # Facial features
    facial_features = meta.get('facial_features', [])
    for feature in facial_features[:3]:  # Limit to 3
        parts.append(feature.replace('_', ' '))

    # Expression
    face = char.get('face', {})
    mouth = face.get('mouth', 'neutral')
    eye_expr = eyes.get('expression', 'neutral')
    if mouth != 'neutral' or eye_expr != 'neutral':
        expr = mouth if mouth != 'neutral' else eye_expr
        parts.append(f"{expr} expression")

    # Makeup
    makeup = meta.get('makeup', [])
    if makeup:
        parts.append(makeup[0].replace('_', ' '))  # Just the first

    # Blush
    blush = face.get('blush', 0)
    if blush and blush > 0.3:
        parts.append("blushing")

    # Glasses
    accessories = char.get('accessories', {})
    glasses = accessories.get('glasses')
    if glasses:
        style = glasses.get('style', 'round')
        frame = glasses.get('frame_color', 'dark')
        parts.append(f"{frame} {style} glasses")

    # Atmosphere
    atmosphere = meta.get('atmosphere')
    if atmosphere:
        parts.append(f"{atmosphere} mood")

    # Art style
    art_style = meta.get('art_style')
    if art_style:
        parts.append(f"{art_style} style")

    return ", ".join(parts)


# =============================================================================
# HIGH-LEVEL API
# =============================================================================

def generate_character(description: str, output_path: Optional[str] = None):
    """
    Generate a character from a natural language description.

    Args:
        description: Natural language description like "happy girl with red hair"
        output_path: Optional path to save the image

    Returns:
        (canvas, spec, description_summary)
    """
    from recipes.loader import render_from_spec

    # Parse description to spec
    spec = parse_description(description)

    # Generate description of what we understood
    summary = describe_spec(spec)

    # Render
    canvas = render_from_spec(spec)

    # Save if path provided
    if output_path:
        canvas.save(output_path)

    return canvas, spec, summary


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python natural_language.py \"description\" [output.png]")
        print("\nExamples:")
        print('  python natural_language.py "happy girl with blonde hair and glasses"')
        print('  python natural_language.py "sad character with black hair, blue eyes"')
        print('  python natural_language.py "dark-skinned person with auburn hair, smiling"')
        print('  python natural_language.py "mysterious woman with raven hair and emerald eyes"')
        print('  python natural_language.py "cheerful redhead wearing cat-eye glasses, blushing"')
        sys.exit(1)

    description = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output/from_description.png'

    print(f"Input: \"{description}\"")
    print()

    canvas, spec, summary = generate_character(description, output_path)

    print(f"Parsed: {summary}")
    print(f"Saved: {output_path}")
