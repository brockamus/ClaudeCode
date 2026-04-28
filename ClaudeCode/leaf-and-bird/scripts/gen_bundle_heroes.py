"""Generate hero images for all 8 bundles via Nano Banana Pro using component
product references, then upload each to its bundle product on Shopify.
"""
import base64, json, os, pathlib, subprocess, sys, time, urllib.request

API_KEY = "GOOGLE_API_KEY_REDACTED"
MODEL = "gemini-3-pro-image-preview"
TOKEN = "SHOPIFY_TOKEN_REDACTED"
SHOP = "leaf-and-bird.myshopify.com"
REST = f"https://{SHOP}/admin/api/2024-10"

ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird")
OUT = ROOT / "images" / "bundles"
OUT.mkdir(parents=True, exist_ok=True)

# Per-component reference image (cleanest bottle shot in lifestyle context)
REF_IMG = {
    "pdrn":           ROOT / "images/products/pdrn-brightening-serum/hero.jpg",
    "vit_glow":       ROOT / "images/products/vitamin-glow-serum/lifestyle-linen.jpg",
    "vit_c":          ROOT / "images/products/vitamin-c-serum/lifestyle-linen.jpg",
    "tallow_ll":      ROOT / "images/products/tallow-cream-lemongrass-lavender/lifestyle-linen.jpg",
    "tallow_ob":      ROOT / "images/products/tallow-cream-orange-bergamot/lifestyle-linen.jpg",
    "tallow_pn":      ROOT / "images/products/tallow-cream-peaceful-night/lifestyle-bedside.jpg",
    "eye_gel":        ROOT / "images/products/peptide-eye-gel-cream/lifestyle-marble.jpg",
    "sleep_collagen": ROOT / "images/products/sleep-plus-collagen-cream/lifestyle-with-lid-off.jpg",
    "dead_sea":       ROOT / "images/products/dead-sea-mud/lifestyle-spa.jpg",
}

PRODUCT_DESCRIPTIONS = {
    "pdrn":           "PDRN serum: amber dropper bottle with white label",
    "vit_glow":       "Vitamin Glow Serum: amber dropper bottle with white label",
    "vit_c":          "Vitamin C Serum: amber dropper bottle with white label",
    "tallow_ll":      "Whipped tallow cream jar: white frosted glass with white lid, lemongrass + lavender accents",
    "tallow_ob":      "Whipped tallow cream jar: white frosted glass with white lid, orange + bergamot accents",
    "tallow_pn":      "Whipped tallow cream jar: white frosted glass with white lid, fir branch accent",
    "eye_gel":        "Peptide Eye Gel-Cream: small frosted glass jar with white lid",
    "sleep_collagen": "Sleep Plus Collagen Cream: frosted glass jar with white lid, lavender accent",
    "dead_sea":       "Dead Sea Mud Mask: frosted glass jar with white lid, dark mud visible",
}

# Bundle product IDs (post-recreation)
BUNDLES = [
    {"slug": "first-drop-duo",       "pid": 10356476838187, "comps": ["vit_glow", "tallow_ll"]},
    {"slug": "radiance-bundle",      "pid": 10355718947115, "comps": ["dead_sea", "vit_glow", "sleep_collagen"]},
    {"slug": "hydrate-and-restore",  "pid": 10356516913451, "comps": ["pdrn", "tallow_ll", "eye_gel"]},
    {"slug": "brightening-set",      "pid": 10356479787307, "comps": ["pdrn", "vit_glow", "vit_c"]},
    {"slug": "pregnancy-safe-edit",  "pid": 10356481655083, "comps": ["tallow_ll", "eye_gel", "vit_glow"]},
    {"slug": "tallow-trio",          "pid": 10356483391787, "comps": ["tallow_ll", "tallow_ob", "tallow_pn"]},
    {"slug": "anti-aging-stack",     "pid": 10356485128491, "comps": ["pdrn", "eye_gel", "sleep_collagen"]},
    {"slug": "full-ritual",          "pid": 10356487029035, "comps": ["pdrn", "tallow_ll", "eye_gel", "vit_glow", "sleep_collagen"]},
]


