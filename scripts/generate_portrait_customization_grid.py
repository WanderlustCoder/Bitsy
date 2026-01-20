#!/usr/bin/env python3
"""Generate a 4x4 portrait customization showcase grid."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait_v2 import TemplatePortraitGenerator


def canvas_to_image(canvas):
    """Convert core.canvas.Canvas to a PIL RGBA image."""
    image = Image.new("RGBA", (canvas.width, canvas.height))
    flat_pixels = [pixel for row in canvas.pixels for pixel in row]
    image.putdata(flat_pixels)
    return image


def main():
    hair_styles = ["bun", "wavy", "ponytail", "straight"]
    skin_tones = [
        (240, 208, 180),
        (210, 170, 135),
        (170, 125, 95),
        (120, 85, 60),
    ]
    mouth_expressions = ["neutral", "smile", "open", "frown"]
    eye_expressions = ["normal", "happy", "surprised", "closed"]
    glasses_rows = [False, True, False, True]

    hair_colors = [
        (60, 40, 30),
        (120, 80, 50),
        (45, 45, 60),
        (90, 70, 100),
    ]
    eye_colors = [
        (70, 50, 90),
        (80, 110, 70),
        (90, 60, 40),
        (60, 80, 120),
    ]
    clothing_colors = [
        (80, 70, 130),
        (60, 90, 110),
        (120, 70, 80),
        (70, 90, 60),
    ]
    glasses_styles = ["round", "square", "cateye", "round"]

    portraits = []
    for row in range(4):
        for col in range(4):
            generator = TemplatePortraitGenerator(
                style_path="templates/anime_standard",
                skin_color=skin_tones[row],
                eye_color=eye_colors[col],
                hair_color=hair_colors[col],
                clothing_color=clothing_colors[row],
                accessory_color=(70, 55, 45),
                has_glasses=glasses_rows[row],
                glasses_style=glasses_styles[col],
                hair_style=hair_styles[col],
                mouth_expression=mouth_expressions[row],
                eye_expression=eye_expressions[row],
            )
            canvas = generator.render()
            portraits.append(canvas_to_image(canvas))

    if not portraits:
        raise RuntimeError("No portraits generated.")

    cols = 4
    rows = 4
    portrait_w, portrait_h = portraits[0].size
    padding = 12
    margin = 16
    title_height = 28

    grid_w = margin * 2 + cols * portrait_w + (cols - 1) * padding
    grid_h = margin * 2 + title_height + rows * portrait_h + (rows - 1) * padding

    background_color = (245, 240, 235, 255)
    grid_image = Image.new("RGBA", (grid_w, grid_h), background_color)

    draw = ImageDraw.Draw(grid_image)
    font = ImageFont.load_default()
    title = "Portrait Customization Options"
    title_bbox = draw.textbbox((0, 0), title, font=font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (grid_w - title_w) // 2
    title_y = margin // 2
    draw.text((title_x, title_y), title, fill=(30, 25, 25, 255), font=font)

    start_y = margin + title_height
    for index, portrait in enumerate(portraits):
        row = index // cols
        col = index % cols
        x = margin + col * (portrait_w + padding)
        y = start_y + row * (portrait_h + padding)
        grid_image.paste(portrait, (x, y), portrait)

    output_path = "assets/showcase/portrait_customization_grid.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    grid_image.save(output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
