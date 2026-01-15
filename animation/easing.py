"""
Easing - Interpolation curves for smooth animations.

Provides a comprehensive set of easing functions for keyframe
interpolation. All functions take t (0-1) and return eased value (0-1).
"""

import math
from typing import Callable, Dict


# Type alias for easing function
EasingFunc = Callable[[float], float]


def clamp(t: float) -> float:
    """Clamp value to 0-1 range."""
    return max(0.0, min(1.0, t))


# =============================================================================
# Linear
# =============================================================================

def linear(t: float) -> float:
    """Linear interpolation - no easing."""
    return clamp(t)


# =============================================================================
# Quadratic (Power of 2)
# =============================================================================

def ease_in_quad(t: float) -> float:
    """Quadratic ease in - accelerating from zero."""
    t = clamp(t)
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease out - decelerating to zero."""
    t = clamp(t)
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease in-out - acceleration then deceleration."""
    t = clamp(t)
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - (-2 * t + 2) ** 2 / 2


# =============================================================================
# Cubic (Power of 3)
# =============================================================================

def ease_in_cubic(t: float) -> float:
    """Cubic ease in - accelerating from zero."""
    t = clamp(t)
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease out - decelerating to zero."""
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease in-out."""
    t = clamp(t)
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 3 / 2


# =============================================================================
# Quartic (Power of 4)
# =============================================================================

def ease_in_quart(t: float) -> float:
    """Quartic ease in."""
    t = clamp(t)
    return t * t * t * t


def ease_out_quart(t: float) -> float:
    """Quartic ease out."""
    t = clamp(t)
    return 1 - (1 - t) ** 4


def ease_in_out_quart(t: float) -> float:
    """Quartic ease in-out."""
    t = clamp(t)
    if t < 0.5:
        return 8 * t * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 4 / 2


# =============================================================================
# Quintic (Power of 5)
# =============================================================================

def ease_in_quint(t: float) -> float:
    """Quintic ease in."""
    t = clamp(t)
    return t * t * t * t * t


def ease_out_quint(t: float) -> float:
    """Quintic ease out."""
    t = clamp(t)
    return 1 - (1 - t) ** 5


def ease_in_out_quint(t: float) -> float:
    """Quintic ease in-out."""
    t = clamp(t)
    if t < 0.5:
        return 16 * t * t * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 5 / 2


# =============================================================================
# Sinusoidal
# =============================================================================

def ease_in_sine(t: float) -> float:
    """Sinusoidal ease in."""
    t = clamp(t)
    return 1 - math.cos(t * math.pi / 2)


def ease_out_sine(t: float) -> float:
    """Sinusoidal ease out."""
    t = clamp(t)
    return math.sin(t * math.pi / 2)


def ease_in_out_sine(t: float) -> float:
    """Sinusoidal ease in-out."""
    t = clamp(t)
    return -(math.cos(math.pi * t) - 1) / 2


# =============================================================================
# Exponential
# =============================================================================

def ease_in_expo(t: float) -> float:
    """Exponential ease in."""
    t = clamp(t)
    if t == 0:
        return 0
    return 2 ** (10 * t - 10)


def ease_out_expo(t: float) -> float:
    """Exponential ease out."""
    t = clamp(t)
    if t == 1:
        return 1
    return 1 - 2 ** (-10 * t)


def ease_in_out_expo(t: float) -> float:
    """Exponential ease in-out."""
    t = clamp(t)
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return 2 ** (20 * t - 10) / 2
    else:
        return (2 - 2 ** (-20 * t + 10)) / 2


# =============================================================================
# Circular
# =============================================================================

def ease_in_circ(t: float) -> float:
    """Circular ease in."""
    t = clamp(t)
    return 1 - math.sqrt(1 - t * t)


def ease_out_circ(t: float) -> float:
    """Circular ease out."""
    t = clamp(t)
    return math.sqrt(1 - (t - 1) ** 2)


def ease_in_out_circ(t: float) -> float:
    """Circular ease in-out."""
    t = clamp(t)
    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t) ** 2)) / 2
    else:
        return (math.sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2


# =============================================================================
# Back (Overshooting)
# =============================================================================

def ease_in_back(t: float) -> float:
    """Back ease in - slight overshoot at start."""
    t = clamp(t)
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t


def ease_out_back(t: float) -> float:
    """Back ease out - slight overshoot at end."""
    t = clamp(t)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_in_out_back(t: float) -> float:
    """Back ease in-out."""
    t = clamp(t)
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    else:
        return ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2


# =============================================================================
# Elastic
# =============================================================================

def ease_in_elastic(t: float) -> float:
    """Elastic ease in - springy start."""
    t = clamp(t)
    if t == 0:
        return 0
    if t == 1:
        return 1
    c4 = (2 * math.pi) / 3
    return -2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * c4)


