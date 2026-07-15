"""Generate The Ordinary-style 'Annotated Ingredients' card.

Overlay design on Nano Banana macro:
- Bold black sans-serif headline (top-left)
- 2 ingredient callouts with name + description
- Thin annotation lines from text to drop endpoints (open circles)
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib, textwrap

MACRO = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum/macro-serum-drop.jpg")
OUT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum/annotated-ingredients.jpg")

INK = (15, 15, 15)
BODY_GREY = (60, 60, 60)

def font(weight, size):
    if weight == "bold":
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)


def wrap_text(draw, text, font, max_w):
    """Wrap text into lines that fit max_w pixels."""
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def draw_text_block(draw, x, y, text, font, fill, max_w, leading_mult=1.18):
    lines = wrap_text(draw, text, font, max_w)
    line_h = int(font.size * leading_mult)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y  # next y


def main():
    img = Image.open(MACRO).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    LEFT_PAD = 60
    LEFT_COL_W = 470  # left text column width
    head_x = LEFT_PAD
    head_y = 70

    # Headline
    head_text = "Key ingredients in\nVegan PDRN\nBrightening Serum:"
    head_font = font("bold", 50)
    line_h = int(50 * 1.08)
    for line in head_text.split("\n"):
        draw.text((head_x, head_y), line, font=head_font, fill=INK)
        head_y += line_h
    head_y += 60  # space below headline

    # Callouts
    callouts = [
        {
            "name": "Polydeoxyribonucleotide\n(PDRN)",
            "desc": "Non-salmon-derived. Signals tissue repair via the adenosine A2A receptor pathway.",
            "y_start": head_y,
            "endpoint": (770, 360),  # point on drop
        },
        {
            "name": "Acetyl Hexapeptide-8\n(Argireline)",
            "desc": "Vegan peptide. Smooths the look of expression lines.",
            "y_start": head_y + 220,
            "endpoint": (760, 700),  # point on drop, lower
        },
    ]

    name_font = font("bold", 24)
    desc_font = font("regular", 19)

    for c in callouts:
        x = LEFT_PAD
        y = c["y_start"]

        # Ingredient name (bold, possibly multi-line)
        for line in c["name"].split("\n"):
            draw.text((x, y), line, font=name_font, fill=INK)
            y += int(24 * 1.18)
        y_after_name = y

        # Annotation line — from end of name (right edge of last line) to endpoint
        last_line = c["name"].split("\n")[-1]
        bbox = draw.textbbox((0, 0), last_line, font=name_font)
        name_right_x = x + (bbox[2] - bbox[0]) + 12
        name_right_y = y_after_name - int(24 * 1.18) + 13
        # Horizontal line then short to endpoint
        ex, ey = c["endpoint"]
        # Draw line: horizontal segment then to endpoint
        mid_x = ex - 10
        draw.line([(name_right_x, name_right_y), (mid_x, name_right_y)], fill=INK, width=2)
        draw.line([(mid_x, name_right_y), (ex - 8, ey)], fill=INK, width=2)
        # Open circle endpoint
        cr = 6
        draw.ellipse((ex - cr, ey - cr, ex + cr, ey + cr), outline=INK, width=2)

        # Description (below name, regular weight, dark grey)
        y += 6
        draw_text_block(draw, x, y, c["desc"], desc_font, BODY_GREY, LEFT_COL_W, leading_mult=1.35)

    img.save(OUT, "JPEG", quality=92)
    print(f"Saved {OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
