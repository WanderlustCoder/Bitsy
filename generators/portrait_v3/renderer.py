"""
Procedural portrait renderer using SDFs and proper lighting.
"""

import math
from typing import Tuple, List, Optional
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas


@dataclass
class Light:
    """Directional light source."""
    direction: Tuple[float, float, float]  # normalized (x, y, z)
    intensity: float = 1.0


class SDF:
    """Signed Distance Field utilities for smooth shape rendering."""

    @staticmethod
    def circle(px: float, py: float, cx: float, cy: float, radius: float) -> float:
        """SDF for a circle. Negative inside, positive outside."""
        dx = px - cx
        dy = py - cy
        return math.sqrt(dx * dx + dy * dy) - radius

    @staticmethod
    def ellipse(px: float, py: float, cx: float, cy: float,
                rx: float, ry: float) -> float:
        """SDF for an ellipse (approximation)."""
        # Normalize to unit circle space
        dx = (px - cx) / rx
        dy = (py - cy) / ry
        dist = math.sqrt(dx * dx + dy * dy)
        # Scale back - this is an approximation but works well
        return (dist - 1.0) * min(rx, ry)

    @staticmethod
    def rounded_rect(px: float, py: float, cx: float, cy: float,
                     w: float, h: float, r: float) -> float:
        """SDF for a rounded rectangle."""
        dx = abs(px - cx) - w + r
        dy = abs(py - cy) - h + r
        outside = math.sqrt(max(dx, 0)**2 + max(dy, 0)**2) - r
        inside = min(max(dx, dy), 0)
        return outside + inside

    @staticmethod
    def smooth_union(d1: float, d2: float, k: float = 0.5) -> float:
        """Smooth union of two SDFs."""
        h = max(k - abs(d1 - d2), 0) / k
        return min(d1, d2) - h * h * k * 0.25

    @staticmethod
    def smooth_subtract(d1: float, d2: float, k: float = 0.5) -> float:
        """Smooth subtraction: d1 minus d2."""
        return SDF.smooth_union(d1, -d2, k)


