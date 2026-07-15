"""Goda-style 'Hero + 3-Benefit Side Panel' card adapted to Leaf & Bird.

Layout:
  Left ~70%: dramatic hero photo of the product
  Right ~30%: deep forest green panel with 3 stacked benefit boxes
              (each: white-outline circle icon + cream serif headline)
  Overlay on hero: circular money-back guarantee seal (top right)
  Overlay bottom of hero: cream pill with leaf/sage emblem + accolade
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum")
HERO = ROOT / "hero-dramatic.jpg"
OUT = ROOT / "phase2-goda-hero.jpg"

# Brand palette — Goda-style adapted to L&B
DARK_GREEN = (38, 60, 47)      # deep forest green (replaces Goda's burgundy)
DARKER_GREEN = (24, 40, 30)    # slightly darker for box backgrounds
CREAM = (245, 232, 220)        # warm cream/blush for text on dark
WHITE = (255, 255, 255)
INK = (15, 15, 15)
GOLD = (210, 178, 122)

GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEORGIA_REG = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(family, size):
    paths = {
        "serif_bold":   GEORGIA_BOLD,
        "serif":        GEORGIA_REG,
        "serif_italic": GEORGIA_ITALIC,
        "sans_bold":    ARIAL_BOLD,
        "sans":         ARIAL_REG,
    }
    return ImageFont.truetype(paths[family], size)


def draw_icon(draw, kind, cx, cy, size=24, color=WHITE, weight=2):
    """White line icons matching Goda's style."""
    s = size // 2
    if kind == "sparkle":
        # Big plus + diagonal sparkles (brightness)
        draw.line([(cx, cy - s), (cx, cy + s)], fill=color, width=weight)
        draw.line([(cx - s, cy), (cx + s, cy)], fill=color, width=weight)
        d = s // 2
        draw.line([(cx - d, cy - d - 2), (cx + d, cy + d + 2)], fill=color, width=1)
        draw.line([(cx + d, cy - d - 2), (cx - d, cy + d + 2)], fill=color, width=1)
    elif kind == "leaf":
        # Leaf shape
        draw.arc((cx - s, cy - s, cx + s, cy + s), start=200, end=20, fill=color, width=weight)
        draw.line([(cx - s + 4, cy + s - 2), (cx + s - 2, cy - s + 4)], fill=color, width=weight)
        # Stem
        draw.line([(cx - s + 4, cy + s - 2), (cx - s + 1, cy + s + 4)], fill=color, width=weight)
    elif kind == "shield-check":
        # Shield outline with checkmark inside
        draw.polygon([(cx, cy - s),
                      (cx + s - 2, cy - s + 4),
                      (cx + s - 4, cy + s - 2),
                      (cx, cy + s),
                      (cx - s + 4, cy + s - 2),
                      (cx - s + 2, cy - s + 4)],
                     outline=color, width=weight)
        # Checkmark
        draw.line([(cx - s + 6, cy + 1),
                   (cx - 2, cy + s - 7),
                   (cx + s - 5, cy - s + 8)], fill=color, width=weight)


def draw_icon_in_circle(draw, kind, cx, cy, ring_r=32, icon_size=28, color=WHITE):
    draw.ellipse((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
                  outline=color, width=2)
    draw_icon(draw, kind, cx, cy, size=icon_size, color=color, weight=2)


def draw_circular_seal(img, draw, cx, cy, radius=85):
    """30-day money back guarantee circular seal (gold/cream on dark)."""
    # Outer circle with thicker stroke, on cream/gold background
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                  fill=CREAM, outline=DARK_GREEN, width=2)
    # Inner border ring
    inner_r = radius - 8
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
                  outline=DARK_GREEN, width=1)
    # "30" big in center
    f_big = font("serif_bold", 38)
    text = "30"
    bbox = draw.textbbox((0, 0), text, font=f_big)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - 32), text, font=f_big, fill=DARK_GREEN)
    # "DAY"
    f_small = font("sans_bold", 16)
    text = "DAY"
    bbox = draw.textbbox((0, 0), text, font=f_small)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + 4), text, font=f_small, fill=DARK_GREEN)
    # Curved "MONEY BACK" arc text — fake it with straight bottom line
    f_curve = font("sans_bold", 11)
    text = "100% GUARANTEE"
    bbox = draw.textbbox((0, 0), text, font=f_curve)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + 28), text, font=f_curve, fill=DARK_GREEN)
    # Top arc text "MONEY BACK"
    text = "MONEY BACK"
    bbox = draw.textbbox((0, 0), text, font=f_curve)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - radius + 12), text, font=f_curve, fill=DARK_GREEN)


