"""Create metafield definitions for Leaf & Bird SEO content storage.

Note: MetafieldDefinition is a GraphQL-only resource in the Shopify Admin API.
This script uses the GraphQL endpoint directly (not the REST helper).
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error


SHOP = os.environ["SHOPIFY_SHOP"]
TOKEN = os.environ["SHOPIFY_TOKEN"]
API_VERSION = "2024-10"
GQL_URL = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"


DEFINITIONS = [
    # Collection metafields (money page content)
    {"owner": "COLLECTION", "namespace": "seo", "key": "h1", "name": "SEO H1",
     "type": "single_line_text_field", "description": "Collection page H1 (overrides title)."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "intro", "name": "SEO intro",
     "type": "multi_line_text_field", "description": "Hero paragraph (40-65 words)."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "body_modules", "name": "SEO body modules",
     "type": "json", "description": "Ordered array of {type, content} modules for diverse page rendering."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} — source of truth for FAQPage schema."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "meta_title", "name": "Meta title",
     "type": "single_line_text_field", "description": "SEO meta title override."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "meta_description", "name": "Meta description",
     "type": "multi_line_text_field", "description": "SEO meta description override."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "primary_keyword", "name": "Primary keyword",
     "type": "single_line_text_field", "description": "Primary target keyword for this page."},
    # Product metafields (FAQ + free-from)
    {"owner": "PRODUCT", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} — source of truth for product FAQPage schema."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "free_from", "name": "Free from list",
     "type": "json", "description": "Array of strings (e.g., ['parabens','sulfates','fragrance'])."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "meta_title", "name": "Meta title",
     "type": "single_line_text_field", "description": "SEO meta title override."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "meta_description", "name": "Meta description",
     "type": "multi_line_text_field", "description": "SEO meta description override."},
    # Article metafields
    {"owner": "ARTICLE", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} for article FAQPage schema."},
    {"owner": "ARTICLE", "namespace": "seo", "key": "primary_keyword", "name": "Primary keyword",
     "type": "single_line_text_field", "description": "Primary target keyword for this article."},
]


CREATE_MUTATION = """
mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition {
      id
      namespace
      key
      ownerType
    }
    userErrors {
      field
      message
      code
    }
  }
}
"""


def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        GQL_URL,
        data=payload,
        method="POST",
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body_text}")
    raise RuntimeError("Max retries exceeded")


def main():
    ok_count = 0
    skip_count = 0
    fail_count = 0

    for d in DEFINITIONS:
        variables = {
            "definition": {
                "namespace": d["namespace"],
                "key": d["key"],
                "name": d["name"],
                "type": d["type"],
                "ownerType": d["owner"],
                "description": d["description"],
            }
        }
        try:
            result = gql(CREATE_MUTATION, variables)
        except RuntimeError as e:
            print(f"FAIL {d['owner']}.{d['namespace']}.{d['key']}: {e}")
            fail_count += 1
            sys.exit(1)

        data = result.get("data", {}).get("metafieldDefinitionCreate", {})
        errors = data.get("userErrors", [])

        if errors:
            # Check if the error indicates the definition already exists
            codes = [e.get("code", "").upper() for e in errors]
            messages = " ".join(e.get("message", "").lower() for e in errors)
            if any(c in ("TAKEN", "ALREADY_EXISTS") for c in codes) or \
               "taken" in messages or "already" in messages or "exists" in messages:
                print(f"SKIP {d['owner']}.{d['namespace']}.{d['key']} (exists)")
                skip_count += 1
            else:
                err_detail = "; ".join(f"{e.get('field')}: {e.get('message')}" for e in errors)
                print(f"FAIL {d['owner']}.{d['namespace']}.{d['key']}: {err_detail}")
                fail_count += 1
                sys.exit(1)
        else:
            print(f"OK   {d['owner']}.{d['namespace']}.{d['key']}")
            ok_count += 1

    print(f"\nDone: {ok_count} created, {skip_count} skipped, {fail_count} failed")


if __name__ == "__main__":
    main()
