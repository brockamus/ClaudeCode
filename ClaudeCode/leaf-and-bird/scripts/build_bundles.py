"""Build out the L&B bundle catalog end-to-end via the Shopify Bundles API."""
import os
import json, time, urllib.request, urllib.error

TOKEN = os.environ["SHOPIFY_TOKEN"]  # source scripts/.env first
SHOP = "leaf-and-bird.myshopify.com"
GQL = f"https://{SHOP}/admin/api/2024-10/graphql.json"
REST = f"https://{SHOP}/admin/api/2024-10"


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
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read())


# ─────────────────────────────────────────────────────────
# Component data (option IDs hardcoded per query result)
# ─────────────────────────────────────────────────────────

COMPONENTS = {
    "pdrn":           {"pid": 10325332066603, "opt_id": "gid://shopify/ProductOption/12902290129195"},
    "tallow_ll":      {"pid": 10325459599659, "opt_id": "gid://shopify/ProductOption/12902441648427"},
    "tallow_ob":      {"pid": 10325331902763, "opt_id": "gid://shopify/ProductOption/12902289965355"},
    "tallow_pn":      {"pid": 10325459763499, "opt_id": "gid://shopify/ProductOption/12902441812267"},
    "eye_gel":        {"pid": 10325332721963, "opt_id": "gid://shopify/ProductOption/12902290784555"},
    "sleep_collagen": {"pid": 10325332361515, "opt_id": "gid://shopify/ProductOption/12902290424107"},
    "vit_c":          {"pid": 10325459960107, "opt_id": "gid://shopify/ProductOption/12902442008875"},
    "vit_glow":       {"pid": 10325332230443, "opt_id": "gid://shopify/ProductOption/12902290293035"},
    "dead_sea":       {"pid": 10325332558123, "opt_id": "gid://shopify/ProductOption/12902290620715"},
}

# Pull pricing
print("Phase 1: Component pricing…")
for k, c in COMPONENTS.items():
    p = rest_get(f"/products/{c['pid']}.json")["product"]
    v = p["variants"][0]
    c["variant_id"] = v["id"]
    c["price"] = float(v["price"])
    c["compare_at"] = float(v.get("compare_at_price") or v["price"])
    c["handle"] = p["handle"]


def make_components(component_keys):
    return [
        {
            "quantity": 1,
            "productId": f"gid://shopify/Product/{COMPONENTS[k]['pid']}",
            "optionSelections": [
                {"componentOptionId": COMPONENTS[k]["opt_id"], "name": "Title", "values": ["Default Title"]}
            ],
        }
        for k in component_keys
    ]


def calc_pricing(component_keys, discount_pct):
    total = sum(COMPONENTS[k]["compare_at"] for k in component_keys)
    return round(total * (1 - discount_pct/100), 2), round(total, 2)


def poll_operation(op_id):
    """Poll a productBundleOperation until COMPLETE/FAILED."""
    q = """query ($id: ID!) {
      productOperation(id: $id) {
        id status
        ... on ProductBundleOperation {
          product { id title handle variants(first:1){edges{node{id sku}}} }
          userErrors { field message }
        }
      }
    }"""
    for i in range(30):
        time.sleep(2)
        d = gql(q, {"id": op_id}).get("data", {}).get("productOperation")
        if not d:
            continue
        if d["status"] in ("COMPLETE", "ACTIVE"):
            return d
        if d["status"] == "FAILED":
            print(f"  FAILED: {d.get('userErrors')}")
            return d
    print("  TIMEOUT polling operation")
    return None


# ─────────────────────────────────────────────────────────
# Phase 2: Convert existing 2 bundles
# ─────────────────────────────────────────────────────────

EXISTING = {
    "Radiance":  {"product_id": 10355718947115, "variant_id": 53357297860907,
                  "components": ["dead_sea", "vit_glow", "sleep_collagen"]},
    "Hydrate":   {"product_id": 10355719176491, "variant_id": 53357298123051,
                  "components": ["pdrn", "tallow_ll", "eye_gel"]},
}

UPDATE_M = """
mutation ($productId: ID!, $components: [ProductBundleComponentInput!]!) {
  productBundleUpdate(input: {productId: $productId, components: $components}) {
    productBundleOperation { id status }
    userErrors { field message }
  }
}
"""

print("\nPhase 2: convert existing 2 bundles…")
for name, info in EXISTING.items():
    pid_gid = f"gid://shopify/Product/{info['product_id']}"
    res = gql(UPDATE_M, {"productId": pid_gid, "components": make_components(info["components"])})
    op = res.get("data", {}).get("productBundleUpdate", {})
    if op.get("userErrors"):
        print(f"  {name}: ERR {op['userErrors']}")
        continue
    op_data = op.get("productBundleOperation")
    if not op_data:
        print(f"  {name}: no operation returned")
        continue
    print(f"  {name}: op={op_data['id']} status={op_data['status']}")
    poll_operation(op_data["id"])
    print(f"    ✓ converted to bundle")


# ─────────────────────────────────────────────────────────
# Phase 3: Create 6 new bundles
# ─────────────────────────────────────────────────────────

