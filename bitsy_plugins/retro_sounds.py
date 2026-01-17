"""
Example sound plugin - Retro game sounds.

Demonstrates how to create a SoundPlugin.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins import SoundPlugin
from sound import SoundEffect


class LevelUpSound(SoundPlugin):
    """Generates a triumphant level-up sound."""

    name = "level_up"
    category = "sfx"
    description = "Triumphant ascending arpeggio for level ups"
    version = "1.0.0"
    author = "Bitsy Examples"
    tags = ["retro", "positive", "fanfare"]

    def generate(self, duration=0.6, base_freq=300, **kwargs):
        """Generate level-up sound effect."""
        effect = SoundEffect(duration=duration)
        effect.set_oscillator('square', base_freq, volume=0.7)
        effect.set_arpeggio([0, 4, 7, 12, 16], speed=8)  # Major chord up
        effect.set_envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.2)
        return effect


class GameOverSound(SoundPlugin):
    """Generates a sad game-over sound."""

    name = "game_over"
    category = "sfx"
    description = "Descending tone for game over"
    version = "1.0.0"
    author = "Bitsy Examples"
    tags = ["retro", "negative", "ending"]

    def generate(self, duration=1.0, start_freq=400, **kwargs):
        """Generate game-over sound effect."""
        effect = SoundEffect(duration=duration)
        effect.set_oscillator('square', start_freq, volume=0.6)
        effect.set_sweep(start_freq, start_freq // 4, curve='exponential')
        effect.set_decay_envelope(duration * 0.8, curve='exponential')
        return effect


class WarpSound(SoundPlugin):
    """Generates a sci-fi warp/teleport sound."""

    name = "warp"
    category = "sfx"
    description = "Sci-fi teleportation sound"
    version = "1.0.0"
    author = "Bitsy Examples"
    tags = ["retro", "scifi", "teleport"]

    def generate(self, duration=0.4, **kwargs):
        """Generate warp sound effect."""
        effect = SoundEffect(duration=duration)
        effect.set_oscillator('sine', 200, volume=0.8)
        effect.set_sweep(200, 2000, curve='exponential')
        effect.set_vibrato(rate=30, depth=50)
        effect.set_envelope(attack=0.02, decay=0.1, sustain=0.5, release=0.15)
        return effect
