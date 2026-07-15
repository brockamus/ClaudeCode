"""Generate 3 Phase 2 sample card types for PDRN — to evaluate before scaling.

1. Benefit Pills overlay (lifestyle photo + bottom-left pill badges with icons)
2. Icon Benefits + Texture macro (3 icon-text blocks left, macro right)
3. Regimen / Routine card (3 products in flow with PREP/TREAT/SEAL labels)

All use Arial Bold for headlines (matches The Ordinary aesthetic).
"""
import os
from PIL import Image, ImageDraw, ImageFont
import pathlib, urllib.request, io

ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum")
LIFESTYLE_BASE = ROOT / "lifestyle-in-hand.jpg"
MACRO_BASE = ROOT / "macro-serum-drop.jpg"

INK = (15, 15, 15)
GREY = (90, 90, 90)
LIGHT_GREY = (200, 200, 200)
PILL_BG = (255, 255, 255, 220)  # semi-transparent white

ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(weight, size):
    return ImageFont.truetype(ARIAL_BOLD if weight == "bold" else ARIAL_REG, size)


def fetch_product_image(handle, width=600):
    """Download a product's hero image from Shopify."""
    import json
    SHOP = "leaf-and-bird.myshopify.com"
    TOKEN = os.environ["SHOPIFY_TOKEN"]
    req = urllib.request.Request(
        f"https://{SHOP}/admin/api/2024-10/products.json?handle={handle}&fields=images",
        headers={"X-Shopify-Access-Token": TOKEN})
    p = json.loads(urllib.request.urlopen(req).read())["products"][0]
    src = p["images"][0]["src"]
    url = f"{src}&width={width}" if "?" in src else f"{src}?width={width}"
    return Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("RGB")


# ─── Icon drawing helpers (vector-style line icons) ────────────────────────

def draw_icon(draw, kind, cx, cy, size=24, color=INK, weight=2):
    """Draw a simple line icon centered at (cx, cy)."""
    s = size // 2  # half-size from center
    if kind == "smoothing":
        # 3 horizontal wavy lines
        for i, dy in enumerate([-s + 6, 0, s - 6]):
            draw.line([(cx - s, cy + dy), (cx - s + 6, cy + dy - 3),
                       (cx - 2, cy + dy + 3), (cx + s - 6, cy + dy - 3),
                       (cx + s, cy + dy)], fill=color, width=weight)
    elif kind == "brightening":
        # 4-pointed star (sparkle)
        draw.line([(cx, cy - s), (cx, cy + s)], fill=color, width=weight)
        draw.line([(cx - s, cy), (cx + s, cy)], fill=color, width=weight)
        # smaller sparkles diagonal
        d = s // 2
        draw.line([(cx - d, cy - d), (cx + d, cy + d)], fill=color, width=1)
        draw.line([(cx + d, cy - d), (cx - d, cy + d)], fill=color, width=1)
    elif kind == "drop":
        # water drop outline (teardrop)
        draw.ellipse((cx - s + 2, cy - 4, cx + s - 2, cy + s), outline=color, width=weight)
        draw.line([(cx, cy - s), (cx - s + 4, cy)], fill=color, width=weight)
        draw.line([(cx, cy - s), (cx + s - 4, cy)], fill=color, width=weight)
    elif kind == "drop-arrow":
        # drop with downward arrow (oil reduction)
        draw_icon(draw, "drop", cx - 4, cy, size=size - 4, color=color, weight=weight)
        # arrow
        ax = cx + s + 2
        draw.line([(ax, cy - s + 4), (ax, cy + s - 4)], fill=color, width=weight)
        draw.line([(ax - 3, cy + s - 6), (ax, cy + s - 4), (ax + 3, cy + s - 6)], fill=color, width=weight)
    elif kind == "leaf":
        # simple leaf with vein
        draw.ellipse((cx - s, cy - s, cx + s, cy + s), outline=color, width=weight)
        draw.line([(cx - s + 4, cy + s - 4), (cx + s - 4, cy - s + 4)], fill=color, width=weight)
    elif kind == "repair":
        # circular arrows (regeneration)
        draw.arc((cx - s, cy - s, cx + s, cy + s), start=30, end=300, fill=color, width=weight)
        draw.line([(cx + s - 6, cy - 4), (cx + s, cy + 2), (cx + s - 4, cy + 8)], fill=color, width=weight)