def ease_out_elastic(t: float) -> float:
    """Elastic ease out - springy end."""
    t = clamp(t)
    if t == 0:
        return 0
    if t == 1:
        return 1
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_out_elastic(t: float) -> float:
    """Elastic ease in-out."""
    t = clamp(t)
    if t == 0:
        return 0
    if t == 1:
        return 1
    c5 = (2 * math.pi) / 4.5
    if t < 0.5:
        return -(2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    else:
        return (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1


# =============================================================================
# Bounce
# =============================================================================

def ease_out_bounce(t: float) -> float:
    """Bounce ease out - bouncing ball effect."""
    t = clamp(t)
    n1 = 7.5625
    d1 = 2.75

    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_in_bounce(t: float) -> float:
    """Bounce ease in."""
    return 1 - ease_out_bounce(1 - t)


def ease_in_out_bounce(t: float) -> float:
    """Bounce ease in-out."""
    t = clamp(t)
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + ease_out_bounce(2 * t - 1)) / 2


# =============================================================================
# Special Animation Curves
# =============================================================================

def step(t: float) -> float:
    """Step function - instant transition at 0.5."""
    return 0.0 if t < 0.5 else 1.0


def step_start(t: float) -> float:
    """Step at start - instant transition at 0."""
    return 0.0 if t <= 0 else 1.0


def step_end(t: float) -> float:
    """Step at end - instant transition at 1."""
    return 1.0 if t >= 1 else 0.0


def ping_pong(t: float) -> float:
    """Ping pong - goes 0->1->0."""
    t = clamp(t)
    if t < 0.5:
        return t * 2
    else:
        return 2 - t * 2


def smooth_step(t: float) -> float:
    """Smooth step (Hermite interpolation)."""
    t = clamp(t)
    return t * t * (3 - 2 * t)


def smoother_step(t: float) -> float:
    """Smoother step (Ken Perlin's improved version)."""
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


# =============================================================================
# Easing Registry
# =============================================================================

EASING_FUNCTIONS: Dict[str, EasingFunc] = {
    # Linear
    'linear': linear,

    # Quadratic
    'ease_in': ease_in_quad,
    'ease_out': ease_out_quad,
    'ease_in_out': ease_in_out_quad,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_out_quad': ease_in_out_quad,

    # Cubic
    'ease_in_cubic': ease_in_cubic,
    'ease_out_cubic': ease_out_cubic,
    'ease_in_out_cubic': ease_in_out_cubic,

    # Quartic
    'ease_in_quart': ease_in_quart,
    'ease_out_quart': ease_out_quart,
    'ease_in_out_quart': ease_in_out_quart,

    # Quintic
    'ease_in_quint': ease_in_quint,
    'ease_out_quint': ease_out_quint,
    'ease_in_out_quint': ease_in_out_quint,

    # Sinusoidal
    'ease_in_sine': ease_in_sine,
    'ease_out_sine': ease_out_sine,
    'ease_in_out_sine': ease_in_out_sine,

    # Exponential
    'ease_in_expo': ease_in_expo,
    'ease_out_expo': ease_out_expo,
    'ease_in_out_expo': ease_in_out_expo,

    # Circular
    'ease_in_circ': ease_in_circ,
    'ease_out_circ': ease_out_circ,
    'ease_in_out_circ': ease_in_out_circ,

    # Back
    'ease_in_back': ease_in_back,
    'ease_out_back': ease_out_back,
    'ease_in_out_back': ease_in_out_back,

    # Elastic
    'ease_in_elastic': ease_in_elastic,
    'ease_out_elastic': ease_out_elastic,
    'ease_in_out_elastic': ease_in_out_elastic,

    # Bounce
    'ease_in_bounce': ease_in_bounce,
    'ease_out_bounce': ease_out_bounce,
    'ease_in_out_bounce': ease_in_out_bounce,
    'bounce': ease_out_bounce,

    # Special
    'step': step,
    'step_start': step_start,
    'step_end': step_end,
    'ping_pong': ping_pong,
    'smooth_step': smooth_step,
    'smoother_step': smoother_step,
}


def get_easing(name: str) -> EasingFunc:
    """Get easing function by name.

    Args:
        name: Easing function name

    Returns:
        Easing function

    Raises:
        KeyError: If name not found
    """
    if name not in EASING_FUNCTIONS:
        available = ', '.join(sorted(EASING_FUNCTIONS.keys()))
        raise KeyError(f"Unknown easing '{name}'. Available: {available}")
    return EASING_FUNCTIONS[name]


def apply_easing(t: float, easing: str) -> float:
    """Apply named easing function to value.

    Args:
        t: Input value 0-1
        easing: Easing function name

    Returns:
        Eased value 0-1
    """
    func = EASING_FUNCTIONS.get(easing, linear)
    return func(t)


def list_easings() -> list:
    """Get list of available easing function names."""
    return sorted(EASING_FUNCTIONS.keys())
