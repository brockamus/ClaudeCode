"""Update bundle discount % (10/15 → 15/25) + rename to Duo/Trio across 3 templates.
Pull each live template, modify the quantity_bundle block settings, push back.
"""
import json, urllib.request

THEME_ID = 186951631147
TOKEN = "SHOPIFY_TOKEN_REDACTED"
URL = f"https://leaf-and-bird.myshopify.com/admin/api/2024-10/themes/{THEME_ID}/assets.json"


def fetch(key):
    req = urllib.request.Request(
        f"{URL}?asset%5Bkey%5D={key.replace('/', '%2F')}",
        headers={"X-Shopify-Access-Token": TOKEN},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["asset"]["value"]


def push(key, value):
    req = urllib.request.Request(
        URL,
        data=json.dumps({"asset": {"key": key, "value": value}}).encode(),
        method="PUT",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


UPDATES = {
    "discount_pct_2": 15,
    "discount_pct_3": 25,
    "title_2": "Duo",
    "title_3": "Trio",
}

for tmpl in ("product.serum.json", "product.tallow-body.json", "product.specialty.json"):
    raw = fetch(f"templates/{tmpl}")
    data = json.loads(raw)
    sec = next(iter(data["sections"].values()))
    target_block_key = None
    for bk, bv in sec.get("blocks", {}).items():
        if bv.get("type") == "quantity_bundle":
            target_block_key = bk
            break
    if not target_block_key:
        print(f"  WARN: no quantity_bundle in {tmpl}, skipping")
        continue
    s = sec["blocks"][target_block_key]["settings"]
    before = {k: s.get(k, "(unset)") for k in UPDATES}
    s.update(UPDATES)
    push(f"templates/{tmpl}", json.dumps(data, indent=2))
    print(f"  {tmpl}  block={target_block_key}")
    for k, v in UPDATES.items():
        print(f"    {k}: {before[k]} → {v}")
