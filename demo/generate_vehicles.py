#!/usr/bin/env python3
import os

from generators.vehicle import (
    VehicleGenerator,
    generate_vehicle,
    list_vehicle_types,
    VehicleType,
    VehiclePalette,
)


def save_vehicle(canvas, output_dir, name):
    path = os.path.join(output_dir, f"{name}.png")
    canvas.save(path)

    scaled = canvas.scale(4)
    scaled_path = os.path.join(output_dir, f"{name}_4x.png")
    scaled.save(scaled_path)


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "vehicles")
    os.makedirs(output_dir, exist_ok=True)

    vehicles = [
        ("car", VehiclePalette.car_red(), "car_red"),
        ("car", VehiclePalette.car_blue(), "car_blue"),
        ("car", VehiclePalette.car_white(), "car_white"),
        ("ship_sailboat", VehiclePalette.wooden_ship(), "ship_sailboat"),
        ("aircraft_plane", VehiclePalette.car_white(), "aircraft_plane"),
        ("spaceship_fighter", VehiclePalette.spaceship(), "spaceship_fighter"),
    ]

    for vehicle_type, palette, name in vehicles:
        canvas = generate_vehicle(
            vehicle_type=vehicle_type,
            width=32,
            height=32,
            palette=palette,
        )
        save_vehicle(canvas, output_dir, name)


if __name__ == "__main__":
    main()
