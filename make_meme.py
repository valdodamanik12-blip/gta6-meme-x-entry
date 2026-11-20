#!/usr/bin/env python3
"""Build meme.png: add black letterbox bars with bold captions to scene.png.

Top bar:    STILL WAITING FOR GTA VI / SINCE 2013
Bottom bar: MY AI AGENT ALREADY GOT PAID / FROM GTA 6 BOUNTIES

The font size is fitted automatically so the widest caption line always
fits inside the image width with a comfortable margin.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SCENE_PATH = HERE / "scene.png"
OUT_PATH = HERE / "meme.png"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TOP_LINES = ["STILL WAITING FOR GTA VI", "SINCE 2013"]
BOTTOM_LINES = ["MY AI AGENT ALREADY GOT PAID", "FROM GTA 6 BOUNTIES"]

SIDE_MARGIN_RATIO = 0.04  # keep 4% of the width free on each side
LINE_GAP_RATIO = 0.18     # vertical gap between the two lines, relative to font size
BAR_PAD_RATIO = 0.35      # padding above/below the text block inside a bar


def fit_font(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int,
             start_size: int) -> ImageFont.FreeTypeFont:
    """Shrink the font from start_size until every line fits max_width."""
    size = start_size
    while size > 10:
        font = ImageFont.truetype(FONT_PATH, size)
        widest = max(draw.textlength(line, font=font) for line in lines)
        if widest <= max_width:
            return font
        size -= 4
    return ImageFont.truetype(FONT_PATH, size)


def draw_bar(draw: ImageDraw.ImageDraw, lines: list[str],
             font: ImageFont.FreeTypeFont, width: int,
             bar_top: int, bar_height: int) -> None:
    """Draw black bar background is already in place; center the two lines."""
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    gap = int(font.size * LINE_GAP_RATIO)
    block_height = line_height * len(lines) + gap * (len(lines) - 1)
    y = bar_top + (bar_height - block_height) // 2
    for line in lines:
        text_width = draw.textlength(line, font=font)
        x = (width - text_width) / 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += line_height + gap


def main() -> None:
    scene = Image.open(SCENE_PATH).convert("RGB")
    width, height = scene.size

    probe = ImageDraw.Draw(scene)
    max_text_width = int(width * (1 - 2 * SIDE_MARGIN_RATIO))
    all_lines = TOP_LINES + BOTTOM_LINES
    font = fit_font(probe, all_lines, max_text_width, start_size=width // 12)

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    gap = int(font.size * LINE_GAP_RATIO)
    pad = int(font.size * BAR_PAD_RATIO)
    bar_height = line_height * 2 + gap + pad * 2

    canvas = Image.new("RGB", (width, height + bar_height * 2), (0, 0, 0))
    canvas.paste(scene, (0, bar_height))

    draw = ImageDraw.Draw(canvas)
    draw_bar(draw, TOP_LINES, font, width, 0, bar_height)
    draw_bar(draw, BOTTOM_LINES, font, width, bar_height + height, bar_height)

    canvas.save(OUT_PATH, "PNG")
    print(f"wrote {OUT_PATH} size={canvas.size} font_size={font.size} "
          f"bar_height={bar_height}")


if __name__ == "__main__":
    main()
