#!/usr/bin/env python3
"""
Bitsy CLI - Command-line interface for pixel art generation.

Usage:
    python -m cli generate character --size 32x32 --output hero.png
    python -m cli generate item sword --output sword.png
    python -m cli list items
    python -m cli info
    python -m cli gallery --output gallery/

Examples:
    # Generate a character
    python -m cli generate character -o char.png

    # Generate a red car
    python -m cli generate vehicle car_sports --palette red -o car.png

    # Generate a brick texture
    python -m cli generate texture brick --size 64x64 -o brick.png

    # List all available generators
    python -m cli list all

    # Show info about a specific generator
    python -m cli info creature
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_generate(args):
    """Handle generate command."""
    from core import Canvas

    # Parse size
    if 'x' in args.size:
        width, height = map(int, args.size.split('x'))
    else:
        width = height = int(args.size)

    generator_type = args.type
    variant = args.variant

    result = None

    if generator_type == 'character':
        from generators import generate_character
        result = generate_character(width, height, seed=args.seed)

    elif generator_type == 'item':
        from generators import generate_item, list_item_types
        if not variant:
            print(f"Item type required. Available: {', '.join(list_item_types())}")
            return 1
        result = generate_item(variant, width=width, height=height, seed=args.seed)

    elif generator_type == 'creature':
        from generators import generate_creature, list_creature_types
        if not variant:
            print(f"Creature type required. Available: {', '.join(list_creature_types())}")
            return 1
        result = generate_creature(variant, width=width, height=height, seed=args.seed)

    elif generator_type == 'prop':
        from generators import generate_prop, list_prop_types
        if not variant:
            print(f"Prop type required. Available: {', '.join(list_prop_types())}")
            return 1
        result = generate_prop(variant, width=width, height=height, seed=args.seed)

    elif generator_type == 'texture':
        from generators import generate_texture, list_texture_types
        if not variant:
            print(f"Texture type required. Available: {', '.join(list_texture_types())}")
            return 1
        result = generate_texture(variant, width=width, height=height, seed=args.seed)

    elif generator_type == 'vehicle':
        from generators import generate_vehicle, list_vehicle_types
        if not variant:
            print(f"Vehicle type required. Available: {', '.join(list_vehicle_types())}")
            return 1
        result = generate_vehicle(variant, width=width, height=height, seed=args.seed)

    elif generator_type == 'structure':
        from generators import generate_house
        result = generate_house(width, height, seed=args.seed)

    elif generator_type == 'sky':
        from generators import generate_sky
        result = generate_sky(width, height, seed=args.seed)

    elif generator_type == 'ground':
        from generators import generate_ground
        result = generate_ground(width, height, seed=args.seed)

    else:
        print(f"Unknown generator type: {generator_type}")
        print("Available: character, item, creature, prop, texture, vehicle, structure, sky, ground")
        return 1

    if result:
        output = args.output or f"{generator_type}_{variant or 'default'}.png"
        result.save(output)
        print(f"Generated: {output} ({result.width}x{result.height})")
        return 0

    return 1


def cmd_list(args):
    """Handle list command."""
    category = args.category

    if category in ('all', 'items', 'item'):
        from generators import list_item_types
        print("Items:", ', '.join(list_item_types()))

    if category in ('all', 'creatures', 'creature'):
        from generators import list_creature_types
        print("Creatures:", ', '.join(list_creature_types()))

    if category in ('all', 'props', 'prop'):
        from generators import list_prop_types
        print("Props:", ', '.join(list_prop_types()))

    if category in ('all', 'textures', 'texture'):
        from generators import list_texture_types
        print("Textures:", ', '.join(list_texture_types()))

    if category in ('all', 'vehicles', 'vehicle'):
        from generators import list_vehicle_types
        print("Vehicles:", ', '.join(list_vehicle_types()))

    if category in ('all', 'structures', 'structure'):
        from generators import list_building_styles, list_dungeon_tile_types
        print("Building styles:", ', '.join(list_building_styles()))
        print("Dungeon tiles:", ', '.join(list_dungeon_tile_types()))

    if category in ('all', 'environments', 'environment'):
        from generators import list_time_of_day, list_weather, list_terrain_types
        print("Times of day:", ', '.join(list_time_of_day()))
        print("Weather:", ', '.join(list_weather()))
        print("Terrain:", ', '.join(list_terrain_types()))

    return 0


def cmd_info(args):
    """Handle info command."""
    print("=" * 60)
    print("BITSY - Pixel Art Generation Toolkit")
    print("=" * 60)
    print()

    if args.generator:
        # Show info about specific generator
        gen = args.generator.lower()
        if gen == 'character':
            print("Character Generator")
            print("-" * 40)
            print("Generates humanoid character sprites.")
            print()
            print("Usage:")
            print("  from generators import generate_character")
            print("  char = generate_character(32, 32, seed=42)")
            print()
            print("Parameters:")
            print("  width, height: Canvas size (default 32x32)")
            print("  seed: Random seed for determinism")
            print("  hd_mode: Enable HD rendering")

        elif gen == 'item':
            from generators import list_item_types
            print("Item Generator")
            print("-" * 40)
            print(f"Available types: {', '.join(list_item_types())}")
            print()
            print("Usage:")
            print("  from generators import generate_item")
            print("  sword = generate_item('sword', seed=42)")

        elif gen == 'creature':
            from generators import list_creature_types
            print("Creature Generator")
            print("-" * 40)
            print(f"Available types: {', '.join(list_creature_types())}")
            print()
            print("Usage:")
            print("  from generators import generate_creature")
            print("  slime = generate_creature('slime', seed=42)")

        elif gen == 'texture':
            from generators import list_texture_types
            print("Texture Generator")
            print("-" * 40)
            print(f"Available types: {', '.join(list_texture_types())}")
            print()
            print("Usage:")
            print("  from generators import generate_texture")
            print("  brick = generate_texture('brick', width=32, height=32)")

        elif gen == 'vehicle':
            from generators import list_vehicle_types
            print("Vehicle Generator")
            print("-" * 40)
            print(f"Available types: {', '.join(list_vehicle_types())}")
            print()
            print("Usage:")
            print("  from generators import generate_vehicle")
            print("  car = generate_vehicle('car_sedan', width=32, height=24)")

        else:
            print(f"Unknown generator: {gen}")
            print("Available: character, item, creature, prop, texture, vehicle")
            return 1
    else:
        # Show general info
        print("Generators available:")
        print("  - character  : Humanoid character sprites")
        print("  - item       : Weapons, potions, keys, etc.")
        print("  - creature   : Slimes, beasts, undead, etc.")
        print("  - prop       : Furniture, chests, vegetation")
        print("  - texture    : Seamless tileable textures")
        print("  - vehicle    : Cars, ships, aircraft, spaceships")
        print("  - structure  : Houses, castles, dungeons")
        print("  - environment: Sky, ground, weather")
        print()
        print("Quick start:")
        print("  from generators import generate_character, generate_item")
        print("  char = generate_character(32, 32)")
        print("  char.save('hero.png')")
        print()
        print("Use 'python -m cli info <generator>' for details.")
        print("Use 'python -m cli list all' to see all available types.")

    return 0


def cmd_gallery(args):
    """Generate a gallery of all available sprites."""
    import os
    from core import Canvas

    output_dir = args.output or 'gallery'
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating gallery in {output_dir}/...")

    # Characters
    from generators import generate_character
    for i in range(4):
        c = generate_character(32, 32, seed=i)
        c.save(f"{output_dir}/character_{i}.png")
    print("  Characters: 4")

    # Items
    from generators import generate_item, list_item_types
    for item_type in list_item_types()[:10]:  # First 10
        item = generate_item(item_type, seed=42)
        item.save(f"{output_dir}/item_{item_type}.png")
    print(f"  Items: 10")

    # Creatures
    from generators import generate_creature, list_creature_types
    for creature_type in list_creature_types()[:6]:
        creature = generate_creature(creature_type, seed=42)
        creature.save(f"{output_dir}/creature_{creature_type}.png")
    print(f"  Creatures: 6")

    # Textures
    from generators import generate_texture, list_texture_types
    for tex_type in ['brick', 'stone', 'wood', 'grass', 'metal', 'fabric']:
        tex = generate_texture(tex_type, width=32, height=32, seed=42)
        tex.save(f"{output_dir}/texture_{tex_type}.png")
    print(f"  Textures: 6")

    # Vehicles
    from generators import generate_vehicle
    for veh_type in ['car_sedan', 'ship_sailboat', 'aircraft_jet', 'spaceship_fighter']:
        veh = generate_vehicle(veh_type, width=32, height=24, seed=42)
        veh.save(f"{output_dir}/vehicle_{veh_type}.png")
    print(f"  Vehicles: 4")

    print(f"\nGallery generated: {output_dir}/ (30 sprites)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Bitsy - Pixel Art Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cli generate item sword -o sword.png
  python -m cli generate texture brick --size 64x64 -o brick.png
  python -m cli list all
  python -m cli info creature
  python -m cli gallery -o gallery/
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a sprite')
    gen_parser.add_argument('type', help='Generator type (character, item, creature, etc.)')
    gen_parser.add_argument('variant', nargs='?', help='Variant/subtype (e.g., sword, slime)')
    gen_parser.add_argument('-s', '--size', default='32x32', help='Size WxH (default: 32x32)')
    gen_parser.add_argument('-o', '--output', help='Output file path')
    gen_parser.add_argument('--seed', type=int, default=42, help='Random seed')
    gen_parser.add_argument('--palette', help='Palette name (if supported)')

    # List command
    list_parser = subparsers.add_parser('list', help='List available types')
    list_parser.add_argument('category', nargs='?', default='all',
                            help='Category to list (all, items, creatures, etc.)')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show generator information')
    info_parser.add_argument('generator', nargs='?', help='Generator to show info for')

    # Gallery command
    gallery_parser = subparsers.add_parser('gallery', help='Generate sprite gallery')
    gallery_parser.add_argument('-o', '--output', default='gallery', help='Output directory')

    args = parser.parse_args()

    if args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'list':
        return cmd_list(args)
    elif args.command == 'info':
        return cmd_info(args)
    elif args.command == 'gallery':
        return cmd_gallery(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
