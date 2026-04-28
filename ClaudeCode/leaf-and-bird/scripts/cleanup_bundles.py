"""Clean up the 6 new bundles: fix handles, prices, compare-at, SKUs, tags, type.
Also add them to /collections/bundles (id 526848950571) and verify components on the
existing 2 are properly attached.
"""
import json, urllib.request, time

TOKEN = "SHOPIFY_TOKEN_REDACTED"
SHOP = "leaf-and-bird.myshopify.com"
GQL = f"https://{SHOP}/admin/api/2024-10/graphql.json"
REST = f"https://{SHOP}/admin/api/2024-10"
BUNDLES_COLL_ID = 526848950571


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(GQL, data=body, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def rest_get(path):
    req = urllib.request.Request(f"{REST}{path}", headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def rest_put(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{REST}{path}", data=data, method="PUT",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read())


def rest_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{REST}{path}", data=data, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read else None


# Bundles to clean up — pulled from Shopify product list
TARGETS = [
    {"product_id": 10356476838187, "current_handle": "the-first-drop-duo",
     "handle": "first-drop-duo", "price": 36.85, "compare_at": 51.90,
     "sku": "LB-BUNDLE-FIRSTDROP",
     "tags": "bundle, vegan, first-time, duo, gift-set, sensitive"},
    {"product_id": 10356479787307, "current_handle": "the-brightening-set",
     "handle": "brightening-set", "price": 53.83, "compare_at": 76.90,
     "sku": "LB-BUNDLE-BRIGHT",
     "tags": "bundle, vegan, brightening, dark-spots, hyperpigmentation"},
    {"product_id": 10356481655083, "current_handle": "the-pregnancy-safe-edit",
     "handle": "pregnancy-safe-edit", "price": 57.13, "compare_at": 87.89,
     "sku": "LB-BUNDLE-PREG",
     "tags": "bundle, vegan, pregnancy-safe, sensitive, postpartum, gift-set"},
    {"product_id": 10356483391787, "current_handle": "the-tallow-trio",
     "handle": "tallow-trio", "price": 56.70, "compare_at": 81.00,
     "sku": "LB-BUNDLE-TALLOW3",
     "tags": "bundle, ancestral, tallow, sensitive, scents"},
    {"product_id": 10356485128491, "current_handle": "the-anti-aging-stack",
     "handle": "anti-aging-stack", "price": 70.69, "compare_at": 100.98,
     "sku": "LB-BUNDLE-AGING",
     "tags": "bundle, vegan, anti-aging, premium, peptides, gift-set"},
    {"product_id": 10356487029035, "current_handle": "the-full-ritual",
     "handle": "full-ritual", "price": 102.43, "compare_at": 152.88,
     "sku": "LB-BUNDLE-FULL",
     "tags": "bundle, vegan, founders, full-routine, premium, gift-set"},
]

# Fix product fields + variant pricing for each
for t in TARGETS:
    pid = t["product_id"]
    p = rest_get(f"/products/{pid}.json")["product"]
    var_id = p["variants"][0]["id"]

    # Update product (handle, tags, type, vendor, status)
    s1, _ = rest_put(f"/products/{pid}.json", {
        "product": {
            "id": pid,
            "handle": t["handle"],
            "tags": t["tags"],
            "product_type": "Skincare Set",
            "vendor": "Leaf & Bird",
            "status": "draft",
        }
    })
    # Update variant (price, compare_at, sku)
    s2, _ = rest_put(f"/variants/{var_id}.json", {
        "variant": {
            "id": var_id,
            "price": str(t["price"]),
            "compare_at_price": str(t["compare_at"]),
            "sku": t["sku"],
        }
    })
    # Add to bundles collection
    s3, _ = rest_post("/collects.json", {
        "collect": {"product_id": pid, "collection_id": BUNDLES_COLL_ID}
    })
    print(f"  /{t['handle']:<24}  product={s1}  variant={s2}  collect={s3}  ${t['price']}/${t['compare_at']}")

# Verify existing 2 bundles' components via productBundle query
print("\nVerifying components on existing 2 bundles…")
verify_q = """
query ($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Product {
      id title handle
      bundleComponents(first: 10) {
        edges { node { quantity componentProduct { title handle } } }
      }
    }
  }
}
"""
res = gql(verify_q, {"ids": [
    "gid://shopify/Product/10355718947115",  # Radiance
    "gid://shopify/Product/10355719176491",  # Hydrate
]})
for n in res.get("data", {}).get("nodes", []):
    if not n: continue
    bcs = (n.get("bundleComponents") or {}).get("edges", [])
    print(f"  /{n['handle']}: {len(bcs)} component(s)")
    for e in bcs:
        c = e["node"]
        print(f"    - {c['quantity']}x {c['componentProduct']['handle']}")

print("\nDONE")
