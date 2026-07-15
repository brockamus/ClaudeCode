"""Ad-hoc: pull 2026 YTD orders and summarize by day for the profit tracker."""
import shopify_api as s
from collections import defaultdict
from datetime import datetime, timezone, timedelta

# Shop is America/Chicago. Use offsets that cover the YTD window.
MIN = "2026-01-01T00:00:00-06:00"
MAX = "2026-06-17T00:00:00-05:00"

cnt = s.get("/orders/count.json", {"status": "any", "created_at_min": MIN, "created_at_max": MAX})
print("Order count YTD 2026:", cnt)

# Pull orders (single page; bump if needed)
params = {
    "status": "any",
    "created_at_min": MIN,
    "created_at_max": MAX,
    "limit": 250,
    "fields": "id,name,created_at,processed_at,financial_status,current_total_price,total_price,subtotal_price,total_discounts,total_tax,line_items,refunds",
}
data = s.get("/orders.json", params)
orders = data.get("orders", [])
print("Orders fetched:", len(orders))

CT = timezone(timedelta(hours=-6))  # approx Central; good enough for day bucket display

by_day = defaultdict(lambda: {"orders": 0, "revenue": 0.0})
for o in orders:
    # bucket by created_at converted to Central
    dt = datetime.fromisoformat(o["created_at"]).astimezone(CT)
    day = dt.strftime("%Y-%m-%d")
    by_day[day]["orders"] += 1
    by_day[day]["revenue"] += float(o.get("total_price") or 0)

print("\n=== Daily summary (Central) ===")
for day in sorted(by_day):
    d = by_day[day]
    print(f"{day}  orders={d['orders']}  revenue=${d['revenue']:.2f}")

print("\n=== Raw order detail ===")
for o in sorted(orders, key=lambda x: x["created_at"]):
    dt = datetime.fromisoformat(o["created_at"]).astimezone(CT)
    print(f"{o['name']}  {dt.strftime('%Y-%m-%d %H:%M')}  total=${o.get('total_price')}  subtotal=${o.get('subtotal_price')}  disc=${o.get('total_discounts')}  tax=${o.get('total_tax')}  status={o.get('financial_status')}")
    for li in o.get("line_items", []):
        print(f"    - {li.get('sku') or '(no sku)'}  x{li.get('quantity')}  {li.get('title')}  @${li.get('price')}")
