"""Batch-generate Phase 2 marketing cards via Nano Banana Pro for all L&B products.

For each product, generates 3 cards:
  - phase2-hero.jpg     — Goda-style hero photo + 3 right-side benefit boxes + 30-day seal + bottom pill
  - phase2-3step.jpg    — Numbered usage steps with serif italic headlines + bottle bleeding off right edge
  - phase2-vs.jpg       — Us vs Theirs split-screen with 6 comparison pills

All use the canonical PDP image at images/products/_refs_audit/<handle>/img-1.jpg
as the bottle reference. Forest green / cream palette throughout (brand drama equivalent).

Idempotent — skips if output already exists. Delete to regenerate.
"""
import argparse, base64, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-pro-image-preview"
OUT_ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products")
REFS_ROOT = OUT_ROOT / "_refs_audit"

# Shared style guidance reused across all 3 card types
STYLE_NOTES = """
STYLE NOTES (apply consistently):
- Color palette: deep mossy forest green background (~#2A4838 — rich, cinematic), warm cream/blush text (~#F5E8DC), elegant accents
- Typography: refined serif (Playfair Display or Georgia) for headlines, sans for body where appropriate
- All text crisp, perfectly readable, well-spaced — NO distorted/garbled text
- Premium luxury clean-beauty advertising aesthetic, magazine quality
- Single polished square image with all elements integrated cohesively (NOT separate elements)
""".strip()