def call_pro(refs_bytes, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    parts = [{"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(b).decode()}} for b in refs_bytes]
    parts.append({"text": prompt})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def extract_image(response):
    for cand in response.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("image/"):
                return base64.b64decode(part["inlineData"]["data"])
    return None


def upload_image(product_id, jpg_path, alt_text):
    """Upload an image to a Shopify product."""
    b64 = base64.b64encode(jpg_path.read_bytes()).decode()
    body = {"image": {"attachment": b64, "alt": alt_text, "filename": jpg_path.name}}
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{REST}/products/{product_id}/images.json", data=data, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, json.loads(r.read())


for b in BUNDLES:
    print(f"\n[{b['slug']}] generating hero…")
    refs = []
    for c in b["comps"]:
        p = REF_IMG.get(c)
        if p and p.exists():
            refs.append(p.read_bytes())
        else:
            print(f"  warn: missing ref for {c} ({p})")
    products_text = ", ".join(PRODUCT_DESCRIPTIONS[c] for c in b["comps"])

    prompt = f"""SQUARE 1:1 cinematic lifestyle product hero for an ecommerce skincare bundle PDP. Editorial magazine quality, photographic realism — NOT illustrated.

PRODUCTS TO INCLUDE (use the reference images for accurate bottle shape and label appearance — keep all bottles consistent and recognizable): {products_text}.

COMPOSITION: Group all the products together on a softly-draped raw linen cloth over warm honey-oak wood. Slightly off-center, intimate close cluster. One product slightly forward as the focal anchor, others arranged behind/beside in a natural, unstaged way. Subtle visible water droplets on the glass. A few sage sprigs and lavender stems scattered with intention (not flatlay-staged). Small dried botanical leaves (eucalyptus or sage) softly bokehed in the background.

LIGHTING: Soft diffused morning sunlight from upper-right through a sheer linen curtain. Gentle golden warmth. Subtle highlights on glass curves, soft natural shadows. NOT harsh, NOT studio. Visible dust motes in a single ray of light for atmosphere.

PALETTE: Cream, oat, sage green, honey-oak wood, soft amber sun glow. Earthy and quiet. NO synthetic colors, NO neon, NO bright whites.

AESTHETIC: Editorial magazine — Kinfolk / Cereal / Goop tier. Quiet luxury, ingredient-literate, modern-natural beauty. NOT commercial advertising, NOT stock photo.

LENS LOOK: 50mm-85mm, shallow depth of field, products in tack-sharp focus, background gently melted.

NO text overlay, NO logos beyond what's already on the product labels, NO additional product labels invented. Aspect ratio 1:1 SQUARE.

Output as a high-resolution photograph."""

    response = call_pro(refs, prompt)
    img = extract_image(response)
    if not img:
        print(f"  ✗ NO IMAGE returned. Response: {json.dumps(response)[:500]}")
        continue

    # Save PNG → JPEG via sips
    out_jpg = OUT / f"{b['slug']}.jpg"
    out_png = out_jpg.with_suffix(".png")
    out_png.write_bytes(img)
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(out_png), "--out", str(out_jpg)],
        check=True, capture_output=True,
    )
    out_png.unlink()
    print(f"  saved {out_jpg.name} ({out_jpg.stat().st_size // 1024}KB)")

    # Upload to product
    alt = f"Leaf & Bird {b['slug'].replace('-', ' ').title()} skincare bundle — {len(b['comps'])} products on linen with botanicals"
    s, _ = upload_image(b["pid"], out_jpg, alt)
    print(f"  uploaded to product {b['pid']}: {s}")
    time.sleep(1)

print("\nALL DONE")
