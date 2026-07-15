"""Reorder PDP images so they appear in clean buyer-friendly order:
  1. hero
  2. lifestyle hero (linen/marble/bedside/spa)
  3. lifestyle in-use (in-hand/in-palm/with-lid-off)
  4. macro
  5. texture
  6. phase2-3step
  7. phase2-vs
  8+. everything else (Supliful auto-generated label images) — preserved relative order
"""
import json, os, re, urllib.request

TOKEN = os.environ["SHOPIFY_TOKEN"]
SHOP = "leaf-and-bird.myshopify.com"

PRODUCTS = [
    "pdrn-brightening-serum", "vitamin-glow-serum", "vitamin-c-serum",
    "peptide-eye-gel-cream", "sleep-plus-collagen-cream",
    "tallow-cream-peaceful-night", "tallow-cream-lemongrass-lavender",
    "tallow-cream-orange-bergamot", "dead-sea-mud",
]

def basename(src):
    return src.split("?")[0].split("/")[-1].lower()

def bucket(name):
    if "phase2-hero" in name or name.endswith("_cover.png"): return 1
    if any(k in name for k in ["lifestyle-linen", "lifestyle-marble", "lifestyle-bedside", "lifestyle-spa"]): return 2
    if any(k in name for k in ["lifestyle-in-hand", "lifestyle-in-palm", "lifestyle-with-lid-off"]): return 3
    if "macro-" in name: return 4
    if "texture-" in name: return 5
    if "phase2-3step" in name or name == "phase2-3step.jpg": return 6
    if "phase2-vs" in name: return 7
    return 8

def api(method, path, body=None):
    headers = {"X-Shopify-Access-Token": TOKEN}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(f"https://{SHOP}/admin/api/2024-10{path}",
                                 data=data, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(req).read())

for handle in PRODUCTS:
    p = api("GET", f"/products.json?handle={handle}&fields=id,images")["products"][0]
    pid = p["id"]
    images = p["images"]
    # Sort by (bucket, original position) so ties (e.g., multiple label images) keep relative order
    sorted_imgs = sorted(images, key=lambda i: (bucket(basename(i["src"])), i["position"]))
    print(f"=== {handle} ===")
    new_images = []
    for idx, img in enumerate(sorted_imgs, start=1):
        new_images.append({"id": img["id"], "position": idx})
        print(f"  {idx:2d}  was={img['position']:2d}  {basename(img['src'])}")
    api("PUT", f"/products/{pid}.json", {"product": {"id": pid, "images": new_images}})
    print(f"  → PUT applied ({len(new_images)} images)")
    print()
