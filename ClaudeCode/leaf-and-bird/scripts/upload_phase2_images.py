"""Re-upload the 3 phase2 PDP images per product after Supliful wipe.

Uploads phase2-hero/3step/vs at positions 1/2/3 (Option A — phase2-hero
becomes the product's main image, Supliful label shots reflow to pos 4+).
Idempotent: skips upload if the target filename already exists on the product.

Usage:
  SHOPIFY_TOKEN=shpat_... python3 scripts/upload_phase2_images.py [--dry-run] [--only <handle>]
"""
import argparse
import base64
import json
import os
import pathlib
import urllib.request

SHOP = os.environ.get("SHOPIFY_SHOP", "leaf-and-bird.myshopify.com")
TOKEN = os.environ["SHOPIFY_TOKEN"]
OUT_ROOT = pathlib.Path(__file__).resolve().parent.parent / "images" / "products"

# (preset, position, alt_template)
PHASE2_MAP = {
    "phase2-hero":  (1, "{name} — branded product hero"),
    "phase2-3step": (2, "{name} — 3-step routine usage guide"),
    "phase2-vs":    (3, "{name} — comparison vs alternatives"),
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
    req = urllib.request.Request(
        f"https://{SHOP}/admin/api/2024-10{path}",
        data=data, headers=headers, method=method,
    )
    return json.loads(urllib.request.urlopen(req).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="Limit to one product handle")
    args = ap.parse_args()

    handles = [args.only] if args.only else list(PRODUCTS)
    total = 0
    for handle in handles:
        if handle not in PRODUCTS:
            continue
        name = PRODUCTS[handle]
        product_dir = OUT_ROOT / handle
        if not product_dir.exists():
            print(f"  {handle}: no image dir, skip")
            continue

        p = api("GET", f"/products.json?handle={handle}&fields=id,images")["products"][0]
        pid = p["id"]
        existing = {img["src"].split("?")[0].split("/")[-1].lower() for img in p["images"]}

        uploaded = 0
        for preset, (position, alt_template) in PHASE2_MAP.items():
            local = product_dir / f"{preset}.jpg"
            if not local.exists():
                print(f"    skip {handle}/{preset}.jpg (not on disk)")
                continue
            filename = f"{handle}-{preset}.jpg"
            if filename.lower() in existing:
                print(f"    skip {filename} (already on product)")
                continue
            alt = alt_template.format(name=name)
            payload = {
                "image": {
                    "attachment": base64.b64encode(local.read_bytes()).decode(),
                    "filename": filename,
                    "alt": alt[:512],
                    "position": position,
                }
            }
            if args.dry_run:
                print(f"    DRY  {filename} -> pos={position} alt={alt!r}")
            else:
                r = api("POST", f"/products/{pid}/images.json", payload)
                print(f"    OK   uploaded {filename} -> pos={position} (id={r['image']['id']})")
                uploaded += 1

        total += uploaded
        print(f"  {handle}: {uploaded} uploaded")

    print(f"\nTotal uploaded: {total}")


if __name__ == "__main__":
    main()
