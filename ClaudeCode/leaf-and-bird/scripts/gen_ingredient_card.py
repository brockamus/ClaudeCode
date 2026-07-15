"""Generate a Phase 2 'What's Inside' ingredient highlight card for a PDP.

Composes a square 1024x1024 image with:
  - Cream background matching the brand "from the journal" callouts
  - Sage eyebrow + product image hero + product name
  - 4 active ingredients with short benefit descriptions
  - Brand mark footer

PDRN test card uses the real ingredient story from the product description.
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib, urllib.request, io

OUT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum/ingredient-card.jpg")
HERO_URL = "https://cdn.shopify.com/s/files/1/0689/7401/8859/files/1774922075658-generated-label-image-0.jpg?width=1200"

# Brand palette
CREAM = (247, 245, 240)
SAGE = (111, 175, 143)
SAGE_DARK = (79, 111, 93)
INK = (26, 26, 26)
GREY = (107, 114, 128)

# Type
def font(weight, size):
    paths = {
        "regular": "/System/Library/Fonts/Helvetica.ttc",
        "bold":    "/System/Library/Fonts/Helvetica.ttc",
        "serif":   "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "serif_bold": "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    }
    return ImageFont.truetype(paths[weight], size)

INGREDIENTS = [
    ("Polydeoxyribonucleotide (PDRN)",
     "Non-salmon-derived. Signals tissue repair via\nthe adenosine A2A receptor pathway."),
    ("Acetyl Hexapeptide-8 (Argireline)",
     "Vegan peptide. Smooths the look of\nexpression lines."),
    ("Sodium Hyaluronate",
     "Low molecular weight HA for plumping\nhydration that penetrates."),
    ("Panthenol (B5) + Glycerin + Sodium PCA",
     "Calms, conditions, and reinforces the\nskin barrier."),
]


def main():
    W = H = 1024
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Eyebrow
    eyebrow = "WHAT'S INSIDE"
    f = font("bold", 18)
    spaced = " ".join(eyebrow)  # letter-spaced effect
    bbox = draw.textbbox((0, 0), spaced, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 60), spaced, font=f, fill=SAGE_DARK)

    # Hero bottle photo (downloaded + cropped to portrait)
    try:
        img_data = urllib.request.urlopen(HERO_URL).read()
        hero = Image.open(io.BytesIO(img_data)).convert("RGB")
        # Crop to roughly portrait 3:4 from center
        hw, hh = hero.size
        target_ratio = 3 / 4
        cur_ratio = hw / hh
        if cur_ratio > target_ratio:
            new_w = int(hh * target_ratio)
            left = (hw - new_w) // 2
            hero = hero.crop((left, 0, left + new_w, hh))
        # Resize to ~360px tall
        hero.thumbnail((420, 380), Image.LANCZOS)
        hx = (W - hero.width) // 2
        img.paste(hero, (hx, 110))
        next_y = 110 + hero.height + 30
    except Exception as e:
        print(f"(skipping hero embed: {e})")
        next_y = 180

    # Product name (serif)
    name_lines = ["Vegan PDRN Brightening Serum"]
    f = font("serif_bold", 30)
    for line in name_lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, next_y), line, font=f, fill=INK)
        next_y += 38

    # Sage divider
    next_y += 14
    draw.line([(W // 2 - 30, next_y), (W // 2 + 30, next_y)], fill=SAGE, width=2)
    next_y += 28

    # Ingredient list
    name_font = font("bold", 18)
    desc_font = font("regular", 16)
    for ing_name, ing_desc in INGREDIENTS:
        # Ingredient name (left-aligned, with sage dot accent)
        bullet_x = 110
        draw.ellipse((bullet_x - 10, next_y + 8, bullet_x - 2, next_y + 16), fill=SAGE)
        draw.text((bullet_x + 5, next_y), ing_name, font=name_font, fill=INK)
        next_y += 24
        # Description
        for line in ing_desc.split("\n"):
            draw.text((bullet_x + 5, next_y), line, font=desc_font, fill=GREY)
            next_y += 22
        next_y += 14

    # Brand mark footer
    f = font("serif", 14)
    brand = "Leaf & Bird"
    bbox = draw.textbbox((0, 0), brand, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 50), brand, font=f, fill=SAGE_DARK)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "JPEG", quality=92)
    print(f"Saved {OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
