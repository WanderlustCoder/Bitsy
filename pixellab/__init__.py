"""PixelLab API client for pixel art generation."""

import base64
import json
import os
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from .config import API_BASE_URL, load_api_key


class PixelLabClient:
    """Thin wrapper around the PixelLab API v2."""

    def __init__(self, api_key=None):
        self.api_key = load_api_key(api_key)
        self.base_url = API_BASE_URL

    # -- Public API --

    def get_balance(self):
        """Check remaining credits and generations."""
        return self._get("/balance")

    def generate_image(self, description, width=64, height=64, *,
                       seed=None, no_background=False, reference_images=None,
                       style_image=None, save_to=None):
        """Generate a pixel art image from a text description.

        Args:
            description: Text description of the image.
            width: Output width (32, 64, 128, or 256).
            height: Output height (32, 64, 128, or 256).
            seed: Seed for reproducibility.
            no_background: Transparent background.
            reference_images: List of file paths for reference images (up to 4).
            style_image: File path for style reference.
            save_to: Path to save PNG + JSON sidecar.

        Returns:
            (image_bytes, metadata_dict)
        """
        body = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
        }
        if seed is not None:
            body["seed"] = seed
        if reference_images:
            body["reference_images"] = [
                _encode_image(p) for p in reference_images[:4]
            ]
        if style_image:
            body["style_image"] = _encode_image(style_image)

        data = self._post("/generate-image-v2", body)
        return self._extract_and_save(data, "generate-image-v2", body, save_to)

    def create_character(self, description, width=64, height=64, *,
                         directions=4, seed=None, outline=None, shading=None,
                         detail=None, view=None, isometric=False,
                         color_image=None, save_to=None):
        """Generate a character with 4 or 8 directional views.

        Args:
            description: Character description.
            width: Image width (32-400).
            height: Image height (32-400).
            directions: 4 or 8 directional views.
            seed: Seed for reproducibility.
            outline/shading/detail: Visual style parameters.
            view: Camera perspective.
            isometric: Isometric rendering.
            color_image: File path for palette reference.
            save_to: Path to save PNG + JSON sidecar.

        Returns:
            (image_bytes, metadata_dict)
        """
        endpoint = (
            "/create-character-with-8-directions" if directions == 8
            else "/create-character-with-4-directions"
        )
        body = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "isometric": isometric,
        }
        if seed is not None:
            body["seed"] = seed
        for key, val in [("outline", outline), ("shading", shading),
                         ("detail", detail), ("view", view)]:
            if val is not None:
                body[key] = val
        if color_image:
            body["color_image"] = _encode_image(color_image)

        data = self._post(endpoint, body)
        return self._extract_and_save(data, endpoint.lstrip("/"), body, save_to)

    def animate_character(self, character_id, animation, *,
                          animation_name=None, description=None,
                          action_description=None, directions=None,
                          seed=None, outline=None, shading=None, detail=None,
                          save_to=None):
        """Animate an existing character with a template animation.

        Args:
            character_id: ID of the character to animate.
            animation: Template animation ID.
            animation_name: Custom name for the animation.
            description/action_description: Optional overrides.
            directions: Specific directions to animate.
            seed: Seed for reproducibility.
            save_to: Path to save PNG + JSON sidecar.

        Returns:
            (response_data, metadata_dict)
        """
        body = {
            "character_id": character_id,
            "template_animation_id": animation,
        }
        if animation_name:
            body["animation_name"] = animation_name
        if description:
            body["description"] = description
        if action_description:
            body["action_description"] = action_description
        if directions:
            body["directions"] = directions
        if seed is not None:
            body["seed"] = seed
        for key, val in [("outline", outline), ("shading", shading),
                         ("detail", detail)]:
            if val is not None:
                body[key] = val

        data = self._post("/animate-character", body)
        metadata = _build_metadata("animate-character", body, data)

        if save_to:
            _save_metadata(save_to, metadata)

        return data, metadata

    def create_tileset(self, lower_description, upper_description, *,
                       tile_size=32, transition_description=None,
                       seed=None, outline=None, shading=None, detail=None,
                       view="high top-down", color_image=None,
                       save_to=None, poll_interval=3, max_wait=120):
        """Generate a Wang tileset (async, polls until complete).

        Args:
            lower_description: Base terrain description.
            upper_description: Elevated terrain description.
            tile_size: 16 or 32 pixels.
            transition_description: Transition zone description.
            seed: Seed for reproducibility.
            view: 'low top-down' or 'high top-down'.
            color_image: File path for palette reference.
            save_to: Path to save PNG + JSON sidecar.
            poll_interval: Seconds between status checks.
            max_wait: Maximum seconds to wait.

        Returns:
            (image_bytes, metadata_dict)
        """
        body = {
            "lower_description": lower_description,
            "upper_description": upper_description,
            "tile_size": {"width": tile_size, "height": tile_size},
            "view": view,
        }
        if transition_description:
            body["transition_description"] = transition_description
        if seed is not None:
            body["seed"] = seed
        for key, val in [("outline", outline), ("shading", shading),
                         ("detail", detail)]:
            if val is not None:
                body[key] = val
        if color_image:
            body["color_image"] = _encode_image(color_image)

        data = self._post("/tilesets", body)
        tileset_id = data.get("data", {}).get("tileset_id") or data.get("tileset_id")
        if not tileset_id:
            raise RuntimeError(f"No tileset_id in response: {data}")

        result = self._poll(f"/tilesets/{tileset_id}", poll_interval, max_wait)
        return self._extract_and_save(
            result, "tilesets", body, save_to, async_id=tileset_id
        )

    def create_isometric_tile(self, description, width=32, height=32, *,
                              seed=None, outline=None, shading=None,
                              detail=None, tile_shape="block",
                              color_image=None, save_to=None,
                              poll_interval=3, max_wait=120):
        """Generate a single isometric tile (async, polls until complete).

        Args:
            description: Tile description.
            width/height: Image dimensions (16-64).
            seed: Seed for reproducibility.
            tile_shape: 'thick tile', 'thin tile', or 'block'.
            color_image: File path for palette reference.
            save_to: Path to save PNG + JSON sidecar.
            poll_interval: Seconds between status checks.
            max_wait: Maximum seconds to wait.

        Returns:
            (image_bytes, metadata_dict)
        """
        body = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "isometric_tile_shape": tile_shape,
        }
        if seed is not None:
            body["seed"] = seed
        for key, val in [("outline", outline), ("shading", shading),
                         ("detail", detail)]:
            if val is not None:
                body[key] = val
        if color_image:
            body["color_image"] = _encode_image(color_image)

        data = self._post("/create-isometric-tile", body)
        tile_id = data.get("data", {}).get("tile_id") or data.get("tile_id")
        if not tile_id:
            raise RuntimeError(f"No tile_id in response: {data}")

        result = self._poll(f"/isometric-tiles/{tile_id}", poll_interval, max_wait)
        return self._extract_and_save(
            result, "create-isometric-tile", body, save_to, async_id=tile_id
        )

    def create_map_object(self, description, width=64, height=64, *,
                          seed=None, view="high top-down", outline=None,
                          shading=None, detail=None, color_image=None,
                          save_to=None):
        """Generate a map object with transparent background.

        Args:
            description: Object description.
            width/height: Image dimensions (32-400).
            seed: Seed for reproducibility.
            view: 'low top-down', 'high top-down', or 'side'.
            color_image: File path for palette reference.
            save_to: Path to save PNG + JSON sidecar.

        Returns:
            (image_bytes, metadata_dict)
        """
        body = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "view": view,
        }
        if seed is not None:
            body["seed"] = seed
        for key, val in [("outline", outline), ("shading", shading),
                         ("detail", detail)]:
            if val is not None:
                body[key] = val
        if color_image:
            body["color_image"] = _encode_image(color_image)

        data = self._post("/map-objects", body)
        return self._extract_and_save(data, "map-objects", body, save_to)

    def edit_image(self, image_path, description, width=None, height=None, *,
                   seed=None, no_background=False, save_to=None):
        """Edit an existing pixel art image.

        Args:
            image_path: Path to the image to edit.
            description: Edit instructions.
            width/height: Target dimensions (defaults to source size).
            seed: Seed for reproducibility.
            no_background: Transparent background.
            save_to: Path to save PNG + JSON sidecar.

        Returns:
            (image_bytes, metadata_dict)
        """
        encoded = _encode_image(image_path)
        body = {
            "image": encoded,
            "description": description,
            "image_size": {"width": width or 64, "height": height or 64},
            "width": width or 64,
            "height": height or 64,
            "no_background": no_background,
        }
        if seed is not None:
            body["seed"] = seed

        data = self._post("/edit-image", body)
        return self._extract_and_save(data, "edit-image", body, save_to)

    # -- Internal --

    def _get(self, path):
        req = Request(
            self.base_url + path,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        with urlopen(req) as resp:
            return json.loads(resp.read())

    def _post(self, path, body):
        data = json.dumps(body).encode()
        req = Request(
            self.base_url + path,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise RuntimeError(
                f"PixelLab API error {e.code} on {path}: {error_body}"
            ) from e

    def _poll(self, path, interval, max_wait):
        start = time.time()
        while time.time() - start < max_wait:
            try:
                result = self._get(path)
                return result
            except HTTPError as e:
                if e.code == 423:  # Still generating
                    time.sleep(interval)
                    continue
                raise
        raise TimeoutError(f"Timed out waiting for {path} after {max_wait}s")

    def _extract_and_save(self, data, endpoint, request_body, save_to,
                          async_id=None):
        image_bytes = _extract_image_bytes(data)
        metadata = _build_metadata(endpoint, request_body, data, async_id)

        if save_to:
            _save_png(save_to, image_bytes)
            _save_metadata(save_to, metadata)

        return image_bytes, metadata


# -- Helpers --

def _encode_image(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    fmt = "png" if path.lower().endswith(".png") else "jpeg"
    return {"type": "base64", "base64": b64, "format": fmt}


def _extract_image_bytes(data):
    """Pull base64 image from a PixelLab response, checking common shapes."""
    # Direct base64 in data
    if isinstance(data, dict):
        inner = data.get("data", data)
        # Single image
        if isinstance(inner, dict) and "base64" in inner:
            return base64.b64decode(inner["base64"])
        # Image in an "image" key
        if isinstance(inner, dict) and isinstance(inner.get("image"), dict):
            return base64.b64decode(inner["image"]["base64"])
        # List of images - return first
        if isinstance(inner, dict) and isinstance(inner.get("images"), list):
            imgs = inner["images"]
            if imgs and isinstance(imgs[0], dict) and "base64" in imgs[0]:
                return base64.b64decode(imgs[0]["base64"])
        # Raw image_data
        if isinstance(inner, dict) and "image_data" in inner:
            return base64.b64decode(inner["image_data"])
    raise ValueError(f"Could not extract image from response: {list(data.keys()) if isinstance(data, dict) else type(data)}")


def _build_metadata(endpoint, request_body, response_data, async_id=None):
    meta = {
        "endpoint": endpoint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": {k: v for k, v in request_body.items()
                    if k not in ("image", "reference_image", "from_image",
                                 "init_image", "inpainting_image", "mask_image",
                                 "color_image", "style_image", "reference_images",
                                 "style_images", "edit_images")},
    }
    if async_id:
        meta["async_id"] = async_id
    usage = (response_data.get("usage") if isinstance(response_data, dict)
             else None)
    if usage:
        meta["usage"] = usage
    return meta


def _save_png(path, image_bytes):
    png_path = path if path.endswith(".png") else path + ".png"
    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)
    with open(png_path, "wb") as f:
        f.write(image_bytes)


def _save_metadata(path, metadata):
    base = path[:-4] if path.endswith(".png") else path
    json_path = base + ".json"
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)
