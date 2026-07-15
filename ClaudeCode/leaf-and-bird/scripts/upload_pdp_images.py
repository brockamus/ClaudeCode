"""Upload generated PDP images to Shopify products with proper alts + positioning.

After batch_pdp_images.py finishes generating images locally, this script:
1. Finds all generated images per product in images/products/<handle>/
2. Uploads each as a new product image via Shopify Admin API
3. Sets descriptive alt text per preset
4. Inserts at positions 2, 3, 4 (right after the existing hero)
5. Idempotent — skips uploading if filename already exists on the product

Usage:
  SHOPIFY_TOKEN=shpat_... python3 upload_pdp_images.py [--dry-run]
"""
import os
import argparse, base64, json, os, pathlib, sys, urllib.request

SHOP = os.environ.get("SHOPIFY_SHOP", "leaf-and-bird.myshopify.com")
TOKEN = os.environ["SHOPIFY_TOKEN"]
OUT_ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products")

# (preset, position, alt_template)
# Position 2,3,4 inserts right after the existing hero (position 1)
PRESET_MAP = {
    "lifestyle-linen":          (2, "{name} — editorial flat-lay lifestyle photo on linen"),
    "lifestyle-marble":         (2, "{name} — lifestyle photo on marble counter"),
    "lifestyle-bedside":        (2, "{name} — bedside table lifestyle photo"),
    "lifestyle-spa":            (2, "{name} — spa-aesthetic lifestyle photo"),
    "lifestyle-in-hand":        (3, "{name} — held in hand, in-use context"),
    "lifestyle-in-palm":        (3, "{name} — cradled in palm lifestyle photo"),
    "lifestyle-with-lid-off":   (3, "{name} — open jar with cream visible inside"),
    "texture-drop":             (4, "{name} — formula texture, drop on fingertip"),
    "texture-dollop":           (4, "{name} — formula texture, dollop on fingertip"),
    "texture-swirl":            (4, "{name} — whipped texture close-up"),
    "macro-serum-drop":         (4, "{name} — macro shot of serum drop"),
}

PRODUCTS = {
    "pdrn-brightening-serum":           "Vegan PDRN Brightening Serum",
    "vitamin-glow-serum":               "Vitamin Glow Serum",
    "vitamin-c-serum":                  "Vitamin C Serum",
    "peptide-eye-gel-cream":            "Peptide Eye Gel-Cream",
    "sleep-plus-collagen-cream":        "Sleep Plus Collagen Cream",
    "tallow-cream-peaceful-night":      "Whipped Tallow Cream — Peaceful Night",
    "tallow-cream-lemongrass-lavender": "Whipped Tallow Cream — Lemongrass & Lavender",
    "tallow-cream-orange-bergamot":     "Whipped Tallow Cream — Orange & Bergamot",
    "dead-sea-mud":                     "Dead Sea Mud Mask",
}


def api(method, path, body=None):
    headers = {"X-Shopify-Access-Token": TOKEN}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(f"https://{SHOP}/admin/api/2024-10{path}",
                                  data=data, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(req).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="Limit to one product handle")
    args = ap.parse_args()

    handles = [args.only] if args.only else list(PRODUCTS)
    total_uploaded = 0
    for handle in handles:
        if handle not in PRODUCTS:
            continue
        name = PRODUCTS[handle]
        product_dir = OUT_ROOT / handle
        if not product_dir.exists():
            print(f"  {handle}: no image dir, skip")
            continue

        # Find generated images (skip hero.jpg)
        images = sorted([p for p in product_dir.glob("*.jpg") if p.stem != "hero"])
        if not images:
            print(f"  {handle}: no generated images, skip")
            continue

        # Get existing image filenames on the product to skip duplicates
        p = api("GET", f"/products.json?handle={handle}&fields=id,images")["products"][0]
        pid = p["id"]
        existing_names = {img["src"].split("?")[0].split("/")[-1].lower() for img in p["images"]}

        uploaded = 0
        for img_path in images:
            preset = img_path.stem
            if preset not in PRESET_MAP:
                print(f"    skip {img_path.name} (no preset mapping)")
                continue
            position, alt_template = PRESET_MAP[preset]
            filename = f"{handle}-{preset}.jpg"
            if filename.lower() in existing_names:
                print(f"    skip {filename} (already on product)")
                continue
            alt = alt_template.format(name=name)
            payload = {
                "image": {
                    "attachment": base64.b64encode(img_path.read_bytes()).decode(),
                    "filename": filename,
                    "alt": alt[:512],
                    "position": position,
                }
            }
            if args.dry_run:
                print(f"    DRY  upload {filename} → pos={position} alt={alt!r}")
            else:
                r = api("POST", f"/products/{pid}/images.json", payload)
                img_id = r["image"]["id"]
                print(f"    OK   uploaded {filename} → pos={position} (id={img_id})")
                uploaded += 1

        total_uploaded += uploaded
        print(f"  {handle}: {uploaded} uploaded ({len(images)} found)")

    print(f"\nTotal images uploaded: {total_uploaded}")


if __name__ == "__main__":
    main()
