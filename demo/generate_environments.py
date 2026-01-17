import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.png import save_png
from generators.environment import (
    generate_sky,
    generate_ground,
    generate_room,
    list_time_of_day,
    list_terrain_types,
    list_room_types,
    TimeOfDay,
    TerrainType,
    RoomType,
)


OUTPUT_DIR = os.path.join("demo", "environments")
SIZE = 64


def _ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _assert_available(value: str, available: list[str], label: str) -> None:
    if value not in available:
        raise ValueError(f"{label} '{value}' is not supported; available: {available}")


def generate_skies() -> None:
    available = list_time_of_day()
    times = [
        TimeOfDay.DAWN.value,
        TimeOfDay.DAY.value,
        TimeOfDay.DUSK.value,
        TimeOfDay.NIGHT.value,
        TimeOfDay.MIDNIGHT.value,
    ]
    for time in times:
        _assert_available(time, available, "time_of_day")
        canvas = generate_sky(width=SIZE, height=SIZE, time_of_day=time)
        save_png(canvas, os.path.join(OUTPUT_DIR, f"sky_{time}.png"))


def generate_terrains() -> None:
    available = list_terrain_types()
    terrains = [
        TerrainType.GRASS.value,
        TerrainType.STONE.value,
        TerrainType.SAND.value,
        TerrainType.SNOW.value,
        TerrainType.DIRT.value,
        TerrainType.WATER.value,
        TerrainType.LAVA.value,
    ]
    for terrain in terrains:
        _assert_available(terrain, available, "terrain")
        canvas = generate_ground(width=SIZE, height=SIZE, terrain=terrain)
        save_png(canvas, os.path.join(OUTPUT_DIR, f"terrain_{terrain}.png"))


def generate_rooms() -> None:
    available = list_room_types()
    rooms = [
        RoomType.DUNGEON.value,
        RoomType.HOUSE.value,
        RoomType.CASTLE.value,
        RoomType.CAVE.value,
        RoomType.FOREST.value,
        RoomType.TEMPLE.value,
    ]
    for room in rooms:
        _assert_available(room, available, "room_type")
        canvas = generate_room(width=SIZE, height=SIZE, room_type=room)
        save_png(canvas, os.path.join(OUTPUT_DIR, f"room_{room}.png"))


def main() -> None:
    _ensure_output_dir()
    generate_skies()
    generate_terrains()
    generate_rooms()


if __name__ == "__main__":
    main()
