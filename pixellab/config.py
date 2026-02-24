"""PixelLab API configuration and key loading."""

import os

API_BASE_URL = "https://api.pixellab.ai/v2"


def load_api_key(explicit_key=None):
    """Load API key with priority: explicit arg > env var > .env file."""
    if explicit_key:
        return explicit_key

    key = os.environ.get("PIXELLAB_API_KEY")
    if key:
        return key

    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("PIXELLAB_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")

    raise ValueError(
        "No PixelLab API key found. Set PIXELLAB_API_KEY env var, "
        "add it to .env, or pass api_key= to PixelLabClient."
    )
