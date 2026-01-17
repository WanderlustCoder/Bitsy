"""
Bitsy Info Module - Quick reference for all available generators.

Usage:
    import info
    info.show()           # Show all available generators
    info.items()          # List all item types
    info.creatures()      # List all creature types
    info.textures()       # List all texture types
    info.vehicles()       # List all vehicle types
    info.quick_start()    # Show quick start examples
"""

from typing import List, Dict


def show():
    """Display overview of all Bitsy generators."""
    print("=" * 60)
    print("BITSY - Pixel Art Generation Toolkit")
    print("=" * 60)
    print()
    print("Generators:")
    print("  character   - Humanoid character sprites")
    print("  item        - Weapons, potions, keys, scrolls")
    print("  creature    - Slimes, ghosts, beasts, elementals")
    print("  prop        - Furniture, chests, vegetation")
    print("  texture     - Seamless tileable textures")
    print("  vehicle     - Cars, ships, aircraft, spaceships")
    print("  structure   - Houses, castles, dungeon tiles")
    print("  environment - Sky, ground, weather effects")
    print()
    print("Functions:")
    print("  info.items()      - List item types")
    print("  info.creatures()  - List creature types")
    print("  info.textures()   - List texture types")
    print("  info.vehicles()   - List vehicle types")
    print("  info.props()      - List prop types")
    print("  info.all_types()  - Get dict of all types")
    print("  info.quick_start() - Show usage examples")
    print()


def items() -> List[str]:
    """List all available item types."""
    from generators import list_item_types
    types = list_item_types()
    print("Item types:", ', '.join(types))
    return types


def creatures() -> List[str]:
    """List all available creature types."""
    from generators import list_creature_types
    types = list_creature_types()
    print("Creature types:", ', '.join(types))
    return types


def props() -> List[str]:
    """List all available prop types."""
    from generators import list_prop_types
    types = list_prop_types()
    print("Prop types:", ', '.join(types))
    return types


def textures() -> List[str]:
    """List all available texture types."""
    from generators import list_texture_types
    types = list_texture_types()
    print("Texture types:", ', '.join(types))
    return types


def vehicles() -> List[str]:
    """List all available vehicle types."""
    from generators import list_vehicle_types
    types = list_vehicle_types()
    print("Vehicle types:", ', '.join(types))
    return types


def structures() -> Dict[str, List[str]]:
    """List all available structure types."""
    from generators import list_building_styles, list_dungeon_tile_types
    result = {
        'building_styles': list_building_styles(),
        'dungeon_tiles': list_dungeon_tile_types()
    }
    print("Building styles:", ', '.join(result['building_styles']))
    print("Dungeon tiles:", ', '.join(result['dungeon_tiles']))
    return result


def environments() -> Dict[str, List[str]]:
    """List all available environment options."""
    from generators import list_time_of_day, list_weather, list_terrain_types
    result = {
        'time_of_day': list_time_of_day(),
        'weather': list_weather(),
        'terrain': list_terrain_types()
    }
    print("Times of day:", ', '.join(result['time_of_day']))
    print("Weather:", ', '.join(result['weather']))
    print("Terrain:", ', '.join(result['terrain']))
    return result


def all_types() -> Dict[str, List[str]]:
    """Get dictionary of all available types."""
    from generators import (
        list_item_types, list_creature_types, list_prop_types,
        list_texture_types, list_vehicle_types,
        list_building_styles, list_dungeon_tile_types,
        list_time_of_day, list_weather, list_terrain_types
    )
    return {
        'items': list_item_types(),
        'creatures': list_creature_types(),
        'props': list_prop_types(),
        'textures': list_texture_types(),
        'vehicles': list_vehicle_types(),
        'building_styles': list_building_styles(),
        'dungeon_tiles': list_dungeon_tile_types(),
        'time_of_day': list_time_of_day(),
        'weather': list_weather(),
        'terrain': list_terrain_types(),
    }


def quick_start():
    """Show quick start examples."""
    print("=" * 60)
    print("BITSY Quick Start")
    print("=" * 60)
    print()
    print("# Generate a character")
    print("from generators import generate_character")
    print("char = generate_character(32, 32, seed=42)")
    print("char.save('hero.png')")
    print()
    print("# Generate items")
    print("from generators import generate_item")
    print("sword = generate_item('sword')")
    print("potion = generate_item('potion_health')")
    print()
    print("# Generate creatures")
    print("from generators import generate_creature")
    print("slime = generate_creature('slime', seed=42)")
    print()
    print("# Generate textures")
    print("from generators import generate_texture")
    print("brick = generate_texture('brick', width=64, height=64)")
    print()
    print("# Generate vehicles")
    print("from generators import generate_vehicle")
    print("car = generate_vehicle('car_sports', width=32, height=24)")
    print()
    print("# All generators support:")
    print("  - seed parameter for deterministic output")
    print("  - Custom palettes for color control")
    print("  - HD mode for higher detail (where supported)")
    print()


def search(query: str) -> List[str]:
    """Search for types matching a query."""
    query = query.lower()
    all_t = all_types()
    matches = []

    for category, types in all_t.items():
        for t in types:
            if query in t.lower():
                matches.append(f"{category}: {t}")

    if matches:
        print(f"Found {len(matches)} matches for '{query}':")
        for m in matches:
            print(f"  {m}")
    else:
        print(f"No matches found for '{query}'")

    return matches


# Show info when module is run directly
if __name__ == '__main__':
    show()