def draw_icon_circle(draw, kind, cx, cy, ring_radius=22, icon_size=20, color=INK):
    """Icon inside a circular outline."""
    draw.ellipse((cx - ring_radius, cy - ring_radius, cx + ring_radius, cy + ring_radius),
                  outline=color, width=2)
    draw_icon(draw, kind, cx, cy, size=icon_size, color=color, weight=2)


# ─── Card 1: Benefit Pills overlay on lifestyle photo ─────────────────────

def card_benefit_pills():
    base = Image.open(LIFESTYLE_BASE).convert("RGB")
    # Resize to 1024x1024 (crop center if not already)
    bw, bh = base.size
    side = min(bw, bh)
    base = base.crop(((bw - side) // 2, (bh - side) // 2, (bw + side) // 2, (bh + side) // 2))
    base = base.resize((1024, 1024), Image.LANCZOS)
    img = base.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    BENEFITS = [
        ("smoothing", "Smoothing"),
        ("brightening", "Brightening"),
        ("drop", "Hydrating"),
    ]

    pill_h = 70
    pill_pad_x = 24
    pill_gap = 14
    text_font = font("bold", 30)
    start_x = 50
    start_y = 1024 - 50 - pill_h * len(BENEFITS) - pill_gap * (len(BENEFITS) - 1)

    for i, (icon_kind, label) in enumerate(BENEFITS):
        # Measure label width
        bbox = draw.textbbox((0, 0), label, font=text_font)
        text_w = bbox[2] - bbox[0]
        pill_w = pill_pad_x + 50 + 12 + text_w + pill_pad_x  # icon+gap+text
        y = start_y + i * (pill_h + pill_gap)
        # Pill rounded rectangle
        draw.rounded_rectangle((start_x, y, start_x + pill_w, y + pill_h),
                                radius=pill_h // 2, fill=PILL_BG)
        # Icon
        cx = start_x + pill_pad_x + 22
        cy = y + pill_h // 2
        draw_icon_circle(draw, icon_kind, cx, cy, ring_radius=20, icon_size=18)
        # Label
        text_y = y + (pill_h - text_font.size) // 2 - 4
        draw.text((cx + 22 + 16, text_y), label, font=text_font, fill=INK)

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out_path = ROOT / "phase2-benefit-pills.jpg"
    out.save(out_path, "JPEG", quality=92)
    print(f"  saved {out_path.name}")


# ─── Card 2: Icon Benefits + Texture Macro ────────────────────────────────

def card_icon_benefits():
    img = Image.new("RGB", (1024, 1024), (245, 244, 240))
    draw = ImageDraw.Draw(img)

    # Right half: paste the macro
    macro = Image.open(MACRO_BASE).convert("RGB").resize((1024, 1024), Image.LANCZOS)
    # Crop right portion of macro and paste
    right_macro = macro.crop((360, 100, 1024, 924))  # the drop portion
    right_macro = right_macro.resize((600, 750), Image.LANCZOS)
    img.paste(right_macro, (424, 137))

    # Left half: 3 icon+text blocks
    BENEFITS = [
        ("repair", "Cell Repair Signals",
         "PDRN signals tissue repair via the\nadenosine A2A receptor pathway."),
        ("drop", "Plumping Hydration",
         "Low-molecular-weight hyaluronic acid\nplumps from below the surface."),
        ("smoothing", "Smooths Expression Lines",
         "Argireline (Acetyl Hexapeptide-8)\nrelaxes the look of dynamic lines."),
    ]

    name_font = font("bold", 28)
    desc_font = font("regular", 18)
    block_h = 230
    start_y = 130
    x = 70

    for i, (icon, name, desc) in enumerate(BENEFITS):
        y = start_y + i * block_h
        # Icon in circle
        draw_icon_circle(draw, icon, x + 32, y + 22, ring_radius=28, icon_size=22)
        # Name
        draw.text((x, y + 70), name, font=name_font, fill=INK)
        # Description
        ty = y + 110
        for line in desc.split("\n"):
            draw.text((x, ty), line, font=desc_font, fill=GREY)
            ty += 26

    out_path = ROOT / "phase2-icon-benefits.jpg"
    img.save(out_path, "JPEG", quality=92)
    print(f"  saved {out_path.name}")


# ─── Card 3: Regimen / Routine card ───────────────────────────────────────

def card_regimen():
    W = H = 1024
    img = Image.new("RGB", (W, H), (245, 244, 240))
    draw = ImageDraw.Draw(img)

    # Headline (top)
    head_font = font("bold", 44)
    head = "A brightening routine."
    draw.text((60, 60), head, font=head_font, fill=INK)

    # Three product photos
    products = [
        ("vitamin-c-serum", "PREP", "Vitamin C Serum", "Triple ascorbic acid +\nferulic for AM antioxidant\nprotection."),
        ("pdrn-brightening-serum", "TREAT", "Vegan PDRN\nBrightening Serum", "Non-salmon-derived PDRN\nwith Argireline. Cell repair\n+ even tone."),
        ("sleep-plus-collagen-cream", "SEAL", "Sleep Plus\nCollagen Cream", "Overnight barrier repair\nwith plant collagen + HA."),
    ]
    n = len(products)
    col_w = W // n
    img_size = 220
    img_y = 220
    label_y = img_y + img_size + 30

    for i, (handle, stage, name, desc) in enumerate(products):
        cx = col_w * i + col_w // 2
        # Product image (centered)
        try:
            pimg = fetch_product_image(handle, width=400)
            pw, ph = pimg.size
            target_ratio = 3 / 4
            if pw / ph > target_ratio:
                new_w = int(ph * target_ratio)
                pimg = pimg.crop(((pw - new_w) // 2, 0, (pw + new_w) // 2, ph))
            pimg.thumbnail((img_size, img_size + 60), Image.LANCZOS)
            img.paste(pimg, (cx - pimg.width // 2, img_y))
        except Exception as e:
            print(f"  (skip {handle} image: {e})")

    # Connecting line + dots (between product images, horizontal at img midline)
    line_y = img_y + img_size // 2 + 30
    dot_xs = [col_w * i + col_w // 2 for i in range(n)]
    draw.line([(dot_xs[0], line_y), (dot_xs[-1], line_y)], fill=INK, width=2)
    for i, dx in enumerate(dot_xs):
        # Open white circle on top of the line
        r = 8
        draw.ellipse((dx - r, line_y - r, dx + r, line_y + r), fill=(245, 244, 240), outline=INK, width=2)

    # Stage label + dot indicator + name + desc
    stage_font = font("bold", 14)
    name_font = font("bold", 22)
    desc_font = font("regular", 16)

    for i, (handle, stage, name, desc) in enumerate(products):
        cx = col_w * i + col_w // 2
        y = label_y + 80
        # Stage with dot indicator (e.g., PREP ●○○)
        dot_str = "●" * (i + 1) + "○" * (n - i - 1)
        stage_label = f"{stage}    {dot_str}"
        bbox = draw.textbbox((0, 0), stage_label, font=stage_font)
        sw = bbox[2] - bbox[0]
        draw.text((cx - sw // 2, y), stage_label, font=stage_font, fill=INK)
        y += 32
        # Name (multiline, centered)
        for line in name.split("\n"):
            bbox = draw.textbbox((0, 0), line, font=name_font)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, y), line, font=name_font, fill=INK)
            y += 30
        y += 12
        # Description (multiline, centered)
        for line in desc.split("\n"):
            bbox = draw.textbbox((0, 0), line, font=desc_font)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, y), line, font=desc_font, fill=GREY)
            y += 22

    out_path = ROOT / "phase2-regimen.jpg"
    img.save(out_path, "JPEG", quality=92)
    print(f"  saved {out_path.name}")


def main():
    card_benefit_pills()
    card_icon_benefits()
    card_regimen()


if __name__ == "__main__":
    main()