NEW = [
    {"key":"first-drop-duo", "title":"The First Drop Duo", "handle":"first-drop-duo",
     "components":["vit_glow","tallow_ll"], "discount_pct":29, "sku":"LB-BUNDLE-FIRSTDROP",
     "tags":"bundle, vegan, first-time, duo, gift-set, sensitive"},
    {"key":"brightening-set", "title":"The Brightening Set", "handle":"brightening-set",
     "components":["pdrn","vit_glow","vit_c"], "discount_pct":30, "sku":"LB-BUNDLE-BRIGHT",
     "tags":"bundle, vegan, brightening, dark-spots, hyperpigmentation"},
    {"key":"pregnancy-safe-edit", "title":"The Pregnancy-Safe Edit", "handle":"pregnancy-safe-edit",
     "components":["tallow_ll","eye_gel","vit_glow"], "discount_pct":35, "sku":"LB-BUNDLE-PREG",
     "tags":"bundle, vegan, pregnancy-safe, sensitive, postpartum, gift-set"},
    {"key":"tallow-trio", "title":"The Tallow Trio", "handle":"tallow-trio",
     "components":["tallow_ll","tallow_ob","tallow_pn"], "discount_pct":30, "sku":"LB-BUNDLE-TALLOW3",
     "tags":"bundle, ancestral, tallow, sensitive, scents"},
    {"key":"anti-aging-stack", "title":"The Anti-Aging Stack", "handle":"anti-aging-stack",
     "components":["pdrn","eye_gel","sleep_collagen"], "discount_pct":30, "sku":"LB-BUNDLE-AGING",
     "tags":"bundle, vegan, anti-aging, premium, peptides, gift-set"},
    {"key":"full-ritual", "title":"The Full Ritual", "handle":"full-ritual",
     "components":["pdrn","tallow_ll","eye_gel","vit_glow","sleep_collagen"], "discount_pct":33, "sku":"LB-BUNDLE-FULL",
     "tags":"bundle, vegan, founders, full-routine, premium, gift-set"},
]

CREATE_M = """
mutation ($input: ProductBundleCreateInput!) {
  productBundleCreate(input: $input) {
    productBundleOperation { id status }
    userErrors { field message }
  }
}
"""

print("\nPhase 3: create 6 new bundles…")
created_bundles = []
for b in NEW:
    price, compare_at = calc_pricing(b["components"], b["discount_pct"])
    print(f"  {b['title']}  list=${compare_at}  price=${price}  ({b['discount_pct']}% off)")
    res = gql(CREATE_M, {"input": {"title": b["title"], "components": make_components(b["components"])}})
    op = res.get("data", {}).get("productBundleCreate", {})
    if op.get("userErrors"):
        print(f"    ERR {op['userErrors']}")
        continue
    op_data = op.get("productBundleOperation")
    if not op_data:
        print(f"    no op returned: {res}")
        continue
    print(f"    op={op_data['id']} status={op_data['status']}")
    polled = poll_operation(op_data["id"])
    if not polled or polled["status"] != "COMPLETE":
        print(f"    failed or timed out")
        continue
    new_product = polled.get("product")
    if not new_product:
        print(f"    no product returned")
        continue
    new_pid_gid = new_product["id"]
    new_pid = int(new_pid_gid.split("/")[-1])
    new_variant_gid = new_product["variants"]["edges"][0]["node"]["id"]
    new_variant_id = int(new_variant_gid.split("/")[-1])
    print(f"    ✓ created product_id={new_pid} variant_id={new_variant_id}")

    # Update product details (handle, tags, type, status=draft) + variant pricing
    rest_put(f"/products/{new_pid}.json", {
        "product": {
            "id": new_pid,
            "handle": b["handle"],
            "tags": b["tags"],
            "product_type": "Skincare Set",
            "vendor": "Leaf & Bird",
            "status": "draft",
        }
    })
    rest_put(f"/variants/{new_variant_id}.json", {
        "variant": {
            "id": new_variant_id,
            "price": str(price),
            "compare_at_price": str(compare_at),
            "sku": b["sku"],
        }
    })
    created_bundles.append({"key": b["key"], "product_id": new_pid, "variant_id": new_variant_id,
                            "price": price, "compare_at": compare_at, "handle": b["handle"]})
    print(f"    updated handle={b['handle']} price=${price} compare=${compare_at} sku={b['sku']}")
    time.sleep(0.5)


# ─────────────────────────────────────────────────────────
# Phase 4: Create /collections/bundles + add all 8
# ─────────────────────────────────────────────────────────

print("\nPhase 4: create /collections/bundles…")
ALL_BUNDLE_PIDS = [10355718947115, 10355719176491] + [b["product_id"] for b in created_bundles]
status, d = rest_post("/custom_collections.json", {
    "custom_collection": {
        "title": "Bundles",
        "handle": "bundles",
        "body_html": "<p>Skincare sets and routines, priced for ritual.</p>",
        "published": False,  # keep unpublished until reviewed
    }
})
coll = d.get("custom_collection") or d.get("collection")
if not coll:
    # Already exists?
    print(f"  collection create response: {d}")
else:
    coll_id = coll["id"]
    print(f"  collection_id={coll_id} handle={coll['handle']}")
    for pid in ALL_BUNDLE_PIDS:
        s, dd = rest_post("/collects.json", {"collect": {"product_id": pid, "collection_id": coll_id}})
        print(f"    +product {pid} → {s}")

print("\nDONE")
print(f"Bundles created: {len(created_bundles)} new + 2 converted = {len(ALL_BUNDLE_PIDS)} total")
for b in created_bundles:
    print(f"  /products/{b['handle']} (id={b['product_id']}) ${b['price']} / ${b['compare_at']}")
