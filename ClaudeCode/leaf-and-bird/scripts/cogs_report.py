"""Pull per-SKU cost from Shopify and compute daily COGS for 2026 YTD orders."""
import shopify_api as s
from collections import defaultdict
from datetime import datetime, timezone, timedelta

MIN = "2026-01-01T00:00:00-06:00"
MAX = "2026-06-17T00:00:00-05:00"
CT = timezone(timedelta(hours=-6))

# 1) Build SKU/variant -> unit cost map from products + inventory items
prod = s.get("/products.json", {"limit": 250, "fields": "id,title,variants"})
variant_cost = {}      # variant_id -> cost
sku_cost = {}          # sku -> cost
inv_to_keys = {}       # inventory_item_id -> (variant_id, sku)
inv_ids = []
for p in prod.get("products", []):
    for v in p.get("variants", []):
        iid = v.get("inventory_item_id")
        if iid:
            inv_ids.append(iid)
            inv_to_keys[iid] = (v["id"], v.get("sku"))

# fetch inventory item costs in chunks
for i in range(0, len(inv_ids), 100):
    chunk = inv_ids[i:i+100]
    r = s.get("/inventory_items.json", {"ids": ",".join(str(x) for x in chunk), "limit": 100})
    for it in r.get("inventory_items", []):
        cost = it.get("cost")
        cost = float(cost) if cost not in (None, "") else None
        vid, sku = inv_to_keys.get(it["id"], (None, None))
        if vid is not None:
            variant_cost[vid] = cost
        if sku:
            sku_cost[sku] = cost

print("=== Per-SKU unit cost (from Shopify 'Cost per item') ===")
for sku, c in sorted(sku_cost.items()):
    print(f"  {sku}: {c}")

# 2) Pull orders and compute daily COGS
params = {
    "status": "any", "created_at_min": MIN, "created_at_max": MAX, "limit": 250,
    "fields": "id,name,created_at,line_items",
}
orders = s.get("/orders.json", params).get("orders", [])

by_day = defaultdict(float)
missing = set()
for o in orders:
    day = datetime.fromisoformat(o["created_at"]).astimezone(CT).strftime("%Y-%m-%d")
    for li in o.get("line_items", []):
        sku = li.get("sku")
        vid = li.get("variant_id")
        qty = li.get("quantity") or 0
        cost = variant_cost.get(vid)
        if cost is None:
            cost = sku_cost.get(sku)
        if cost is None:
            missing.add(f"{sku}/{vid}")
            continue
        by_day[day] += cost * qty

print("\n=== Daily COGS (Central) ===")
for day in sorted(by_day):
    print(f"{day}  COGS=${by_day[day]:.2f}")

# Monthly rollups
may = sum(v for d, v in by_day.items() if d.startswith("2026-05"))
jun = sum(v for d, v in by_day.items() if d.startswith("2026-06"))
print(f"\nMay COGS total: ${may:.2f}")
print(f"June COGS total: ${jun:.2f}")
if missing:
    print("\n!! Missing cost for:", missing)
