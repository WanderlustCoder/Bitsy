"""
Vehicle Generator - Pixel art vehicles for games.

Provides generators for various vehicle types:
- Cars (sedan, sports, truck, van)
- Ships (sailboat, speedboat, warship)
- Aircraft (plane, helicopter, jet)
- Spaceships (fighter, cruiser, shuttle)
"""

import random
from typing import Optional, List, Dict, Callable
from enum import Enum

from core import Canvas
from core.png_writer import Color


class VehicleType(Enum):
    """Types of vehicles that can be generated."""
    CAR = "car"
    SHIP = "ship"
    AIRCRAFT = "aircraft"
    SPACESHIP = "spaceship"


class VehiclePalette:
    """Color palette for vehicles."""

    def __init__(self, body: Color, highlight: Color, shadow: Color,
                 accent: Color, window: Color = (100, 150, 200, 255)):
        self.body = body
        self.highlight = highlight
        self.shadow = shadow
        self.accent = accent
        self.window = window

    @classmethod
    def car_red(cls) -> 'VehiclePalette':
        """Red car colors."""
        return cls(
            body=(200, 50, 50, 255),
            highlight=(240, 100, 100, 255),
            shadow=(140, 30, 30, 255),
            accent=(60, 60, 60, 255),
            window=(100, 150, 200, 255)
        )

    @classmethod
    def car_blue(cls) -> 'VehiclePalette':
        """Blue car colors."""
        return cls(
            body=(50, 100, 200, 255),
            highlight=(100, 150, 240, 255),
            shadow=(30, 60, 140, 255),
            accent=(60, 60, 60, 255),
            window=(100, 150, 200, 255)
        )

    @classmethod
    def car_white(cls) -> 'VehiclePalette':
        """White car colors."""
        return cls(
            body=(240, 240, 240, 255),
            highlight=(255, 255, 255, 255),
            shadow=(180, 180, 180, 255),
            accent=(60, 60, 60, 255),
            window=(100, 150, 200, 255)
        )

    @classmethod
    def military(cls) -> 'VehiclePalette':
        """Military green/camo colors."""
        return cls(
            body=(80, 100, 60, 255),
            highlight=(110, 130, 90, 255),
            shadow=(50, 70, 40, 255),
            accent=(60, 60, 50, 255),
            window=(80, 100, 80, 255)
        )

    @classmethod
    def spaceship(cls) -> 'VehiclePalette':
        """Sci-fi spaceship colors."""
        return cls(
            body=(180, 180, 190, 255),
            highlight=(220, 220, 230, 255),
            shadow=(120, 120, 130, 255),
            accent=(100, 150, 200, 255),
            window=(50, 200, 255, 255)
        )

    @classmethod
    def wooden_ship(cls) -> 'VehiclePalette':
        """Wooden ship colors."""
        return cls(
            body=(139, 90, 43, 255),
            highlight=(181, 137, 77, 255),
            shadow=(101, 67, 33, 255),
            accent=(240, 230, 200, 255),  # sail color
            window=(101, 67, 33, 255)
        )