def draw_bottom_pill(img, draw, x, y, w, h, label):
    """Cream rounded pill with sage/leaf emblem + label."""
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=WHITE)
    # Leaf emblem (small filled oval)
    ex = x + 28
    ey = y + h // 2
    draw.ellipse((ex - 8, ey - 9, ex + 8, ey + 9), fill=DARK_GREEN)
    # Tiny check accent (white stem on the leaf)
    draw.line([(ex, ey - 5), (ex - 2, ey + 2), (ex - 4, ey - 1)], fill=WHITE, width=2)
    # Label
    f = font("serif_bold", 22)
    bbox = draw.textbbox((0, 0), label, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((x + 56, y + (h - 22) // 2 - 4), label, font=f, fill=INK)


def main():
    W = H = 1024
    panel_w = 304
    photo_w = W - panel_w  # 720

    img = Image.new("RGB", (W, H), DARK_GREEN)
    draw = ImageDraw.Draw(img)

    # ── Left: hero photo ──
    hero = Image.open(HERO).convert("RGB")
    hw, hh = hero.size
    # Crop to fit photo_w x H aspect
    target_ratio = photo_w / H
    cur_ratio = hw / hh
    if cur_ratio > target_ratio:
        new_w = int(hh * target_ratio)
        hero = hero.crop(((hw - new_w) // 2, 0, (hw + new_w) // 2, hh))
    else:
        new_h = int(hw / target_ratio)
        hero = hero.crop((0, (hh - new_h) // 2, hw, (hh + new_h) // 2))
    hero = hero.resize((photo_w, H), Image.LANCZOS)
    img.paste(hero, (0, 0))

    # ── Right panel: 3 stacked benefit boxes ──
    BENEFITS = [
        ("sparkle",      "Visibly\nBrighter Skin"),
        ("leaf",         "100% Vegan\nNon-Salmon PDRN"),
        ("shield-check", "Pregnancy-\nFriendly"),
    ]
    panel_x = photo_w
    box_h = (H - 30) // 3  # gaps top/bottom
    gap = 8
    box_y = 12
    box_inner_pad = 10

    for i, (icon_kind, label) in enumerate(BENEFITS):
        bx = panel_x + box_inner_pad
        by = box_y + i * (box_h + gap // 2)
        bw = panel_w - 2 * box_inner_pad
        bh = box_h - gap
        # Box with rounded corners
        draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=10, fill=DARKER_GREEN)
        # Icon centered horizontally, ~25% from top
        cx = bx + bw // 2
        cy = by + 70
        draw_icon_in_circle(draw, icon_kind, cx, cy, ring_r=34, icon_size=30, color=CREAM)
        # Label centered (serif, 2 lines)
        f = font("serif_bold", 24)
        text_y = by + 130
        for line in label.split("\n"):
            bbox = draw.textbbox((0, 0), line, font=f)
            tw = bbox[2] - bbox[0]
            draw.text((bx + (bw - tw) // 2, text_y), line, font=f, fill=CREAM)
            text_y += 30

    # ── Overlay: circular trust seal (top right of photo region) ──
    seal_cx = photo_w - 110
    seal_cy = 110
    draw_circular_seal(img, draw, seal_cx, seal_cy, radius=85)

    # ── Overlay: bottom pill ──
    pill_w = 380
    pill_h = 54
    pill_x = 30
    pill_y = H - pill_h - 30
    draw_bottom_pill(img, draw, pill_x, pill_y, pill_w, pill_h,
                      "K-Beauty Grade Vegan PDRN")

    img.save(OUT, "JPEG", quality=92)
    print(f"Saved {OUT.name} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