class ProceduralPortraitRenderer:
    """
    Renders anime-style portraits procedurally with proper lighting.

    Phase 1: Grayscale face with lighting
    """

    def __init__(
        self,
        width: int = 64,
        height: int = 96,
        # Light settings - softer for cute aesthetic
        light_dir: Tuple[float, float, float] = (-0.4, -0.2, 0.9),
        ambient: float = 0.5,  # Higher ambient for softer shading
        # Face parameters
        face_y_offset: float = 0.0,  # -1 to 1, shift face up/down
    ):
        self.width = width
        self.height = height
        self.ambient = ambient
        self.face_y_offset = face_y_offset

        # Normalize light direction
        lx, ly, lz = light_dir
        mag = math.sqrt(lx*lx + ly*ly + lz*lz)
        self.light = Light(direction=(lx/mag, ly/mag, lz/mag))

    def render(self) -> Canvas:
        """Render a grayscale face with proper lighting."""
        canvas = Canvas(self.width, self.height)

        # Face center (positioned for portrait framing with forehead visible)
        face_cx = self.width / 2
        face_cy = self.height * 0.42 + (self.face_y_offset * self.height * 0.1)

        # Face dimensions - soft oval, slightly taller than wide
        face_rx = self.width * 0.36  # horizontal radius
        face_ry = self.height * 0.26  # vertical radius (taller than wide)

        # Render each pixel
        for y in range(self.height):
            for x in range(self.width):
                color = self._shade_pixel(x + 0.5, y + 0.5, face_cx, face_cy, face_rx, face_ry)
                if color is not None:
                    canvas.set_pixel_solid(x, y, color)

        return canvas

    def _shade_pixel(
        self,
        px: float, py: float,
        face_cx: float, face_cy: float,
        face_rx: float, face_ry: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Calculate shading for a single pixel."""

        # Check if pixel is an eye (render differently)
        eye_color = self._get_eye_color(px, py, face_cx, face_cy, face_rx, face_ry)
        if eye_color is not None:
            return eye_color

        # Check if pixel is mouth
        mouth_color = self._get_mouth_color(px, py, face_cx, face_cy, face_rx, face_ry)
        if mouth_color is not None:
            return mouth_color

        # Check if pixel is nose highlight/detail
        nose_color = self._get_nose_color(px, py, face_cx, face_cy, face_rx, face_ry)
        if nose_color is not None:
            return nose_color

        # Check if pixel is eyebrow
        brow_color = self._get_eyebrow_color(px, py, face_cx, face_cy, face_rx, face_ry)
        if brow_color is not None:
            return brow_color

        # Get distance to face shape
        face_dist = self._face_sdf(px, py, face_cx, face_cy, face_rx, face_ry)

        # Anti-aliasing: smooth edge over ~1.5 pixels
        if face_dist > 1.5:
            return None  # Outside face

        # Calculate alpha for anti-aliased edge
        if face_dist > -0.5:
            alpha = int(255 * (1.0 - (face_dist + 0.5) / 2.0))
            alpha = max(0, min(255, alpha))
        else:
            alpha = 255

        # Calculate surface normal for lighting (approximate from SDF gradient)
        normal = self._estimate_normal(px, py, face_cx, face_cy, face_rx, face_ry)

        # Calculate lighting
        light_value = self._calculate_lighting(normal, px, py, face_cx, face_cy, face_rx, face_ry)

        # Apply eye socket darkening
        light_value = self._apply_eye_sockets(light_value, px, py, face_cx, face_cy, face_rx, face_ry)

        # Apply nose shadow
        light_value = self._apply_nose_shadow(light_value, px, py, face_cx, face_cy, face_rx, face_ry)

        # Convert to grayscale
        gray = int(255 * light_value)
        gray = max(0, min(255, gray))

        return (gray, gray, gray, alpha)

    def _face_sdf(
        self,
        px: float, py: float,
        cx: float, cy: float,
        rx: float, ry: float
    ) -> float:
        """SDF for face shape - inverted egg with soft cheeks tapering to chin."""
        # Calculate vertical position relative to face center
        rel_y = (py - cy) / ry  # -1 at top, +1 at bottom

        # Width varies by vertical position:
        # - Full width at forehead/upper face
        # - Slight cheek fullness in middle
        # - Taper to smaller chin at bottom

        if rel_y < -0.3:
            # Upper face / forehead area - full width
            width_factor = 1.0
        elif rel_y < 0.2:
            # Cheek area - slight fullness
            cheek_pos = (rel_y + 0.3) / 0.5  # 0 to 1 through cheek zone
            width_factor = 1.0 + 0.05 * math.sin(cheek_pos * math.pi)  # Gentle bulge
        else:
            # Chin area - taper down
            chin_pos = (rel_y - 0.2) / 0.8  # 0 to 1 toward chin
            chin_pos = min(chin_pos, 1.0)
            width_factor = 1.0 - chin_pos * 0.25  # Taper to 75% width at chin

        local_rx = rx * width_factor

        return SDF.ellipse(px, py, cx, cy, local_rx, ry)

    def _estimate_normal(
        self,
        px: float, py: float,
        cx: float, cy: float,
        rx: float, ry: float
    ) -> Tuple[float, float, float]:
        """Estimate surface normal from SDF gradient."""
        eps = 0.5

        # Gradient in x and y
        dx = (self._face_sdf(px + eps, py, cx, cy, rx, ry) -
              self._face_sdf(px - eps, py, cx, cy, rx, ry)) / (2 * eps)
        dy = (self._face_sdf(px, py + eps, cx, cy, rx, ry) -
              self._face_sdf(px, py - eps, cx, cy, rx, ry)) / (2 * eps)

        # For a 3D-ish look, estimate Z from distance to center
        dist_to_center = math.sqrt(((px - cx) / rx)**2 + ((py - cy) / ry)**2)
        dz = math.sqrt(max(0, 1 - dist_to_center * dist_to_center * 0.8))

        # Normalize
        mag = math.sqrt(dx*dx + dy*dy + dz*dz)
        if mag < 0.001:
            return (0, 0, 1)
        return (dx/mag, dy/mag, dz/mag)

    def _calculate_lighting(
        self,
        normal: Tuple[float, float, float],
        px: float, py: float,
        cx: float, cy: float,
        rx: float, ry: float
    ) -> float:
        """Calculate soft lighting for cute aesthetic."""
        nx, ny, nz = normal
        lx, ly, lz = self.light.direction

        # Soft Lambert diffuse
        diffuse = max(0, nx * lx + ny * ly + nz * lz)
        # Soften the diffuse by raising to a power less than 1
        diffuse = math.pow(diffuse, 0.7)

        # Combine with high ambient for soft look
        light = self.ambient + (1.0 - self.ambient) * diffuse * self.light.intensity * 0.6

        # Very subtle rim lighting
        rim = max(0, -nx * lx * 0.3)
        light += rim * 0.08

        return min(1.0, light)

    def _apply_eye_sockets(
        self,
        light: float,
        px: float, py: float,
        cx: float, cy: float,
        rx: float, ry: float
    ) -> float:
        """Subtle eye socket shading - very light for cute aesthetic."""
        # Eye positions (match eye rendering)
        eye_y = cy + ry * 0.05
        eye_spacing = rx * 0.30

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing

        # Socket radius
        socket_rx = rx * 0.18
        socket_ry = ry * 0.10

        # Very subtle darkening
        for ex in [left_eye_x, right_eye_x]:
            dist = SDF.ellipse(px, py, ex, eye_y, socket_rx, socket_ry)
            if dist < socket_rx:
                factor = 1.0 - max(0, (socket_rx - dist) / socket_rx) * 0.03
                light *= factor

        return light

    def _apply_nose_shadow(
        self,
        light: float,
        px: float, py: float,
        cx: float, cy: float,
        rx: float, ry: float
    ) -> float:
        """Nose shadow - removed for cute anime style."""
        # No nose shadow for cleaner, cuter look
        return light

    def _get_eye_color(
        self,
        px: float, py: float,
        face_cx: float, face_cy: float,
        face_rx: float, face_ry: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Render eyes with iris, pupil, and catchlight."""
        # Eye positions - in lower-middle of face, leaving forehead space
        eye_y = face_cy + face_ry * 0.05  # Slightly below center
        eye_spacing = face_rx * 0.30  # Comfortable spacing

        # Eye dimensions - almond shaped, proportional
        eye_rx = face_rx * 0.17
        eye_ry = face_ry * 0.13

        for eye_x in [face_cx - eye_spacing, face_cx + eye_spacing]:
            # Sclera (white of eye)
            sclera_dist = SDF.ellipse(px, py, eye_x, eye_y, eye_rx, eye_ry)

            if sclera_dist < 1.0:
                # Inside eye area
                alpha = 255 if sclera_dist < 0 else int(255 * (1.0 - sclera_dist))

                # Iris (colored part)
                iris_rx = eye_rx * 0.7
                iris_ry = eye_ry * 0.85
                iris_dist = SDF.ellipse(px, py, eye_x, eye_y + eye_ry * 0.1, iris_rx, iris_ry)

                if iris_dist < 0:
                    # Inside iris
                    # Pupil (dark center)
                    pupil_r = iris_rx * 0.45
                    pupil_dist = SDF.circle(px, py, eye_x, eye_y + eye_ry * 0.15, pupil_r)

                    if pupil_dist < 0:
                        # Pupil - very dark
                        gray = 25
                    else:
                        # Iris gradient - darker at edges
                        iris_factor = abs(iris_dist) / iris_rx
                        gray = int(80 + iris_factor * 40)

                    # Catchlight (bright reflection)
                    catchlight_x = eye_x - eye_rx * 0.25
                    catchlight_y = eye_y - eye_ry * 0.2
                    catchlight_dist = SDF.circle(px, py, catchlight_x, catchlight_y, eye_rx * 0.2)

                    if catchlight_dist < 0:
                        gray = 250  # Bright white catchlight

                    # Secondary smaller catchlight
                    catch2_x = eye_x + eye_rx * 0.15
                    catch2_y = eye_y + eye_ry * 0.25
                    catch2_dist = SDF.circle(px, py, catch2_x, catch2_y, eye_rx * 0.1)
                    if catch2_dist < 0:
                        gray = min(255, gray + 80)

                    return (gray, gray, gray, alpha)
                else:
                    # Sclera - white with slight shading
                    edge_dark = min(1.0, abs(sclera_dist) / eye_rx) * 0.15
                    gray = int(245 - edge_dark * 40)
                    return (gray, gray, gray, alpha)

        return None

    def _get_mouth_color(
        self,
        px: float, py: float,
        face_cx: float, face_cy: float,
        face_rx: float, face_ry: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Render a simple, small mouth."""
        mouth_y = face_cy + face_ry * 0.50  # In lower face area
        mouth_rx = face_rx * 0.13
        mouth_ry = face_ry * 0.03

        # Mouth line (small, subtle)
        mouth_dist = SDF.ellipse(px, py, face_cx, mouth_y, mouth_rx, mouth_ry)

        if mouth_dist < 0.6:
            alpha = 255 if mouth_dist < 0 else int(255 * (1.0 - mouth_dist / 0.6))
            # Softer mouth color
            gray = 150
            return (gray, gray, gray, alpha)

        return None

    def _get_nose_color(
        self,
        px: float, py: float,
        face_cx: float, face_cy: float,
        face_rx: float, face_ry: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Render nose - virtually invisible, just a tiny hint."""
        # Nose is almost invisible in anime style - just 1-2 pixels max
        # Only render if we want a tiny shadow hint, otherwise return None
        return None  # No visible nose for cute anime style

    def _get_eyebrow_color(
        self,
        px: float, py: float,
        face_cx: float, face_cy: float,
        face_rx: float, face_ry: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Render eyebrows - positioned above eyes."""
        brow_y = face_cy - face_ry * 0.15  # Above the eyes
        eye_spacing = face_rx * 0.30  # Match eye spacing

        brow_rx = face_rx * 0.15
        brow_ry = face_ry * 0.035

        for brow_x in [face_cx - eye_spacing, face_cx + eye_spacing]:
            # Slight arch - raise outer edge
            is_left = brow_x < face_cx
            if is_left:
                arch_offset = (px - (brow_x - brow_rx)) / (brow_rx * 2) * face_ry * 0.03
            else:
                arch_offset = ((brow_x + brow_rx) - px) / (brow_rx * 2) * face_ry * 0.03

            brow_dist = SDF.ellipse(px, py - arch_offset, brow_x, brow_y, brow_rx, brow_ry)

            if brow_dist < 0.8:
                alpha = 255 if brow_dist < 0 else int(255 * (1.0 - brow_dist / 0.8))
                # Dark eyebrows
                gray = 60
                return (gray, gray, gray, alpha)

        return None


def test_render():
    """Test the renderer."""
    renderer = ProceduralPortraitRenderer(width=64, height=96)
    canvas = renderer.render()
    canvas.save('output/portrait_v3_test.png')
    print(f"Rendered {canvas.width}x{canvas.height} portrait")
    return canvas


if __name__ == "__main__":
    test_render()