class VehicleGenerator:
    """Generator for pixel art vehicles."""

    def __init__(self, width: int, height: int, seed: int = 42):
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.palette = VehiclePalette.car_red()

    def set_palette(self, palette: VehiclePalette) -> None:
        """Set the color palette."""
        self.palette = palette

    def generate_car(self, style: str = 'sedan', view: str = 'side') -> Canvas:
        """Generate a car sprite.

        Args:
            style: Car style ('sedan', 'sports', 'truck', 'van')
            view: View angle ('side', 'top')

        Returns:
            Canvas with car sprite
        """
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))
        self.rng = random.Random(self.seed)

        if view == 'top':
            return self._draw_car_top(canvas, style)
        return self._draw_car_side(canvas, style)

    def _draw_car_side(self, canvas: Canvas, style: str) -> Canvas:
        """Draw side-view car."""
        w, h = self.width, self.height

        # Calculate proportions based on style
        if style == 'sports':
            body_height = h // 3
            roof_height = h // 4
            wheel_r = max(2, h // 6)
        elif style == 'truck':
            body_height = h // 2
            roof_height = h // 4
            wheel_r = max(2, h // 5)
        elif style == 'van':
            body_height = h * 2 // 5
            roof_height = h // 3
            wheel_r = max(2, h // 6)
        else:  # sedan
            body_height = h // 3
            roof_height = h // 4
            wheel_r = max(2, h // 6)

        ground_y = h - wheel_r - 2
        body_y = ground_y - body_height

        # Draw body
        body_left = wheel_r + 1
        body_right = w - wheel_r - 2

        for y in range(body_y, ground_y):
            for x in range(body_left, body_right):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Add body shading
        for y in range(body_y, body_y + 2):
            for x in range(body_left, body_right):
                canvas.set_pixel_solid(x, y, self.palette.highlight)
        for y in range(ground_y - 2, ground_y):
            for x in range(body_left, body_right):
                canvas.set_pixel_solid(x, y, self.palette.shadow)

        # Draw roof/cabin based on style
        if style == 'truck':
            # Truck has cab at front
            cab_width = w // 3
            roof_left = body_right - cab_width
            roof_y = body_y - roof_height
            for y in range(roof_y, body_y):
                for x in range(roof_left, body_right):
                    canvas.set_pixel_solid(x, y, self.palette.body)
            # Window
            for y in range(roof_y + 2, body_y - 1):
                for x in range(roof_left + 2, body_right - 2):
                    canvas.set_pixel_solid(x, y, self.palette.window)
        elif style == 'van':
            # Van has tall rectangular cabin
            roof_y = body_y - roof_height
            for y in range(roof_y, body_y):
                for x in range(body_left + 2, body_right - 2):
                    canvas.set_pixel_solid(x, y, self.palette.body)
            # Windows
            win_y = roof_y + 2
            for y in range(win_y, body_y - 1):
                for x in range(body_left + 4, body_right - 4):
                    if (x - body_left) % 6 < 4:  # Multiple windows
                        canvas.set_pixel_solid(x, y, self.palette.window)
        else:
            # Sedan/sports have curved roof
            roof_y = body_y - roof_height
            roof_left = body_left + w // 6
            roof_right = body_right - w // 6
            for y in range(roof_y, body_y):
                for x in range(roof_left, roof_right):
                    canvas.set_pixel_solid(x, y, self.palette.body)
            # Windshield slopes
            for i in range(min(3, roof_height)):
                canvas.set_pixel_solid(roof_left - i, roof_y + i, self.palette.body)
                canvas.set_pixel_solid(roof_right + i, roof_y + i, self.palette.body)
            # Window
            for y in range(roof_y + 1, body_y - 1):
                for x in range(roof_left + 1, roof_right - 1):
                    canvas.set_pixel_solid(x, y, self.palette.window)

        # Draw wheels
        wheel_y = ground_y
        wheel1_x = body_left + wheel_r
        wheel2_x = body_right - wheel_r - 1

        for dy in range(-wheel_r, wheel_r + 1):
            for dx in range(-wheel_r, wheel_r + 1):
                if dx * dx + dy * dy <= wheel_r * wheel_r:
                    # Tire (dark)
                    canvas.set_pixel_solid(wheel1_x + dx, wheel_y + dy, self.palette.accent)
                    canvas.set_pixel_solid(wheel2_x + dx, wheel_y + dy, self.palette.accent)
                    # Hub (lighter)
                    if dx * dx + dy * dy <= (wheel_r // 2) ** 2:
                        canvas.set_pixel_solid(wheel1_x + dx, wheel_y + dy, self.palette.shadow)
                        canvas.set_pixel_solid(wheel2_x + dx, wheel_y + dy, self.palette.shadow)

        return canvas

    def _draw_car_top(self, canvas: Canvas, style: str) -> Canvas:
        """Draw top-down view car."""
        w, h = self.width, self.height

        # Body dimensions
        body_w = w * 2 // 3
        body_h = h - 4
        body_x = (w - body_w) // 2
        body_y = 2

        # Draw body
        for y in range(body_y, body_y + body_h):
            for x in range(body_x, body_x + body_w):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Round the corners
        for corner in [(body_x, body_y), (body_x + body_w - 1, body_y),
                       (body_x, body_y + body_h - 1), (body_x + body_w - 1, body_y + body_h - 1)]:
            canvas.set_pixel_solid(corner[0], corner[1], (0, 0, 0, 0))

        # Window/roof area
        win_margin = max(2, body_w // 4)
        for y in range(body_y + 3, body_y + body_h - 3):
            for x in range(body_x + win_margin, body_x + body_w - win_margin):
                canvas.set_pixel_solid(x, y, self.palette.window)

        # Wheels (small rectangles on sides)
        wheel_w = 2
        wheel_h = max(2, body_h // 4)
        # Front wheels
        for y in range(body_y + 2, body_y + 2 + wheel_h):
            for x in range(body_x - wheel_w, body_x):
                canvas.set_pixel_solid(x, y, self.palette.accent)
            for x in range(body_x + body_w, body_x + body_w + wheel_w):
                canvas.set_pixel_solid(x, y, self.palette.accent)
        # Rear wheels
        for y in range(body_y + body_h - wheel_h - 2, body_y + body_h - 2):
            for x in range(body_x - wheel_w, body_x):
                canvas.set_pixel_solid(x, y, self.palette.accent)
            for x in range(body_x + body_w, body_x + body_w + wheel_w):
                canvas.set_pixel_solid(x, y, self.palette.accent)

        return canvas

    def generate_ship(self, style: str = 'sailboat', view: str = 'side') -> Canvas:
        """Generate a ship sprite.

        Args:
            style: Ship style ('sailboat', 'speedboat', 'warship')
            view: View angle ('side', 'top')

        Returns:
            Canvas with ship sprite
        """
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))
        self.rng = random.Random(self.seed)

        if view == 'top':
            return self._draw_ship_top(canvas, style)
        return self._draw_ship_side(canvas, style)

    def _draw_ship_side(self, canvas: Canvas, style: str) -> Canvas:
        """Draw side-view ship."""
        w, h = self.width, self.height

        # Hull dimensions
        hull_height = h // 3
        hull_y = h - hull_height - 2
        water_y = h - 2

        # Draw hull (boat shape)
        for y in range(hull_y, water_y):
            # Hull narrows toward bottom
            t = (y - hull_y) / max(hull_height - 1, 1)
            indent = int(t * w // 6)
            for x in range(indent + 1, w - indent - 1):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Hull shading
        for x in range(2, w - 2):
            canvas.set_pixel_solid(x, hull_y, self.palette.highlight)
            canvas.set_pixel_solid(x, water_y - 1, self.palette.shadow)

        if style == 'sailboat':
            # Draw mast and sail
            mast_x = w // 2
            mast_top = 2
            mast_bottom = hull_y

            # Mast
            for y in range(mast_top, mast_bottom):
                canvas.set_pixel_solid(mast_x, y, self.palette.shadow)

            # Sail (triangle)
            sail_width = w // 3
            for y in range(mast_top + 1, hull_y - 2):
                t = (y - mast_top) / (hull_y - mast_top - 3)
                sail_x = int(sail_width * (1 - t))
                for x in range(mast_x + 1, mast_x + 1 + sail_x):
                    canvas.set_pixel_solid(x, y, self.palette.accent)

        elif style == 'speedboat':
            # Low profile with windshield
            cabin_h = h // 6
            cabin_y = hull_y - cabin_h
            cabin_w = w // 3
            cabin_x = w // 3

            for y in range(cabin_y, hull_y):
                for x in range(cabin_x, cabin_x + cabin_w):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Windshield
            for y in range(cabin_y + 1, hull_y - 1):
                for x in range(cabin_x + 1, cabin_x + cabin_w - 1):
                    canvas.set_pixel_solid(x, y, self.palette.window)

        elif style == 'warship':
            # Superstructure
            super_h = h // 4
            super_y = hull_y - super_h
            super_w = w // 2
            super_x = w // 4

            for y in range(super_y, hull_y):
                for x in range(super_x, super_x + super_w):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Bridge/tower
            tower_h = h // 6
            tower_w = w // 6
            tower_x = w // 2 - tower_w // 2
            for y in range(super_y - tower_h, super_y):
                for x in range(tower_x, tower_x + tower_w):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Gun turret
            gun_x = w // 6
            gun_y = hull_y - 2
            for x in range(gun_x, gun_x + 4):
                canvas.set_pixel_solid(x, gun_y, self.palette.shadow)
                canvas.set_pixel_solid(x, gun_y - 1, self.palette.shadow)

        return canvas

    def _draw_ship_top(self, canvas: Canvas, style: str) -> Canvas:
        """Draw top-down ship."""
        w, h = self.width, self.height

        # Hull (pointed oval shape)
        cx, cy = w // 2, h // 2
        for y in range(h):
            for x in range(w):
                # Ellipse check with pointed bow
                dy = (y - cy) / (h // 2)
                dx = (x - cx) / (w // 2)
                # Make front pointed
                if dy < 0:
                    dy = dy * 1.5
                if dx * dx + dy * dy <= 1.0:
                    canvas.set_pixel_solid(x, y, self.palette.body)

        return canvas

    def generate_aircraft(self, style: str = 'plane', view: str = 'side') -> Canvas:
        """Generate an aircraft sprite.

        Args:
            style: Aircraft style ('plane', 'helicopter', 'jet')
            view: View angle ('side', 'top')

        Returns:
            Canvas with aircraft sprite
        """
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))
        self.rng = random.Random(self.seed)

        if view == 'top':
            return self._draw_aircraft_top(canvas, style)
        return self._draw_aircraft_side(canvas, style)

    def _draw_aircraft_side(self, canvas: Canvas, style: str) -> Canvas:
        """Draw side-view aircraft."""
        w, h = self.width, self.height

        if style == 'helicopter':
            # Fuselage
            body_h = h // 3
            body_y = h // 2 - body_h // 2
            body_w = w * 2 // 3
            body_x = w // 6

            for y in range(body_y, body_y + body_h):
                for x in range(body_x, body_x + body_w):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Tail boom
            tail_h = max(2, body_h // 2)
            tail_y = body_y + body_h // 4
            for y in range(tail_y, tail_y + tail_h):
                for x in range(1, body_x):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Main rotor
            rotor_y = body_y - 2
            for x in range(2, w - 2):
                canvas.set_pixel_solid(x, rotor_y, self.palette.shadow)

            # Tail rotor
            for y in range(tail_y - 2, tail_y + tail_h + 2):
                canvas.set_pixel_solid(2, y, self.palette.shadow)

            # Cockpit window
            for y in range(body_y + 1, body_y + body_h - 1):
                for x in range(body_x + body_w - 4, body_x + body_w - 1):
                    canvas.set_pixel_solid(x, y, self.palette.window)

        else:  # plane or jet
            # Fuselage
            body_h = max(3, h // 4)
            body_y = h // 2 - body_h // 2
            nose_x = w - 4
            tail_x = 2

            for y in range(body_y, body_y + body_h):
                for x in range(tail_x, nose_x):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Nose cone (pointed)
            for i in range(3):
                for y in range(body_y + i, body_y + body_h - i):
                    canvas.set_pixel_solid(nose_x + i, y, self.palette.body)

            # Wings
            wing_y = body_y + body_h // 2
            wing_h = h // 3
            wing_w = w // 3
            wing_x = w // 3

            for y in range(wing_y - wing_h // 2, wing_y + wing_h // 2 + 1):
                for x in range(wing_x, wing_x + wing_w):
                    # Taper wings
                    t = abs(y - wing_y) / (wing_h // 2 + 0.1)
                    if x < wing_x + wing_w * (1 - t * 0.5):
                        canvas.set_pixel_solid(x, y, self.palette.body)

            # Tail fin
            fin_h = h // 4
            for y in range(body_y - fin_h, body_y):
                canvas.set_pixel_solid(tail_x + 2, y, self.palette.body)
                canvas.set_pixel_solid(tail_x + 3, y, self.palette.body)

            # Cockpit
            for y in range(body_y + 1, body_y + body_h - 1):
                for x in range(nose_x - 4, nose_x - 1):
                    canvas.set_pixel_solid(x, y, self.palette.window)

            # Jet engines (for jet style)
            if style == 'jet':
                engine_y = body_y + body_h
                for x in range(tail_x, tail_x + 4):
                    canvas.set_pixel_solid(x, engine_y, self.palette.shadow)
                    canvas.set_pixel_solid(x, engine_y + 1, self.palette.accent)

        return canvas

    def _draw_aircraft_top(self, canvas: Canvas, style: str) -> Canvas:
        """Draw top-down aircraft."""
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2

        # Fuselage
        fuse_w = w // 5
        for y in range(2, h - 2):
            for x in range(cx - fuse_w // 2, cx + fuse_w // 2 + 1):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Wings
        wing_y = cy
        wing_span = w // 2 - 2
        wing_chord = h // 4
        for y in range(wing_y - wing_chord // 2, wing_y + wing_chord // 2):
            for x in range(cx - wing_span, cx + wing_span + 1):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Tail
        tail_y = h - 4
        tail_span = w // 4
        for x in range(cx - tail_span, cx + tail_span + 1):
            canvas.set_pixel_solid(x, tail_y, self.palette.body)
            canvas.set_pixel_solid(x, tail_y + 1, self.palette.body)

        return canvas

    def generate_spaceship(self, style: str = 'fighter', view: str = 'side') -> Canvas:
        """Generate a spaceship sprite.

        Args:
            style: Spaceship style ('fighter', 'cruiser', 'shuttle')
            view: View angle ('side', 'top')

        Returns:
            Canvas with spaceship sprite
        """
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))
        self.rng = random.Random(self.seed)

        if view == 'top':
            return self._draw_spaceship_top(canvas, style)
        return self._draw_spaceship_side(canvas, style)

    def _draw_spaceship_side(self, canvas: Canvas, style: str) -> Canvas:
        """Draw side-view spaceship."""
        w, h = self.width, self.height
        cy = h // 2

        if style == 'fighter':
            # Sleek fighter craft
            body_h = max(3, h // 4)

            # Main body (tapered)
            for x in range(2, w - 2):
                t = x / w
                half_h = int(body_h * (0.3 + 0.7 * (1 - abs(t - 0.3) * 2)))
                for y in range(cy - half_h, cy + half_h + 1):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Cockpit
            cockpit_x = w * 2 // 3
            for y in range(cy - 1, cy + 2):
                for x in range(cockpit_x, cockpit_x + 3):
                    canvas.set_pixel_solid(x, y, self.palette.window)

            # Engine glow
            for y in range(cy - 1, cy + 2):
                canvas.set_pixel_solid(1, y, self.palette.accent)

            # Wings
            wing_x = w // 3
            for i in range(h // 4):
                canvas.set_pixel_solid(wing_x + i, cy - body_h - i, self.palette.body)
                canvas.set_pixel_solid(wing_x + i, cy + body_h + i, self.palette.body)

        elif style == 'cruiser':
            # Large capital ship
            body_h = h // 3

            for y in range(cy - body_h, cy + body_h):
                for x in range(4, w - 2):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Bridge tower
            bridge_h = body_h // 2
            bridge_x = w // 2
            for y in range(cy - body_h - bridge_h, cy - body_h):
                for x in range(bridge_x, bridge_x + w // 6):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Engine block
            for y in range(cy - body_h + 2, cy + body_h - 2):
                canvas.set_pixel_solid(2, y, self.palette.accent)
                canvas.set_pixel_solid(3, y, self.palette.shadow)

        else:  # shuttle
            # Rounded shuttle shape
            body_h = h // 3
            body_w = w - 8

            for y in range(cy - body_h, cy + body_h):
                for x in range(4, 4 + body_w):
                    canvas.set_pixel_solid(x, y, self.palette.body)

            # Rounded nose
            for i in range(3):
                for y in range(cy - body_h + i + 1, cy + body_h - i - 1):
                    canvas.set_pixel_solid(4 + body_w + i, y, self.palette.body)

            # Cargo bay doors (lines)
            for y in range(cy - body_h + 2, cy + body_h - 2, 3):
                for x in range(6, 4 + body_w - 2):
                    canvas.set_pixel_solid(x, y, self.palette.shadow)

            # Engines
            for y in range(cy - 2, cy + 3):
                canvas.set_pixel_solid(2, y, self.palette.accent)
                canvas.set_pixel_solid(3, y, self.palette.shadow)

        return canvas

    def _draw_spaceship_top(self, canvas: Canvas, style: str) -> Canvas:
        """Draw top-down spaceship."""
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2

        # Arrow/delta shape
        for y in range(2, h - 2):
            t = (y - 2) / (h - 4)
            half_w = int((w // 2 - 2) * (1 - t))
            for x in range(cx - half_w, cx + half_w + 1):
                canvas.set_pixel_solid(x, y, self.palette.body)

        # Cockpit
        for y in range(3, 6):
            for x in range(cx - 1, cx + 2):
                canvas.set_pixel_solid(x, y, self.palette.window)

        # Engines at rear
        for x in range(cx - 2, cx + 3):
            canvas.set_pixel_solid(x, h - 3, self.palette.accent)

        return canvas


# Registry of vehicle generators
VEHICLE_GENERATORS: Dict[str, Callable] = {}


def _register_generators():
    """Register all vehicle type generators."""
    global VEHICLE_GENERATORS
    VEHICLE_GENERATORS = {
        'car': lambda gen, **kw: gen.generate_car(**kw),
        'car_sedan': lambda gen, **kw: gen.generate_car(style='sedan', **kw),
        'car_sports': lambda gen, **kw: gen.generate_car(style='sports', **kw),
        'car_truck': lambda gen, **kw: gen.generate_car(style='truck', **kw),
        'car_van': lambda gen, **kw: gen.generate_car(style='van', **kw),
        'ship': lambda gen, **kw: gen.generate_ship(**kw),
        'ship_sailboat': lambda gen, **kw: gen.generate_ship(style='sailboat', **kw),
        'ship_speedboat': lambda gen, **kw: gen.generate_ship(style='speedboat', **kw),
        'ship_warship': lambda gen, **kw: gen.generate_ship(style='warship', **kw),
        'aircraft': lambda gen, **kw: gen.generate_aircraft(**kw),
        'aircraft_plane': lambda gen, **kw: gen.generate_aircraft(style='plane', **kw),
        'aircraft_helicopter': lambda gen, **kw: gen.generate_aircraft(style='helicopter', **kw),
        'aircraft_jet': lambda gen, **kw: gen.generate_aircraft(style='jet', **kw),
        'spaceship': lambda gen, **kw: gen.generate_spaceship(**kw),
        'spaceship_fighter': lambda gen, **kw: gen.generate_spaceship(style='fighter', **kw),
        'spaceship_cruiser': lambda gen, **kw: gen.generate_spaceship(style='cruiser', **kw),
        'spaceship_shuttle': lambda gen, **kw: gen.generate_spaceship(style='shuttle', **kw),
    }


_register_generators()


def list_vehicle_types() -> List[str]:
    """List all available vehicle types."""
    return sorted(VEHICLE_GENERATORS.keys())


def generate_vehicle(vehicle_type: str,
                     width: int = 32,
                     height: int = 24,
                     seed: int = 42,
                     palette: Optional[VehiclePalette] = None,
                     **kwargs) -> Canvas:
    """Generate a vehicle of the specified type.

    Args:
        vehicle_type: Type of vehicle to generate
        width: Vehicle width in pixels
        height: Vehicle height in pixels
        seed: Random seed for deterministic generation
        palette: Optional color palette
        **kwargs: Additional arguments (view='side'|'top')

    Returns:
        Canvas with vehicle sprite

    Raises:
        ValueError: If vehicle_type is not recognized
    """
    if vehicle_type not in VEHICLE_GENERATORS:
        available = ', '.join(sorted(VEHICLE_GENERATORS.keys()))
        raise ValueError(f"Unknown vehicle type '{vehicle_type}'. Available: {available}")

    gen = VehicleGenerator(width, height, seed)

    # Set palette based on vehicle type if not provided
    if palette:
        gen.set_palette(palette)
    else:
        palette_map = {
            'car': VehiclePalette.car_red,
            'car_sedan': VehiclePalette.car_red,
            'car_sports': VehiclePalette.car_red,
            'car_truck': VehiclePalette.car_blue,
            'car_van': VehiclePalette.car_white,
            'ship': VehiclePalette.wooden_ship,
            'ship_sailboat': VehiclePalette.wooden_ship,
            'ship_speedboat': VehiclePalette.car_white,
            'ship_warship': VehiclePalette.military,
            'aircraft': VehiclePalette.car_white,
            'aircraft_plane': VehiclePalette.car_white,
            'aircraft_helicopter': VehiclePalette.military,
            'aircraft_jet': VehiclePalette.military,
            'spaceship': VehiclePalette.spaceship,
            'spaceship_fighter': VehiclePalette.spaceship,
            'spaceship_cruiser': VehiclePalette.spaceship,
            'spaceship_shuttle': VehiclePalette.car_white,
        }
        if vehicle_type in palette_map:
            gen.set_palette(palette_map[vehicle_type]())

    return VEHICLE_GENERATORS[vehicle_type](gen, **kwargs)


__all__ = [
    'VehicleType',
    'VehiclePalette',
    'VehicleGenerator',
    'generate_vehicle',
    'list_vehicle_types',
    'VEHICLE_GENERATORS',
]
