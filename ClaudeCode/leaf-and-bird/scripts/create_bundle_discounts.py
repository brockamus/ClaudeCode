"""Create the advertorial bundle discount codes via GraphQL.

Requires the custom app to have `write_discounts` (and `read_discounts`) scope.
Run:  python create_bundle_discounts.py

Creates:
  TALLOW2BUNDLE  -> 15% off the tallow cream, minimum quantity 2
  TALLOW3BUNDLE  -> 25% off the tallow cream, minimum quantity 3

Both are restricted to the Orange & Bergamot product so the code only ever
discounts that item, and gated by minimum quantity so they can't be abused
on a smaller order. Applied silently via the cart permalinks on the lander.
"""
import os, json, requests

SHOP = os.environ["SHOPIFY_SHOP"]
TOKEN = os.environ["SHOPIFY_TOKEN"]
API = "2024-10"
GQL = f"https://{SHOP}/admin/api/{API}/graphql.json"
HEAD = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

PRODUCT_GID = "gid://shopify/Product/10325331902763"  # Tallow Cream — Orange & Bergamot
STARTS_AT = "2026-06-24T00:00:00Z"

MUT = """
mutation create($code:String!, $title:String!, $pct:Float!, $minqty:UnsignedInt64!,
                $startsAt:DateTime!, $product:ID!){
  discountCodeBasicCreate(basicCodeDiscount:{
    title:$title,
    code:$code,
    startsAt:$startsAt,
    appliesOncePerCustomer:false,
    customerSelection:{ all:true },
    minimumRequirement:{ quantity:{ greaterThanOrEqualToQuantity:$minqty } },
    customerGets:{
      value:{ percentage:$pct },
      items:{ products:{ productsToAdd:[$product] } }
    },
    combinesWith:{ orderDiscounts:false, productDiscounts:false, shippingDiscounts:true }
  }){
    codeDiscountNode{ id }
    userErrors{ field message }
  }
}
"""

TIERS = [
    {"code": "TALLOW2BUNDLE", "title": "Tallow 2-Jar Bundle (15% off)", "pct": 0.15, "minqty": "2"},
    {"code": "TALLOW3BUNDLE", "title": "Tallow 3-Jar Bundle (25% off)", "pct": 0.25, "minqty": "3"},
]


def run():
    for t in TIERS:
        variables = {
            "code": t["code"], "title": t["title"], "pct": t["pct"],
            "minqty": t["minqty"], "startsAt": STARTS_AT, "product": PRODUCT_GID,
        }
        r = requests.post(GQL, headers=HEAD, json={"query": MUT, "variables": variables})
        data = r.json()
        if data.get("errors"):
            print(f"[{t['code']}] GraphQL errors:", json.dumps(data["errors"]))
            continue
        res = data["data"]["discountCodeBasicCreate"]
        if res["userErrors"]:
            print(f"[{t['code']}] userErrors:", json.dumps(res["userErrors"]))
        else:
            print(f"[{t['code']}] created: {res['codeDiscountNode']['id']}")


if __name__ == "__main__":
    run()
