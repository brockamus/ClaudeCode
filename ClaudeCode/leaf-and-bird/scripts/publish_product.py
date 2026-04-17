"""Publish a drafted product page (body, title, handle, metafields, meta tags) to Shopify."""
import json
import sys
import pathlib
import shopify_api


def publish(draft_path):
    d = json.loads(pathlib.Path(draft_path).read_text(encoding="utf-8"))
    pid = d["product_id"]

    # 1. Update product core fields
    update = {"product": {
        "id": pid,
        "title": d["title"],
        "body_html": d["body_html"],
        "product_type": d.get("product_type") or None,
        "tags": d.get("tags") or None,
    }}
    if d.get("new_handle"):
        update["product"]["handle"] = d["new_handle"]
    resp = shopify_api.put(f"/products/{pid}.json", update)
    print(f"Updated product {pid}: {resp['product']['title']}")

    # 2. Set meta_title + meta_description via Shopify SEO fields (handled via metafields `global.title_tag` / `global.description_tag`)
    if d.get("meta_title"):
        _upsert_metafield(pid, "products", "global", "title_tag", "single_line_text_field", d["meta_title"])
    if d.get("meta_description"):
        _upsert_metafield(pid, "products", "global", "description_tag", "multi_line_text_field", d["meta_description"])

    # 3. Set FAQ metafield
    if d.get("faq_json"):
        _upsert_metafield(pid, "products", "seo", "faq_json", "json", json.dumps(d["faq_json"]))

    # 4. Set free_from metafield
    if d.get("free_from"):
        _upsert_metafield(pid, "products", "seo", "free_from", "json", json.dumps(d["free_from"]))

    print("Done.")


def _upsert_metafield(owner_id, owner_resource, namespace, key, type_, value):
    existing = shopify_api.get(f"/{owner_resource}/{owner_id}/metafields.json")["metafields"]
    for m in existing:
        if m["namespace"] == namespace and m["key"] == key:
            shopify_api.put(f"/metafields/{m['id']}.json",
                            {"metafield": {"id": m["id"], "value": value, "type": type_}})
            print(f"  updated metafield {namespace}.{key}")
            return
    shopify_api.post(f"/{owner_resource}/{owner_id}/metafields.json",
                     {"metafield": {"namespace": namespace, "key": key, "type": type_, "value": value}})
    print(f"  created metafield {namespace}.{key}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publish_product.py <path/to/draft.json>")
        sys.exit(2)
    publish(sys.argv[1])
