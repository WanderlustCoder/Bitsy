import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from core import Canvas
from generators.scene import Scene, SceneLayer, create_scene, generate_parallax_background
from generators.environment import generate_sky, generate_ground, generate_room
from generators.prop import generate_prop
from generators.character import generate_character
from generators.structure import generate_house
from generators.creature import generate_creature


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "scenes")
SCENE_SIZE = 128


def _layer_canvas(width: int, height: int) -> Canvas:
    return Canvas(width, height, (0, 0, 0, 0))


def build_rpg_field() -> Canvas:
    scene: Scene = create_scene(width=SCENE_SIZE, height=SCENE_SIZE)

    for layer in generate_parallax_background(
        SCENE_SIZE, SCENE_SIZE, layers=2, seed=11
    ):
        scene.add_layer(layer)

    grass = generate_ground(SCENE_SIZE, SCENE_SIZE, terrain="grass", seed=12)
    scene.add_layer(
        SceneLayer(
            name="grass",
            canvas=grass,
            z_order=-10,
            offset_y=SCENE_SIZE // 2,
            is_background=True,
        )
    )

    midground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    tree = generate_prop("tree", width=32, height=48, seed=13)
    flowers_a = generate_prop("flower", width=12, height=12, seed=14)
    flowers_b = generate_prop("flower", width=12, height=12, seed=15)
    midground.blit(tree, 12, 42)
    midground.blit(flowers_a, 72, 78)
    midground.blit(flowers_b, 92, 74)
    scene.add_layer(SceneLayer(name="field_props", canvas=midground, z_order=10))

    foreground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    hero = generate_character(width=24, height=32, seed=16)
    foreground.blit(hero, 54, 78)
    scene.add_layer(SceneLayer(name="hero", canvas=foreground, z_order=20))

    return scene.render()


def build_dungeon() -> Canvas:
    scene: Scene = create_scene(width=SCENE_SIZE, height=SCENE_SIZE)

    dungeon_bg = generate_room(SCENE_SIZE, SCENE_SIZE, room_type="dungeon", seed=21)
    scene.add_layer(SceneLayer(name="dungeon_bg", canvas=dungeon_bg, z_order=-20))

    midground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    chest = generate_prop("chest", variant="treasure", width=24, height=20, seed=22)
    midground.blit(chest, 80, 82)
    scene.add_layer(SceneLayer(name="treasure", canvas=midground, z_order=10))

    foreground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    skeleton = generate_creature("skeleton", width=24, height=32, seed=23)
    foreground.blit(skeleton, 36, 74)
    scene.add_layer(SceneLayer(name="skeleton", canvas=foreground, z_order=20))

    return scene.render()


def build_village() -> Canvas:
    scene: Scene = create_scene(width=SCENE_SIZE, height=SCENE_SIZE)

    sky = generate_sky(SCENE_SIZE, SCENE_SIZE, time_of_day="day", seed=31)
    scene.add_layer(SceneLayer(name="sky", canvas=sky, z_order=-100, is_background=True))

    ground = generate_ground(SCENE_SIZE, SCENE_SIZE, terrain="grass", seed=32)
    scene.add_layer(
        SceneLayer(
            name="ground",
            canvas=ground,
            z_order=-10,
            offset_y=SCENE_SIZE // 2,
            is_background=True,
        )
    )

    midground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    house = generate_house(width=64, height=64, style="cottage", seed=33)
    tree = generate_prop("tree", width=28, height=40, seed=34)
    bush = generate_prop("bush", width=20, height=16, seed=35)
    midground.blit(house, 40, 34)
    midground.blit(tree, 8, 52)
    midground.blit(bush, 92, 84)
    scene.add_layer(SceneLayer(name="village_props", canvas=midground, z_order=10))

    foreground = _layer_canvas(SCENE_SIZE, SCENE_SIZE)
    villager = generate_character(width=24, height=32, seed=36)
    foreground.blit(villager, 22, 78)
    scene.add_layer(SceneLayer(name="villager", canvas=foreground, z_order=20))

    return scene.render()


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    scenes = {
        "scene_rpg_field.png": build_rpg_field(),
        "scene_dungeon.png": build_dungeon(),
        "scene_village.png": build_village(),
    }

    for filename, canvas in scenes.items():
        canvas.save(os.path.join(OUTPUT_DIR, filename))


if __name__ == "__main__":
    main()
