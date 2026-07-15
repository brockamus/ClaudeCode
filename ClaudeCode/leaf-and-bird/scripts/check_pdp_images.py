"""Check which uploaded PDP images still exist on Shopify products.

Compares local files in images/products/<handle>/*.jpg against the current
images on each product. Reports which custom uploads are missing (likely
wiped by a Supliful sync) so you know what to re-upload.

Usage:
  SHOPIFY_TOKEN=shpat_... python3 scripts/check_pdp_images.py
"""
import json
import os
import pathlib
import sys
import urllib.request

SHOP = os.environ.get("SHOPIFY_SHOP", "leaf-and-bird.myshopify.com")
TOKEN = os.environ["SHOPIFY_TOKEN"]
OUT_ROOT = pathlib.Path(__file__).resolve().parent.parent / "images" / "products"

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


def api(method, path):
    req = urllib.request.Request(
        f"https://{SHOP}/admin/api/2024-10{path}",
        headers={"X-Shopify-Access-Token": TOKEN},
        method=method,
    )
    return json.loads(urllib.request.urlopen(req).read())


def expected_filenames(handle):
    """Local files we previously generated for upload (excluding hero)."""
    d = OUT_ROOT / handle
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.jpg")):
        if p.stem == "hero":
            continue
        out.append(f"{handle}-{p.stem}.jpg")
    return out


def main():
    grand_present = 0
    grand_missing = 0
    grand_other = 0
    summary = []

    for handle, name in PRODUCTS.items():
        try:
            res = api("GET", f"/products.json?handle={handle}&fields=id,images,title")
            products = res.get("products") or []
            if not products:
                print(f"\n{handle}: NOT FOUND on shop")
                continue
            p = products[0]
        except Exception as e:
            print(f"\n{handle}: ERROR {e}")
            continue

        live_filenames = []
        for img in p["images"]:
            fname = img["src"].split("?")[0].split("/")[-1].lower()
            live_filenames.append(fname)

        expected = expected_filenames(handle)
        # Strip Shopify's _<hash> suffix when matching (e.g. foo.jpg -> foo_abc123.jpg)
        def base_stem(fname):
            stem = fname.rsplit(".", 1)[0]
            # remove trailing _XXXX hash that Shopify sometimes appends
            return stem

        live_set_norm = set()
        for fname in live_filenames:
            stem = fname.rsplit(".", 1)[0]
            live_set_norm.add(stem)
            # Also store version without trailing _hash
            if "_" in stem:
                live_set_norm.add(stem.rsplit("_", 1)[0])

        present = []
        missing = []
        for exp in expected:
            exp_stem = exp.rsplit(".", 1)[0]
            if exp_stem in live_set_norm:
                present.append(exp)
            else:
                missing.append(exp)

        # "Other" images on product that aren't ours and aren't recognized as supliful hero
        custom_stems = {e.rsplit(".", 1)[0] for e in expected}
        other = []
        for fname in live_filenames:
            stem = fname.rsplit(".", 1)[0]
            base = stem.rsplit("_", 1)[0] if "_" in stem else stem
            if stem in custom_stems or base in custom_stems:
                continue
            other.append(fname)

        grand_present += len(present)
        grand_missing += len(missing)
        grand_other += len(other)

        print(f"\n{handle}  ({len(p['images'])} images live on product)")
        print(f"  custom uploads found:    {len(present)}/{len(expected)}")
        for f in present:
            print(f"    OK   {f}")
        if missing:
            print(f"  custom uploads MISSING:  {len(missing)}")
            for f in missing:
                print(f"    MISS {f}")
        if other:
            print(f"  other images on product: {len(other)}")
            for f in other:
                print(f"    --   {f}")

        summary.append((handle, len(present), len(missing), len(other)))

    print("\n" + "=" * 60)
    print(f"{'handle':<40} {'kept':>5} {'gone':>5} {'other':>6}")
    print("-" * 60)
    for h, p, m, o in summary:
        print(f"{h:<40} {p:>5} {m:>5} {o:>6}")
    print("-" * 60)
    print(f"{'TOTAL':<40} {grand_present:>5} {grand_missing:>5} {grand_other:>6}")


if __name__ == "__main__":
    main()