# Per-product card configurations
PRODUCTS = {
    "vitamin-glow-serum": {
        "name": "Vitamin Glow Serum",
        "label_text": "Leaf & Bird VITAMIN GLOW SERUM Multi-Active Brightening",
        "bottle_color": "white opaque",
        "hero_benefits": [
            ("4-point sparkle star", "Multi-Active\\nBrightening"),
            ("simple leaf outline", "Sensitive-Skin\\nSafe"),
            ("water droplet outline", "Gentle\\nVitamin C"),
        ],
        "bottom_pill": "K-Beauty Grade Brightening Stack",
        "steps": [
            ("Cleanse Gently", "Start with clean, hydrated skin. A soothing toner preps for layering."),
            ("Apply 3-5 Drops", "Press across face and neck. The milky serum melts in within seconds."),
            ("Lock + Protect", "Follow with moisturizer. AM finish with SPF 30+ — Vitamin C amplifies sun damage if unprotected."),
        ],
        "vs_pills": [
            "Niacinamide + Vit C stack",
            "Sensitive-skin gentle",
            "Honest INCI disclosure",
            "K-beauty grade actives",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "vitamin-c-serum": {
        "name": "Vitamin C Serum",
        "label_text": "Leaf & Bird VITAMIN C SERUM Brightens and evens skin tone, reduces appearance of redness, deep hydration",
        "bottle_color": "amber glass",
        "hero_benefits": [
            ("4-point sparkle star", "AM Antioxidant\\nShield"),
            ("circular arrow regeneration", "Triple Ascorbic\\nAcid"),
            ("shield outline with checkmark", "Free Radical\\nDefense"),
        ],
        "bottom_pill": "Stabilized with Ferulic Acid",
        "steps": [
            ("Cleanse + Tone", "Start clean, slightly damp. Vitamin C absorbs best on hydrated skin."),
            ("Apply Vitamin C", "3-4 drops, press into face and neck. Wait 60 seconds before next layer."),
            ("Always Layer SPF", "Vitamin C amplifies brightening only with daily sunscreen — non-negotiable."),
        ],
        "vs_pills": [
            "Triple-form ascorbic acid",
            "Ferulic-stabilized",
            "Sensitive-skin layering safe",
            "Honest INCI disclosure",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "peptide-eye-gel-cream": {
        "name": "Peptide Eye Gel-Cream",
        "label_text": "Leaf & Bird PEPTIDE EYE GEL-CREAM Visibly reduces fine lines, refreshes tired-looking eyes, deeply hydrating",
        "bottle_color": "white pump bottle",
        "hero_benefits": [
            ("3 wavy smoothing lines", "Smooths Fine\\nLines"),
            ("simple leaf outline", "Vegan Peptide\\nFormula"),
            ("circle with diagonal slash", "Caffeine\\n+ Fragrance Free"),
        ],
        "bottom_pill": "Acetyl Tetrapeptide-5 Eye Treatment",
        "steps": [
            ("Pat Eye Area Clean", "After cleansing, ensure under-eye is gently patted dry."),
            ("Pea-Sized Dollop", "Use ring finger — lightest touch. A little goes far."),
            ("Tap, Don't Rub", "Gently tap until absorbed. Use AM and PM for best results."),
        ],
        "vs_pills": [
            "Vegan peptides (no marine)",
            "Caffeine-free formula",
            "Fragrance-free + sensitive-eye safe",
            "Honest INCI disclosure",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "sleep-plus-collagen-cream": {
        "name": "Sleep Plus Collagen Cream",
        "label_text": "Leaf & Bird SLEEP PLUS COLLAGEN CREAM Infused with hyaluronic acid for deep hydration",
        "bottle_color": "white jar with white lid",
        "hero_benefits": [
            ("crescent moon outline", "Overnight\\nRepair"),
            ("simple leaf outline", "Plant-Based\\nCollagen"),
            ("water droplet outline", "Hyaluronic Acid\\nInfused"),
        ],
        "bottom_pill": "Vegan Collagen + Melatonin Night Cream",
        "steps": [
            ("Cleanse Evening", "Start with a thoroughly cleansed face after the day."),
            ("Apply Generous Layer", "Massage a quarter-sized scoop in upward circles."),
            ("Wake to Plumper Skin", "Wake hydrated. The barrier-strengthening actives work overnight."),
        ],
        "vs_pills": [
            "Plant-based vegan collagen",
            "Melatonin for night repair",
            "No marketing filler ingredients",
            "Honest INCI disclosure",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "tallow-cream-peaceful-night": {
        "name": "Whipped Tallow Cream — Peaceful Night",
        "label_text": "Leaf & Bird TALLOW CREAM PEACEFUL NIGHT Grass-Fed Rich in vitamins A, D, E, & K Deeply nourishing",
        "bottle_color": "white jar with white lid, ivory whipped balm visible",
        "hero_benefits": [
            ("crescent moon outline", "Overnight\\nRestoration"),
            ("simple leaf outline", "100% Grass-Fed\\nTallow"),
            ("flame outline", "Calming\\nAromatherapy"),
        ],
        "bottom_pill": "Whipped with Siberian Fir + Lavender",
        "steps": [
            ("Cleanse + Tone Evening", "Start with thoroughly cleansed, slightly damp skin."),
            ("Warm a Pea-Sized Scoop", "Rub between palms — body heat melts the whipped balm into oil."),
            ("Massage Into Skin", "Press into face, neck, and any dry patches. Inhale the calming aroma."),
        ],
        "vs_pills": [
            "100% grass-fed tallow",
            "Ancestral formula",
            "Lipid-rich for barrier repair",
            "Whipped texture (no greasy feel)",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "tallow-cream-lemongrass-lavender": {
        "name": "Whipped Tallow Cream — Lemongrass & Lavender",
        "label_text": "Leaf & Bird TALLOW CREAM LEMONGRASS & LAVENDER Grass-Fed Rich in vitamins A, D, E, & K Deeply nourishing",
        "bottle_color": "white jar with white lid, ivory whipped balm visible",
        "hero_benefits": [
            ("shield outline with checkmark", "Eczema-\\nFriendly"),
            ("simple leaf outline", "100% Grass-Fed\\nTallow"),
            ("flame outline", "Lemongrass\\n+ Lavender"),
        ],
        "bottom_pill": "Daytime + Sensitive-Skin Approved",
        "steps": [
            ("Cleanse Skin", "Start clean and slightly damp — body or face."),
            ("Warm a Scoop", "Rub between palms — body heat melts the whipped balm to oil."),
            ("Massage Into Damp Skin", "Press anywhere dry, irritated, or in need of a barrier reset."),
        ],
        "vs_pills": [
            "100% grass-fed tallow",
            "Eczema + sensitive-skin safe",
            "Lipid-rich barrier repair",
            "Whipped (non-greasy)",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "tallow-cream-orange-bergamot": {
        "name": "Whipped Tallow Cream — Orange & Bergamot",
        "label_text": "Leaf & Bird TALLOW CREAM ORANGE & BERGAMOT Grass-Fed Rich in vitamins A, D, E, & K Deeply nourishing",
        "bottle_color": "white jar with white lid, ivory whipped balm visible",
        "hero_benefits": [
            ("4-point sparkle star", "Brightening\\nDaytime Use"),
            ("simple leaf outline", "100% Grass-Fed\\nTallow"),
            ("flame outline", "Orange + Bergamot\\nAromatherapy"),
        ],
        "bottom_pill": "Daytime Tallow + Citrus Aromatherapy",
        "steps": [
            ("Cleanse + Tone", "Start clean and slightly damp."),
            ("Warm a Scoop", "Rub between palms — body heat melts the whipped balm into oil."),
            ("Apply + Layer SPF", "Press into face and neck. Always finish daytime use with SPF 30+."),
        ],
        "vs_pills": [
            "100% grass-fed tallow",
            "Real citrus essential oils",
            "Lipid-rich barrier repair",
            "Whipped (non-greasy)",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
    "dead-sea-mud": {
        "name": "Dead Sea Mud Mask",
        "label_text": "Leaf & Bird DEAD SEA MUD ALL-NATURAL Tones & refreshes skin, refines pore appearance, targets blackheads, whiteheads, oily skin",
        "bottle_color": "white jar with BLACK twist-off lid, light-tan whipped mud visible",
        "hero_benefits": [
            ("water droplet with downward arrow", "Detoxifies\\nPores"),
            ("circle with '3' inside", "3-Ingredient\\nFormula"),
            ("crystal/diamond outline", "Mineral-Rich\\nDead Sea Clay"),
        ],
        "bottom_pill": "Weekly Mineral Detox Mask",
        "steps": [
            ("Cleanse Skin", "Start with a clean, slightly damp face."),
            ("Apply Even Layer", "Spread a thin even coat across face, avoiding eye area."),
            ("Rinse After 10-15 min", "Allow mud to mostly dry, then rinse with warm water."),
        ],
        "vs_pills": [
            "3-ingredient formula",
            "Real Dead Sea mineral clay",
            "No synthetic acids or fragrance",
            "Pregnancy-friendly",
            "30-day clean-skin promise",
            "Made in USA",
        ],
    },
}


def call_pro(ref_path, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    ref_bytes = pathlib.Path(ref_path).read_bytes()
    body = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(ref_bytes).decode()}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def extract_image_bytes(response):
    for cand in response.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("image/"):
                return base64.b64decode(part["inlineData"]["data"])
    return None


def save_image(out_path, img_bytes):
    png_path = out_path.with_suffix(".png")
    png_path.write_bytes(img_bytes)
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png_path), "--out", str(out_path)],
        check=True, capture_output=True,
    )
    png_path.unlink()


# ── Per-card-type prompt builders ──

def hero_prompt(cfg):
    benefits_text = "\n".join(
        f"Box {i+1} ({['top','middle','bottom'][i]}): icon = {b[0]}, headline = '{b[1]}'"
        for i, b in enumerate(cfg["hero_benefits"])
    )
    return f"""Create a polished square 1:1 product marketing card in luxury direct-response skincare advertising style.

LAYOUT: 70/30 vertical split.
LEFT 70%: Photographic hero. Show this exact {cfg['bottle_color']} skincare bottle/jar (preserve shape, label '{cfg['label_text']}' EXACTLY as in reference) on draped pale cream linen with deep mossy forest green silk/velvet background. A feminine hand with elegant natural fingernails reaches from upper-left to lightly touch the product. Cinematic side lighting, soft shadows, premium editorial advertising aesthetic.

OVERLAY ON HERO (top right): Circular cream-colored 'guarantee' seal — top arc 'MONEY BACK', center '30 DAY' bold serif, bottom arc '100% GUARANTEE'. Deep forest green text on cream, double-ring border.

OVERLAY ON HERO (bottom left): Horizontal cream pill-shaped badge with small sage-green leaf emblem on the left, bold serif text '{cfg['bottom_pill']}'.

RIGHT 30%: Three stacked benefit boxes on deep forest green panel. Each box: rounded corners, slightly darker green, top contains a thin white-line outline circle (~65px) with a simple white-line icon, bottom contains bold cream serif headline (Playfair-style), 2 lines, centered.

The 3 boxes:
{benefits_text}

{STYLE_NOTES}"""


def step_prompt(cfg):
    steps_text = "\n".join(
        f"Step {i+1}: '{i+1} | {s[0]}'\nDescription: '{s[1]}'"
        for i, s in enumerate(cfg["steps"])
    )
    return f"""Create a polished square 1:1 product marketing card in luxury direct-response skincare advertising style.

LAYOUT: Solid deep mossy forest green background (rich, cinematic, NOT flat). On the right edge of the card, place this exact {cfg['bottle_color']} skincare bottle/jar (preserve shape, label '{cfg['label_text']}' EXACTLY as in reference) cropped/extending off the right edge so only ~60% is visible — dramatic close-up product placement. Held lightly between forefinger and thumb of a feminine hand emerging from bottom-right.

LEFT 65%: Three numbered steps stacked vertically with generous spacing.

Each step format:
[NUMBER] | [Headline in elegant cream serif italic, like Playfair Italic or Georgia Italic]
[Description in lighter cream sans-serif, 2-3 lines]

The numbers are large elegant cream serif (~60-70px). Vertical pipe '|' separator is thin and elegant.

{steps_text}

{STYLE_NOTES}"""


def vs_prompt(cfg):
    pills_text = "\n".join(f"{i+1}. '{p}'" for i, p in enumerate(cfg["vs_pills"]))
    return f"""Create a polished square 1:1 product comparison marketing card in luxury direct-response skincare advertising style.

LAYOUT: Vertical 50/50 split.
LEFT HALF: Solid deep mossy forest green background (rich, cinematic). At bottom-left, prominently show this exact {cfg['bottle_color']} skincare bottle/jar (preserve shape, label '{cfg['label_text']}' EXACTLY as in reference) — extends from lower-left edge, slightly tilted toward viewer.
RIGHT HALF: Solid clean white/off-white background. At bottom-right, show a generic anonymous competitor amber/clear glass bottle with black cap — vague, not branded, just a representative 'other' bottle.

ABOVE the two bottles, at the top:
- Centered on LEFT half: large elegant serif word 'Us' in cream/blush color
- Centered on RIGHT half: large elegant serif word 'Theirs' in deep forest green or near-black
(About 80px font, Playfair Display Bold or Georgia Bold)

CENTER (overlapping the dividing line, middle vertically): Column of 6 horizontal benefit pills, each pill a soft cream/blush rounded rectangle. Each pill:
- Small green checkmark on LEFT
- Center: benefit label in dark serif text (~22px)
- Small red X on RIGHT

The 6 pills (top to bottom):
{pills_text}

{STYLE_NOTES}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="Only run for one product handle")
    ap.add_argument("--type", choices=["hero","3step","vs","all"], default="all")
    args = ap.parse_args()

    handles = [args.only] if args.only else list(PRODUCTS)
    types_to_run = ["hero","3step","vs"] if args.type == "all" else [args.type]
    builders = {"hero": hero_prompt, "3step": step_prompt, "vs": vs_prompt}

    total = sum(len(types_to_run) for h in handles if h in PRODUCTS)
    done = 0
    for handle in handles:
        if handle not in PRODUCTS:
            continue
        cfg = PRODUCTS[handle]
        ref = REFS_ROOT / handle / "img-1.jpg"
        if not ref.exists():
            print(f"  [skip] {handle}: no ref {ref}")
            continue
        out_dir = OUT_ROOT / handle
        out_dir.mkdir(parents=True, exist_ok=True)
        for ctype in types_to_run:
            done += 1
            out_path = out_dir / f"phase2-{ctype}.jpg"
            if out_path.exists():
                print(f"  [{done}/{total}] {handle}/{ctype} (skip — exists)")
                continue
            prompt = builders[ctype](cfg)
            print(f"  [{done}/{total}] {handle}/{ctype}...", end=" ", flush=True)
            try:
                resp = call_pro(ref, prompt)
                img_bytes = extract_image_bytes(resp)
                if not img_bytes:
                    print("NO IMAGE")
                    continue
                save_image(out_path, img_bytes)
                print(f"OK ({out_path.stat().st_size // 1024}KB)")
            except urllib.error.HTTPError as e:
                print(f"HTTP {e.code}: {e.read().decode()[:200]}")
            except Exception as e:
                print(f"ERR: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
